import { apiPost } from '$lib/utils/api';

export interface Credentials {
        email: string;
        password: string;
}

export interface RegisterPayload extends Credentials {
        full_name?: string;
}

export interface AuthResponse {
        access_token: string;
        refresh_token: string;
        expires_at?: number;
        user?: {
                id: string;
                email?: string;
                name?: string;
                role?: string;
        };
}

export function login(credentials: Credentials) {
        return apiPost<AuthResponse>('/api/v1/auth/login', credentials);
}

export function register(payload: RegisterPayload) {
        return apiPost<AuthResponse>('/api/v1/auth/register', payload);
}

export function logout() {
        return apiPost<{ success: boolean }>('/api/v1/auth/logout', {});
}
