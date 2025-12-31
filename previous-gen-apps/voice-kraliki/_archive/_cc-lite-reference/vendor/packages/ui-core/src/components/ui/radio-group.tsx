import * as React from "react"
import * as RadioGroupPrimitive from "@radix-ui/react-radio-group"
import { Circle } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const radioGroupVariants = cva(
  "grid gap-2",
  {
    variants: {
      orientation: {
        vertical: "grid-cols-1",
        horizontal: "grid-flow-col auto-cols-max gap-4",
      },
    },
    defaultVariants: {
      orientation: "vertical",
    },
  }
)

const radioGroupItemVariants = cva(
  "aspect-square h-4 w-4 rounded-full border border-primary text-primary ring-offset-background focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      size: {
        default: "h-4 w-4",
        sm: "h-3 w-3",
        lg: "h-5 w-5",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const radioGroupIndicatorVariants = cva(
  "flex items-center justify-center",
  {
    variants: {
      size: {
        default: "",
        sm: "",
        lg: "",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const radioGroupIndicatorIconVariants = cva(
  "fill-current text-current",
  {
    variants: {
      size: {
        default: "h-2.5 w-2.5",
        sm: "h-2 w-2",
        lg: "h-3 w-3",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface RadioGroupProps
  extends React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root>,
    VariantProps<typeof radioGroupVariants> {}

export interface RadioGroupItemProps
  extends React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item>,
    VariantProps<typeof radioGroupItemVariants> {}

const RadioGroup = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Root>,
  RadioGroupProps
>(({ className, orientation, ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Root
      className={cn(radioGroupVariants({ orientation, className }))}
      {...props}
      ref={ref}
    />
  )
})
RadioGroup.displayName = RadioGroupPrimitive.Root.displayName

const RadioGroupItem = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  RadioGroupItemProps
>(({ className, size, ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Item
      ref={ref}
      className={cn(radioGroupItemVariants({ size, className }))}
      {...props}
    >
      <RadioGroupPrimitive.Indicator
        className={cn(radioGroupIndicatorVariants({ size }))}
      >
        <Circle className={cn(radioGroupIndicatorIconVariants({ size }))} />
      </RadioGroupPrimitive.Indicator>
    </RadioGroupPrimitive.Item>
  )
})
RadioGroupItem.displayName = RadioGroupPrimitive.Item.displayName

// Convenience component that includes label
export interface RadioGroupOptionProps extends RadioGroupItemProps {
  label?: string
  description?: string
  labelProps?: React.LabelHTMLAttributes<HTMLLabelElement>
}

const RadioGroupOption = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  RadioGroupOptionProps
>(({ label, description, labelProps, className, id, size, ...props }, ref) => {
  const itemId = id || `radio-${Math.random().toString(36).slice(2, 9)}`
  
  return (
    <div className="flex items-start space-x-2">
      <RadioGroupItem
        ref={ref}
        id={itemId}
        className={className}
        size={size}
        {...props}
      />
      {(label || description) && (
        <div className="grid gap-1.5 leading-none">
          {label && (
            <label
              htmlFor={itemId}
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
              {...labelProps}
            >
              {label}
            </label>
          )}
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      )}
    </div>
  )
})
RadioGroupOption.displayName = "RadioGroupOption"

// Convenience component for a complete radio group with options
export interface RadioGroupWithOptionsProps
  extends Omit<RadioGroupProps, 'children'> {
  options: Array<{
    value: string
    label?: string
    description?: string
    disabled?: boolean
  }>
  size?: VariantProps<typeof radioGroupItemVariants>["size"]
}

const RadioGroupWithOptions = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Root>,
  RadioGroupWithOptionsProps
>(({ options, size, ...props }, ref) => {
  return (
    <RadioGroup ref={ref} {...props}>
      {options.map((option) => (
        <RadioGroupOption
          key={option.value}
          value={option.value}
          label={option.label}
          description={option.description}
          disabled={option.disabled}
          size={size}
        />
      ))}
    </RadioGroup>
  )
})
RadioGroupWithOptions.displayName = "RadioGroupWithOptions"

export { 
  RadioGroup, 
  RadioGroupItem, 
  RadioGroupOption, 
  RadioGroupWithOptions 
}