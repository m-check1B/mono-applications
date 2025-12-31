/**
 * Test data fixtures for E2E tests
 * CC-Lite 2026 - AI Call Center Platform
 */

/**
 * Backend URL - from environment or default
 */
export const BACKEND_URL =
	process.env.VITE_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Frontend URL - from environment or default
 */
export const FRONTEND_URL =
	process.env.PLAYWRIGHT_BASE_URL || process.env.FRONTEND_URL || 'http://localhost:3000';

/**
 * Test user credentials (matches CC-Lite test credentials)
 */
export const TEST_USER = {
	email: process.env.TEST_USER_EMAIL || 'testuser@example.com',
	password: process.env.TEST_USER_PASSWORD || 'test123',
	name: 'Test User',
	role: 'user'
};

/**
 * Test admin user credentials
 */
export const TEST_ADMIN = {
	email: process.env.TEST_ADMIN_EMAIL || 'admin@example.com',
	password: process.env.TEST_ADMIN_PASSWORD || 'AdminPassword123!',
	name: 'Admin User',
	role: 'admin'
};

/**
 * Test agent user credentials
 */
export const TEST_AGENT = {
	email: process.env.TEST_AGENT_EMAIL || 'agent@example.com',
	password: process.env.TEST_AGENT_PASSWORD || 'AgentPassword123!',
	name: 'Agent User',
	role: 'agent'
};

/**
 * Test users collection
 */
export const TEST_USERS = {
	user: TEST_USER,
	admin: TEST_ADMIN,
	agent: TEST_AGENT
};

/**
 * Test phone numbers for various scenarios
 */
export const TEST_PHONE_NUMBERS = {
	// Valid test numbers
	valid: {
		us: '+15551234567',
		uk: '+447911123456',
		international: '+33612345678'
	},

	// Invalid test numbers
	invalid: {
		tooShort: '+1555',
		noCountryCode: '5551234567',
		invalidFormat: 'not-a-phone-number'
	},

	// Special test numbers (for testing different scenarios)
	special: {
		// Number that will simulate a busy signal
		busy: '+15559998888',
		// Number that will simulate no answer
		noAnswer: '+15559997777',
		// Number that will simulate call failure
		failed: '+15559996666',
		// Number that will succeed
		success: '+15559995555'
	}
};

/**
 * Test companies
 */
export const TEST_COMPANIES = [
	{
		id: 'company-1',
		name: 'Acme Corporation',
		domain: 'acme.com',
		phone: '+15551111111',
		address: '123 Main St, San Francisco, CA 94102',
		settings: {
			allowedProviders: ['twilio', 'vonage'],
			defaultProvider: 'twilio'
		}
	},
	{
		id: 'company-2',
		name: 'TechCorp Inc',
		domain: 'techcorp.com',
		phone: '+15552222222',
		address: '456 Tech Ave, New York, NY 10001',
		settings: {
			allowedProviders: ['twilio'],
			defaultProvider: 'twilio'
		}
	},
	{
		id: 'company-3',
		name: 'Global Solutions Ltd',
		domain: 'globalsolutions.com',
		phone: '+15553333333',
		address: '789 Business Blvd, London, UK',
		settings: {
			allowedProviders: ['vonage', 'twilio'],
			defaultProvider: 'vonage'
		}
	}
];

/**
 * Test provider configurations
 */
export const TEST_PROVIDERS = {
	twilio: {
		id: 'twilio-1',
		name: 'Twilio',
		type: 'twilio',
		enabled: true,
		config: {
			accountSid: 'AC_test_account_sid',
			authToken: 'test_auth_token',
			phoneNumber: '+15550001111'
		},
		priority: 1
	},
	vonage: {
		id: 'vonage-1',
		name: 'Vonage',
		type: 'vonage',
		enabled: true,
		config: {
			apiKey: 'test_api_key',
			apiSecret: 'test_api_secret',
			applicationId: 'test_app_id'
		},
		priority: 2
	},
	plivo: {
		id: 'plivo-1',
		name: 'Plivo',
		type: 'plivo',
		enabled: false,
		config: {
			authId: 'test_auth_id',
			authToken: 'test_auth_token'
		},
		priority: 3
	}
};

