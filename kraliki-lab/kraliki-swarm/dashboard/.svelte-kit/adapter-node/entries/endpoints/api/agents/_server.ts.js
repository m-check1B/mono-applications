import { json } from "@sveltejs/kit";
import { g as getAgentStatus } from "../../../../chunks/data.js";
const GET = async () => {
  try {
    const agents = await getAgentStatus();
    return json({
      agents,
      totalActive: agents.filter((a) => a.status === "running").length,
      totalCompleted: agents.filter((a) => a.status === "completed").length,
      totalFailed: agents.filter((a) => a.status === "failed").length
    });
  } catch (e) {
    return json({
      agents: [],
      totalActive: 0,
      totalCompleted: 0,
      totalFailed: 0,
      error: "Failed to get agent status"
    });
  }
};
export {
  GET
};
