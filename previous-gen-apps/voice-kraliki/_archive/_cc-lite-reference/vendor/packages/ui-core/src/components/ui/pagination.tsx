import * as React from "react"
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"
import { Button } from "./button"

const paginationVariants = cva(
  "flex items-center justify-center space-x-2",
  {
    variants: {
      size: {
        default: "",
        sm: "space-x-1",
        lg: "space-x-4",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const paginationItemVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "hover:bg-accent hover:text-accent-foreground",
        active: "bg-primary text-primary-foreground hover:bg-primary/90",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 w-10",
        sm: "h-8 w-8 text-xs",
        lg: "h-12 w-12 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface PaginationProps extends VariantProps<typeof paginationVariants> {
  className?: string
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showFirstLast?: boolean
  showPrevNext?: boolean
  showPageNumbers?: boolean
  maxVisiblePages?: number
  disabled?: boolean
  showInfo?: boolean
  totalItems?: number
  itemsPerPage?: number
}

const Pagination = React.forwardRef<HTMLDivElement, PaginationProps>(
  ({
    className,
    currentPage,
    totalPages,
    onPageChange,
    showFirstLast = false,
    showPrevNext = true,
    showPageNumbers = true,
    maxVisiblePages = 5,
    disabled = false,
    showInfo = false,
    totalItems,
    itemsPerPage,
    size,
    ...props
  }, ref) => {
    
    const getVisiblePages = () => {
      if (totalPages <= maxVisiblePages) {
        return Array.from({ length: totalPages }, (_, i) => i + 1)
      }

      const halfVisible = Math.floor(maxVisiblePages / 2)
      let start = Math.max(currentPage - halfVisible, 1)
      let end = Math.min(start + maxVisiblePages - 1, totalPages)

      if (end - start + 1 < maxVisiblePages) {
        start = Math.max(end - maxVisiblePages + 1, 1)
      }

      const pages = []
      
      if (start > 1) {
        pages.push(1)
        if (start > 2) {
          pages.push('...')
        }
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      if (end < totalPages) {
        if (end < totalPages - 1) {
          pages.push('...')
        }
        pages.push(totalPages)
      }

      return pages
    }

    const visiblePages = getVisiblePages()
    
    const canGoPrevious = currentPage > 1 && !disabled
    const canGoNext = currentPage < totalPages && !disabled

    const handlePageClick = (page: number) => {
      if (page !== currentPage && !disabled) {
        onPageChange(page)
      }
    }

    const getItemInfo = () => {
      if (!totalItems || !itemsPerPage) return null
      
      const start = (currentPage - 1) * itemsPerPage + 1
      const end = Math.min(currentPage * itemsPerPage, totalItems)
      
      return `${start}-${end} of ${totalItems} items`
    }

    return (
      <div ref={ref} className="flex flex-col items-center space-y-4">
        {showInfo && totalItems && itemsPerPage && (
          <div className="text-sm text-muted-foreground">
            {getItemInfo()}
          </div>
        )}
        
        <nav
          className={cn(paginationVariants({ size }), className)}
          role="navigation"
          aria-label="pagination"
          {...props}
        >
          {/* First page button */}
          {showFirstLast && (
            <Button
              variant="ghost"
              size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
              onClick={() => handlePageClick(1)}
              disabled={!canGoPrevious}
              aria-label="Go to first page"
            >
              First
            </Button>
          )}

          {/* Previous page button */}
          {showPrevNext && (
            <Button
              variant="ghost"
              size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
              onClick={() => handlePageClick(currentPage - 1)}
              disabled={!canGoPrevious}
              aria-label="Go to previous page"
            >
              <ChevronLeft className={cn(
                size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4"
              )} />
              <span className="sr-only">Previous</span>
            </Button>
          )}

          {/* Page numbers */}
          {showPageNumbers && visiblePages.map((page, index) => {
            if (page === '...') {
              return (
                <div
                  key={`ellipsis-${index}`}
                  className={cn(paginationItemVariants({ size }))}
                >
                  <MoreHorizontal className={cn(
                    size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4"
                  )} />
                </div>
              )
            }

            const pageNumber = page as number
            const isCurrentPage = pageNumber === currentPage

            return (
              <Button
                key={pageNumber}
                variant={isCurrentPage ? "default" : "ghost"}
                size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
                onClick={() => handlePageClick(pageNumber)}
                disabled={disabled}
                aria-label={`Go to page ${pageNumber}`}
                aria-current={isCurrentPage ? "page" : undefined}
                className={cn(
                  size === "sm" ? "h-8 w-8" : size === "lg" ? "h-12 w-12" : "h-10 w-10"
                )}
              >
                {pageNumber}
              </Button>
            )
          })}

          {/* Next page button */}
          {showPrevNext && (
            <Button
              variant="ghost"
              size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
              onClick={() => handlePageClick(currentPage + 1)}
              disabled={!canGoNext}
              aria-label="Go to next page"
            >
              <ChevronRight className={cn(
                size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4"
              )} />
              <span className="sr-only">Next</span>
            </Button>
          )}

          {/* Last page button */}
          {showFirstLast && (
            <Button
              variant="ghost"
              size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
              onClick={() => handlePageClick(totalPages)}
              disabled={!canGoNext}
              aria-label="Go to last page"
            >
              Last
            </Button>
          )}
        </nav>
      </div>
    )
  }
)
Pagination.displayName = "Pagination"

// Simple pagination component with minimal controls
export interface SimplePaginationProps extends VariantProps<typeof paginationVariants> {
  className?: string
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  disabled?: boolean
}

const SimplePagination = React.forwardRef<HTMLDivElement, SimplePaginationProps>(
  ({
    className,
    currentPage,
    totalPages,
    onPageChange,
    disabled = false,
    size,
    ...props
  }, ref) => {
    
    const canGoPrevious = currentPage > 1 && !disabled
    const canGoNext = currentPage < totalPages && !disabled

    return (
      <nav
        ref={ref}
        className={cn(paginationVariants({ size }), className)}
        role="navigation"
        aria-label="pagination"
        {...props}
      >
        <Button
          variant="ghost"
          size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!canGoPrevious}
          aria-label="Go to previous page"
        >
          <ChevronLeft className={cn(
            size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4"
          )} />
          Previous
        </Button>
        
        <div className="flex items-center space-x-2 px-4">
          <span className="text-sm font-medium">
            Page {currentPage} of {totalPages}
          </span>
        </div>
        
        <Button
          variant="ghost"
          size={size === "sm" ? "sm" : size === "lg" ? "lg" : "default"}
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!canGoNext}
          aria-label="Go to next page"
        >
          Next
          <ChevronRight className={cn(
            size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4"
          )} />
        </Button>
      </nav>
    )
  }
)
SimplePagination.displayName = "SimplePagination"

export { Pagination, SimplePagination }