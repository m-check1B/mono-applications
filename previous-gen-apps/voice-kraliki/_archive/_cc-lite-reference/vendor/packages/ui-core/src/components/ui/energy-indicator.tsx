import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const energyIndicatorVariants = cva(
  "relative rounded-full border-2 border-border overflow-hidden bg-background",
  {
    variants: {
      size: {
        default: "h-6 w-16",
        sm: "h-4 w-12",
        lg: "h-8 w-20",
        xl: "h-10 w-24",
      },
      variant: {
        default: "",
        minimal: "border-0",
        outlined: "border-2 border-border",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

const energyFillVariants = cva(
  "h-full transition-all duration-300 ease-out rounded-full",
  {
    variants: {
      level: {
        critical: "bg-red-500 shadow-sm shadow-red-500/50",
        low: "bg-orange-500 shadow-sm shadow-orange-500/50",
        medium: "bg-yellow-500 shadow-sm shadow-yellow-500/50",
        high: "bg-green-500 shadow-sm shadow-green-500/50",
        full: "bg-emerald-500 shadow-sm shadow-emerald-500/50",
      },
      animated: {
        true: "animate-pulse",
        false: "",
      },
    },
    defaultVariants: {
      level: "medium",
      animated: false,
    },
  }
)

const energyLabelVariants = cva(
  "text-xs font-medium",
  {
    variants: {
      level: {
        critical: "text-red-600 dark:text-red-400",
        low: "text-orange-600 dark:text-orange-400",
        medium: "text-yellow-600 dark:text-yellow-400",
        high: "text-green-600 dark:text-green-400",
        full: "text-emerald-600 dark:text-emerald-400",
      },
    },
    defaultVariants: {
      level: "medium",
    },
  }
)

export interface EnergyIndicatorProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof energyIndicatorVariants> {
  value: number // 0-100
  max?: number
  showLabel?: boolean
  showPercentage?: boolean
  label?: string
  animated?: boolean
  pulsate?: boolean
  customColors?: {
    critical?: string
    low?: string
    medium?: string
    high?: string
    full?: string
  }
}

const EnergyIndicator = React.forwardRef<HTMLDivElement, EnergyIndicatorProps>(
  ({
    className,
    value,
    max = 100,
    showLabel = false,
    showPercentage = false,
    label,
    animated = false,
    pulsate = false,
    customColors,
    size,
    variant,
    ...props
  }, ref) => {
    
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
    
    const getEnergyLevel = (percentage: number): "critical" | "low" | "medium" | "high" | "full" => {
      if (percentage <= 10) return "critical"
      if (percentage <= 25) return "low"
      if (percentage <= 60) return "medium"
      if (percentage <= 90) return "high"
      return "full"
    }

    const energyLevel = getEnergyLevel(percentage)
    const shouldAnimate = animated || (pulsate && energyLevel === "critical")

    const getCustomColor = () => {
      if (!customColors) return undefined
      return customColors[energyLevel]
    }

    const customColor = getCustomColor()

    return (
      <div ref={ref} className="flex items-center space-x-2" {...props}>
        {showLabel && (
          <span className={cn(energyLabelVariants({ level: energyLevel }))}>
            {label || "Energy"}:
          </span>
        )}
        
        <div className="flex items-center space-x-2">
          <div className={cn(energyIndicatorVariants({ size, variant }), className)}>
            <div
              className={cn(energyFillVariants({ 
                level: energyLevel, 
                animated: shouldAnimate 
              }))}
              style={{
                width: `${percentage}%`,
                backgroundColor: customColor,
                boxShadow: customColor ? `0 1px 2px ${customColor}50` : undefined,
              }}
            />
            
            {/* Optional inner glow effect for high energy */}
            {energyLevel === "full" && (
              <div 
                className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"
                style={{ animationDuration: "2s" }}
              />
            )}
          </div>
          
          {showPercentage && (
            <span className={cn(
              "text-xs font-mono tabular-nums",
              energyLabelVariants({ level: energyLevel })
            )}>
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      </div>
    )
  }
)
EnergyIndicator.displayName = "EnergyIndicator"

// Circular energy indicator variant
export interface CircularEnergyIndicatorProps
  extends Omit<EnergyIndicatorProps, 'size' | 'variant'> {
  size?: number
  strokeWidth?: number
  showValue?: boolean
}

const CircularEnergyIndicator = React.forwardRef<HTMLDivElement, CircularEnergyIndicatorProps>(
  ({
    className,
    value,
    max = 100,
    size = 64,
    strokeWidth = 4,
    showValue = true,
    customColors,
    animated = false,
    pulsate = false,
    ...props
  }, ref) => {
    
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
    const radius = (size - strokeWidth) / 2
    const circumference = 2 * Math.PI * radius
    const strokeDasharray = circumference
    const strokeDashoffset = circumference - (percentage / 100) * circumference
    
    const getEnergyLevel = (percentage: number): "critical" | "low" | "medium" | "high" | "full" => {
      if (percentage <= 10) return "critical"
      if (percentage <= 25) return "low"
      if (percentage <= 60) return "medium"
      if (percentage <= 90) return "high"
      return "full"
    }

    const energyLevel = getEnergyLevel(percentage)
    
    const getStrokeColor = () => {
      if (customColors && customColors[energyLevel]) {
        return customColors[energyLevel]
      }
      
      switch (energyLevel) {
        case "critical": return "#ef4444"
        case "low": return "#f97316"
        case "medium": return "#eab308"
        case "high": return "#22c55e"
        case "full": return "#10b981"
        default: return "#6b7280"
      }
    }

    const shouldAnimate = animated || (pulsate && energyLevel === "critical")

    return (
      <div ref={ref} className={cn("relative inline-flex items-center justify-center", className)} {...props}>
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            className="text-muted-foreground/20"
          />
          
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={getStrokeColor()}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={cn(
              "transition-all duration-300 ease-out",
              shouldAnimate && "animate-pulse"
            )}
            style={{
              filter: energyLevel === "full" ? "drop-shadow(0 0 4px currentColor)" : undefined,
            }}
          />
        </svg>
        
        {/* Center value */}
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn(
              "font-mono text-sm font-semibold tabular-nums",
              energyLabelVariants({ level: energyLevel })
            )}>
              {Math.round(percentage)}%
            </span>
          </div>
        )}
      </div>
    )
  }
)
CircularEnergyIndicator.displayName = "CircularEnergyIndicator"

// Battery-style energy indicator
export interface BatteryEnergyIndicatorProps extends EnergyIndicatorProps {
  showBatteryTip?: boolean
}

const BatteryEnergyIndicator = React.forwardRef<HTMLDivElement, BatteryEnergyIndicatorProps>(
  ({
    className,
    value,
    max = 100,
    showBatteryTip = true,
    size,
    animated = false,
    pulsate = false,
    customColors,
    ...props
  }, ref) => {
    
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
    const energyLevel = percentage <= 10 ? "critical" : percentage <= 25 ? "low" : percentage <= 60 ? "medium" : percentage <= 90 ? "high" : "full"
    const shouldAnimate = animated || (pulsate && energyLevel === "critical")

    const getCustomColor = () => {
      if (!customColors) return undefined
      return customColors[energyLevel]
    }

    const customColor = getCustomColor()

    return (
      <div ref={ref} className={cn("flex items-center", className)} {...props}>
        <div className={cn(
          "relative rounded-sm border-2 border-border bg-background",
          size === "sm" ? "h-3 w-8" : size === "lg" ? "h-5 w-12" : size === "xl" ? "h-6 w-14" : "h-4 w-10"
        )}>
          <div
            className={cn(energyFillVariants({ 
              level: energyLevel, 
              animated: shouldAnimate 
            }), "rounded-xs")}
            style={{
              width: `${percentage}%`,
              backgroundColor: customColor,
              boxShadow: customColor ? `0 1px 2px ${customColor}50` : undefined,
            }}
          />
        </div>
        
        {/* Battery tip */}
        {showBatteryTip && (
          <div className={cn(
            "rounded-r-full border-r-2 border-t-2 border-b-2 border-border bg-background",
            size === "sm" ? "h-1.5 w-0.5 ml-0.5" : size === "lg" ? "h-2.5 w-1 ml-0.5" : size === "xl" ? "h-3 w-1 ml-1" : "h-2 w-0.5 ml-0.5"
          )} />
        )}
      </div>
    )
  }
)
BatteryEnergyIndicator.displayName = "BatteryEnergyIndicator"

export { 
  EnergyIndicator,
  CircularEnergyIndicator,
  BatteryEnergyIndicator,
}