import { d as isLocalRequest, g as getLocalUser, a as verifyIdToken } from "../../chunks/auth.js";
import { redirect } from "@sveltejs/kit";
const load = async ({ request, cookies, url }) => {
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/auth/")) {
    return { user: null };
  }
  if (isLocalRequest(request)) {
    return { user: getLocalUser() };
  }
  const sessionToken = cookies.get("session");
  if (!sessionToken) {
    throw redirect(302, "/auth/login");
  }
  try {
    const sessionData = JSON.parse(atob(sessionToken));
    if (sessionData.isLocal) {
      return {
        user: {
          id: sessionData.sub || "local-user",
          name: sessionData.name || "Local User",
          email: sessionData.email,
          isLocal: true
        }
      };
    }
  } catch {
  }
  const userData = await verifyIdToken(sessionToken);
  if (!userData) {
    cookies.delete("session", { path: "/" });
    throw redirect(302, "/auth/login");
  }
  return {
    user: {
      id: userData.sub,
      name: userData.name || userData.preferred_username || "User",
      email: userData.email,
      isLocal: false
    }
  };
};
export {
  load
};
