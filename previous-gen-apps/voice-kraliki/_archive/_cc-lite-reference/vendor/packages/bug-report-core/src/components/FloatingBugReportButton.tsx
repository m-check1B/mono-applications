import React from 'react'
import { useBugReport } from './BugReportProvider'
import { Button } from '@unified/ui-core'
import { Bug } from 'lucide-react'
import { cn } from '@unified/ui-core'

export function FloatingBugReportButton() {
  const { setIsOpen, config, pendingReportsCount } = useBugReport()
  
  if (!config.enabled) {
    return null
  }

  const positionClasses = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4'
  }

  return (
    <div
      className={cn(
        'fixed z-50',
        positionClasses[config.position || 'bottom-right']
      )}
    >
      <Button
        onClick={() => setIsOpen(true)}
        size="icon"
        variant="default"
        className="rounded-full shadow-lg hover:shadow-xl transition-shadow relative"
        aria-label="Report a bug"
      >
        <Bug className="h-5 w-5" />
        {pendingReportsCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {pendingReportsCount}
          </span>
        )}
      </Button>
    </div>
  )
}