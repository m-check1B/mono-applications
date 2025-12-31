import { json } from "@sveltejs/kit";
import { exec } from "child_process";
import { promisify } from "util";
const execAsync = promisify(exec);
const ARENA_DIR = "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/arena";
async function getTraces(query) {
  try {
    let cmd = `python3 ${ARENA_DIR}/decision_trace.py query`;
    if (query.agent_id) cmd += ` -a "${query.agent_id}"`;
    if (query.decision_type) cmd += ` -t "${query.decision_type}"`;
    if (query.linear_issue) cmd += ` -i "${query.linear_issue}"`;
    cmd += ` -l ${query.limit || 50}`;
    const pythonCmd = `python3 -c "
import json
import sys
sys.path.insert(0, '${ARENA_DIR}')
from decision_trace import get_traces, get_stats
traces = get_traces(
    agent_id=${query.agent_id ? `'${query.agent_id}'` : "None"},
    decision_type=${query.decision_type ? `'${query.decision_type}'` : "None"},
    linear_issue=${query.linear_issue ? `'${query.linear_issue}'` : "None"},
    limit=${query.limit || 50}
)
print(json.dumps(traces))
"`;
    const { stdout } = await execAsync(pythonCmd);
    return JSON.parse(stdout.trim());
  } catch (error) {
    console.error("Error getting traces:", error);
    return [];
  }
}
async function getStats() {
  try {
    const pythonCmd = `python3 -c "
import json
import sys
sys.path.insert(0, '${ARENA_DIR}')
from decision_trace import get_stats
print(json.dumps(get_stats()))
"`;
    const { stdout } = await execAsync(pythonCmd);
    return JSON.parse(stdout.trim());
  } catch (error) {
    console.error("Error getting stats:", error);
    return {
      total_traces: 0,
      by_type: {},
      by_agent: {},
      by_outcome: {},
      by_genome: {}
    };
  }
}
const GET = async ({ url }) => {
  const agent_id = url.searchParams.get("agent_id") || void 0;
  const decision_type = url.searchParams.get("type") || void 0;
  const linear_issue = url.searchParams.get("issue") || void 0;
  const limit = parseInt(url.searchParams.get("limit") || "50");
  const statsOnly = url.searchParams.get("stats") === "true";
  if (statsOnly) {
    const stats2 = await getStats();
    return json(stats2);
  }
  const [traces, stats] = await Promise.all([
    getTraces({ agent_id, decision_type, linear_issue, limit }),
    getStats()
  ]);
  return json({
    traces,
    stats,
    timestamp: (/* @__PURE__ */ new Date()).toISOString()
  });
};
export {
  GET
};
