import { d as derived, w as writable } from "./index.js";
const initialState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  loading: true
};
function createAuthStore() {
  const { subscribe, set, update } = writable(initialState);
  return {
    subscribe,
    setTokens: (accessToken2, refreshToken) => {
      update((state) => ({
        ...state,
        accessToken: accessToken2,
        refreshToken
      }));
    },
    setUser: (user) => {
      update((state) => ({
        ...state,
        user,
        loading: false
      }));
    },
    logout: () => {
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        loading: false
      });
    },
    setLoading: (loading) => {
      update((state) => ({ ...state, loading }));
    }
  };
}
const authStore = createAuthStore();
const isAuthenticated = derived(
  authStore,
  ($auth) => !!$auth.accessToken && !!$auth.user
);
const currentUser = derived(authStore, ($auth) => $auth.user);
derived(authStore, ($auth) => $auth.accessToken);
export {
  currentUser as c,
  isAuthenticated as i
};
