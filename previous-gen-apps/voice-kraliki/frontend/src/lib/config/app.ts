export interface AppConfig {
	backendUrl: string;
	wsUrl: string;
	defaultFromNumber: string;
	countryFromNumbers: Record<string, string>;
}

export const APP_CONFIG_KEY = Symbol('app-config');
