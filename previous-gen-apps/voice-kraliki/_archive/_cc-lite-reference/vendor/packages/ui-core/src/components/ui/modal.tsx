import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "./dialog"

const modalVariants = cva(
  "fixed left-[50%] top-[50%] z-50 grid w-full translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
  {
    variants: {
      size: {
        default: "max-w-lg",
        sm: "max-w-md",
        lg: "max-w-4xl",
        xl: "max-w-6xl",
        full: "max-w-[95vw] max-h-[95vh]",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface ModalProps extends VariantProps<typeof modalVariants> {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

export interface ModalContentProps
  extends React.ComponentPropsWithoutRef<typeof DialogContent>,
    VariantProps<typeof modalVariants> {}

const Modal = ({ children, ...props }: ModalProps) => {
  return <Dialog {...props}>{children}</Dialog>
}

const ModalTrigger = DialogTrigger

const ModalContent = React.forwardRef<
  React.ElementRef<typeof DialogContent>,
  ModalContentProps
>(({ className, size, children, ...props }, ref) => (
  <DialogContent
    ref={ref}
    className={cn(modalVariants({ size, className }))}
    {...props}
  >
    {children}
  </DialogContent>
))
ModalContent.displayName = "ModalContent"

const ModalHeader = DialogHeader
const ModalFooter = DialogFooter
const ModalTitle = DialogTitle
const ModalDescription = DialogDescription
const ModalClose = DialogClose

export {
  Modal,
  ModalTrigger,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalTitle,
  ModalDescription,
  ModalClose,
}