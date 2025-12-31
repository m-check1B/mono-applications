import { b as private_env } from "./shared-server.js";
import { createRemoteJWKSet, jwtVerify } from "jose";
import { l as logger } from "./logger.js";
const ZITADEL_DOMAIN = private_env.ZITADEL_DOMAIN || "identity.verduona.dev";
const CLIENT_ID = private_env.ZITADEL_CLIENT_ID || "";
const CLIENT_SECRET = private_env.ZITADEL_CLIENT_SECRET || "";
const JWKS = createRemoteJWKSet(new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/keys`));
function getRedirectUri() {
  if (private_env.SSO_REDIRECT_URI) {
    return private_env.SSO_REDIRECT_URI;
  }
  return private_env.ORIGIN ? `${private_env.ORIGIN}/auth/sso/callback` : "http://localhost:5173/auth/sso/callback";
}
function isAuthConfigured() {
  return !!(CLIENT_ID && CLIENT_SECRET);
}
function createAuthorizationURL(state) {
  if (!CLIENT_ID) return null;
  const url = new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/authorize`);
  url.searchParams.set("client_id", CLIENT_ID);
  url.searchParams.set("redirect_uri", getRedirectUri());
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", "openid profile email");
  url.searchParams.set("state", state);
  return url;
}
async function validateAuthorizationCode(code) {
  if (!CLIENT_ID || !CLIENT_SECRET) return null;
  try {
    const response = await fetch(`https://${ZITADEL_DOMAIN}/oauth/v2/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + btoa(`${CLIENT_ID}:${CLIENT_SECRET}`)
      },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        redirect_uri: getRedirectUri()
      })
    });
    if (!response.ok) {
      const errorText = await response.text();
      logger.error("Token exchange failed", new Error(errorText));
      return null;
    }
    const tokens = await response.json();
    return {
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      idToken: tokens.id_token
    };
  } catch (error) {
    logger.error("Failed to validate authorization code", error);
    return null;
  }
}
async function verifyIdToken(idToken) {
  try {
    const { payload } = await jwtVerify(idToken, JWKS, {
      issuer: `https://${ZITADEL_DOMAIN}`
    });
    if (!payload.sub) {
      logger.error("ID token missing sub claim");
      return null;
    }
    return payload;
  } catch (error) {
    logger.error("ID token verification failed", error);
    return null;
  }
}
export {
  verifyIdToken as a,
  createAuthorizationURL as c,
  isAuthConfigured as i,
  validateAuthorizationCode as v
};
