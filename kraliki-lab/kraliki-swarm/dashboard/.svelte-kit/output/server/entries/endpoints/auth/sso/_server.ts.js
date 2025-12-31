import { error, redirect } from "@sveltejs/kit";
import { i as isSsoDisabled, b as isAuthConfigured, c as createAuthorizationURL } from "../../../../chunks/auth.js";
const GET = async ({ cookies }) => {
  if (isSsoDisabled()) {
    throw error(404, "SSO is disabled.");
  }
  if (!isAuthConfigured()) {
    throw error(503, "SSO is not configured. Please contact administrator.");
  }
  const state = crypto.randomUUID();
  cookies.set("oauth_state", state, {
    path: "/",
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 10
    // 10 minutes
  });
  const authUrl = createAuthorizationURL(state);
  if (!authUrl) {
    throw error(500, "Failed to create authorization URL");
  }
  throw redirect(302, authUrl.toString());
};
export {
  GET
};