/**
 * Mock API responses
 */
export const MOCK_API_RESPONSES = {
	/**
	 * Successful login response
	 */
	loginSuccess: {
		access_token: 'mock_access_token_1234567890',
		refresh_token: 'mock_refresh_token_0987654321',
		expires_at: Date.now() + 3600000, // 1 hour from now
		user: {
			id: 'user-123',
			email: TEST_USER.email,
			name: TEST_USER.name,
			role: TEST_USER.role
		}
	},

	/**
	 * Failed login response
	 */
	loginFailure: {
		error: 'Invalid credentials',
		detail: 'The email or password you entered is incorrect'
	},

	/**
	 * User profile response
	 */
	userProfile: {
		id: 'user-123',
		email: TEST_USER.email,
		name: TEST_USER.name,
		role: TEST_USER.role,
		createdAt: '2024-01-01T00:00:00Z',
		lastLogin: new Date().toISOString()
	},

	/**
	 * Call list response
	 */
	callList: [
		{
			id: 'call-1',
			phoneNumber: '+15551234567',
			direction: 'outbound',
			status: 'completed',
			duration: 125,
			startTime: '2024-01-15T10:30:00Z',
			endTime: '2024-01-15T10:32:05Z',
			provider: 'twilio'
		},
		{
			id: 'call-2',
			phoneNumber: '+15559876543',
			direction: 'inbound',
			status: 'completed',
			duration: 300,
			startTime: '2024-01-15T11:00:00Z',
			endTime: '2024-01-15T11:05:00Z',
			provider: 'vonage'
		},
		{
			id: 'call-3',
			phoneNumber: '+15555555555',
			direction: 'outbound',
			status: 'failed',
			duration: 0,
			startTime: '2024-01-15T12:00:00Z',
			endTime: '2024-01-15T12:00:05Z',
			provider: 'twilio'
		}
	],

	/**
	 * Start call response
	 */
	startCall: {
		id: 'call-new-123',
		phoneNumber: '+15551234567',
		direction: 'outbound',
		status: 'in-progress',
		startTime: new Date().toISOString(),
		provider: 'twilio'
	},

	/**
	 * End call response
	 */
	endCall: {
		id: 'call-new-123',
		status: 'completed',
		duration: 45,
		endTime: new Date().toISOString()
	},

	/**
	 * Provider health status
	 */
	providerHealth: {
		twilio: {
			status: 'healthy',
			latency: 50,
			successRate: 0.99,
			lastCheck: new Date().toISOString()
		},
		vonage: {
			status: 'healthy',
			latency: 75,
			successRate: 0.98,
			lastCheck: new Date().toISOString()
		},
		plivo: {
			status: 'down',
			latency: 0,
			successRate: 0,
			lastCheck: new Date().toISOString()
		}
	},

	/**
	 * Analytics data
	 */
	analytics: {
		totalCalls: 1250,
		completedCalls: 1100,
		failedCalls: 150,
		averageDuration: 180,
		totalDuration: 225000,
		callsByProvider: {
			twilio: 750,
			vonage: 500
		},
		callsByDay: [
			{ date: '2024-01-15', count: 45 },
			{ date: '2024-01-14', count: 52 },
			{ date: '2024-01-13', count: 38 }
		]
	},

	/**
	 * Compliance data
	 */
	compliance: {
		recordingEnabled: true,
		consentRequired: true,
		retentionDays: 90,
		encryptionEnabled: true,
		gdprCompliant: true
	}
};

/**
 * Test call scenarios
 */
