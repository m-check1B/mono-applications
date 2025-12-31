import { writable } from 'svelte/store';

export type ToastType = 'success' | 'info' | 'warning' | 'error';

// ✨ Gap #12: Enhanced toast with undo/retry actions
export interface ToastAction {
	label: string;
	onClick: () => void | Promise<void>;
}

export interface ToastMessage {
	id: string;
	type: ToastType;
	message: string;
	timeout?: number;
	action?: ToastAction; // ✨ Gap #12: Undo/retry support
}

function createToastStore() {
	const { subscribe, update } = writable<ToastMessage[]>([]);

	function push(
		message: string,
		type: ToastType = 'info',
		timeout = 4000,
		action?: ToastAction // ✨ Gap #12: Optional action
	) {
		const id = crypto.randomUUID?.() || String(Date.now());
		const toast: ToastMessage = { id, type, message, timeout, action };

		update((list) => [...list, toast]);

		if (timeout > 0) {
			setTimeout(() => dismiss(id), timeout);
		}
	}

	function dismiss(id: string) {
		update((list) => list.filter((t) => t.id !== id));
	}

	return {
		subscribe,
		push,
		success: (message: string, timeout?: number, action?: ToastAction) =>
			push(message, 'success', timeout, action),
		info: (message: string, timeout?: number, action?: ToastAction) =>
			push(message, 'info', timeout, action),
		warning: (message: string, timeout?: number, action?: ToastAction) =>
			push(message, 'warning', timeout, action),
		error: (message: string, timeout?: number, action?: ToastAction) =>
			push(message, 'error', timeout, action),
		dismiss,

		// ✨ Gap #12: Convenience methods for common patterns
		successWithUndo: (
			message: string,
			onUndo: () => void | Promise<void>,
			timeout = 6000
		) => {
			push(message, 'success', timeout, {
				label: 'Undo',
				onClick: onUndo
			});
		},

		errorWithRetry: (
			message: string,
			onRetry: () => void | Promise<void>,
			timeout = 8000
		) => {
			push(message, 'error', timeout, {
				label: 'Retry',
				onClick: onRetry
			});
		}
	};
}

export const toast = createToastStore();
