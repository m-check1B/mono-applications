// @ts-nocheck
import type { PageLoad } from './$types';

export const load = async ({ parent }: Parameters<PageLoad>[0]) => {
	const parentData = await parent();
	
	// Generate session data for the chat
	const sessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
	const userId = 'user_123'; // In real app, get from auth
	const companyId = 'company_456'; // In real app, get from user context

	return {
		...parentData,
		sessionId,
		userId,
		companyId
	};
};