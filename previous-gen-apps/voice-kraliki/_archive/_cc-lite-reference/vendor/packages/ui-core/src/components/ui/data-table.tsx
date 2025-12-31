import * as React from "react"
import { ChevronDown, ChevronUp, ChevronsUpDown, MoreHorizontal } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"
import { Button } from "./button"
import { Checkbox } from "./checkbox"

const dataTableVariants = cva(
  "w-full border-collapse bg-background",
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

const dataTableRowVariants = cva(
  "border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",
  {
    variants: {
      clickable: {
        true: "cursor-pointer",
        false: "",
      },
    },
    defaultVariants: {
      clickable: false,
    },
  }
)

const dataTableHeaderVariants = cva(
  "h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",
  {
    variants: {
      sortable: {
        true: "cursor-pointer hover:text-accent-foreground",
        false: "",
      },
    },
    defaultVariants: {
      sortable: false,
    },
  }
)

const dataTableCellVariants = cva(
  "px-4 py-2 align-middle [&:has([role=checkbox])]:pr-0",
  {
    variants: {
      size: {
        default: "h-12",
        sm: "h-10",
        lg: "h-14",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

// Types
export interface Column<T = any> {
  id: string
  header: React.ReactNode
  accessorKey?: keyof T
  accessorFn?: (row: T) => any
  cell?: (info: { getValue: () => any; row: { original: T } }) => React.ReactNode
  sortable?: boolean
  width?: string | number
  minWidth?: string | number
  maxWidth?: string | number
}

export interface SortingState {
  id: string
  desc: boolean
}

export interface DataTableProps<T = any> extends VariantProps<typeof dataTableVariants> {
  data: T[]
  columns: Column<T>[]
  className?: string
  onRowClick?: (row: T) => void
  sorting?: SortingState[]
  onSortingChange?: (sorting: SortingState[]) => void
  selection?: string[]
  onSelectionChange?: (selection: string[]) => void
  getRowId?: (row: T, index: number) => string
  loading?: boolean
  emptyMessage?: string
  stickyHeader?: boolean
}

const DataTable = <T,>({
  data,
  columns,
  className,
  onRowClick,
  sorting = [],
  onSortingChange,
  selection = [],
  onSelectionChange,
  getRowId = (_, index) => index.toString(),
  loading = false,
  emptyMessage = "No data available",
  stickyHeader = false,
  size,
  ...props
}: DataTableProps<T>) => {
  const [internalSorting, setInternalSorting] = React.useState<SortingState[]>(sorting)
  
  const currentSorting = onSortingChange ? sorting : internalSorting
  const setSorting = onSortingChange || setInternalSorting

  const hasSelection = columns.some(col => col.id === 'select')
  const isAllSelected = selection.length > 0 && selection.length === data.length
  const isIndeterminate = selection.length > 0 && selection.length < data.length

  const handleSort = (columnId: string) => {
    setSorting(prev => {
      const existing = prev.find(s => s.id === columnId)
      if (existing) {
        if (existing.desc) {
          return prev.filter(s => s.id !== columnId)
        } else {
          return prev.map(s => s.id === columnId ? { ...s, desc: true } : s)
        }
      } else {
        return [...prev, { id: columnId, desc: false }]
      }
    })
  }

  const getSortIcon = (columnId: string) => {
    const sort = currentSorting.find(s => s.id === columnId)
    if (!sort) return <ChevronsUpDown className="ml-2 h-4 w-4" />
    return sort.desc ? <ChevronDown className="ml-2 h-4 w-4" /> : <ChevronUp className="ml-2 h-4 w-4" />
  }

  const sortedData = React.useMemo(() => {
    if (currentSorting.length === 0) return data

    return [...data].sort((a, b) => {
      for (const sort of currentSorting) {
        const column = columns.find(col => col.id === sort.id)
        if (!column) continue

        let aValue: any
        let bValue: any

        if (column.accessorFn) {
          aValue = column.accessorFn(a)
          bValue = column.accessorFn(b)
        } else if (column.accessorKey) {
          aValue = a[column.accessorKey]
          bValue = b[column.accessorKey]
        } else {
          continue
        }

        if (aValue < bValue) return sort.desc ? 1 : -1
        if (aValue > bValue) return sort.desc ? -1 : 1
      }
      return 0
    })
  }, [data, currentSorting, columns])

  const handleSelectAll = () => {
    if (isAllSelected) {
      onSelectionChange?.([])
    } else {
      const allIds = data.map((row, index) => getRowId(row, index))
      onSelectionChange?.(allIds)
    }
  }

  const handleRowSelect = (rowId: string) => {
    if (selection.includes(rowId)) {
      onSelectionChange?.(selection.filter(id => id !== rowId))
    } else {
      onSelectionChange?.([...selection, rowId])
    }
  }

  const getCellValue = (row: T, column: Column<T>) => {
    if (column.accessorFn) {
      return column.accessorFn(row)
    } else if (column.accessorKey) {
      return row[column.accessorKey]
    }
    return null
  }

  if (loading) {
    return (
      <div className="w-full">
        <table className={cn(dataTableVariants({ size }), className)} {...props}>
          <thead className={stickyHeader ? "sticky top-0 z-10 bg-background" : ""}>
            <tr className="border-b">
              {columns.map((column) => (
                <th
                  key={column.id}
                  className={cn(dataTableHeaderVariants())}
                  style={{
                    width: column.width,
                    minWidth: column.minWidth,
                    maxWidth: column.maxWidth,
                  }}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 5 }).map((_, index) => (
              <tr key={index} className="border-b">
                {columns.map((column) => (
                  <td key={column.id} className={cn(dataTableCellVariants({ size }))}>
                    <div className="h-4 w-3/4 animate-pulse bg-muted rounded" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="w-full">
        <table className={cn(dataTableVariants({ size }), className)} {...props}>
          <thead className={stickyHeader ? "sticky top-0 z-10 bg-background" : ""}>
            <tr className="border-b">
              {columns.map((column) => (
                <th
                  key={column.id}
                  className={cn(dataTableHeaderVariants())}
                  style={{
                    width: column.width,
                    minWidth: column.minWidth,
                    maxWidth: column.maxWidth,
                  }}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
        </table>
        <div className="flex items-center justify-center h-24 text-muted-foreground">
          {emptyMessage}
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <table className={cn(dataTableVariants({ size }), className)} {...props}>
        <thead className={stickyHeader ? "sticky top-0 z-10 bg-background" : ""}>
          <tr className="border-b">
            {columns.map((column) => (
              <th
                key={column.id}
                className={cn(dataTableHeaderVariants({ 
                  sortable: column.sortable && column.id !== 'select' 
                }))}
                style={{
                  width: column.width,
                  minWidth: column.minWidth,
                  maxWidth: column.maxWidth,
                }}
                onClick={() => {
                  if (column.sortable && column.id !== 'select') {
                    handleSort(column.id)
                  }
                }}
              >
                <div className="flex items-center">
                  {column.id === 'select' ? (
                    <Checkbox
                      checked={isAllSelected}
                      indeterminate={isIndeterminate}
                      onCheckedChange={handleSelectAll}
                      aria-label="Select all"
                    />
                  ) : (
                    <>
                      {column.header}
                      {column.sortable && getSortIcon(column.id)}
                    </>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, index) => {
            const rowId = getRowId(row, index)
            const isSelected = selection.includes(rowId)
            
            return (
              <tr
                key={rowId}
                className={cn(dataTableRowVariants({ 
                  clickable: !!onRowClick 
                }))}
                data-state={isSelected ? "selected" : undefined}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => (
                  <td
                    key={column.id}
                    className={cn(dataTableCellVariants({ size }))}
                  >
                    {column.id === 'select' ? (
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={() => handleRowSelect(rowId)}
                        aria-label="Select row"
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : column.cell ? (
                      column.cell({
                        getValue: () => getCellValue(row, column),
                        row: { original: row }
                      })
                    ) : (
                      getCellValue(row, column)
                    )}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

// Helper components
const DataTableColumnHeader = ({ 
  children, 
  sortable = false,
  onSort 
}: { 
  children: React.ReactNode
  sortable?: boolean
  onSort?: () => void
}) => {
  return (
    <div className={cn(
      "flex items-center space-x-2",
      sortable && "cursor-pointer hover:text-accent-foreground"
    )} onClick={onSort}>
      {children}
    </div>
  )
}

const DataTableRowActions = ({ 
  children 
}: { 
  children: React.ReactNode 
}) => {
  return (
    <div className="flex items-center space-x-2">
      {children}
    </div>
  )
}

export { 
  DataTable,
  DataTableColumnHeader,
  DataTableRowActions,
  type Column,
  type SortingState 
}