export const TEST_CALL_SCENARIOS = {
	/**
	 * Successful outbound call
	 */
	successfulOutbound: {
		phoneNumber: TEST_PHONE_NUMBERS.special.success,
		expectedDuration: 30,
		expectedStatus: 'completed'
	},

	/**
	 * Failed call (number busy)
	 */
	busyNumber: {
		phoneNumber: TEST_PHONE_NUMBERS.special.busy,
		expectedStatus: 'failed',
		expectedError: 'Number is busy'
	},

	/**
	 * No answer
	 */
	noAnswer: {
		phoneNumber: TEST_PHONE_NUMBERS.special.noAnswer,
		expectedStatus: 'no-answer',
		timeout: 30000
	},

	/**
	 * Call with provider failover
	 */
	providerFailover: {
		phoneNumber: TEST_PHONE_NUMBERS.valid.us,
		primaryProvider: 'twilio',
		fallbackProvider: 'vonage'
	}
};

/**
 * Test form data
 */
export const TEST_FORM_DATA = {
	/**
	 * Valid registration form
	 */
	validRegistration: {
		name: 'New Test User',
		email: 'new.user@example.com',
		password: 'ValidPassword123!',
		confirmPassword: 'ValidPassword123!'
	},

	/**
	 * Invalid registration form (password mismatch)
	 */
	invalidRegistration: {
		name: 'Test User',
		email: 'test@example.com',
		password: 'Password123!',
		confirmPassword: 'DifferentPassword123!'
	},

	/**
	 * Valid call form
	 */
	validCall: {
		phoneNumber: TEST_PHONE_NUMBERS.valid.us,
		provider: 'twilio',
		recordCall: true
	},

	/**
	 * Invalid call form (invalid phone)
	 */
	invalidCall: {
		phoneNumber: TEST_PHONE_NUMBERS.invalid.tooShort,
		provider: 'twilio'
	}
};

/**
 * Test API endpoints
 */
export const TEST_ENDPOINTS = {
	auth: {
		login: '/api/v1/auth/login',
		register: '/api/v1/auth/register',
		logout: '/api/v1/auth/logout',
		refresh: '/api/v1/auth/refresh'
	},
	calls: {
		list: '/api/v1/calls',
		start: '/api/v1/calls/start',
		end: '/api/v1/calls/:id/end',
		get: '/api/v1/calls/:id'
	},
	providers: {
		list: '/api/v1/providers',
		health: '/api/v1/providers/health',
		switch: '/api/v1/providers/switch'
	},
	analytics: {
		dashboard: '/api/v1/analytics/dashboard',
		reports: '/api/v1/analytics/reports'
	},
	companies: {
		list: '/api/v1/companies',
		get: '/api/v1/companies/:id',
		settings: '/api/v1/companies/:id/settings'
	},
	compliance: {
		settings: '/api/v1/compliance/settings',
		reports: '/api/v1/compliance/reports'
	}
};

/**
 * Test timeouts
 */
export const TEST_TIMEOUTS = {
	short: 5000, // 5 seconds
	medium: 10000, // 10 seconds
	long: 30000, // 30 seconds
	callConnection: 15000, // 15 seconds for call to connect
	pageLoad: 10000 // 10 seconds for page to load
};

/**
 * Test environment settings
 */
export const TEST_ENV = {
	isCI: process.env.CI === 'true',
	headless: process.env.HEADLESS !== 'false',
	slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO, 10) : 0,
	video: process.env.VIDEO === 'true',
	screenshot: process.env.SCREENSHOT === 'on-failure'
};

/**
 * CC-Lite specific test data
 */
