import * as React from "react"
import { Command as CommandPrimitive } from "cmdk"
import { Search } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const commandVariants = cva(
  "flex h-full w-full flex-col overflow-hidden rounded-md bg-popover text-popover-foreground",
  {
    variants: {
      size: {
        default: "text-sm",
        sm: "text-xs",
        lg: "text-base",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const commandInputVariants = cva(
  "flex items-center border-b px-3",
  {
    variants: {
      size: {
        default: "h-11",
        sm: "h-9",
        lg: "h-12",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const commandListVariants = cva(
  "max-h-[300px] overflow-y-auto overflow-x-hidden",
  {
    variants: {
      size: {
        default: "p-1",
        sm: "p-0.5",
        lg: "p-2",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const commandItemVariants = cva(
  "relative flex cursor-default select-none items-center rounded-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50",
  {
    variants: {
      size: {
        default: "px-2 py-1.5 text-sm",
        sm: "px-1.5 py-1 text-xs",
        lg: "px-3 py-2 text-base",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const commandGroupVariants = cva(
  "overflow-hidden text-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground",
  {
    variants: {
      size: {
        default: "",
        sm: "[&_[cmdk-group-heading]]:px-1.5 [&_[cmdk-group-heading]]:py-1 [&_[cmdk-group-heading]]:text-xs",
        lg: "[&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-2 [&_[cmdk-group-heading]]:text-sm",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const commandSeparatorVariants = cva(
  "-mx-1 h-px bg-border",
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

export interface CommandProps
  extends React.ComponentPropsWithoutRef<typeof CommandPrimitive>,
    VariantProps<typeof commandVariants> {}

const Command = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive>,
  CommandProps
>(({ className, size, ...props }, ref) => (
  <CommandPrimitive
    ref={ref}
    className={cn(commandVariants({ size }), className)}
    {...props}
  />
))
Command.displayName = CommandPrimitive.displayName

export interface CommandInputProps
  extends React.ComponentPropsWithoutRef<typeof CommandPrimitive.Input>,
    VariantProps<typeof commandInputVariants> {
  showSearchIcon?: boolean
}

const CommandInput = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.Input>,
  CommandInputProps
>(({ className, size, showSearchIcon = true, ...props }, ref) => (
  <div className={cn(commandInputVariants({ size }))}>
    {showSearchIcon && <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />}
    <CommandPrimitive.Input
      ref={ref}
      className={cn(
        "flex h-full w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  </div>
))
CommandInput.displayName = CommandPrimitive.Input.displayName

export interface CommandListProps
  extends React.ComponentPropsWithoutRef<typeof CommandPrimitive.List>,
    VariantProps<typeof commandListVariants> {}

const CommandList = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.List>,
  CommandListProps
>(({ className, size, ...props }, ref) => (
  <CommandPrimitive.List
    ref={ref}
    className={cn(commandListVariants({ size }), className)}
    {...props}
  />
))
CommandList.displayName = CommandPrimitive.List.displayName

const CommandEmpty = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.Empty>,
  React.ComponentPropsWithoutRef<typeof CommandPrimitive.Empty>
>(({ className, ...props }, ref) => (
  <CommandPrimitive.Empty
    ref={ref}
    className={cn("py-6 text-center text-sm", className)}
    {...props}
  />
))
CommandEmpty.displayName = CommandPrimitive.Empty.displayName

export interface CommandGroupProps
  extends React.ComponentPropsWithoutRef<typeof CommandPrimitive.Group>,
    VariantProps<typeof commandGroupVariants> {}

const CommandGroup = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.Group>,
  CommandGroupProps
>(({ className, size, ...props }, ref) => (
  <CommandPrimitive.Group
    ref={ref}
    className={cn(commandGroupVariants({ size }), className)}
    {...props}
  />
))
CommandGroup.displayName = CommandPrimitive.Group.displayName

export interface CommandSeparatorProps
  extends React.ComponentPropsWithoutRef<typeof CommandPrimitive.Separator>,
    VariantProps<typeof commandSeparatorVariants> {}

const CommandSeparator = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.Separator>,
  CommandSeparatorProps
>(({ className, size, ...props }, ref) => (
  <CommandPrimitive.Separator
    ref={ref}
    className={cn(commandSeparatorVariants({ size }), className)}
    {...props}
  />
))
CommandSeparator.displayName = CommandPrimitive.Separator.displayName

export interface CommandItemProps
  extends React.ComponentPropsWithoutRef<typeof CommandPrimitive.Item>,
    VariantProps<typeof commandItemVariants> {
  icon?: React.ReactNode
  shortcut?: string
}

const CommandItem = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.Item>,
  CommandItemProps
>(({ className, size, icon, shortcut, children, ...props }, ref) => (
  <CommandPrimitive.Item
    ref={ref}
    className={cn(commandItemVariants({ size }), className)}
    {...props}
  >
    <div className="flex items-center w-full">
      {icon && <div className="mr-2 flex h-4 w-4 items-center justify-center">{icon}</div>}
      <div className="flex-1">{children}</div>
      {shortcut && (
        <div className="ml-auto text-xs tracking-widest text-muted-foreground">
          {shortcut}
        </div>
      )}
    </div>
  </CommandPrimitive.Item>
))
CommandItem.displayName = CommandPrimitive.Item.displayName

// Convenience wrapper component for a complete command palette
export interface CommandPaletteProps extends CommandProps {
  placeholder?: string
  emptyMessage?: string
  children: React.ReactNode
}

const CommandPalette = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive>,
  CommandPaletteProps
>(({ placeholder = "Type a command or search...", emptyMessage = "No results found.", children, ...props }, ref) => (
  <Command ref={ref} {...props}>
    <CommandInput placeholder={placeholder} />
    <CommandList>
      <CommandEmpty>{emptyMessage}</CommandEmpty>
      {children}
    </CommandList>
  </Command>
))
CommandPalette.displayName = "CommandPalette"

// Command shortcuts component for displaying keyboard shortcuts
const CommandShortcut = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) => {
  return (
    <span
      className={cn(
        "ml-auto text-xs tracking-widest text-muted-foreground",
        className
      )}
      {...props}
    />
  )
}
CommandShortcut.displayName = "CommandShortcut"

export {
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandShortcut,
  CommandSeparator,
  CommandPalette,
}