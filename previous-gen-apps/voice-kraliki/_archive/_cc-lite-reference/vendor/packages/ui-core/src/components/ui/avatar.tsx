import * as React from "react"
import * as AvatarPrimitive from "@radix-ui/react-avatar"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const avatarVariants = cva(
  "relative flex shrink-0 overflow-hidden rounded-full",
  {
    variants: {
      size: {
        default: "h-10 w-10",
        sm: "h-8 w-8",
        lg: "h-12 w-12",
        xl: "h-16 w-16",
        "2xl": "h-20 w-20",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const avatarImageVariants = cva("aspect-square h-full w-full")

const avatarFallbackVariants = cva(
  "flex h-full w-full items-center justify-center rounded-full bg-muted font-medium text-muted-foreground",
  {
    variants: {
      size: {
        default: "text-sm",
        sm: "text-xs",
        lg: "text-base",
        xl: "text-lg",
        "2xl": "text-xl",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface AvatarProps
  extends React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root>,
    VariantProps<typeof avatarVariants> {}

export interface AvatarImageProps
  extends React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image> {}

export interface AvatarFallbackProps
  extends React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>,
    VariantProps<typeof avatarFallbackVariants> {}

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  AvatarProps
>(({ className, size, ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn(avatarVariants({ size, className }))}
    {...props}
  />
))
Avatar.displayName = AvatarPrimitive.Root.displayName

const AvatarImage = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Image>,
  AvatarImageProps
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image
    ref={ref}
    className={cn(avatarImageVariants({ className }))}
    {...props}
  />
))
AvatarImage.displayName = AvatarPrimitive.Image.displayName

const AvatarFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Fallback>,
  AvatarFallbackProps
>(({ className, size, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn(avatarFallbackVariants({ size, className }))}
    {...props}
  />
))
AvatarFallback.displayName = AvatarPrimitive.Fallback.displayName

// Utility function to generate initials from a name
export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .map((word) => word.charAt(0))
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

// Convenience component that combines everything
export interface AvatarWithFallbackProps extends AvatarProps {
  src?: string
  alt?: string
  fallback?: string
  name?: string
}

const AvatarWithFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  AvatarWithFallbackProps
>(({ src, alt, fallback, name, size, className, ...props }, ref) => {
  const fallbackText = fallback || (name ? getInitials(name) : "?")
  
  return (
    <Avatar ref={ref} size={size} className={className} {...props}>
      {src && <AvatarImage src={src} alt={alt || name} />}
      <AvatarFallback size={size}>{fallbackText}</AvatarFallback>
    </Avatar>
  )
})
AvatarWithFallback.displayName = "AvatarWithFallback"

export { Avatar, AvatarImage, AvatarFallback, AvatarWithFallback }