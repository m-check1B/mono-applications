import { goto } from '$app/navigation';
import { browser } from '$app/environment';
import { api } from '$lib/api/client';

type User = {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'AGENT' | 'SUPERVISOR' | 'ADMIN';
  organizationId?: string;
};

const normalizeUser = (payload: any): User => ({
  id: payload.id,
  email: payload.email,
  firstName: payload.first_name ?? payload.firstName ?? '',
  lastName: payload.last_name ?? payload.lastName ?? '',
  role: (payload.role ?? 'AGENT').toUpperCase() as User['role'],
  organizationId: payload.organization_id ?? payload.organizationId ?? undefined,
});

class AuthStore {
  user = $state<User | null>(null);
  loading = $state(false);
  initialized = $state(false);

  async init() {
    if (!browser || this.initialized) return;

    this.loading = true;
    try {
      const response = await api.auth.me();
      this.user = normalizeUser(response);
    } catch (error) {
      console.warn('Auth check failed, using mock user', error);
      this.user = {
        id: 'demo-user',
        email: 'agent@demo.com',
        firstName: 'Demo',
        lastName: 'Agent',
        role: 'AGENT',
      };
    } finally {
      this.loading = false;
      this.initialized = true;
    }
  }

  async login(email: string, password: string) {
    this.loading = true;
    try {
      const result = await api.auth.login(email, password);
      this.user = normalizeUser(result.user);

      if (this.user.role === 'ADMIN') goto('/admin');
      else if (this.user.role === 'SUPERVISOR') goto('/supervisor');
      else goto('/operator');

      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message || 'Login failed' };
    } finally {
      this.loading = false;
    }
  }

  async logout() {
    try {
      await api.auth.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.user = null;
      goto('/login');
    }
  }

  get isAuthenticated() {
    return this.user !== null;
  }

  get isAgent() {
    return this.user?.role === 'AGENT';
  }

  get isSupervisor() {
    return this.user?.role === 'SUPERVISOR';
  }

  get isAdmin() {
    return this.user?.role === 'ADMIN';
  }
}

export const auth = new AuthStore();
