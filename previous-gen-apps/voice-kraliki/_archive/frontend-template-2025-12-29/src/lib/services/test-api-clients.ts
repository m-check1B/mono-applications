/**
 * Test file for API client integrations
 * This file can be used to verify that the new API clients work correctly
 */

import {
	getCompanies,
	createCompany,
	getCompanyStats,
	getIndustries,
	getCompanySizes,
	type CompanyCreate
} from './companies';

import {
	getAnalyticsSummary,
	getActiveCalls,
	getCallCounts,
	getRealtimeMetrics,
	startCallTracking,
	endCallTracking,
	type StartCallTrackingRequest,
	type EndCallTrackingRequest
} from './analytics';

import {
	captureConsent,
	checkConsent,
	getRetentionPolicies,
	detectRegion,
	type ConsentRequest,
	type ConsentCheckRequest
} from './compliance';

/**
 * Test companies API
 */
export async function testCompaniesAPI() {
	console.log('Testing Companies API...');
	
	try {
		// Test getting industries and sizes first
		const industries = await getIndustries();
		console.log('✓ Industries:', industries.industries.length);
		
		const sizes = await getCompanySizes();
		console.log('✓ Company sizes:', sizes.sizes.length);
		
		// Test listing companies
		const companies = await getCompanies({ limit: 5 });
		console.log('✓ Companies list:', companies.length);
		
		// Test creating a company
		const newCompanyData: CompanyCreate = {
			name: 'Test Company',
			domain: 'testcompany.com',
			industry: 'Technology',
			size: 'small',
			phone_number: '+1234567890',
			email: 'test@testcompany.com'
		};
		
		const newCompany = await createCompany(newCompanyData);
		console.log('✓ Company created:', newCompany.id);
		
		// Test getting company stats
		const stats = await getCompanyStats(newCompany.id);
		console.log('✓ Company stats:', stats.total_calls);
		
		console.log('Companies API test completed successfully!');
		return true;
	} catch (error) {
		console.error('Companies API test failed:', error);
		return false;
	}
}

/**
 * Test analytics API
 */
export async function testAnalyticsAPI() {
	console.log('Testing Analytics API...');
	
	try {
		// Test getting analytics summary
		const summary = await getAnalyticsSummary();
		console.log('✓ Analytics summary:', summary.summary.total_calls);
		
		// Test getting active calls
		const activeCalls = await getActiveCalls();
		console.log('✓ Active calls:', activeCalls.count);
		
		// Test getting call counts
		const counts = await getCallCounts();
		console.log('✓ Call counts:', counts.counts);
		
		// Test getting realtime metrics
		const realtime = await getRealtimeMetrics();
		console.log('✓ Realtime metrics:', realtime.active_calls);
		
		// Test call tracking (mock data)
		const callId = `test-call-${Date.now()}`;
		const sessionId = `test-session-${Date.now()}`;
		
		const startRequest: StartCallTrackingRequest = {
			call_id: callId,
			session_id: sessionId,
			provider_id: 'test-provider'
		};
		
		await startCallTracking(startRequest);
		console.log('✓ Call tracking started');
		
		const endRequest: EndCallTrackingRequest = {
			call_id: callId,
			outcome: 'success'
		};
		
		await endCallTracking(endRequest);
		console.log('✓ Call tracking ended');
		
		console.log('Analytics API test completed successfully!');
		return true;
	} catch (error) {
		console.error('Analytics API test failed:', error);
		return false;
	}
}

/**
 * Test compliance API
 */
export async function testComplianceAPI() {
	console.log('Testing Compliance API...');
	
	try {
		// Test region detection
		const region = await detectRegion('+1234567890');
		console.log('✓ Region detection:', region.region);
		
		// Test getting retention policies
		const policies = await getRetentionPolicies();
		console.log('✓ Retention policies:', policies.count);
		
		// Test consent capture
		const consentRequest: ConsentRequest = {
			session_id: `test-session-${Date.now()}`,
			customer_phone: '+1234567890',
			consent_type: 'recording',
			status: 'granted',
			method: 'verbal'
		};
		
		const consent = await captureConsent(consentRequest);
		console.log('✓ Consent captured:', consent.consent_id);
		
		// Test consent check
		const checkRequest: ConsentCheckRequest = {
			customer_phone: '+1234567890',
			consent_type: 'recording'
		};
		
		const consentCheck = await checkConsent(checkRequest);
		console.log('✓ Consent check:', consentCheck.has_consent);
		
		console.log('Compliance API test completed successfully!');
		return true;
	} catch (error) {
		console.error('Compliance API test failed:', error);
		return false;
	}
}

/**
 * Run all API tests
 */
export async function runAllAPITests() {
	console.log('🧪 Starting API Client Integration Tests...\n');
	
	const results = {
		companies: await testCompaniesAPI(),
		analytics: await testAnalyticsAPI(),
		compliance: await testComplianceAPI()
	};
	
	const passed = Object.values(results).filter(Boolean).length;
	const total = Object.keys(results).length;
	
	console.log(`\n📊 Test Results: ${passed}/${total} API clients working correctly`);
	
	if (passed === total) {
		console.log('🎉 All API client integrations are working!');
	} else {
		console.log('⚠️ Some API client integrations need attention');
	}
	
	return results;
}

/**
 * Quick health check for all APIs
 */
export async function quickHealthCheck() {
	const checks = [
		{ name: 'Companies', fn: () => getIndustries() },
		{ name: 'Analytics', fn: () => getCallCounts() },
		{ name: 'Compliance', fn: () => getRetentionPolicies() }
	];
	
	const results: Record<string, boolean> = {};
	
	for (const check of checks) {
		try {
			await check.fn();
			results[check.name] = true;
		} catch (error) {
			results[check.name] = false;
		}
	}
	
	return results;
}