<script lang="ts">
    import { onMount } from "svelte";
    import { browser } from "$app/environment";
    import { settingsStore } from "$lib/stores/settings";
    import { contextPanelStore } from "$lib/stores/contextPanel";
    import {
        SaveIcon as Save,
        Trash2Icon as Trash2,
        KeyIcon as Key,
        ActivityIcon as Activity,
        CreditCardIcon as CreditCard,
        FileTextIcon as FileText,
        DownloadIcon as Download,
        Loader2Icon as Loader2,
        AlertTriangleIcon as AlertTriangle,
        ZapIcon as Zap,
        CheckIcon as Check,
    } from "lucide-svelte";
    import { api } from "$lib/api/client";
    import { authStore } from "$lib/stores/auth";
    import { logger } from "$lib/utils/logger";
    import NotificationSettings from "$lib/components/NotificationSettings.svelte";

    let apiKey = $state("");
    let activeTab = $state<"general" | "billing" | "exports">("general");
    let academyUrl = $state("https://learn.kraliki.com");

    $effect(() => {
        if (
            $contextPanelStore.data?.tab &&
            ["general", "billing", "exports"].includes(
                $contextPanelStore.data.tab,
            )
        ) {
            activeTab = $contextPanelStore.data.tab;
        }
    });

    $effect(() => {
        if (!browser) return;
        const host = window.location.hostname;
        const isDevHost =
            host === "localhost" ||
            host === "127.0.0.1" ||
            host.endsWith("verduona.dev") ||
            host.endsWith("verduona.localhost");
        academyUrl = isDevHost ? "https://learn.verduona.dev" : "https://learn.kraliki.com";
    });

    // Exports state
    let exportStartDate = $state(new Date().toISOString().split("T")[0]);
    let exportEndDate = $state(new Date().toISOString().split("T")[0]);
    let isExporting = $state(false);

    // Billing state
    let subscriptionStatus = $state<any>(null);
    let isLoadingBilling = $state(false);

    onMount(async () => {
        await settingsStore.loadSettings();
        if ($settingsStore.openRouterKey) {
            apiKey = $settingsStore.openRouterKey;
        }
        loadBillingStatus();
    });

    async function loadBillingStatus() {
        isLoadingBilling = true;
        try {
            subscriptionStatus = await api.billing.subscriptionStatus();
        } catch (e) {
            logger.error('Failed to load billing status', e);
        } finally {
            isLoadingBilling = false;
        }
    }

    async function handleSave() {
        await settingsStore.saveOpenRouterKey(apiKey);
    }

    async function handleDelete() {
        if (confirm("Are you sure you want to delete your API key?")) {
            await settingsStore.deleteOpenRouterKey();
            apiKey = "";
        }
    }

    async function handleManageSubscription() {
        try {
            const session: any = await api.billing.portalSession();
            window.location.href = session.url;
        } catch (e) {
            alert("Failed to redirect to billing portal");
        }
    }

    async function handleExport(format: "csv" | "json") {
        isExporting = true;
        try {
            // In a real app, this would trigger a download
            // For now we just call the API to verify connectivity
            await api.exports.generateInvoice({
                start_date: exportStartDate,
                end_date: exportEndDate,
                format,
            });
            alert(`Export started for ${format.toUpperCase()}`);
        } catch (e: any) {
            alert("Export failed: " + e.detail);
        } finally {
            isExporting = false;
        }
    }
</script>

