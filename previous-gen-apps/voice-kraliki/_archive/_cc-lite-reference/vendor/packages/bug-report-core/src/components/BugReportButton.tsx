import React from 'react'
import { useBugReport } from './BugReportProvider'
import { Button, ButtonProps } from '@unified/ui-core'
import { Bug } from 'lucide-react'

export interface BugReportButtonProps extends Omit<ButtonProps, 'onClick'> {
  showIcon?: boolean
  showPendingCount?: boolean
}

export function BugReportButton({ 
  children,
  showIcon = true,
  showPendingCount = true,
  ...props 
}: BugReportButtonProps) {
  const { setIsOpen, pendingReportsCount, config } = useBugReport()
  
  if (!config.enabled) {
    return null
  }

  return (
    <Button
      onClick={() => setIsOpen(true)}
      {...props}
    >
      {showIcon && <Bug className="mr-2 h-4 w-4" />}
      {children || 'Report Bug'}
      {showPendingCount && pendingReportsCount > 0 && (
        <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
          {pendingReportsCount}
        </span>
      )}
    </Button>
  )
}