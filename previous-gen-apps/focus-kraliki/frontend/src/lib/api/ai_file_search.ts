/**
 * AI File Search API Client
 * Gemini-powered file search for knowledge base
 */

import { api } from './client';

export interface FileSearchCitation {
	documentName: string;
	knowledgeItemId?: string;
	excerpt?: string;
}

export interface FileSearchResponse {
	answer: string;
	citations: FileSearchCitation[];
}

export interface FileSearchRequest {
	query: string;
	context?: Record<string, any>;
}

/**
 * Query the AI file search endpoint
 * @param query - The user's search query
 * @param context - Optional additional context
 * @returns AI-generated answer with citations
 */
export async function aiFileSearchQuery(
	query: string,
	context?: Record<string, any>
): Promise<FileSearchResponse> {
	try {
		const response = await api.post<FileSearchResponse>('/ai/file-search/query', {
			query,
			context
		});

		return response;
	} catch (error: any) {
		// Enhance error message for better UX
		if (error.status === 404) {
			throw new Error(
				'AI File Search endpoint not found. Make sure the backend is running with Gemini integration enabled.'
			);
		} else if (error.status === 503) {
			throw new Error(
				'AI File Search is temporarily unavailable. Please try again in a few moments.'
			);
		} else {
			throw new Error(error.detail || 'File search failed. Please try again.');
		}
	}
}
