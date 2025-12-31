import { dev } from '$app/environment';
import { env } from '$env/dynamic/public';

export const BACKEND_URL =
	env.PUBLIC_BACKEND_URL && env.PUBLIC_BACKEND_URL.trim().length > 0
		? env.PUBLIC_BACKEND_URL
		: dev
			? 'http://localhost:8000'
			: 'https://gemini-api.verduona.com';

export const WS_URL =
	env.PUBLIC_WS_URL && env.PUBLIC_WS_URL.trim().length > 0
		? env.PUBLIC_WS_URL
		: BACKEND_URL.replace(/^http/, 'ws');

const TELNYX_DEFAULT_FROM_NUMBER =
	env.PUBLIC_TELNYX_FROM_NUMBER && env.PUBLIC_TELNYX_FROM_NUMBER.trim().length > 0
		? env.PUBLIC_TELNYX_FROM_NUMBER
		: '';

export const DEFAULT_FROM_NUMBER =
	TELNYX_DEFAULT_FROM_NUMBER.length > 0
		? TELNYX_DEFAULT_FROM_NUMBER
		: env.PUBLIC_TWILIO_FROM_NUMBER && env.PUBLIC_TWILIO_FROM_NUMBER.trim().length > 0
			? env.PUBLIC_TWILIO_FROM_NUMBER
			: '+420228810376';

export const COUNTRY_FROM_NUMBERS = {
	US:
		env.PUBLIC_TELNYX_FROM_NUMBER_US && env.PUBLIC_TELNYX_FROM_NUMBER_US.trim().length > 0
			? env.PUBLIC_TELNYX_FROM_NUMBER_US
			: env.PUBLIC_TWILIO_FROM_NUMBER_US && env.PUBLIC_TWILIO_FROM_NUMBER_US.trim().length > 0
				? env.PUBLIC_TWILIO_FROM_NUMBER_US
				: '+18455954168',
	CZ:
		env.PUBLIC_TELNYX_FROM_NUMBER_CZ && env.PUBLIC_TELNYX_FROM_NUMBER_CZ.trim().length > 0
			? env.PUBLIC_TELNYX_FROM_NUMBER_CZ
			: env.PUBLIC_TWILIO_FROM_NUMBER_CZ && env.PUBLIC_TWILIO_FROM_NUMBER_CZ.trim().length > 0
				? env.PUBLIC_TWILIO_FROM_NUMBER_CZ
				: '+420228810376',
	ES:
		env.PUBLIC_TELNYX_FROM_NUMBER_ES && env.PUBLIC_TELNYX_FROM_NUMBER_ES.trim().length > 0
			? env.PUBLIC_TELNYX_FROM_NUMBER_ES
			: env.PUBLIC_TWILIO_FROM_NUMBER_ES && env.PUBLIC_TWILIO_FROM_NUMBER_ES.trim().length > 0
				? env.PUBLIC_TWILIO_FROM_NUMBER_ES
				: '+34123456789'
} as const;

export const STORAGE_KEYS = {
	auth: 'operator-console.auth',
	theme: 'operator-console.theme',
	targetCompanies: 'operator-console.target-companies'
} as const;
