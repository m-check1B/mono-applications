/**
 * Knowledge Store
 * Svelte writable store for knowledge management
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import {
	OFFLINE_STORES,
	clearOfflineStore,
	isOnline,
	offlineKnowledge,
	offlineKnowledgeTypes,
	queueOperation
} from '$lib/utils/offlineStorage';

export interface ItemType {
	id: string;
	userId: string;
	name: string;
	icon: string;
	color: string;
	createdAt?: string;
	updatedAt?: string;
}

export interface KnowledgeItem {
	id: string;
	userId: string;
	typeId: string;
	title: string;
	content: string;
	item_metadata?: any;
	completed: boolean;
	createdAt?: string;
	updatedAt?: string;
}

export interface KnowledgeState {
	items: KnowledgeItem[];
	itemTypes: ItemType[];
	isLoading: boolean;
	error: string | null;
	selectedTypeId: string | null;
}

const initialState: KnowledgeState = {
	items: [],
	itemTypes: [],
	isLoading: false,
	error: null,
	selectedTypeId: null
};

function createKnowledgeStore() {
	const { subscribe, set, update } = writable<KnowledgeState>(initialState);

	return {
		subscribe,

		// Item Types
		async loadItemTypes() {
			update((state) => ({ ...state, isLoading: true, error: null }));

			try {
				if (!isOnline()) {
					const itemTypes = await offlineKnowledgeTypes.getAll();

					update((state) => ({
						...state,
						itemTypes,
						isLoading: false
					}));

					return { success: true, itemTypes };
				}

				const response: any = await api.knowledge.listItemTypes();
				const itemTypes = response.itemTypes || [];

				await clearOfflineStore(OFFLINE_STORES.KNOWLEDGE_TYPES);
				for (const itemType of itemTypes) {
					await offlineKnowledgeTypes.save(itemType);
				}

				update((state) => ({
					...state,
					itemTypes,
					isLoading: false
				}));

				return { success: true, itemTypes };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to load item types';
				update((state) => ({
					...state,
					isLoading: false,
					error: errorMessage
				}));
				return { success: false, error: errorMessage };
			}
		},

		async createItemType(data: { name: string; icon?: string; color?: string }) {
			try {
				if (!isOnline()) {
					return { success: false, error: 'Offline mode: cannot create item types.' };
				}

				const newType: any = await api.knowledge.createItemType(data);
				await offlineKnowledgeTypes.save(newType);

				update((state) => ({
					...state,
					itemTypes: [...state.itemTypes, newType]
				}));

				return { success: true, itemType: newType };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to create item type';
				return { success: false, error: errorMessage };
			}
		},

		async updateItemType(typeId: string, updates: any) {
			try {
				if (!isOnline()) {
					return { success: false, error: 'Offline mode: cannot update item types.' };
				}

				const updatedType: any = await api.knowledge.updateItemType(typeId, updates);
				await offlineKnowledgeTypes.save(updatedType);

				update((state) => ({
					...state,
					itemTypes: state.itemTypes.map((t) => (t.id === typeId ? updatedType : t))
				}));

				return { success: true, itemType: updatedType };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to update item type';
				return { success: false, error: errorMessage };
			}
		},

		async deleteItemType(typeId: string) {
			try {
				if (!isOnline()) {
					return { success: false, error: 'Offline mode: cannot delete item types.' };
				}

				await api.knowledge.deleteItemType(typeId);
				await offlineKnowledgeTypes.delete(typeId);

				update((state) => ({
					...state,
					itemTypes: state.itemTypes.filter((t) => t.id !== typeId)
				}));

				return { success: true };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to delete item type';
				return { success: false, error: errorMessage };
			}
		},

		// Knowledge Items
		async loadKnowledgeItems(filters?: { typeId?: string; completed?: boolean }) {
			update((state) => ({ ...state, isLoading: true, error: null }));

			try {
				if (!isOnline()) {
					const offlineItems = await offlineKnowledge.getAll();
					const items = offlineItems.filter((item: KnowledgeItem) => {
						if (filters?.typeId && item.typeId !== filters.typeId) return false;
						if (filters?.completed !== undefined && item.completed !== filters.completed) return false;
						return true;
					});

					update((state) => ({
						...state,
						items,
						isLoading: false
					}));

					return { success: true, items };
				}

				const response: any = await api.knowledge.listKnowledgeItems(filters);
				const items = response.items || [];

				await clearOfflineStore(OFFLINE_STORES.KNOWLEDGE);
				for (const item of items) {
					await offlineKnowledge.save(item);
				}

				update((state) => ({
					...state,
					items,
					isLoading: false
				}));

				return { success: true, items };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to load knowledge items';
				update((state) => ({
					...state,
					isLoading: false,
					error: errorMessage
				}));
				return { success: false, error: errorMessage };
			}
		},

		async createKnowledgeItem(data: {
			typeId: string;
			title: string;
			content: string;
			item_metadata?: any;
			completed?: boolean;
		}) {
			try {
				if (!isOnline()) {
					const now = new Date().toISOString();
					const offlineItem: KnowledgeItem = {
						id: crypto.randomUUID?.() || `offline-${Date.now()}`,
						userId: 'offline',
						typeId: data.typeId,
						title: data.title,
						content: data.content,
						item_metadata: data.item_metadata,
						completed: data.completed ?? false,
						createdAt: now,
						updatedAt: now
					};

					await offlineKnowledge.save(offlineItem);
					await queueOperation({
						type: 'create',
						entity: 'knowledge',
						data,
						endpoint: '/knowledge/items'
					});

					update((state) => ({
						...state,
						items: [offlineItem, ...state.items]
					}));

					return { success: true, item: offlineItem };
				}

				const newItem: any = await api.knowledge.createKnowledgeItem(data);
				await offlineKnowledge.save(newItem);

				update((state) => ({
					...state,
					items: [newItem, ...state.items]
				}));

				return { success: true, item: newItem };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to create knowledge item';
				return { success: false, error: errorMessage };
			}
		},

		async updateKnowledgeItem(itemId: string, updates: any) {
			try {
				if (!isOnline()) {
					const now = new Date().toISOString();
					let updatedItem: KnowledgeItem | null = null;

					update((state) => {
						const items = state.items.map((item): KnowledgeItem => {
							if (item.id !== itemId) return item;
							const updated: KnowledgeItem = {
								...item,
								...updates,
								updatedAt: now
							};
							updatedItem = updated;
							return updated;
						});

						return {
							...state,
							items
						};
					});

					if (updatedItem) {
						await offlineKnowledge.save(updatedItem);
					}

					await queueOperation({
						type: 'update',
						entity: 'knowledge',
						data: updates,
						endpoint: `/knowledge/items/${itemId}`
					});

					return { success: true, item: updatedItem };
				}

				const updatedItem: any = await api.knowledge.updateKnowledgeItem(itemId, updates);
				await offlineKnowledge.save(updatedItem);

				update((state) => ({
					...state,
					items: state.items.map((i) => (i.id === itemId ? updatedItem : i))
				}));

				return { success: true, item: updatedItem };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to update knowledge item';
				return { success: false, error: errorMessage };
			}
		},

		async toggleKnowledgeItem(itemId: string) {
			try {
				if (!isOnline()) {
					let updatedItem: KnowledgeItem | null = null;

					update((state) => {
						const items = state.items.map((item) => {
							if (item.id !== itemId) return item;
							updatedItem = {
								...item,
								completed: !item.completed,
								updatedAt: new Date().toISOString()
							};
							return updatedItem;
						});

						return {
							...state,
							items
						};
					});

					if (updatedItem) {
						await offlineKnowledge.save(updatedItem);
					}

					await queueOperation({
						type: 'create',
						entity: 'knowledge',
						data: {},
						endpoint: `/knowledge/items/${itemId}/toggle`
					});

					return { success: true, item: updatedItem };
				}

				const updatedItem: any = await api.knowledge.toggleKnowledgeItem(itemId);
				await offlineKnowledge.save(updatedItem);

				update((state) => ({
					...state,
					items: state.items.map((i) => (i.id === itemId ? updatedItem : i))
				}));

				return { success: true, item: updatedItem };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to toggle knowledge item';
				return { success: false, error: errorMessage };
			}
		},

		async deleteKnowledgeItem(itemId: string) {
			try {
				if (!isOnline()) {
					await offlineKnowledge.delete(itemId);
					await queueOperation({
						type: 'delete',
						entity: 'knowledge',
						data: {},
						endpoint: `/knowledge/items/${itemId}`
					});

					update((state) => ({
						...state,
						items: state.items.filter((i) => i.id !== itemId)
					}));

					return { success: true };
				}

				await api.knowledge.deleteKnowledgeItem(itemId);

				update((state) => ({
					...state,
					items: state.items.filter((i) => i.id !== itemId)
				}));

				return { success: true };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to delete knowledge item';
				return { success: false, error: errorMessage };
			}
		},

		async searchKnowledgeItems(query: string, typeId?: string) {
			update((state) => ({ ...state, isLoading: true }));

			try {
				if (!isOnline()) {
					const offlineItems = await offlineKnowledge.getAll();
					const q = query.toLowerCase();
					const items = offlineItems.filter((item: KnowledgeItem) => {
						if (typeId && item.typeId !== typeId) return false;
						return (
							item.title.toLowerCase().includes(q) ||
							(item.content || '').toLowerCase().includes(q)
						);
					});

					update((state) => ({
						...state,
						items,
						isLoading: false
					}));

					return { success: true, items };
				}

				const response: any = await api.knowledge.searchKnowledgeItems(query, typeId);
				const items = response.items || [];

				update((state) => ({
					...state,
					items,
					isLoading: false
				}));

				return { success: true, items };
			} catch (error: any) {
				const errorMessage = error.detail || 'Search failed';
				update((state) => ({
					...state,
					isLoading: false,
					error: errorMessage
				}));
				return { success: false, error: errorMessage };
			}
		},

		setSelectedTypeId(typeId: string | null) {
			update((state) => ({ ...state, selectedTypeId: typeId }));
		},

		clearError() {
			update((state) => ({ ...state, error: null }));
		}
	};
}

export const knowledgeStore = createKnowledgeStore();
