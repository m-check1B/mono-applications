import { error, redirect } from "@sveltejs/kit";
import { v as validateAuthorizationCode, a as verifyIdToken } from "../../../../../chunks/auth.js";
const GET = async ({ url, cookies }) => {
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const storedState = cookies.get("oauth_state");
  cookies.delete("oauth_state", { path: "/" });
  if (!state || state !== storedState) {
    throw error(400, "Invalid state parameter");
  }
  if (!code) {
    throw error(400, "Missing authorization code");
  }
  const tokens = await validateAuthorizationCode(code);
  if (!tokens) {
    throw error(500, "Failed to validate authorization code");
  }
  const userData = await verifyIdToken(tokens.idToken);
  if (!userData) {
    throw error(500, "Failed to verify ID token");
  }
  cookies.set("sso_session", btoa(JSON.stringify({
    sub: userData.sub,
    name: userData.name || userData.preferred_username,
    email: userData.email
  })), {
    path: "/",
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7
    // 1 week
  });
  throw redirect(302, "/dashboard");
};
export {
  GET
};
