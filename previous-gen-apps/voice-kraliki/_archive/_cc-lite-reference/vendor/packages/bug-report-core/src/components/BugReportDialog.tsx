import React, { useState, useRef, useEffect } from 'react'
import { useBugReport } from './BugReportProvider'
import { BugReport } from '../types'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@unified/ui-core'
import { Button } from '@unified/ui-core'
import { Input } from '@unified/ui-core'
import { Textarea } from '@unified/ui-core'
import { Label } from '@unified/ui-core'
import { Alert, AlertDescription } from '@unified/ui-core'
import { Loader2, Camera, AlertCircle, CheckCircle } from 'lucide-react'

export function BugReportDialog() {
  const {
    isOpen,
    setIsOpen,
    submitReport,
    captureScreenshot,
    isSubmitting,
    config
  } = useBugReport()

  const [formData, setFormData] = useState<Partial<BugReport>>({
    message: '',
    name: '',
    url: typeof window !== 'undefined' ? window.location.href : ''
  })
  const [screenshot, setScreenshot] = useState<string | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [submitResult, setSubmitResult] = useState<{
    success: boolean
    message: string
  } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!isOpen) {
      // Reset form when dialog closes
      setFormData({
        message: '',
        name: '',
        url: typeof window !== 'undefined' ? window.location.href : ''
      })
      setScreenshot(null)
      setSubmitResult(null)
    }
  }, [isOpen])

  const handleCaptureScreenshot = async () => {
    setIsCapturing(true)
    try {
      const screenshotData = await captureScreenshot()
      if (screenshotData) {
        setScreenshot(screenshotData)
      }
    } catch (error) {
      console.error('Failed to capture screenshot:', error)
    } finally {
      setIsCapturing(false)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setScreenshot(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.message?.trim()) {
      setSubmitResult({
        success: false,
        message: 'Please describe the issue'
      })
      return
    }

    const report: BugReport = {
      message: formData.message,
      name: formData.name || 'Anonymous',
      url: formData.url || window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      environment: config.environments[0] || 'production',
      metadata: {
        screenshot: screenshot
      }
    }

    const result = await submitReport(report)
    
    if (result.success) {
      setSubmitResult({
        success: true,
        message: result.issueUrl 
          ? `Bug report submitted successfully! Track it at: ${result.issueUrl}`
          : 'Bug report submitted successfully!'
      })
      
      // Close dialog after 2 seconds on success
      setTimeout(() => {
        setIsOpen(false)
      }, 2000)
    } else {
      setSubmitResult({
        success: false,
        message: result.error || 'Failed to submit bug report'
      })
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Report a Bug</DialogTitle>
          <DialogDescription>
            Help us improve by reporting any issues you encounter
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Name (optional)</Label>
              <Input
                id="name"
                placeholder="Your name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                disabled={isSubmitting}
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="message">Describe the issue *</Label>
              <Textarea
                id="message"
                placeholder="What went wrong? Please be as specific as possible..."
                className="min-h-[100px]"
                value={formData.message}
                onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                disabled={isSubmitting}
                required
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="url">Page URL</Label>
              <Input
                id="url"
                value={formData.url}
                onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                disabled={isSubmitting}
              />
            </div>
            
            {config.captureScreenshot && (
              <div className="grid gap-2">
                <Label>Screenshot (optional)</Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleCaptureScreenshot}
                    disabled={isCapturing || isSubmitting}
                  >
                    {isCapturing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Capturing...
                      </>
                    ) : (
                      <>
                        <Camera className="mr-2 h-4 w-4" />
                        Capture Screen
                      </>
                    )}
                  </Button>
                  
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isSubmitting}
                  >
                    Upload Image
                  </Button>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileUpload}
                  />
                </div>
                
                {screenshot && (
                  <div className="relative mt-2">
                    <img
                      src={screenshot}
                      alt="Screenshot"
                      className="w-full rounded-md border"
                      style={{ maxHeight: '200px', objectFit: 'contain' }}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2"
                      onClick={() => setScreenshot(null)}
                    >
                      Remove
                    </Button>
                  </div>
                )}
              </div>
            )}
            
            {submitResult && (
              <Alert variant={submitResult.success ? 'default' : 'destructive'}>
                {submitResult.success ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>{submitResult.message}</AlertDescription>
              </Alert>
            )}
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Report'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}