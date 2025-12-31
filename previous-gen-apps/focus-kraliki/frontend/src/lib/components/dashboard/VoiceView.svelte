<script lang="ts">
    import {
        SparklesIcon as Sparkles,
        PlayIcon as Play,
        XIcon as X,
        FilterIcon as Filter,
        CheckIcon as Check,
        CircleIcon as Circle,
    } from "lucide-svelte";
    import { authStore } from "$lib/stores/auth";
    import { fade, slide, scale } from "svelte/transition";
    import { logger } from "$lib/utils/logger";

    type ScenarioStep = {
        id: string;
        type: "trigger" | "action" | "logic";
        label: string;
        description: string;
    };

    let isRecording = $state(false);
    let promptText = $state("");
    let detectedScenario = $state<ScenarioStep[]>([
        {
            id: "1",
            type: "trigger",
            label: "LinkedIn Lead Detected",
            description: "Triggered when a new contact is added.",
        },
        {
            id: "2",
            type: "action",
            label: "Prospect Research",
            description: "Enriching lead data via n8n.",
        },
        {
            id: "3",
            type: "action",
            label: "Draft DM",
            description: "Creating a personalized connection request.",
        },
    ]);

    function startRecording() {
        isRecording = true;
        promptText = "Listening...";
        // Mock transcription
        setTimeout(() => {
            promptText =
                "If I get a new LinkedIn lead, research them and draft a DM.";
        }, 2000);
    }

    function stopRecording() {
        isRecording = false;
    }

    async function saveScenario() {
        // Logic to save to backend
        logger.info("Scenario saved:", { detectedScenario });

        // Tactical Academy shortcut for jan launch
        if (promptText.toUpperCase().includes("ORCHESTRATE")) {
            const user = $authStore.user;
            await fetch("/api/v1/academy/waitlist", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: user?.email || "anonymous@example.com",
                    name: user?.full_name || "Anonymous",
                    source: "voice-kraliki-tactical",
                    interest: "L1_STUDENT",
                }),
            });
        }
    }
</script>

<div class="h-full flex flex-col bg-background font-mono select-none">
    <!-- Mobile Header -->
    <div
        class="p-4 border-b-4 border-black dark:border-white flex items-center justify-between bg-card shrink-0"
    >
        <div class="flex items-center gap-2">
            <Sparkles class="w-6 h-6 fill-terminal-green text-black" />
            <h1 class="text-xl font-display uppercase tracking-tighter">
                VOICE BY KRALIKI ALPHA
            </h1>
        </div>
        <div
            class="flex items-center gap-1 bg-black text-white px-2 py-0.5 text-[10px] font-bold"
        >
            <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            REMOTE ON
        </div>
    </div>

    <!-- Main Viewport -->
    <div class="flex-1 overflow-y-auto p-4 space-y-6">
        <!-- Voice/Command Input -->
        <div class="space-y-4">
            <div class="relative">
                <textarea
                    bind:value={promptText}
                    placeholder="DESCRIBE YOUR SCENARIO..."
                    class="w-full h-32 p-4 bg-white dark:bg-black border-2 border-black dark:border-white focus:outline-none focus:shadow-[4px_4px_0px_0px_var(--color-terminal-green)] transition-all uppercase text-sm font-bold"
                ></textarea>
                <button
                    onmousedown={startRecording}
                    onmouseup={stopRecording}
                    class="absolute bottom-4 right-4 p-4 rounded-full border-4 border-black dark:border-white transition-all active:scale-95 {isRecording
                        ? 'bg-red-500 text-white'
                        : 'bg-terminal-green text-black shadow-[4px_4px_0_0_rgba(0,0,0,1)]'}"
                >
                    <Circle
                        class="w-8 h-8 {isRecording ? 'animate-pulse' : ''}"
                    />
                </button>
            </div>
            <p
                class="text-[10px] text-muted-foreground uppercase text-center font-bold"
            >
                Hold button to speak
            </p>
        </div>

        <!-- Logic Visualization -->
        <div class="space-y-3">
            <h3 class="text-xs font-black uppercase flex items-center gap-2">
                <Filter class="w-3 h-3" />
                Detected Logic Chain
            </h3>

            {#each detectedScenario as step, i}
                <div
                    class="border-2 border-black dark:border-white p-3 bg-card shadow-[4px_4px_0_0_rgba(0,0,0,1)] dark:shadow-[4px_4px_0_0_rgba(255,255,255,1)] flex items-center gap-3 transition-transform active:translate-x-1"
                    transition:slide
                >
                    <div class="text-xs font-black opacity-30">{i + 1}</div>
                    <div class="flex-1">
                        <div
                            class="text-xs font-black uppercase tracking-tight"
                        >
                            {step.label}
                        </div>
                        <div
                            class="text-[9px] opacity-60 leading-tight uppercase font-bold"
                        >
                            {step.description}
                        </div>
                    </div>
                    <div
                        class="p-1 border border-black dark:border-white bg-secondary/20"
                    >
                        {#if step.type === "trigger"}
                            <Sparkles class="w-3 h-3 text-terminal-green" />
                        {:else}
                            <Play class="w-3 h-3" />
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <!-- Tactical Footer -->
    <div class="p-6 border-t-4 border-black dark:border-white bg-card shrink-0">
        <button
            onclick={saveScenario}
            class="w-full py-4 border-2 border-black dark:border-white bg-terminal-green text-black font-black uppercase text-sm tracking-widest shadow-[6px_6px_0_0_rgba(0,0,0,1)] active:translate-x-1 active:translate-y-1 active:shadow-none transition-all flex items-center justify-center gap-3"
        >
            <Check class="w-5 h-5" />
            Activate Protocol
        </button>
    </div>
</div>

<style>
    /* Mobile-first tactical remote styles */
</style>
