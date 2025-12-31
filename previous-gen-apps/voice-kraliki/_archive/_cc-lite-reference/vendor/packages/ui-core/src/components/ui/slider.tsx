import * as React from "react"
import * as SliderPrimitive from "@radix-ui/react-slider"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const sliderVariants = cva(
  "relative flex w-full touch-none select-none items-center",
  {
    variants: {
      orientation: {
        horizontal: "flex-row",
        vertical: "flex-col h-full",
      },
      size: {
        default: "",
        sm: "",
        lg: "",
      },
    },
    defaultVariants: {
      orientation: "horizontal",
      size: "default",
    },
  }
)

const sliderTrackVariants = cva(
  "relative grow overflow-hidden rounded-full bg-secondary",
  {
    variants: {
      orientation: {
        horizontal: "h-2 w-full",
        vertical: "w-2 h-full",
      },
      size: {
        default: "",
        sm: "h-1 [&[data-orientation=vertical]]:w-1",
        lg: "h-3 [&[data-orientation=vertical]]:w-3",
      },
    },
    defaultVariants: {
      orientation: "horizontal",
      size: "default",
    },
  }
)

const sliderRangeVariants = cva(
  "absolute bg-primary",
  {
    variants: {
      orientation: {
        horizontal: "h-full",
        vertical: "w-full",
      },
    },
    defaultVariants: {
      orientation: "horizontal",
    },
  }
)

const sliderThumbVariants = cva(
  "block rounded-full border-2 border-primary bg-background ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      size: {
        default: "h-5 w-5",
        sm: "h-4 w-4",
        lg: "h-6 w-6",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface SliderProps
  extends React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>,
    VariantProps<typeof sliderVariants> {
  showValue?: boolean
  showTicks?: boolean
  step?: number
  formatValue?: (value: number) => string
}

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(({ className, orientation, size, showValue, showTicks, step, formatValue, ...props }, ref) => {
  const [value, setValue] = React.useState(props.defaultValue || [0])
  const currentValue = props.value || value

  const handleValueChange = (newValue: number[]) => {
    setValue(newValue)
    props.onValueChange?.(newValue)
  }

  const min = props.min || 0
  const max = props.max || 100
  const stepValue = step || 1

  const ticks = showTicks && stepValue > 0
    ? Array.from({ length: Math.floor((max - min) / stepValue) + 1 }, (_, i) => min + i * stepValue)
    : []

  return (
    <div className={cn("relative w-full", className)}>
      <SliderPrimitive.Root
        ref={ref}
        className={cn(sliderVariants({ orientation, size }))}
        orientation={orientation}
        value={currentValue}
        onValueChange={handleValueChange}
        step={stepValue}
        {...props}
      >
        <SliderPrimitive.Track
          className={cn(sliderTrackVariants({ orientation, size }))}
        >
          <SliderPrimitive.Range
            className={cn(sliderRangeVariants({ orientation }))}
          />
        </SliderPrimitive.Track>
        <SliderPrimitive.Thumb
          className={cn(sliderThumbVariants({ size }))}
        />
      </SliderPrimitive.Root>
      
      {showValue && (
        <div className="mt-2 text-center text-sm text-muted-foreground">
          {formatValue ? formatValue(currentValue[0]) : currentValue[0]}
        </div>
      )}
      
      {showTicks && orientation === "horizontal" && (
        <div className="relative mt-1">
          <div className="flex justify-between text-xs text-muted-foreground">
            {ticks.map((tick) => (
              <span key={tick} className="text-center">
                {formatValue ? formatValue(tick) : tick}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
})
Slider.displayName = SliderPrimitive.Root.displayName

// Range slider with two thumbs
export interface RangeSliderProps extends Omit<SliderProps, 'value' | 'defaultValue' | 'onValueChange'> {
  value?: [number, number]
  defaultValue?: [number, number]
  onValueChange?: (value: [number, number]) => void
  showValues?: boolean
  formatValue?: (value: number) => string
}

const RangeSlider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  RangeSliderProps
>(({ className, orientation, size, showValues, formatValue, ...props }, ref) => {
  const [value, setValue] = React.useState<[number, number]>(props.defaultValue || [0, 100])
  const currentValue = props.value || value

  const handleValueChange = (newValue: number[]) => {
    const rangeValue: [number, number] = [newValue[0], newValue[1]]
    setValue(rangeValue)
    props.onValueChange?.(rangeValue)
  }

  return (
    <div className={cn("relative w-full", className)}>
      <SliderPrimitive.Root
        ref={ref}
        className={cn(sliderVariants({ orientation, size }))}
        orientation={orientation}
        value={currentValue}
        onValueChange={handleValueChange}
        {...props}
      >
        <SliderPrimitive.Track
          className={cn(sliderTrackVariants({ orientation, size }))}
        >
          <SliderPrimitive.Range
            className={cn(sliderRangeVariants({ orientation }))}
          />
        </SliderPrimitive.Track>
        <SliderPrimitive.Thumb
          className={cn(sliderThumbVariants({ size }))}
        />
        <SliderPrimitive.Thumb
          className={cn(sliderThumbVariants({ size }))}
        />
      </SliderPrimitive.Root>
      
      {showValues && (
        <div className="mt-2 flex justify-between text-sm text-muted-foreground">
          <span>{formatValue ? formatValue(currentValue[0]) : currentValue[0]}</span>
          <span>{formatValue ? formatValue(currentValue[1]) : currentValue[1]}</span>
        </div>
      )}
    </div>
  )
})
RangeSlider.displayName = "RangeSlider"

export { Slider, RangeSlider }