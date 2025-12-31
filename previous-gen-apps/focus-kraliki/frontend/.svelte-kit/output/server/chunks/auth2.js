import { w as writable } from "./index.js";
import { a as api } from "./client.js";
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null
};
const TOKEN_COOKIE = "focus_token";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 30;
const getGoogleRedirectUri = () => {
  if (typeof window !== "undefined") {
    return `${window.location.origin}/auth/google/callback`;
  }
  return "";
};
const setTokenCookie = (token) => {
  if (typeof document === "undefined") {
    return;
  }
  if (token) {
    document.cookie = `${TOKEN_COOKIE}=${token}; Path=/; Max-Age=${COOKIE_MAX_AGE}; SameSite=Lax`;
  } else {
    document.cookie = `${TOKEN_COOKIE}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;
  }
};
function createAuthStore() {
  const { subscribe, set, update } = writable(initialState);
  return {
    subscribe,
    async login(email, password) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.auth.login({ email, password });
        const newState = {
          user: response.user,
          token: response.token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        };
        api.setToken(response.token);
        localStorage.setItem("token", response.token);
        setTokenCookie(response.token);
        set(newState);
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Login failed";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async register(email, password, full_name) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.auth.register({ email, password, name: full_name });
        const newState = {
          user: response.user,
          token: response.token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        };
        api.setToken(response.token);
        localStorage.setItem("token", response.token);
        setTokenCookie(response.token);
        set(newState);
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Registration failed";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async getGoogleAuthUrl(state) {
      try {
        const response = await api.google.getAuthUrl({
          redirect_uri: getGoogleRedirectUri(),
          state
        });
        return response;
      } catch (error) {
        throw error;
      }
    },
    async loginWithGoogle(code, redirectUri) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.google.login({ code, redirect_uri: redirectUri });
        const newState = {
          user: response.user,
          token: response.token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        };
        api.setToken(response.token);
        localStorage.setItem("token", response.token);
        setTokenCookie(response.token);
        set(newState);
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Google login failed";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async restoreSession(token) {
      update((state) => ({ ...state, isLoading: true }));
      try {
        api.setToken(token);
        const user = await api.auth.me();
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
        setTokenCookie(token);
        return { success: true };
      } catch (error) {
        localStorage.removeItem("token");
        api.setToken(null);
        setTokenCookie(null);
        set(initialState);
        return { success: false };
      }
    },
    async logout() {
      try {
        await api.auth.logout();
      } catch (error) {
      }
      localStorage.removeItem("token");
      api.setToken(null);
      setTokenCookie(null);
      set(initialState);
    },
    clearError() {
      update((state) => ({ ...state, error: null }));
    }
  };
}
const authStore = createAuthStore();
export {
  authStore as a
};
