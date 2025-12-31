import { createRemoteJWKSet, jwtVerify } from "jose";
import crypto from "crypto";
import fs from "fs";
import path from "path";
let envLoaded = false;
function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) {
    return;
  }
  const lines = fs.readFileSync(filePath, "utf-8").split(/\r?\n/);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) {
      continue;
    }
    const [keyPart, ...valueParts] = line.split("=");
    const key = keyPart.trim();
    if (!key || (process.env[key] ?? "") !== "") {
      continue;
    }
    let value = valueParts.join("=").trim();
    if (value.startsWith('"') && value.endsWith('"') || value.startsWith("'") && value.endsWith("'")) {
      value = value.slice(1, -1);
    }
    process.env[key] = value;
  }
}
function loadEnvFiles() {
  if (envLoaded) {
    return;
  }
  envLoaded = true;
  const envPaths = [
    path.resolve(process.cwd(), ".env"),
    "/home/adminmatej/github/secrets/kraliki-dashboard.env",
    "/home/adminmatej/github/secrets/kraliki-swarm-dashboard.env"
  ];
  for (const envPath of envPaths) {
    loadEnvFile(envPath);
  }
}
loadEnvFiles();
const ZITADEL_DOMAIN = process.env.ZITADEL_DOMAIN || "identity.verduona.dev";
const CLIENT_ID = process.env.ZITADEL_CLIENT_ID || "";
const CLIENT_SECRET = process.env.ZITADEL_CLIENT_SECRET || "";
const SSO_DISABLED = process.env.SSO_DISABLED === "true";
const LOCAL_AUTH_EMAIL = process.env.LOCAL_AUTH_EMAIL || "";
const LOCAL_AUTH_PASSWORD = process.env.LOCAL_AUTH_PASSWORD || "";
const LOCAL_AUTH_NAME = process.env.LOCAL_AUTH_NAME || "Local User";
const DEFAULT_AUTH_STORE_PATH = "/home/adminmatej/github/secrets/kraliki-swarm-dashboard-users.json";
const LEGACY_AUTH_STORE_PATH = "/home/adminmatej/github/secrets/kraliki-dashboard-users.json";
function getLocalAuthStorePath() {
  const directPath = (process.env.LOCAL_AUTH_STORE_PATH || "").trim();
  if (directPath) {
    return directPath;
  }
  const env = (process.env.KRALIKI_ENV || "").trim().toUpperCase();
  if (env) {
    const envPath = (process.env[`LOCAL_AUTH_STORE_PATH_${env}`] || "").trim();
    if (envPath) {
      return envPath;
    }
  }
  if (fs.existsSync(DEFAULT_AUTH_STORE_PATH)) {
    return DEFAULT_AUTH_STORE_PATH;
  }
  return LEGACY_AUTH_STORE_PATH;
}
const LOCAL_AUTH_STORE_PATH = getLocalAuthStorePath();
function normalizeEmail(email) {
  return email.trim().toLowerCase();
}
function readLocalUsers() {
  try {
    if (!fs.existsSync(LOCAL_AUTH_STORE_PATH)) {
      return [];
    }
    const raw = fs.readFileSync(LOCAL_AUTH_STORE_PATH, "utf-8");
    if (!raw.trim()) {
      return [];
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error("Failed to read local auth store:", error);
    return [];
  }
}
function writeLocalUsers(users) {
  const dir = path.dirname(LOCAL_AUTH_STORE_PATH);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(LOCAL_AUTH_STORE_PATH, JSON.stringify(users, null, 2));
}
function hashPassword(password, salt) {
  return crypto.scryptSync(password, salt, 64).toString("hex");
}
function verifyPassword(password, record) {
  const candidate = Buffer.from(hashPassword(password, record.salt), "hex");
  const stored = Buffer.from(record.passwordHash, "hex");
  if (candidate.length !== stored.length) {
    return false;
  }
  return crypto.timingSafeEqual(candidate, stored);
}
function findLocalUser(email) {
  const normalized = normalizeEmail(email);
  const users = readLocalUsers();
  return users.find((user) => user.email === normalized) || null;
}
function createLocalUser(name, email, password) {
  const normalizedEmail = normalizeEmail(email);
  if (!normalizedEmail || !name.trim()) {
    return { error: "Name and email are required" };
  }
  if (password.length < 8) {
    return { error: "Password must be at least 8 characters long" };
  }
  if (findLocalUser(normalizedEmail)) {
    return { error: "Account already exists for this email" };
  }
  const salt = crypto.randomBytes(16).toString("hex");
  const passwordHash = hashPassword(password, salt);
  const userRecord = {
    id: normalizedEmail,
    name: name.trim(),
    email: normalizedEmail,
    passwordHash,
    salt,
    createdAt: (/* @__PURE__ */ new Date()).toISOString()
  };
  const users = readLocalUsers();
  users.push(userRecord);
  writeLocalUsers(users);
  return {
    user: {
      id: userRecord.id,
      name: userRecord.name,
      email: userRecord.email,
      isLocal: true
    }
  };
}
function validateLocalCredentials(email, password) {
  if (email === LOCAL_AUTH_EMAIL && password === LOCAL_AUTH_PASSWORD && LOCAL_AUTH_EMAIL) {
    return {
      id: email,
      name: LOCAL_AUTH_NAME,
      email,
      isLocal: true
    };
  }
  const localUser = findLocalUser(email);
  if (localUser && verifyPassword(password, localUser)) {
    return {
      id: localUser.id,
      name: localUser.name,
      email: localUser.email,
      isLocal: true
    };
  }
  return null;
}
function isLocalAuthConfigured() {
  if (LOCAL_AUTH_EMAIL && LOCAL_AUTH_PASSWORD) {
    return true;
  }
  return readLocalUsers().length > 0;
}
const JWKS = createRemoteJWKSet(new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/keys`));
function getRedirectUri() {
  return process.env.ORIGIN ? `${process.env.ORIGIN}/auth/callback` : "http://localhost:8099/auth/callback";
}
function isLocalRequest(request) {
  const forwardedFor = request.headers.get("x-forwarded-for");
  const realIp = request.headers.get("x-real-ip");
  const host = request.headers.get("host");
  if (forwardedFor) {
    const firstIp = forwardedFor.split(",")[0].trim();
    return firstIp === "127.0.0.1" || firstIp === "::1";
  }
  if (realIp) {
    return realIp === "127.0.0.1" || realIp === "::1";
  }
  if (host) {
    const hostWithoutPort = host.split(":")[0];
    return hostWithoutPort === "localhost" || hostWithoutPort === "127.0.0.1" || hostWithoutPort.startsWith("172.17.") || // Docker bridge
    hostWithoutPort.startsWith("10.204.");
  }
  const url = new URL(request.url);
  return url.hostname === "localhost" || url.hostname === "127.0.0.1";
}
function getLocalUser() {
  return {
    id: "local-agent",
    name: "Local Agent",
    isLocal: true
  };
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
      console.error("Token exchange failed:", await response.text());
      return null;
    }
    const tokens = await response.json();
    return {
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      idToken: tokens.id_token
    };
  } catch (error) {
    console.error("Failed to validate authorization code:", error);
    return null;
  }
}
function isAuthConfigured() {
  if (SSO_DISABLED) {
    return false;
  }
  return !!(CLIENT_ID && CLIENT_SECRET);
}
function shouldUseSecureCookies(url, request) {
  const forwardedProto = request?.headers.get("x-forwarded-proto")?.split(",")[0]?.trim().toLowerCase();
  if (forwardedProto) {
    return forwardedProto === "https";
  }
  return url.protocol === "https:";
}
function isSsoDisabled() {
  return SSO_DISABLED;
}
async function verifyIdToken(idToken) {
  try {
    const { payload } = await jwtVerify(idToken, JWKS, {
      issuer: `https://${ZITADEL_DOMAIN}`
      // Don't verify audience for ID tokens (varies by flow)
    });
    if (!payload.sub) {
      console.error("ID token missing sub claim");
      return null;
    }
    return payload;
  } catch (error) {
    console.error("ID token verification failed:", error);
    return null;
  }
}
export {
  verifyIdToken as a,
  isAuthConfigured as b,
  createAuthorizationURL as c,
  isLocalRequest as d,
  isLocalAuthConfigured as e,
  validateLocalCredentials as f,
  getLocalUser as g,
  createLocalUser as h,
  isSsoDisabled as i,
  shouldUseSecureCookies as s,
  validateAuthorizationCode as v
};
