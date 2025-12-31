import { getContext } from 'svelte';
import { APP_CONFIG_KEY, type AppConfig } from '$lib/config/app';

export function useAppConfig(): AppConfig {
	const config = getContext<AppConfig | undefined>(APP_CONFIG_KEY);

	if (!config) {
		throw new Error('AppConfig context is missing. Make sure you are inside the root layout.');
	}

	return config;
}
