import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const skeletonVariants = cva(
  "animate-pulse rounded-md bg-muted",
  {
    variants: {
      variant: {
        default: "bg-muted",
        subtle: "bg-muted/50",
        shimmer: "bg-gradient-to-r from-muted via-muted/50 to-muted bg-[length:200%_100%] animate-shimmer",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

function Skeleton({
  className,
  variant,
  ...props
}: SkeletonProps) {
  return (
    <div
      className={cn(skeletonVariants({ variant, className }))}
      {...props}
    />
  )
}

// Predefined skeleton components for common use cases
const SkeletonText = React.forwardRef<
  HTMLDivElement,
  SkeletonProps & { lines?: number }
>(({ lines = 1, className, ...props }, ref) => (
  <div ref={ref} className="space-y-2">
    {Array.from({ length: lines }).map((_, index) => (
      <Skeleton
        key={index}
        className={cn(
          "h-4 w-full",
          index === lines - 1 && lines > 1 ? "w-3/4" : "",
          className
        )}
        {...props}
      />
    ))}
  </div>
))
SkeletonText.displayName = "SkeletonText"

const SkeletonAvatar = React.forwardRef<
  HTMLDivElement,
  SkeletonProps & { size?: "sm" | "default" | "lg" | "xl" | "2xl" }
>(({ size = "default", className, ...props }, ref) => {
  const sizeClasses = {
    sm: "h-8 w-8",
    default: "h-10 w-10",
    lg: "h-12 w-12",
    xl: "h-16 w-16",
    "2xl": "h-20 w-20",
  }
  
  return (
    <Skeleton
      ref={ref}
      className={cn("rounded-full", sizeClasses[size], className)}
      {...props}
    />
  )
})
SkeletonAvatar.displayName = "SkeletonAvatar"

const SkeletonButton = React.forwardRef<
  HTMLDivElement,
  SkeletonProps & { size?: "sm" | "default" | "lg" }
>(({ size = "default", className, ...props }, ref) => {
  const sizeClasses = {
    sm: "h-9 w-20",
    default: "h-10 w-24",
    lg: "h-11 w-28",
  }
  
  return (
    <Skeleton
      ref={ref}
      className={cn(sizeClasses[size], className)}
      {...props}
    />
  )
})
SkeletonButton.displayName = "SkeletonButton"

const SkeletonCard = React.forwardRef<
  HTMLDivElement,
  SkeletonProps
>(({ className, ...props }, ref) => (
  <div ref={ref} className="space-y-3">
    <Skeleton className="h-4 w-2/3" {...props} />
    <SkeletonText lines={2} {...props} />
    <div className="flex items-center space-x-2">
      <SkeletonAvatar size="sm" {...props} />
      <Skeleton className="h-3 w-16" {...props} />
    </div>
  </div>
))
SkeletonCard.displayName = "SkeletonCard"

const SkeletonTable = React.forwardRef<
  HTMLDivElement,
  SkeletonProps & { rows?: number; cols?: number }
>(({ rows = 5, cols = 4, className, ...props }, ref) => (
  <div ref={ref} className="space-y-3">
    {/* Header */}
    <div className="flex space-x-4">
      {Array.from({ length: cols }).map((_, index) => (
        <Skeleton key={`header-${index}`} className="h-4 flex-1" {...props} />
      ))}
    </div>
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={`row-${rowIndex}`} className="flex space-x-4">
        {Array.from({ length: cols }).map((_, colIndex) => (
          <Skeleton 
            key={`cell-${rowIndex}-${colIndex}`} 
            className="h-4 flex-1" 
            {...props} 
          />
        ))}
      </div>
    ))}
  </div>
))
SkeletonTable.displayName = "SkeletonTable"

export { 
  Skeleton,
  SkeletonText,
  SkeletonAvatar,
  SkeletonButton,
  SkeletonCard,
  SkeletonTable,
}