<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { CheckCircle2, X, Info, AlertTriangle, XCircle } from 'lucide-svelte';

	interface Props {
		message?: string;
		type?: 'success' | 'info' | 'warning' | 'error';
		duration?: number;
		onClose?: (() => void) | null;
	}

	let { message = '', type = 'info', duration = 3000, onClose = null }: Props = $props();

	let visible = $state(true);

	onMount(() => {
		if (duration > 0) {
			const timer = setTimeout(() => {
				close();
			}, duration);

			return () => clearTimeout(timer);
		}
	});

	function close() {
		visible = false;
		if (onClose) {
			setTimeout(onClose, 300); // Wait for fade out
		}
	}

	function getIcon() {
		switch (type) {
			case 'success':
				return CheckCircle2;
			case 'error':
				return XCircle;
			case 'warning':
				return AlertTriangle;
			default:
				return Info;
		}
	}

	function getStyles() {
		switch (type) {
			case 'success':
				return 'bg-green-400 text-black border-black';
			case 'error':
				return 'bg-red-500 text-white border-black';
			case 'warning':
				return 'bg-yellow-400 text-black border-black';
			default:
				return 'bg-white text-black border-black';
		}
	}

	let Icon = $derived(getIcon());
</script>

{#if visible}
	<div
		class="fixed top-4 right-4 z-50 max-w-sm"
		transition:fly={{ y: -20, duration: 300 }}
	>
		<div
			class="flex items-center gap-3 p-4 border-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] {getStyles()}"
			role="alert"
		>
			<Icon class="w-5 h-5 flex-shrink-0" />
			<p class="flex-1 text-sm font-black uppercase">{message}</p>
			<button
				class="p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors border border-transparent hover:border-current"
				onclick={close}
				aria-label="Close notification"
			>
				<X class="w-4 h-4" />
			</button>
		</div>
	</div>
{/if}
