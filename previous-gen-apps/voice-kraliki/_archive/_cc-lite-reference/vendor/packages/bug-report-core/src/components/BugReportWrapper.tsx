import React from 'react'
import { BugReportProvider, BugReportProviderProps } from './BugReportProvider'

/**
 * Wrapper component that provides bug reporting functionality to your app
 * This includes the provider, dialog, and optional floating button
 */
export function BugReportWrapper({ 
  children,
  ...props 
}: BugReportProviderProps) {
  return (
    <BugReportProvider {...props}>
      {children}
    </BugReportProvider>
  )
}