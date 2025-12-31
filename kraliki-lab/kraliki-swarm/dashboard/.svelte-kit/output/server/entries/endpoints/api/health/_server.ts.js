import { json } from "@sveltejs/kit";
import { exec } from "child_process";
import { promisify } from "util";
const execAsync = promisify(exec);
async function checkPm2() {
  try {
    const { stdout } = await execAsync("pm2 jlist 2>/dev/null");
    const processes = JSON.parse(stdout);
    const online = processes.filter((p) => p.pm2_env?.status === "online").length;
    const total = processes.length;
    return {
      service: "pm2",
      status: online === total ? "healthy" : "unhealthy",
      message: `${online}/${total} processes online`
    };
  } catch {
    return { service: "pm2", status: "unknown", message: "pm2 not available" };
  }
}
async function checkRedis() {
  try {
    const { stdout } = await execAsync("docker exec kraliki-redis redis-cli ping 2>/dev/null || redis-cli ping 2>/dev/null");
    return {
      service: "redis",
      status: stdout.trim() === "PONG" ? "healthy" : "unhealthy"
    };
  } catch {
    return { service: "redis", status: "unknown" };
  }
}
const GET = async () => {
  const checks = await Promise.all([checkPm2(), checkRedis()]);
  const allHealthy = checks.every((c) => c.status === "healthy");
  return json({
    status: allHealthy ? "healthy" : "degraded",
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    checks
  });
};
export {
  GET
};
