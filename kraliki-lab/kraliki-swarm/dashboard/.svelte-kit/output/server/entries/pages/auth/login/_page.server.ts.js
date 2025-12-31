import { fail, redirect } from "@sveltejs/kit";
import { i as isSsoDisabled, e as isLocalAuthConfigured, b as isAuthConfigured, f as validateLocalCredentials, s as shouldUseSecureCookies, c as createAuthorizationURL } from "../../../../chunks/auth.js";
const load = () => {
  return {
    authConfigured: isAuthConfigured(),
    localAuthConfigured: isLocalAuthConfigured(),
    ssoDisabled: isSsoDisabled()
  };
};
const actions = {
  default: async ({ request, cookies, url }) => {
    const data = await request.formData();
    const email = data.get("email")?.toString() || "";
    const password = data.get("password")?.toString() || "";
    if (!email || !password) {
      return fail(400, { error: "Email and password required" });
    }
    const user = validateLocalCredentials(email, password);
    if (user) {
      const sessionData = btoa(JSON.stringify({
        sub: user.id,
        name: user.name,
        email: user.email,
        isLocal: true
      }));
      cookies.set("session", sessionData, {
        path: "/",
        httpOnly: true,
        secure: shouldUseSecureCookies(url, request),
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7
        // 1 week
      });
      throw redirect(302, "/");
    }
    if (isAuthConfigured()) {
      const state = crypto.randomUUID();
      cookies.set("oauth_state", state, {
        path: "/",
        httpOnly: true,
        secure: true,
        sameSite: "lax",
        maxAge: 60 * 10
      });
      const authUrl = createAuthorizationURL(state);
      if (authUrl) {
        throw redirect(302, authUrl.toString());
      }
    }
    return fail(401, { error: "Invalid credentials" });
  }
};
export {
  actions,
  load
};
