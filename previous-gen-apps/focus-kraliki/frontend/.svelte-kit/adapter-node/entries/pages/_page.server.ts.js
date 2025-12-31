import { redirect } from "@sveltejs/kit";
import { l as logger } from "../../chunks/logger.js";
const TOKEN_COOKIE = "focus_token";
const load = async ({ cookies, fetch }) => {
  const token = cookies.get(TOKEN_COOKIE);
  if (!token) {
    throw redirect(307, "/login");
  }
  try {
    const response = await fetch("/api/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    if (response.ok) {
      throw redirect(307, "/dashboard");
    }
  } catch (error) {
    logger.error("Failed to validate auth token on server load", error);
  }
  cookies.delete(TOKEN_COOKIE, { path: "/" });
  throw redirect(307, "/login");
};
export {
  load
};
