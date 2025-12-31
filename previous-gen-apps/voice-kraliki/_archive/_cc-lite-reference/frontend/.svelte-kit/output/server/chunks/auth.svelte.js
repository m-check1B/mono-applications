import "clsx";
import { t as trpc } from "./client.js";
import { g as goto } from "./client2.js";
class AuthStore {
  user = null;
  loading = false;
  initialized = false;
  async init() {
    return;
  }
  async login(email, password) {
    this.loading = true;
    try {
      const result = await trpc.auth.login.mutate({ email, password });
      this.user = result.user;
      if (this.user.role === "ADMIN") {
        goto("/admin");
      } else if (this.user.role === "SUPERVISOR") {
        goto("/supervisor");
      } else {
        goto("/operator");
      }
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message || "Login failed" };
    } finally {
      this.loading = false;
    }
  }
  async logout() {
    try {
      await trpc.auth.logout.mutate();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      this.user = null;
      goto();
    }
  }
  get isAuthenticated() {
    return this.user !== null;
  }
  get isAgent() {
    return this.user?.role === "AGENT";
  }
  get isSupervisor() {
    return this.user?.role === "SUPERVISOR";
  }
  get isAdmin() {
    return this.user?.role === "ADMIN";
  }
}
const auth = new AuthStore();
export {
  auth as a
};
