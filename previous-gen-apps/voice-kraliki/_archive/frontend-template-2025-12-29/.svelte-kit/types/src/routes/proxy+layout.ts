// @ts-nocheck
import type { LayoutLoad } from './$types';
import { BACKEND_URL, WS_URL, COUNTRY_FROM_NUMBERS, DEFAULT_FROM_NUMBER } from '$lib/config/env';

export const load = () => {
	return {
		config: {
			backendUrl: BACKEND_URL,
			wsUrl: WS_URL,
			defaultFromNumber: DEFAULT_FROM_NUMBER,
			countryFromNumbers: COUNTRY_FROM_NUMBERS
		}
	};
};
;null as any as LayoutLoad;