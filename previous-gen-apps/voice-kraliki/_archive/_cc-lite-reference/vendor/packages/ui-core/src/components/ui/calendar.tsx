import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"
import { Button } from "./button"

const calendarVariants = cva(
  "p-3 border rounded-lg bg-background",
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

const calendarHeaderVariants = cva(
  "flex items-center justify-between mb-4",
  {
    variants: {
      size: {
        default: "",
        sm: "mb-2",
        lg: "mb-6",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const calendarGridVariants = cva(
  "grid grid-cols-7 gap-1",
  {
    variants: {
      size: {
        default: "",
        sm: "gap-0.5",
        lg: "gap-2",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const calendarCellVariants = cva(
  "flex items-center justify-center rounded-md cursor-pointer transition-colors",
  {
    variants: {
      size: {
        default: "h-9 w-9",
        sm: "h-8 w-8",
        lg: "h-10 w-10",
      },
      variant: {
        default: "hover:bg-accent hover:text-accent-foreground",
        selected: "bg-primary text-primary-foreground hover:bg-primary/90",
        today: "bg-accent text-accent-foreground font-semibold",
        outside: "text-muted-foreground opacity-50",
        disabled: "text-muted-foreground opacity-30 cursor-not-allowed",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

interface CalendarDate {
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  isSelected: boolean
  isDisabled: boolean
}

export interface CalendarProps extends VariantProps<typeof calendarVariants> {
  className?: string
  selected?: Date | Date[]
  onDateSelect?: (date: Date) => void
  disabled?: (date: Date) => boolean
  multiple?: boolean
  showOutsideDays?: boolean
  initialMonth?: Date
  minDate?: Date
  maxDate?: Date
  weekStartsOn?: 0 | 1 | 2 | 3 | 4 | 5 | 6
}

const Calendar = React.forwardRef<HTMLDivElement, CalendarProps>(
  ({
    className,
    selected,
    onDateSelect,
    disabled,
    multiple = false,
    showOutsideDays = true,
    initialMonth = new Date(),
    minDate,
    maxDate,
    weekStartsOn = 0,
    size,
    ...props
  }, ref) => {
    const [currentMonth, setCurrentMonth] = React.useState(initialMonth)
    
    const today = new Date()
    const selectedDates = React.useMemo(() => {
      if (!selected) return []
      return Array.isArray(selected) ? selected : [selected]
    }, [selected])

    const isDateSelected = (date: Date) => {
      return selectedDates.some(selectedDate => 
        date.getTime() === selectedDate.getTime()
      )
    }

    const isDateDisabled = (date: Date) => {
      if (disabled && disabled(date)) return true
      if (minDate && date < minDate) return true
      if (maxDate && date > maxDate) return true
      return false
    }

    const getDaysInMonth = (date: Date): CalendarDate[] => {
      const year = date.getFullYear()
      const month = date.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const daysInMonth = lastDay.getDate()
      
      // Calculate the starting day offset
      const startOffset = (firstDay.getDay() - weekStartsOn + 7) % 7
      
      const days: CalendarDate[] = []
      
      // Add previous month days if showing outside days
      if (showOutsideDays && startOffset > 0) {
        const prevMonth = new Date(year, month - 1, 0)
        for (let i = startOffset - 1; i >= 0; i--) {
          const date = new Date(year, month - 1, prevMonth.getDate() - i)
          days.push({
            date,
            isCurrentMonth: false,
            isToday: date.toDateString() === today.toDateString(),
            isSelected: isDateSelected(date),
            isDisabled: isDateDisabled(date),
          })
        }
      }
      
      // Add current month days
      for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day)
        days.push({
          date,
          isCurrentMonth: true,
          isToday: date.toDateString() === today.toDateString(),
          isSelected: isDateSelected(date),
          isDisabled: isDateDisabled(date),
        })
      }
      
      // Add next month days to fill the grid
      const remainingCells = 42 - days.length // 6 rows × 7 days
      if (showOutsideDays && remainingCells > 0) {
        for (let day = 1; day <= remainingCells; day++) {
          const date = new Date(year, month + 1, day)
          days.push({
            date,
            isCurrentMonth: false,
            isToday: date.toDateString() === today.toDateString(),
            isSelected: isDateSelected(date),
            isDisabled: isDateDisabled(date),
          })
        }
      }
      
      return days
    }

    const handleDateClick = (calendarDate: CalendarDate) => {
      if (calendarDate.isDisabled || !onDateSelect) return
      onDateSelect(calendarDate.date)
    }

    const navigateMonth = (direction: 'prev' | 'next') => {
      setCurrentMonth(prev => {
        const newMonth = new Date(prev)
        if (direction === 'prev') {
          newMonth.setMonth(prev.getMonth() - 1)
        } else {
          newMonth.setMonth(prev.getMonth() + 1)
        }
        return newMonth
      })
    }

    const days = getDaysInMonth(currentMonth)
    const weekDays = React.useMemo(() => {
      const days = [...DAYS_OF_WEEK]
      const rotated = [...days.slice(weekStartsOn), ...days.slice(0, weekStartsOn)]
      return rotated
    }, [weekStartsOn])

    return (
      <div ref={ref} className={cn(calendarVariants({ size }), className)} {...props}>
        {/* Header */}
        <div className={cn(calendarHeaderVariants({ size }))}>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateMonth('prev')}
            className="h-8 w-8 p-0"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <h2 className="font-semibold">
            {MONTHS[currentMonth.getMonth()]} {currentMonth.getFullYear()}
          </h2>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateMonth('next')}
            className="h-8 w-8 p-0"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Days of week header */}
        <div className={cn(calendarGridVariants({ size }), "mb-2")}>
          {weekDays.map((day) => (
            <div
              key={day}
              className={cn(
                "flex items-center justify-center font-medium text-muted-foreground",
                size === "sm" ? "h-6" : size === "lg" ? "h-8" : "h-7"
              )}
            >
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className={cn(calendarGridVariants({ size }))}>
          {days.map((calendarDate, index) => {
            const { date, isCurrentMonth, isToday, isSelected, isDisabled } = calendarDate
            
            let variant: VariantProps<typeof calendarCellVariants>["variant"] = "default"
            
            if (isDisabled) variant = "disabled"
            else if (isSelected) variant = "selected"
            else if (isToday) variant = "today"
            else if (!isCurrentMonth) variant = "outside"
            
            return (
              <div
                key={index}
                className={cn(calendarCellVariants({ size, variant }))}
                onClick={() => handleDateClick(calendarDate)}
              >
                {date.getDate()}
              </div>
            )
          })}
        </div>
      </div>
    )
  }
)
Calendar.displayName = "Calendar"

export { Calendar }