export const CC_LITE_TEST_DATA = {
	/**
	 * Test campaigns
	 */
	campaigns: [
		{
			id: 1,
			name: 'Insurance Renewal',
			language: 'en',
			stepsCount: 5,
			description: 'Multi-step follow-up call with sentiment tracking.'
		},
		{
			id: 2,
			name: 'Solar Outreach',
			language: 'en',
			stepsCount: 4,
			description: 'Energy-efficiency appointment setting.'
		},
		{
			id: 3,
			name: 'Customer Re-engagement',
			language: 'en',
			stepsCount: 3,
			description: 'Generic follow-up script for dormant accounts.'
		}
	],

	/**
	 * Available countries for calls
	 */
	countries: [
		{ code: 'US', name: 'United States', flag: '🇺🇸' },
		{ code: 'CZ', name: 'Czech Republic', flag: '🇨🇿' },
		{ code: 'ES', name: 'Spain', flag: '🇪🇸' }
	],

	/**
	 * Available languages
	 */
	languages: [
		{ code: 'en', label: 'English' },
		{ code: 'es', label: 'Spanish' },
		{ code: 'cz', label: 'Czech' }
	],

	/**
	 * Audio modes
	 */
	audioModes: ['twilio', 'local'],

	/**
	 * AI Providers
	 */
	providers: [
		{
			id: 'gemini',
			name: 'Google Gemini Live',
			capabilities: { realtime: true, multimodal: true, functionCalling: true }
		},
		{
			id: 'openai',
			name: 'OpenAI Realtime',
			capabilities: { realtime: true, multimodal: false, functionCalling: true }
		},
		{
			id: 'deepgram_nova3',
			name: 'Deepgram Nova 3',
			capabilities: { realtime: true, multimodal: false, functionCalling: true }
		}
	],

	/**
	 * Analytics tabs
	 */
	analyticsTabs: ['overview', 'metrics', 'health'],

	/**
	 * Test target company
	 */
	testCompany: {
		name: 'Test Corp Inc',
		phone: '+15551234567'
	},

	/**
	 * Test AI instructions
	 */
	testAIInstructions:
		'You are a professional sales representative conducting outbound calls. Be friendly, professional, and helpful.'
};

/**
 * Mock API responses for CC-Lite
 */
export const CC_LITE_MOCK_RESPONSES = {
	/**
	 * Campaigns list response
	 */
	campaignsList: CC_LITE_TEST_DATA.campaigns,

	/**
	 * Empty campaigns response
	 */
	emptyCampaigns: [],

	/**
	 * Voice config response
	 */
	voiceConfig: {
		voices: {
			alloy: { gender: 'neutral', characteristics: 'warm, balanced' },
			echo: { gender: 'male', characteristics: 'clear, professional' },
			fable: { gender: 'female', characteristics: 'expressive, storytelling' },
			onyx: { gender: 'male', characteristics: 'deep, authoritative' },
			nova: { gender: 'female', characteristics: 'friendly, conversational' },
			shimmer: { gender: 'female', characteristics: 'soft, calming' }
		},
		currentDefault: 'alloy',
		voiceDescriptions: {
			alloy: 'Alloy — neutral · warm, balanced',
			echo: 'Echo — male · clear, professional',
			fable: 'Fable — female · expressive, storytelling',
			onyx: 'Onyx — male · deep, authoritative',
			nova: 'Nova — female · friendly, conversational',
			shimmer: 'Shimmer — female · soft, calming'
		}
	},

	/**
	 * Models config response
	 */
	modelsConfig: {
		availableModels: {
			'gpt-4o-realtime': { name: 'GPT-4o Realtime' },
			'gemini-2.0-flash-live': { name: 'Gemini 2.0 Flash Live' },
			'deepgram-nova-3': { name: 'Deepgram Nova 3' }
		},
		defaultModel: 'gpt-4o-realtime'
	},

	/**
	 * Analytics dashboard response
	 */
	analyticsDashboard: {
		totalCalls: 1250,
		completedCalls: 1100,
		failedCalls: 150,
		averageDuration: 180,
		callsByProvider: {
			gemini: 450,
			openai: 500,
			deepgram: 300
		}
	},

	/**
	 * Provider health response
	 */
	providerHealth: {
		gemini: { status: 'healthy', latency: 45, successRate: 0.99 },
		openai: { status: 'healthy', latency: 52, successRate: 0.98 },
		deepgram: { status: 'healthy', latency: 38, successRate: 0.995 }
	}
};
