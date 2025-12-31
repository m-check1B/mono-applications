import { json } from "@sveltejs/kit";
import { readFile } from "fs/promises";
import { existsSync } from "fs";
const KRALIKI_BASE = process.env.KRALIKI_DIR || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm";
const PATHS = {
  leaderboard: `${KRALIKI_BASE}/arena/data/leaderboard.json`,
  fitness: `${KRALIKI_BASE}/data/fitness/agents.json`
};
const LAB_NAMES = {
  CC: "Claude",
  OC: "OpenCode",
  CX: "Codex",
  GE: "Gemini",
  GR: "Grok"
};
function parseAgentId(agentId) {
  const parts = agentId.split("-");
  if (parts.length >= 2 && LAB_NAMES[parts[0]]) {
    return { lab: parts[0], labName: LAB_NAMES[parts[0]], role: parts[1] };
  }
  if (agentId.startsWith("darwin-") && parts.length >= 3) {
    const cli = parts[1];
    const cliToLab = { claude: "CC", gemini: "GE", codex: "CX", opencode: "OC" };
    const lab = cliToLab[cli] || null;
    return { lab, labName: lab ? LAB_NAMES[lab] : null, role: parts.slice(2).join("-") };
  }
  return { lab: null, labName: null, role: null };
}
async function readJsonFile(path, fallback) {
  try {
    if (!existsSync(path)) return fallback;
    const content = await readFile(path, "utf-8");
    return JSON.parse(content);
  } catch {
    return fallback;
  }
}
const GET = async () => {
  try {
    const [leaderboardData, fitnessData] = await Promise.all([
      readJsonFile(PATHS.leaderboard, null),
      readJsonFile(PATHS.fitness, null)
    ]);
    const combined = [];
    const seenIds = /* @__PURE__ */ new Set();
    if (leaderboardData?.rankings) {
      for (const entry of leaderboardData.rankings) {
        const parsed = parseAgentId(entry.id);
        const fitness = fitnessData?.agents?.[entry.id];
        const tasksCompleted = fitness?.tasks_completed ?? 0;
        const tasksAttempted = fitness?.tasks_attempted ?? 0;
        const successRate = tasksAttempted > 0 ? tasksCompleted / tasksAttempted * 100 : 0;
        combined.push({
          id: entry.id,
          lab: parsed.lab,
          labName: parsed.labName,
          role: parsed.role,
          points: entry.points ?? 0,
          rank: entry.rank ?? "Spawn",
          badge: entry.badge ?? "",
          achievements: entry.achievements ?? [],
          wins: entry.wins ?? 0,
          losses: entry.losses ?? 0,
          fitnessScore: fitness?.fitness_score ?? null,
          tasksCompleted,
          tasksAttempted,
          successRate: Math.round(successRate * 10) / 10,
          avgQualityScore: fitness?.avg_quality_score ?? 0,
          coordinationScore: fitness?.coordination_score ?? 0,
          learningScore: fitness?.learning_score ?? 0,
          totalTokens: fitness?.total_tokens ?? 0,
          lastActive: fitness?.last_report ?? null
        });
        seenIds.add(entry.id);
      }
    }
    if (fitnessData?.agents) {
      for (const [agentId, fitness] of Object.entries(fitnessData.agents)) {
        if (seenIds.has(agentId)) continue;
        const parsed = parseAgentId(agentId);
        const tasksCompleted = fitness.tasks_completed ?? 0;
        const tasksAttempted = fitness.tasks_attempted ?? 0;
        const successRate = tasksAttempted > 0 ? tasksCompleted / tasksAttempted * 100 : 0;
        combined.push({
          id: agentId,
          lab: parsed.lab,
          labName: parsed.labName,
          role: parsed.role,
          points: 0,
          rank: "Spawn",
          badge: "",
          achievements: [],
          wins: 0,
          losses: 0,
          fitnessScore: fitness.fitness_score ?? null,
          tasksCompleted,
          tasksAttempted,
          successRate: Math.round(successRate * 10) / 10,
          avgQualityScore: fitness.avg_quality_score ?? 0,
          coordinationScore: fitness.coordination_score ?? 0,
          learningScore: fitness.learning_score ?? 0,
          totalTokens: fitness.total_tokens ?? 0,
          lastActive: fitness.last_report ?? null
        });
      }
    }
    combined.sort((a, b) => {
      if (b.points !== a.points) return b.points - a.points;
      return (b.fitnessScore ?? 0) - (a.fitnessScore ?? 0);
    });
    const analytics = {
      totalAgents: combined.length,
      totalPoints: combined.reduce((sum, a) => sum + a.points, 0),
      avgFitness: combined.filter((a) => a.fitnessScore !== null).length > 0 ? Math.round(combined.filter((a) => a.fitnessScore !== null).reduce((sum, a) => sum + (a.fitnessScore ?? 0), 0) / combined.filter((a) => a.fitnessScore !== null).length * 10) / 10 : 0,
      byLab: {},
      byRole: {}
    };
    for (const agent of combined) {
      const lab = agent.lab || "unknown";
      const role = agent.role || "unknown";
      if (!analytics.byLab[lab]) {
        analytics.byLab[lab] = { agents: 0, points: 0, avgFitness: 0 };
      }
      analytics.byLab[lab].agents += 1;
      analytics.byLab[lab].points += agent.points;
      if (!analytics.byRole[role]) {
        analytics.byRole[role] = { agents: 0, points: 0 };
      }
      analytics.byRole[role].agents += 1;
      analytics.byRole[role].points += agent.points;
    }
    for (const lab of Object.keys(analytics.byLab)) {
      const labAgents = combined.filter((a) => (a.lab || "unknown") === lab && a.fitnessScore !== null);
      if (labAgents.length > 0) {
        analytics.byLab[lab].avgFitness = Math.round(
          labAgents.reduce((sum, a) => sum + (a.fitnessScore ?? 0), 0) / labAgents.length * 10
        ) / 10;
      }
    }
    return json({
      entries: combined,
      analytics,
      governor: leaderboardData?.governor ?? null,
      pendingChallenges: leaderboardData?.pending_challenges ?? [],
      recentEvents: leaderboardData?.recent_events?.slice(0, 20) ?? [],
      season: leaderboardData?.season ?? null,
      lastUpdated: leaderboardData?.last_updated ?? (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch (e) {
    console.error("Failed to fetch leaderboard:", e);
    return json({
      entries: [],
      analytics: { totalAgents: 0, totalPoints: 0, avgFitness: 0, byLab: {}, byRole: {} },
      governor: null,
      pendingChallenges: [],
      recentEvents: [],
      season: null,
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString()
    });
  }
};
export {
  GET
};
