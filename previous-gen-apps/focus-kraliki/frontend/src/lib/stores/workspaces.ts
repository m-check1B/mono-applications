import { writable } from 'svelte/store';
import { api } from '$lib/api/client';

export interface WorkspaceSummary {
	id: string;
	name: string;
	description?: string;
	color?: string;
	memberCount?: number;
}

export interface WorkspaceMember {
	id: string;
	userId: string;
	email?: string;
	name?: string;
	role: string;
}

interface WorkspaceState {
	workspaces: WorkspaceSummary[];
	activeWorkspaceId: string | null;
	members: WorkspaceMember[];
	isLoading: boolean;
	membersLoading: boolean;
	error: string | null;
}

const initialState: WorkspaceState = {
	workspaces: [],
	activeWorkspaceId: null,
	members: [],
	isLoading: false,
	membersLoading: false,
	error: null
};

function createWorkspacesStore() {
	const { subscribe, update, set } = writable<WorkspaceState>(initialState);

	return {
		subscribe,

		async loadWorkspaces() {
			update((state) => ({ ...state, isLoading: true, error: null }));
			try {
				const response: any = await api.workspaces.list();
				const activeWorkspaceId = response.activeWorkspaceId || null;

				set({
					workspaces: response.workspaces || [],
					activeWorkspaceId,
					members: [],
					isLoading: false,
					membersLoading: false,
					error: null
				});

				return { success: true, activeWorkspaceId };
			} catch (error: any) {
				update((state) => ({
					...state,
					isLoading: false,
					error: error.detail || 'Failed to load workspaces'
				}));
				return { success: false, error: error.detail };
			}
		},

		async loadMembers(workspaceId: string) {
			if (!workspaceId) return { success: false, error: 'No workspace selected' };

			update((state) => ({ ...state, membersLoading: true }));
			try {
				const members = (await api.workspaces.members(workspaceId)) as WorkspaceMember[];
				update((state) => ({
					...state,
					members,
					membersLoading: false
				}));
				return { success: true, members };
			} catch (error: any) {
				update((state) => ({
					...state,
					membersLoading: false,
					error: error.detail || 'Failed to load members'
				}));
				return { success: false, error: error.detail };
			}
		},

		async switchWorkspace(workspaceId: string) {
			try {
				await api.workspaces.switch(workspaceId);
				const members = (await api.workspaces.members(workspaceId)) as WorkspaceMember[];
				update((state) => ({
					...state,
					activeWorkspaceId: workspaceId,
					members
				}));
				return { success: true };
			} catch (error: any) {
				update((state) => ({
					...state,
					error: error.detail || 'Failed to switch workspace'
				}));
				return { success: false, error: error.detail };
			}
		},

		async inviteMember(workspaceId: string, email: string, role: string) {
			try {
				const member = (await api.workspaces.inviteMember(workspaceId, { email, role })) as WorkspaceMember;
				update((state) => ({
					...state,
					members: [...state.members, member]
				}));
				return { success: true, member };
			} catch (error: any) {
				return { success: false, error: error.detail || 'Failed to invite member' };
			}
		},

		async updateMemberRole(workspaceId: string, memberId: string, role: string) {
			try {
				const member = (await api.workspaces.updateMember(workspaceId, memberId, { role })) as WorkspaceMember;
				update((state) => ({
					...state,
					members: state.members.map((m) => (m.id === memberId ? member : m))
				}));
				return { success: true };
			} catch (error: any) {
				return { success: false, error: error.detail || 'Failed to update role' };
			}
		},

		async removeMember(workspaceId: string, memberId: string) {
			try {
				await api.workspaces.removeMember(workspaceId, memberId);
				update((state) => ({
					...state,
					members: state.members.filter((m) => m.id !== memberId)
				}));
				return { success: true };
			} catch (error: any) {
				return { success: false, error: error.detail || 'Failed to remove member' };
			}
		}
	};
}

export const workspacesStore = createWorkspacesStore();
