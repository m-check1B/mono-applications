<script lang="ts">
    import { onMount } from "svelte";
    import { notificationsStore } from "$lib/stores/notifications";
    import {
        BellIcon as Bell,
        BellOffIcon as BellOff,
        Loader2Icon as Loader2,
        CheckIcon as Check,
        AlertTriangleIcon as AlertTriangle,
        SendIcon as Send,
    } from "lucide-svelte";

    let testSending = $state(false);
    let testResult = $state<{ success: boolean; message: string } | null>(null);

    onMount(async () => {
        await notificationsStore.initialize();
    });

    async function handleToggle() {
        if ($notificationsStore.isSubscribed) {
            await notificationsStore.disablePush();
        } else {
            await notificationsStore.enablePush();
        }
    }

    async function handlePrefChange(key: keyof typeof $notificationsStore.preferences, value: boolean) {
        await notificationsStore.updatePreferences({ [key]: value });
    }

    async function handleTestNotification() {
        testSending = true;
        testResult = null;
        const result = await notificationsStore.testNotification();
        testResult = result.success
            ? { success: true, message: "Test notification sent!" }
            : { success: false, message: result.error || "Failed to send" };
        testSending = false;

        // Clear result after 3 seconds
        setTimeout(() => {
            testResult = null;
        }, 3000);
    }
</script>

<div class="brutal-card p-6">
    <div class="flex items-start gap-4 mb-6">
        <div class="p-3 bg-yellow-400 border-2 border-black dark:border-white">
            {#if $notificationsStore.isSubscribed}
                <Bell class="w-6 h-6 text-black" />
            {:else}
                <BellOff class="w-6 h-6 text-black" />
            {/if}
        </div>
        <div>
            <h3 class="text-xl font-black uppercase">Push Notifications</h3>
            <p class="text-sm text-muted-foreground mt-1">
                Get reminded about tasks, deadlines, and focus sessions.
            </p>
        </div>
    </div>

    {#if !$notificationsStore.isSupported}
        <div class="p-4 bg-amber-100 dark:bg-amber-900/30 border-2 border-black dark:border-white text-sm">
            <div class="flex items-center gap-2 font-bold">
                <AlertTriangle class="w-4 h-4" />
                Push notifications are not supported in this browser.
            </div>
            <p class="mt-1 text-muted-foreground">
                Try using Chrome, Firefox, or Edge for push notification support.
            </p>
        </div>
    {:else}
        <div class="space-y-6">
            <!-- Main Toggle -->
            <div class="flex items-center justify-between p-4 border-2 border-black dark:border-white bg-secondary/20">
                <div>
                    <p class="font-bold uppercase text-sm">Enable Notifications</p>
                    <p class="text-xs text-muted-foreground mt-1">
                        {#if $notificationsStore.permission === 'denied'}
                            Permission blocked. Enable in browser settings.
                        {:else if $notificationsStore.isSubscribed}
                            You'll receive push notifications.
                        {:else}
                            Receive alerts even when Focus is closed.
                        {/if}
                    </p>
                </div>
                <button
                    class="brutal-btn {$notificationsStore.isSubscribed ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black'} flex items-center gap-2"
                    onclick={handleToggle}
                    disabled={$notificationsStore.isLoading || $notificationsStore.permission === 'denied'}
                >
                    {#if $notificationsStore.isLoading}
                        <Loader2 class="w-4 h-4 animate-spin" />
                    {:else if $notificationsStore.isSubscribed}
                        <Check class="w-4 h-4" />
                        Enabled
                    {:else}
                        Enable
                    {/if}
                </button>
            </div>

            {#if $notificationsStore.error}
                <div class="p-3 bg-destructive border-2 border-black dark:border-white text-destructive-foreground text-sm font-bold flex items-center gap-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] uppercase">
                    <AlertTriangle class="w-4 h-4" />
                    {$notificationsStore.error}
                </div>
            {/if}

            <!-- Notification Preferences -->
            {#if $notificationsStore.isSubscribed}
                <div class="space-y-3">
                    <h4 class="font-bold uppercase text-xs text-muted-foreground">Notification Types</h4>

                    <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors">
                        <div>
                            <p class="font-bold text-sm">Task Reminders</p>
                            <p class="text-xs text-muted-foreground">Due dates and scheduled tasks</p>
                        </div>
                        <input
                            type="checkbox"
                            checked={$notificationsStore.preferences.taskReminders}
                            onchange={() => handlePrefChange('taskReminders', !$notificationsStore.preferences.taskReminders)}
                            class="w-5 h-5 accent-primary"
                        />
                    </label>

                    <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors">
                        <div>
                            <p class="font-bold text-sm">Daily Digest</p>
                            <p class="text-xs text-muted-foreground">Morning summary of your day</p>
                        </div>
                        <input
                            type="checkbox"
                            checked={$notificationsStore.preferences.dailyDigest}
                            onchange={() => handlePrefChange('dailyDigest', !$notificationsStore.preferences.dailyDigest)}
                            class="w-5 h-5 accent-primary"
                        />
                    </label>

                    <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors">
                        <div>
                            <p class="font-bold text-sm">Pomodoro Alerts</p>
                            <p class="text-xs text-muted-foreground">Break and session reminders</p>
                        </div>
                        <input
                            type="checkbox"
                            checked={$notificationsStore.preferences.pomodoroAlerts}
                            onchange={() => handlePrefChange('pomodoroAlerts', !$notificationsStore.preferences.pomodoroAlerts)}
                            class="w-5 h-5 accent-primary"
                        />
                    </label>

                    <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors">
                        <div>
                            <p class="font-bold text-sm">Project Updates</p>
                            <p class="text-xs text-muted-foreground">Progress and milestone alerts</p>
                        </div>
                        <input
                            type="checkbox"
                            checked={$notificationsStore.preferences.projectUpdates}
                            onchange={() => handlePrefChange('projectUpdates', !$notificationsStore.preferences.projectUpdates)}
                            class="w-5 h-5 accent-primary"
                        />
                    </label>
                </div>

                <!-- Test Notification -->
                <div class="pt-4 border-t-2 border-black dark:border-white">
                    <div class="flex items-center gap-4">
                        <button
                            class="brutal-btn bg-secondary text-foreground flex items-center gap-2"
                            onclick={handleTestNotification}
                            disabled={testSending}
                        >
                            {#if testSending}
                                <Loader2 class="w-4 h-4 animate-spin" />
                                Sending...
                            {:else}
                                <Send class="w-4 h-4" />
                                Test Notification
                            {/if}
                        </button>
                        {#if testResult}
                            <span class="text-sm font-bold {testResult.success ? 'text-green-600' : 'text-red-600'}">
                                {testResult.message}
                            </span>
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
    {/if}
</div>
