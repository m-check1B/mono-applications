import { w as writable } from "./index.js";
import { a as api } from "./client.js";
const initialState = {
  workspaces: [],
  activeWorkspaceId: null,
  members: [],
  isLoading: false,
  membersLoading: false,
  error: null
};
function createWorkspacesStore() {
  const { subscribe, update, set } = writable(initialState);
  return {
    subscribe,
    async loadWorkspaces() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.workspaces.list();
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
      } catch (error) {
        update((state) => ({
          ...state,
          isLoading: false,
          error: error.detail || "Failed to load workspaces"
        }));
        return { success: false, error: error.detail };
      }
    },
    async loadMembers(workspaceId) {
      if (!workspaceId) return { success: false, error: "No workspace selected" };
      update((state) => ({ ...state, membersLoading: true }));
      try {
        const members = await api.workspaces.members(workspaceId);
        update((state) => ({
          ...state,
          members,
          membersLoading: false
        }));
        return { success: true, members };
      } catch (error) {
        update((state) => ({
          ...state,
          membersLoading: false,
          error: error.detail || "Failed to load members"
        }));
        return { success: false, error: error.detail };
      }
    },
    async switchWorkspace(workspaceId) {
      try {
        await api.workspaces.switch(workspaceId);
        const members = await api.workspaces.members(workspaceId);
        update((state) => ({
          ...state,
          activeWorkspaceId: workspaceId,
          members
        }));
        return { success: true };
      } catch (error) {
        update((state) => ({
          ...state,
          error: error.detail || "Failed to switch workspace"
        }));
        return { success: false, error: error.detail };
      }
    },
    async inviteMember(workspaceId, email, role) {
      try {
        const member = await api.workspaces.inviteMember(workspaceId, { email, role });
        update((state) => ({
          ...state,
          members: [...state.members, member]
        }));
        return { success: true, member };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to invite member" };
      }
    },
    async updateMemberRole(workspaceId, memberId, role) {
      try {
        const member = await api.workspaces.updateMember(workspaceId, memberId, { role });
        update((state) => ({
          ...state,
          members: state.members.map((m) => m.id === memberId ? member : m)
        }));
        return { success: true };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to update role" };
      }
    },
    async removeMember(workspaceId, memberId) {
      try {
        await api.workspaces.removeMember(workspaceId, memberId);
        update((state) => ({
          ...state,
          members: state.members.filter((m) => m.id !== memberId)
        }));
        return { success: true };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to remove member" };
      }
    }
  };
}
const workspacesStore = createWorkspacesStore();
export {
  workspacesStore as w
};
