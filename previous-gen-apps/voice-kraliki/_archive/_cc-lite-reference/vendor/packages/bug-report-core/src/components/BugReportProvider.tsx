import React, { createContext, useContext, useEffect, useState } from 'react'
import { BugReportConfig, BugReport, BugReportResult } from '../types'
import { BugReportService } from '../service'
import { BugReportConfigManager } from '../config'

interface BugReportContextValue {
  config: BugReportConfig
  isOpen: boolean
  setIsOpen: (open: boolean) => void
  submitReport: (report: BugReport) => Promise<BugReportResult>
  pendingReportsCount: number
  captureScreenshot: () => Promise<string | null>
  isSubmitting: boolean
}

const BugReportContext = createContext<BugReportContextValue | undefined>(undefined)

export interface BugReportProviderProps {
  children: React.ReactNode
  config: Partial<BugReportConfig>
  showFloatingButton?: boolean
  customButton?: React.ReactNode
}

export function BugReportProvider({ 
  children, 
  config: userConfig,
  showFloatingButton = true,
  customButton
}: BugReportProviderProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [pendingReportsCount, setPendingReportsCount] = useState(0)
  const [service] = useState(() => new BugReportService())
  const [configManager] = useState(() => BugReportConfigManager.getInstance())

  // Initialize config
  useEffect(() => {
    configManager.updateConfig(userConfig)
  }, [userConfig, configManager])

  // Track pending reports
  useEffect(() => {
    const updatePendingCount = () => {
      const pending = service.getPendingReports()
      setPendingReportsCount(pending.length)
    }

    updatePendingCount()
    const interval = setInterval(updatePendingCount, 5000)
    return () => clearInterval(interval)
  }, [service])

  // Capture console errors if enabled
  useEffect(() => {
    const config = configManager.getConfig()
    if (!config.captureConsoleErrors) return

    const originalError = console.error
    console.error = (...args) => {
      originalError(...args)
      
      // Store error for potential bug report
      const errorMessage = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ')
      
      if (typeof window !== 'undefined') {
        const errors = window.__bugReportErrors || []
        errors.push({
          message: errorMessage,
          timestamp: new Date().toISOString(),
          stack: new Error().stack
        })
        window.__bugReportErrors = errors.slice(-10) // Keep last 10 errors
      }
    }

    return () => {
      console.error = originalError
    }
  }, [configManager])

  const captureScreenshot = async (): Promise<string | null> => {
    if (typeof window === 'undefined') return null
    
    try {
      // Check if we have html2canvas available
      const html2canvas = (window as any).html2canvas
      if (!html2canvas) {
        console.warn('html2canvas not available for screenshot capture')
        return null
      }

      const canvas = await html2canvas(document.body, {
        logging: false,
        useCORS: true,
        allowTaint: false,
        scale: 0.5, // Reduce size for storage
        width: window.innerWidth,
        height: window.innerHeight,
        windowWidth: window.innerWidth,
        windowHeight: window.innerHeight
      })

      return canvas.toDataURL('image/png')
    } catch (error) {
      console.error('Failed to capture screenshot:', error)
      return null
    }
  }

  const submitReport = async (report: BugReport): Promise<BugReportResult> => {
    setIsSubmitting(true)
    try {
      // Add metadata
      const enrichedReport: BugReport = {
        ...report,
        url: report.url || window.location.href,
        userAgent: report.userAgent || navigator.userAgent,
        timestamp: report.timestamp || new Date().toISOString(),
        environment: report.environment || (process.env.NODE_ENV as any) || 'development',
        metadata: {
          ...report.metadata,
          screenWidth: window.screen.width,
          screenHeight: window.screen.height,
          windowWidth: window.innerWidth,
          windowHeight: window.innerHeight,
          errors: window.__bugReportErrors || []
        }
      }

      // Try to submit immediately
      const result = await service.submitReport(enrichedReport)
      
      if (!result.success && navigator.onLine === false) {
        // Save for later if offline
        service.savePendingReport(enrichedReport)
        return {
          success: false,
          error: 'Report saved for submission when online'
        }
      }

      return result
    } finally {
      setIsSubmitting(false)
    }
  }

  const value: BugReportContextValue = {
    config: configManager.getConfig(),
    isOpen,
    setIsOpen,
    submitReport,
    pendingReportsCount,
    captureScreenshot,
    isSubmitting
  }

  return (
    <BugReportContext.Provider value={value}>
      {children}
      {showFloatingButton && !customButton && (
        <FloatingBugReportButton />
      )}
      {customButton}
      <BugReportDialog />
    </BugReportContext.Provider>
  )
}

export function useBugReport() {
  const context = useContext(BugReportContext)
  if (!context) {
    throw new Error('useBugReport must be used within BugReportProvider')
  }
  return context
}

// Import components after context is defined to avoid circular deps
import { FloatingBugReportButton } from './FloatingBugReportButton'
import { BugReportDialog } from './BugReportDialog'

// Extend window interface for error tracking
declare global {
  interface Window {
    __bugReportErrors?: Array<{
      message: string
      timestamp: string
      stack?: string
    }>
  }
}