<div class="space-y-6">
    <div
        class="flex flex-col md:flex-row md:items-center justify-between gap-4"
    >
        <div>
            <h2 class="text-3xl font-black uppercase tracking-tighter">
                Settings
            </h2>
            <p class="text-muted-foreground font-mono text-sm mt-1">
                Manage your preferences and account.
            </p>
        </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b-2 border-black dark:border-white overflow-x-auto">
        <button
            class="px-6 py-3 font-bold uppercase text-sm border-r-2 border-black dark:border-white transition-colors whitespace-nowrap
            {activeTab === 'general'
                ? 'bg-black text-white dark:bg-white dark:text-black'
                : 'hover:bg-secondary'}"
            onclick={() => (activeTab = "general")}
        >
            General
        </button>
        <button
            class="px-6 py-3 font-bold uppercase text-sm border-r-2 border-black dark:border-white transition-colors whitespace-nowrap
            {activeTab === 'billing'
                ? 'bg-black text-white dark:bg-white dark:text-black'
                : 'hover:bg-secondary'}"
            onclick={() => (activeTab = "billing")}
        >
            Billing
        </button>
        <button
            class="px-6 py-3 font-bold uppercase text-sm transition-colors whitespace-nowrap
            {activeTab === 'exports'
                ? 'bg-black text-white dark:bg-white dark:text-black'
                : 'hover:bg-secondary'}"
            onclick={() => (activeTab = "exports")}
        >
            Exports
        </button>
    </div>

    {#if activeTab === "general"}
        <!-- API Key Section -->
        <div class="brutal-card p-6">
            <div class="flex items-start gap-4 mb-6">
                <div
                    class="p-3 bg-primary border-2 border-black dark:border-white"
                >
                    <Key class="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                    <h3 class="text-xl font-black uppercase">
                        OpenRouter API Key
                    </h3>
                    <p class="text-sm text-muted-foreground mt-1">
                        Required for AI features. Your key is stored locally and
                        encrypted.
                    </p>
                </div>
            </div>

            <div class="space-y-4">
                <div class="space-y-2">
                    <label for="apiKey" class="text-xs font-bold uppercase"
                        >API Key</label
                    >
                    <input
                        id="apiKey"
                        type="password"
                        bind:value={apiKey}
                        placeholder="sk-or-..."
                        class="w-full p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>

                <div class="flex gap-3">
                    <button
                        class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2"
                        onclick={handleSave}
                        disabled={$settingsStore.isLoading}
                    >
                        {#if $settingsStore.isLoading}
                            <Loader2 class="w-4 h-4 animate-spin" />
                        {:else}
                            <Save class="w-4 h-4" />
                        {/if}
                        Save Key
                    </button>
                    {#if $settingsStore.openRouterKey}
                        <button
                            class="brutal-btn bg-red-500 text-white border-black flex items-center gap-2"
                            onclick={handleDelete}
                            disabled={$settingsStore.isLoading}
                        >
                            <Trash2 class="w-4 h-4" />
                            Delete
                        </button>
                    {/if}
                </div>

                {#if $settingsStore.error}
                    <div
                        class="p-3 bg-destructive border-2 border-black dark:border-white text-destructive-foreground text-sm font-bold flex items-center gap-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] uppercase"
                    >
                        <AlertTriangle class="w-4 h-4" />
                        Error: {$settingsStore.error}
                    </div>
                {/if}

                {#if $settingsStore.isKeyValid === true}
                    <div
                        class="p-3 bg-primary border-2 border-black dark:border-white text-primary-foreground text-sm font-bold shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] uppercase"
                    >
                        API Key is valid and active.
                    </div>
                {/if}
            </div>
        </div>

        <!-- Usage Stats -->
        {#if $settingsStore.usageStats}
            <div class="brutal-card p-6">
                <div class="flex items-start gap-4 mb-6">
                    <div
                        class="p-3 bg-secondary border-2 border-black dark:border-white"
                    >
                        <Activity class="w-6 h-6" />
                    </div>
                    <div>
                        <h3 class="text-xl font-black uppercase">
                            Usage Statistics
                        </h3>
                        <p class="text-sm text-muted-foreground mt-1">
                            Monitor your AI token consumption.
                        </p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div
                        class="p-4 border-2 border-black dark:border-white bg-secondary/20"
                    >
                        <p
                            class="text-xs font-bold uppercase text-muted-foreground"
                        >
                            Total Requests
                        </p>
                        <p class="text-2xl font-black font-mono mt-1">
                            {$settingsStore.usageStats.total_requests}
                        </p>
                    </div>
                    <div
                        class="p-4 border-2 border-black dark:border-white bg-secondary/20"
                    >
                        <p
                            class="text-xs font-bold uppercase text-muted-foreground"
                        >
                            Tokens Used
                        </p>
                        <p class="text-2xl font-black font-mono mt-1">
                            {$settingsStore.usageStats.total_tokens?.toLocaleString() ||
                                0}
                        </p>
                    </div>
                    <div
                        class="p-4 border-2 border-black dark:border-white bg-secondary/20"
                    >
                        <p
                            class="text-xs font-bold uppercase text-muted-foreground"
                        >
                            Est. Cost
                        </p>
                        <p class="text-2xl font-black font-mono mt-1">
                            ${$settingsStore.usageStats.cost_estimate?.toFixed(
                                4,
                            ) || "0.0000"}
                        </p>
                    </div>
                </div>
            </div>
        {/if}

        <!-- Push Notifications -->
        <NotificationSettings />
    {:else if activeTab === "billing"}
        <div class="brutal-card p-6">
            <div class="flex items-start gap-4 mb-6">
                <div
                    class="p-3 bg-green-400 border-2 border-black dark:border-white"
                >
                    <CreditCard class="w-6 h-6 text-black dark:text-white" />
                </div>
                <div>
                    <h3 class="text-xl font-black uppercase">Subscription</h3>
                    <p class="text-sm text-muted-foreground mt-1">
                        Manage your Focus by Kraliki Premium subscription.
                    </p>
                </div>
            </div>

            {#if isLoadingBilling}
                <div class="flex justify-center py-8">
                    <div
                        class="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full"
                    ></div>
                </div>
            {:else if subscriptionStatus}
                <div class="space-y-6">
                    <div
                        class="flex items-center justify-between p-4 border-2 border-black dark:border-white bg-secondary/20"
                    >
                        <div>
                            <p
                                class="text-xs font-bold uppercase text-muted-foreground"
                            >
                                Status
                            </p>
                            <p
                                class="text-lg font-black uppercase flex items-center gap-2"
                            >
                                {subscriptionStatus.isPremium
                                    ? "Premium Active"
                                    : "Free Plan"}
                                {#if subscriptionStatus.isPremium}
                                    <span
                                        class="w-3 h-3 bg-green-500 rounded-full border border-black"
                                    ></span>
                                {/if}
                            </p>
                        </div>
                        {#if subscriptionStatus.currentPeriodEnd}
                            <div class="text-right">
                                <p
                                    class="text-xs font-bold uppercase text-muted-foreground"
                                >
                                    Renews
                                </p>
                                <p class="font-mono font-bold">
                                    {new Date(
                                        subscriptionStatus.currentPeriodEnd *
                                            1000,
                                    ).toLocaleDateString()}
                                </p>
                            </div>
                        {/if}
                    </div>

                    <button
                        class="brutal-btn bg-black text-white dark:bg-white dark:text-black w-full md:w-auto"
                        onclick={handleManageSubscription}
                    >
                        {subscriptionStatus.hasSubscription
                            ? "Manage Subscription"
                            : "Upgrade to Premium"}
                    </button>
                </div>
            {:else}
                <p class="text-red-500 font-bold">
                    Failed to load subscription status.
                </p>
            {/if}
        </div>
    {:else if activeTab === "exports"}
        <div class="brutal-card p-6">
            <div class="flex items-start gap-4 mb-6">
                <div
                    class="p-3 bg-blue-400 border-2 border-black dark:border-white"
                >
                    <FileText class="w-6 h-6 text-black dark:text-white" />
                </div>
                <div>
                    <h3 class="text-xl font-black uppercase">
                        Invoices & Exports
                    </h3>
                    <p class="text-sm text-muted-foreground mt-1">
                        Generate reports of your billable hours.
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                    <label
                        for="exportStartDate"
                        class="text-xs font-bold uppercase">Start Date</label
                    >
                    <input
                        id="exportStartDate"
                        type="date"
                        bind:value={exportStartDate}
                        class="w-full p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>
                <div class="space-y-2">
                    <label
                        for="exportEndDate"
                        class="text-xs font-bold uppercase">End Date</label
                    >
                    <input
                        id="exportEndDate"
                        type="date"
                        bind:value={exportEndDate}
                        class="w-full p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>
            </div>

            <div class="flex gap-4 mt-6">
                <button
                    class="brutal-btn bg-white text-black flex-1 flex items-center justify-center gap-2"
                    onclick={() => handleExport("csv")}
                    disabled={isExporting}
                >
                    <Download class="w-4 h-4" />
                    Export CSV
                </button>
                <button
                    class="brutal-btn bg-white text-black flex-1 flex items-center justify-center gap-2"
                    onclick={() => handleExport("json")}
                    disabled={isExporting}
                >
                    <Download class="w-4 h-4" />
                    Export JSON
                </button>
            </div>
        </div>

        <!-- Academy Section (Phase 3 Monetization) -->
        <div class="brutal-card p-6 bg-terminal-green/10 border-terminal-green">
            <div class="flex items-start gap-4 mb-6">
                <div
                    class="p-3 bg-terminal-green border-2 border-black dark:border-white"
                >
                    <Zap class="w-6 h-6 text-black" />
                </div>
                <div>
                    <h3 class="text-xl font-black uppercase">
                        AI Automation Academy
                    </h3>
                    <p class="text-sm text-muted-foreground mt-1 font-bold">
                        {#if $authStore.user?.academyStatus === "WAITLIST"}
                            Status: Waitlisted (Early Bird)
                        {:else if $authStore.user?.academyStatus === "STUDENT"}
                            Status: Level 1 Student (Active)
                        {:else}
                            Level 1: Student (Beginner) — Q1 2026 Batch
                        {/if}
                    </p>
                </div>
            </div>

            <div class="space-y-4">
                {#if $authStore.user?.academyStatus === "WAITLIST"}
                    <p class="text-sm leading-relaxed">
                        You're on the list! We'll notify you as soon as the Q1
                        2026 batch opens for enrollment. Your early bird
                        discount is locked in.
                    </p>
                    <div
                        class="flex items-center gap-2 text-terminal-green font-bold"
                    >
                        <Check class="w-4 h-4" />
                        Waitlist Confirmed
                    </div>
                {:else if $authStore.user?.academyStatus === "STUDENT"}
                    <p class="text-sm leading-relaxed">
                        Welcome, Student. Your Academy dashboard and course
                        content will be available here starting Jan 1, 2026.
                    </p>
                    <button
                        class="brutal-btn bg-black text-white dark:bg-white dark:text-black opacity-50 cursor-not-allowed"
                    >
                        Academy Dashboard (Unlocks Jan 1)
                    </button>
                {:else}
                    <p class="text-sm leading-relaxed">
                        Join the waitlist for the first Academy batch. Learn to
                        move from "fear" to "mastery" with the same tools we use
                        to build Focus by Kraliki.
                    </p>
                    <a
                        href={academyUrl}
                        target="_blank"
                        class="brutal-btn bg-black text-white dark:bg-white dark:text-black inline-flex items-center gap-2"
                    >
                        Join Waitlist (€49 Early Bird)
                    </a>
                {/if}
            </div>
        </div>
    {/if}
</div>
