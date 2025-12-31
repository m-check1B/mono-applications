/**
 * Convert a data URL to a Blob
 */
export function dataURLtoBlob(dataURL: string): Blob {
  try {
    const arr = dataURL.split(',');
    const mime = arr[0].match(/:(.*?);/)?.[1] || 'application/octet-stream';
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    
    return new Blob([u8arr], { type: mime });
  } catch (error) {
    console.error('Error converting data URL to blob:', error);
    return new Blob([]);
  }
}

/**
 * Show a notification to the user
 */
export function showNotification(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
  if (typeof window === 'undefined') return;
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `bug-report-notification bug-report-notification-${type}`;
  notification.textContent = message;
  
  // Style the notification
  notification.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 4px;
    font-size: 14px;
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
    ${type === 'success' ? 'background: #4CAF50; color: white;' : ''}
    ${type === 'error' ? 'background: #f44336; color: white;' : ''}
    ${type === 'info' ? 'background: #2196F3; color: white;' : ''}
  `;
  
  document.body.appendChild(notification);
  
  // Remove after 5 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 5000);
}

/**
 * Capture current viewport as screenshot
 */
export async function captureScreenshot(): Promise<Blob | null> {
  if (typeof window === 'undefined') return null;
  
  try {
    // Use html2canvas if available
    if ((window as any).html2canvas) {
      const canvas = await (window as any).html2canvas(document.body);
      return new Promise((resolve) => {
        canvas.toBlob((blob: Blob | null) => {
          resolve(blob);
        });
      });
    }
    
    // Fallback to browser screenshot API if available
    if ('mediaDevices' in navigator && 'getDisplayMedia' in navigator.mediaDevices) {
      try {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: { mediaSource: 'screen' } as any
        });
        
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(video, 0, 0);
        
        stream.getTracks().forEach(track => track.stop());
        
        return new Promise((resolve) => {
          canvas.toBlob((blob) => {
            resolve(blob);
          });
        });
      } catch (error) {
        console.warn('Screen capture failed:', error);
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error capturing screenshot:', error);
    return null;
  }
}

/**
 * Get browser and OS information
 */
export function getBrowserInfo(): {
  browser: string;
  version: string;
  os: string;
  platform: string;
} {
  const userAgent = navigator.userAgent;
  let browser = 'Unknown';
  let version = 'Unknown';
  let os = 'Unknown';
  const platform = navigator.platform;
  
  // Detect browser
  if (userAgent.indexOf('Firefox') > -1) {
    browser = 'Firefox';
    version = userAgent.match(/Firefox\/(\d+\.?\d*)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('Chrome') > -1) {
    browser = 'Chrome';
    version = userAgent.match(/Chrome\/(\d+\.?\d*)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('Safari') > -1) {
    browser = 'Safari';
    version = userAgent.match(/Version\/(\d+\.?\d*)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('Edge') > -1) {
    browser = 'Edge';
    version = userAgent.match(/Edge\/(\d+\.?\d*)/)?.[1] || 'Unknown';
  }
  
  // Detect OS
  if (userAgent.indexOf('Windows') > -1) {
    os = 'Windows';
  } else if (userAgent.indexOf('Mac') > -1) {
    os = 'macOS';
  } else if (userAgent.indexOf('Linux') > -1) {
    os = 'Linux';
  } else if (userAgent.indexOf('Android') > -1) {
    os = 'Android';
  } else if (userAgent.indexOf('iOS') > -1) {
    os = 'iOS';
  }
  
  return { browser, version, os, platform };
}

/**
 * Collect console errors for bug reports
 */
export function setupErrorCollection(): { getErrors: () => string[] } {
  const errors: string[] = [];
  const maxErrors = 50;
  
  if (typeof window === 'undefined') {
    return { getErrors: () => [] };
  }
  
  // Capture console errors
  const originalError = console.error;
  console.error = function(...args) {
    const errorMessage = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' ');
    
    errors.push(`[${new Date().toISOString()}] ${errorMessage}`);
    
    // Keep only last N errors
    if (errors.length > maxErrors) {
      errors.shift();
    }
    
    // Call original console.error
    originalError.apply(console, args);
  };
  
  // Capture unhandled errors
  window.addEventListener('error', (event) => {
    const errorMessage = `Unhandled error: ${event.message} at ${event.filename}:${event.lineno}:${event.colno}`;
    errors.push(`[${new Date().toISOString()}] ${errorMessage}`);
    
    if (errors.length > maxErrors) {
      errors.shift();
    }
  });
  
  // Capture unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    const errorMessage = `Unhandled promise rejection: ${event.reason}`;
    errors.push(`[${new Date().toISOString()}] ${errorMessage}`);
    
    if (errors.length > maxErrors) {
      errors.shift();
    }
  });
  
  return {
    getErrors: () => [...errors]
  };
}

/**
 * Get app version information
 */
export function getAppVersion(): {
  version: string;
  environment: 'development' | 'staging' | 'production' | 'alpha' | 'beta';
} {
  // Try to get from meta tags
  if (typeof document !== 'undefined') {
    const versionMeta = document.querySelector('meta[name="app-version"]');
    const envMeta = document.querySelector('meta[name="app-environment"]');
    
    if (versionMeta || envMeta) {
      return {
        version: versionMeta?.getAttribute('content') || 'unknown',
        environment: (envMeta?.getAttribute('content') as any) || 'production'
      };
    }
  }
  
  // Try to get from window object
  if (typeof window !== 'undefined' && (window as any).APP_VERSION) {
    return {
      version: (window as any).APP_VERSION,
      environment: (window as any).APP_ENV || 'production'
    };
  }
  
  // Fallback to default values
  return {
    version: 'unknown',
    environment: 'production'
  };
}