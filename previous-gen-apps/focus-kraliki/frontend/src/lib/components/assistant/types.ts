import type { ComponentType } from 'svelte';

export interface AssistantNavItem {
	label: string;
	icon: ComponentType;
	href?: string;
	disabled?: boolean;
	badge?: string;
}
