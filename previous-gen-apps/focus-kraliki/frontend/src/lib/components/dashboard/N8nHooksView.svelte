<script lang="ts">
    import { onMount } from "svelte";
    import {
        Play,
        Activity,
        AlertCircle,
        Check,
        Clock,
        ExternalLink,
    } from "lucide-svelte";
    import { fade, slide } from "svelte/transition";
    import { logger } from "$lib/utils/logger";

    type Workflow = {
        id: string;
        name: string;
        active: boolean;
        lastRun?: string;
        status: "success" | "failed" | "running" | "idle";
    };

    let workflows = $state<Workflow[]>([
        {
            id: "1",
            name: "Prospect Research (L1 Academy)",
            active: true,
            lastRun: "2 hours ago",
            status: "success",
        },
        {
            id: "2",
            name: "LinkedIn Personalization Engine",
            active: true,
            lastRun: "15 mins ago",
            status: "running",
        },
        {
            id: "3",
            name: "Stripe Invoice Reconciliation",
            active: false,
            status: "idle",
        },
        {
            id: "4",
            name: "Lab by Kraliki Provisioning Audit",
            active: true,
            lastRun: "1 day ago",
            status: "failed",
        },
    ]);

    function getStatusColor(status: Workflow["status"]) {
        switch (status) {
            case "success":
                return "text-terminal-green";
            case "failed":
                return "text-destructive";
            case "running":
                return "text-primary animate-pulse";
            default:
                return "text-muted-foreground";
        }
    }

    async function triggerWorkflow(id: string) {
        const wf = workflows.find((w) => w.id === id);
        if (!wf) return;

        wf.status = "running";

        try {
            const response = await fetch(`/api/v1/orchestration/${id}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ context: { source: "dashboard" } }),
            });

            const result = await response.json();

            if (response.ok && result.success) {
                wf.status = "success";
                wf.lastRun = "just now";
            } else {
                wf.status = "failed";
                logger.error(
                    "Orchestration failed",
                    result.detail || "Unknown error",
                );
            }
        } catch (error) {
            logger.error("Orchestration trigger failed", error);
            wf.status = "failed";
        }
    }
</script>

<div class="p-6 space-y-8 font-mono">
    <div
        class="flex items-center justify-between border-b-4 border-black dark:border-white pb-4"
    >
        <h1 class="text-3xl font-display uppercase tracking-tighter">
            Workflow Orchestration
        </h1>
        <div
            class="flex items-center gap-2 bg-terminal-green text-black px-3 py-1 text-xs font-bold"
        >
            <Activity class="w-4 h-4" />
            SYSTEM LIVE
        </div>
    </div>

    <div class="grid gap-4">
        {#each workflows as workflow}
            <div
                class="border-2 border-black dark:border-white p-4 transition-all hover:translate-x-1 hover:translate-y-1 shadow-[4px_4px_0_0_rgba(0,0,0,1)] dark:shadow-[4px_4px_0_0_rgba(255,255,255,1)] bg-card"
                transition:slide
            >
                <div class="flex items-start justify-between">
                    <div class="space-y-1">
                        <div class="flex items-center gap-2">
                            <span class="text-lg font-black uppercase"
                                >{workflow.name}</span
                            >
                            {#if !workflow.active}
                                <span
                                    class="bg-muted text-muted-foreground px-2 py-0.5 text-[10px] font-bold"
                                    >INACTIVE</span
                                >
                            {/if}
                        </div>
                        <div class="flex items-center gap-4 text-xs opacity-70">
                            <span class="flex items-center gap-1">
                                <Clock class="w-3 h-3" />
                                {workflow.lastRun || "Never run"}
                            </span>
                            <span
                                class="flex items-center gap-1 font-bold {getStatusColor(
                                    workflow.status,
                                )}"
                            >
                                {#if workflow.status === "success"}
                                    <Check class="w-3 h-3" />
                                {:else if workflow.status === "failed"}
                                    <AlertCircle class="w-3 h-3" />
                                {/if}
                                {workflow.status.toUpperCase()}
                            </span>
                        </div>
                    </div>

                    <div class="flex items-center gap-2">
                        <button
                            onclick={() => triggerWorkflow(workflow.id)}
                            class="btn btn-sm btn-primary flex items-center gap-2"
                            disabled={workflow.status === "running"}
                        >
                            <Play class="w-3 h-3 fill-current" />
                            RUN
                        </button>
                        <a
                            href="https://n8n.verduona.io"
                            target="_blank"
                            class="btn btn-sm btn-ghost p-2"
                            title="Open in n8n"
                        >
                            <ExternalLink class="w-4 h-4" />
                        </a>
                    </div>
                </div>
            </div>
        {/each}
    </div>

    <div class="mt-8 border-t-2 border-black dark:border-white pt-6">
        <h3 class="text-sm font-black uppercase mb-4">Latest Execution Logs</h3>
        <div
            class="bg-black text-terminal-green p-4 text-[10px] space-y-1 overflow-x-auto border-2 border-black dark:border-white shadow-[4px_4px_0_0_rgba(0,0,0,1)]"
        >
            <p>
                [2025-12-22 18:35:01] INFO: Triggering flow 'Prospect
                Research'...
            </p>
            <p>
                [2025-12-22 18:35:04] SUCCESS: 14 new leads extracted and pushed
                to CRM.
            </p>
            <p>
                [2025-12-22 18:36:12] WARNING: LinkedIn rate limits detected.
                Throttling engine...
            </p>
            <p class="animate-pulse">_</p>
        </div>
    </div>
</div>

<style>
    @reference "../../../app.css";

    .btn {
        @apply border-2 border-black dark:border-white font-black uppercase text-[10px] tracking-widest transition-all;
    }
    .btn-primary {
        @apply bg-terminal-green text-black hover:shadow-[2px_2px_0_0_rgba(0,0,0,1)];
    }
    .btn-ghost {
        @apply hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black;
    }
</style>
