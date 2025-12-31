<script lang="ts">
    import { onMount } from 'svelte';
    import { calendarStore } from '$lib/stores/calendar';
    import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, RefreshCw, Plus, Clock } from 'lucide-svelte';

    let currentDate = $state(new Date());
    let view = $state<'month' | 'week'>('week');

    let startDate = $derived(getStartDate(currentDate, view));
    let endDate = $derived(getEndDate(currentDate, view));

    // Effect to load events when date range changes
    $effect(() => {
        if (startDate && endDate) {
            calendarStore.loadEvents(startDate.toISOString(), endDate.toISOString());
        }
    });

    onMount(() => {
        calendarStore.checkSyncStatus();
    });

    function getStartDate(date: Date, v: 'month' | 'week') {
        const d = new Date(date);
        if (v === 'month') {
            d.setDate(1);
        } else {
            const day = d.getDay();
            const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is sunday
            d.setDate(diff);
        }
        d.setHours(0, 0, 0, 0);
        return d;
    }

    function getEndDate(date: Date, v: 'month' | 'week') {
        const d = new Date(date);
        if (v === 'month') {
            d.setMonth(d.getMonth() + 1);
            d.setDate(0);
        } else {
            const start = getStartDate(date, 'week');
            d.setDate(start.getDate() + 6);
        }
        d.setHours(23, 59, 59, 999);
        return d;
    }

    function next() {
        const d = new Date(currentDate);
        if (view === 'month') {
            d.setMonth(d.getMonth() + 1);
        } else {
            d.setDate(d.getDate() + 7);
        }
        currentDate = d;
    }

    function prev() {
        const d = new Date(currentDate);
        if (view === 'month') {
            d.setMonth(d.getMonth() - 1);
        } else {
            d.setDate(d.getDate() - 7);
        }
        currentDate = d;
    }

    function formatTime(dateStr: string) {
        return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function isSameDay(d1: Date, d2: Date) {
        return d1.getFullYear() === d2.getFullYear() &&
               d1.getMonth() === d2.getMonth() &&
               d1.getDate() === d2.getDate();
    }

    async function handleSync() {
        await calendarStore.syncGoogleCalendar();
        // Reload current view
        calendarStore.loadEvents(startDate.toISOString(), endDate.toISOString());
    }

    // Helper to get days for the grid
    function getDays() {
        const days = [];
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        // If month view, pad start to monday
        if (view === 'month') {
            const day = start.getDay();
            const diff = start.getDate() - day + (day === 0 ? -6 : 1);
            start.setDate(diff);
        }

        const current = new Date(start);
        // 42 days for month grid (6 rows), 7 for week
        const count = view === 'month' ? 42 : 7;

        for (let i = 0; i < count; i++) {
            days.push(new Date(current));
            current.setDate(current.getDate() + 1);
        }
        return days;
    }
</script>

<div class="space-y-6 h-full flex flex-col">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
            <h2 class="text-3xl font-black uppercase tracking-tighter">Calendar</h2>
            <div class="flex items-center border-2 border-black dark:border-white">
                <button 
                    class="p-2 hover:bg-secondary transition-colors border-r-2 border-black dark:border-white"
                    onclick={prev}
                >
                    <ChevronLeft class="w-5 h-5" />
                </button>
                <span class="px-4 py-2 font-mono font-bold min-w-[140px] text-center">
                    {currentDate.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}
                </span>
                <button 
                    class="p-2 hover:bg-secondary transition-colors border-l-2 border-black dark:border-white"
                    onclick={next}
                >
                    <ChevronRight class="w-5 h-5" />
                </button>
            </div>
        </div>

        <div class="flex items-center gap-3">
            <div class="flex border-2 border-black dark:border-white">
                <button
                    class="px-4 py-2 text-sm font-bold uppercase transition-colors {view === 'week' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black dark:bg-black dark:text-white hover:bg-secondary'}"
                    onclick={() => view = 'week'}
                >
                    Week
                </button>
                <button
                    class="px-4 py-2 text-sm font-bold uppercase transition-colors border-l-2 border-black dark:border-white {view === 'month' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black dark:bg-black dark:text-white hover:bg-secondary'}"
                    onclick={() => view = 'month'}
                >
                    Month
                </button>
            </div>

            <button 
                class="brutal-btn bg-white text-black flex items-center gap-2"
                onclick={handleSync}
                disabled={$calendarStore.isLoading}
            >
                <RefreshCw class="w-4 h-4 {$calendarStore.isLoading ? 'animate-spin' : ''}" />
                Sync
            </button>
        </div>
    </div>

    <!-- Calendar Grid -->
    <div class="flex-1 border-2 border-black dark:border-white bg-white dark:bg-black flex flex-col overflow-hidden">
        <!-- Weekday Headers -->
        <div class="grid grid-cols-7 border-b-2 border-black dark:border-white bg-secondary">
            {#each ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as day}
                <div class="p-2 text-center font-black uppercase text-sm border-r-2 border-black dark:border-white last:border-r-0">
                    {day}
                </div>
            {/each}
        </div>

        <!-- Days -->
        <div class="flex-1 grid grid-cols-7 {view === 'month' ? 'grid-rows-6' : 'grid-rows-1'}">
            {#each getDays() as day}
                {@const isToday = isSameDay(day, new Date())}
                {@const isCurrentMonth = day.getMonth() === currentDate.getMonth()}
                {@const dayEvents = $calendarStore.events.filter(e => isSameDay(new Date(e.startTime), day))}
                
                <div class="border-r-2 border-b-2 border-black dark:border-white last:border-r-0 p-2 min-h-[100px] relative group hover:bg-secondary/10 transition-colors
                    {!isCurrentMonth && view === 'month' ? 'bg-muted/20 text-muted-foreground' : ''}
                    {isToday ? 'bg-primary/5' : ''}"
                >
                    <span class="absolute top-2 right-2 text-sm font-mono font-bold {isToday ? 'text-primary' : ''}">
                        {day.getDate()}
                    </span>

                    <div class="mt-6 space-y-1">
                        {#each dayEvents as event}
                            <div class="text-xs p-1 border border-black dark:border-white bg-white dark:bg-black truncate cursor-pointer hover:bg-secondary transition-colors">
                                {#if !event.isAllDay}
                                    <span class="font-mono text-[10px] opacity-70">{formatTime(event.startTime)}</span>
                                {/if}
                                <span class="font-bold">{event.title}</span>
                            </div>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div>
