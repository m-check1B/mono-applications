import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const spinnerVariants = cva("animate-spin", {
  variants: {
    size: {
      default: "h-4 w-4",
      sm: "h-3 w-3",
      lg: "h-6 w-6",
      xl: "h-8 w-8",
      "2xl": "h-12 w-12",
    },
    variant: {
      default: "text-muted-foreground",
      primary: "text-primary",
      secondary: "text-secondary",
      destructive: "text-destructive",
    },
  },
  defaultVariants: {
    size: "default",
    variant: "default",
  },
})

export interface SpinnerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {
  type?: "default" | "dots" | "pulse"
}

const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size, variant, type = "default", ...props }, ref) => {
    if (type === "dots") {
      return (
        <div
          ref={ref}
          className={cn("flex space-x-1", className)}
          {...props}
        >
          {[0, 1, 2].map((index) => (
            <div
              key={index}
              className={cn(
                "rounded-full animate-pulse",
                spinnerVariants({ size, variant }),
                "animate-bounce"
              )}
              style={{
                animationDelay: `${index * 0.1}s`,
                animationDuration: "1s",
              }}
            />
          ))}
        </div>
      )
    }

    if (type === "pulse") {
      return (
        <div
          ref={ref}
          className={cn(
            "rounded-full animate-pulse",
            spinnerVariants({ size, variant }),
            className
          )}
          style={{
            animationDuration: "1.5s",
          }}
          {...props}
        />
      )
    }

    // Default spinner (circular)
    return (
      <div
        ref={ref}
        className={cn(spinnerVariants({ size, variant }), className)}
        {...props}
      >
        <svg
          className="w-full h-full"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="m12 2a10 10 0 0 1 10 10h-4a6 6 0 0 0-6-6z"
          />
        </svg>
      </div>
    )
  }
)
Spinner.displayName = "Spinner"

// Spinner with text
export interface SpinnerWithTextProps extends SpinnerProps {
  text?: string
  position?: "top" | "bottom" | "left" | "right"
}

const SpinnerWithText = React.forwardRef<HTMLDivElement, SpinnerWithTextProps>(
  ({ text, position = "right", className, ...props }, ref) => {
    const flexDirection = {
      top: "flex-col-reverse",
      bottom: "flex-col",
      left: "flex-row-reverse",
      right: "flex-row",
    }

    const spacing = {
      top: "space-y-2",
      bottom: "space-y-2",
      left: "space-x-2",
      right: "space-x-2",
    }

    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center",
          flexDirection[position],
          spacing[position],
          className
        )}
      >
        <Spinner {...props} />
        {text && (
          <span className="text-sm text-muted-foreground">{text}</span>
        )}
      </div>
    )
  }
)
SpinnerWithText.displayName = "SpinnerWithText"

// Loading overlay component
export interface LoadingOverlayProps extends SpinnerProps {
  isLoading: boolean
  children: React.ReactNode
  text?: string
  backdrop?: boolean
}

const LoadingOverlay = ({
  isLoading,
  children,
  text,
  backdrop = true,
  ...spinnerProps
}: LoadingOverlayProps) => {
  if (!isLoading) {
    return <>{children}</>
  }

  return (
    <div className="relative">
      {children}
      <div
        className={cn(
          "absolute inset-0 z-50 flex items-center justify-center",
          backdrop && "bg-background/80 backdrop-blur-sm"
        )}
      >
        <SpinnerWithText text={text} {...spinnerProps} />
      </div>
    </div>
  )
}

export { Spinner, SpinnerWithText, LoadingOverlay }