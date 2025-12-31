import { exec } from "child_process";
import { promisify } from "util";
import { readdir, stat, readFile, open } from "fs/promises";
import { existsSync } from "fs";
const execAsync = promisify(exec);
const KRALIKI_BASE = process.env.KRALIKI_DIR || process.env.KRALIKI_DATA_PATH || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm";
const GITHUB_BASE = process.env.GITHUB_PATH || "/home/adminmatej/github";
const AGENT_LOGS_DIR = `${KRALIKI_BASE}/logs/agents`;
const PATHS = {
  kralikiStats: `${KRALIKI_BASE}/logs/daily/latest.json`,
  linear: `${KRALIKI_BASE}/data/linear.json`,
  pendingLinear: `${KRALIKI_BASE}/data/pending_linear_issues.json`,
  leaderboard: `${KRALIKI_BASE}/arena/data/leaderboard.json`,
  socialFeed: `${KRALIKI_BASE}/arena/data/social_feed.json`,
  blackboard: `${KRALIKI_BASE}/arena/data/board.json`,
  tasks: `${KRALIKI_BASE}/tasks/queue.json`,
  recall: `http://127.0.0.1:3020/api/stats`,
  circuitBreakers: `${KRALIKI_BASE}/control/circuit-breakers.json`,
  fitness: `${KRALIKI_BASE}/data/fitness/agents.json`
};
async function readJsonFile(path, fallback) {
  try {
    if (!existsSync(path)) return fallback;
    const content = await readFile(path, "utf-8");
    return JSON.parse(content);
  } catch {
    return fallback;
  }
}
async function getFitnessData() {
  return await readJsonFile(PATHS.fitness, null);
}
async function getDecisionTraceStats() {
  const ARENA_DIR = `${KRALIKI_BASE}/arena`;
  const TRACES_FILE = `${ARENA_DIR}/data/decision_traces.json`;
  try {
    const data = await readJsonFile(TRACES_FILE, null);
    if (!data || !data.traces) return null;
    const traces = data.traces;
    const today = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
    const stats = {
      total_traces: traces.length,
      traces_today: 0,
      by_type: {},
      by_outcome: {},
      recent_traces: []
    };
    for (const trace of traces) {
      if (trace.timestamp?.startsWith(today)) {
        stats.traces_today++;
      }
      const dtype = trace.decision_type || "unknown";
      stats.by_type[dtype] = (stats.by_type[dtype] || 0) + 1;
      const outcome = trace.outcome || "pending";
      stats.by_outcome[outcome] = (stats.by_outcome[outcome] || 0) + 1;
    }
    const sortedTraces = [...traces].sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || "")).slice(0, 5);
    stats.recent_traces = sortedTraces.map((t) => ({
      trace_id: t.trace_id,
      timestamp: t.timestamp,
      agent_id: t.agent_id,
      decision_type: t.decision_type,
      decision: t.decision,
      reasoning: t.reasoning,
      outcome: t.outcome,
      linear_issue: t.linear_issue
    }));
    return stats;
  } catch {
    return null;
  }
}
async function getGenomeStats() {
  const GENOMES_DIR = `${KRALIKI_BASE}/genomes`;
  const TRACES_FILE = `${KRALIKI_BASE}/arena/data/decision_traces.json`;
  try {
    const genomeFiles = await readdir(GENOMES_DIR).catch(() => []);
    const genomeNames = genomeFiles.filter((f) => f.endsWith(".md") && !f.startsWith("_")).map((f) => f.replace(".md", ""));
    const tracesData = await readJsonFile(TRACES_FILE, null);
    const traces = tracesData?.traces || [];
    const today = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
    const leaderboard = await readJsonFile(PATHS.leaderboard, null);
    const rankings = leaderboard?.rankings || [];
    const genomeData = {};
    for (const name of genomeNames) {
      const parts = name.split("_");
      const cli = parts[0] || "unknown";
      genomeData[name] = {
        name,
        cli,
        spawns_today: 0,
        points_earned: 0,
        decisions: 0,
        last_active: null
      };
    }
    for (const trace of traces) {
      const genome = trace.genome;
      if (!genome) continue;
      if (!genomeData[genome]) {
        const parts = genome.split("_");
        genomeData[genome] = {
          name: genome,
          cli: parts[0] || "unknown",
          spawns_today: 0,
          points_earned: 0,
          decisions: 0,
          last_active: null
        };
      }
      genomeData[genome].decisions++;
      if (trace.decision_type === "spawn" && trace.timestamp?.startsWith(today)) {
        genomeData[genome].spawns_today++;
      }
      const timestamp = trace.timestamp;
      if (timestamp && (!genomeData[genome].last_active || timestamp > genomeData[genome].last_active)) {
        genomeData[genome].last_active = timestamp;
      }
    }
    for (const agent of rankings) {
      const agentId = agent.id || "";
      const parts = agentId.split("-");
      if (parts.length >= 2) {
        const lab = parts[0];
        const role = parts[1];
        const cliMap = { CC: "claude", OC: "opencode", CX: "codex", GE: "gemini", GR: "grok" };
        const cli = cliMap[lab] || lab.toLowerCase();
        const genomeName = `${cli}_${role}`;
        if (genomeData[genomeName]) {
          genomeData[genomeName].points_earned += agent.points || 0;
        }
      }
    }
    const allGenomes = Object.values(genomeData);
    const activeToday = allGenomes.filter((g) => g.spawns_today > 0 || g.last_active?.startsWith(today));
    const topPerformers = [...allGenomes].sort((a, b) => b.points_earned + b.spawns_today * 10 - (a.points_earned + a.spawns_today * 10)).slice(0, 10);
    const byCli = {};
    for (const genome of allGenomes) {
      if (!byCli[genome.cli]) {
        byCli[genome.cli] = { genomes: 0, spawns: 0, points: 0 };
      }
      byCli[genome.cli].genomes++;
      byCli[genome.cli].spawns += genome.spawns_today;
      byCli[genome.cli].points += genome.points_earned;
    }
    return {
      total_genomes: allGenomes.length,
      active_today: activeToday.length,
      top_performers: topPerformers,
      by_cli: byCli
    };
  } catch {
    return null;
  }
}
async function getLinearData() {
  return await readJsonFile(PATHS.linear, null);
}
async function getPendingLinearIssues() {
  const data = await readJsonFile(PATHS.pendingLinear, null);
  if (!data || !data.issues || data.issues.length === 0) return null;
  return data;
}
async function getRecallData() {
  try {
    const res = await fetch(PATHS.recall, { signal: AbortSignal.timeout(2e3) });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}
async function getCircuitBreakers() {
  return await readJsonFile(PATHS.circuitBreakers, null);
}
async function getMemoryStats() {
  const MEMORY_DIR = `${KRALIKI_BASE}/arena/data/memories`;
  try {
    if (!existsSync(MEMORY_DIR)) return null;
    const files = await readdir(MEMORY_DIR);
    const jsonlFiles = files.filter((f) => f.endsWith(".jsonl"));
    if (jsonlFiles.length === 0) return null;
    let totalMemories = 0;
    let oldestMemory = null;
    let newestMemory = null;
    let totalSizeKb = 0;
    let ephemeralCount = 0;
    const ephemeralPattern = /^[A-Z]{2}-[a-z_]+-\d{2}:\d{2}\.\d{2}\.\d{2}\.[A-Z]{2}$/;
    const agentData = [];
    for (const file of jsonlFiles) {
      const filePath = `${MEMORY_DIR}/${file}`;
      const agentName = file.replace(".jsonl", "");
      const isEphemeral = ephemeralPattern.test(agentName);
      if (isEphemeral) ephemeralCount++;
      try {
        const fileStat = await stat(filePath);
        const sizeKb = fileStat.size / 1024;
        totalSizeKb += sizeKb;
        const content = await readFile(filePath, "utf-8");
        const lines = content.trim().split("\n").filter((l) => l);
        const count = lines.length;
        totalMemories += count;
        let firstTime = null;
        let lastTime = null;
        for (const line of lines) {
          try {
            const mem = JSON.parse(line);
            const time = mem?.metadata?.time;
            if (time) {
              if (!firstTime) firstTime = time;
              lastTime = time;
            }
          } catch {
          }
        }
        if (firstTime) {
          if (!oldestMemory || firstTime < oldestMemory) {
            oldestMemory = firstTime;
          }
        }
        if (lastTime) {
          if (!newestMemory || lastTime > newestMemory) {
            newestMemory = lastTime;
          }
        }
        agentData.push({
          agent: agentName,
          count,
          size_kb: Math.round(sizeKb * 10) / 10,
          last_active: lastTime?.slice(0, 10) || "?",
          ephemeral: isEphemeral
        });
      } catch {
      }
    }
    agentData.sort((a, b) => b.count - a.count);
    const topAgents = agentData.slice(0, 10);
    let mgrepAvailable = false;
    try {
      const res = await fetch(`http://localhost:8001/v1/stores/kraliki_memories`, {
        signal: AbortSignal.timeout(1e3)
      });
      mgrepAvailable = res.ok;
    } catch {
    }
    return {
      total_memories: totalMemories,
      total_agents: jsonlFiles.length,
      ephemeral_files: ephemeralCount,
      oldest_memory: oldestMemory,
      newest_memory: newestMemory,
      total_size_kb: Math.round(totalSizeKb * 10) / 10,
      top_agents: topAgents,
      mgrep_available: mgrepAvailable
    };
  } catch {
    return null;
  }
}
async function getActivityHeatMap() {
  try {
    const { stdout } = await execAsync(`
			find ${GITHUB_BASE} -type f -mmin -120 				-not -path '*/.git/*' 				-not -path '*/node_modules/*' 				-not -path '*/.venv/*' 				-not -path '*/__pycache__/*' 				-not -path '*/.pm2/*' 				-not -path '*/logs/*' 				-not -path '*/progress/*' 				-not -path '*/mgrep-selfhosted/data/*' 				-not -name '*.log' 				2>/dev/null | 			sed 's|${GITHUB_BASE}/||' | 			awk -F'/' '{if(NF>=2) print $1"/"$2; else print $1}' | 			sort | uniq -c | sort -rn | head -12
		`);
    return stdout.split("\n").filter((line) => line.trim()).map((line) => {
      const match = line.trim().match(/^(\d+)\s+(.+)$/);
      if (match) {
        return { count: parseInt(match[1]), folder: match[2] };
      }
      return null;
    }).filter((item) => item !== null);
  } catch {
    return [];
  }
}
async function getRecentFiles() {
  try {
    const { stdout } = await execAsync(`
			find ${GITHUB_BASE} -type f -mmin -120 				-not -path '*/.git/*' 				-not -path '*/node_modules/*' 				-not -path '*/.venv/*' 				-not -path '*/__pycache__/*' 				-not -path '*/.pm2/*' 				-not -path '*/logs/*' 				-not -name '*.log' 				-printf '%T+ %p
' 2>/dev/null | 			sort -r | head -15 | 			sed 's|${GITHUB_BASE}/||'
		`);
    return stdout.split("\n").filter((line) => line.trim()).map((line) => {
      const parts = line.split(" ");
      const time = parts[0]?.split(".")[0]?.replace("T", " ") || "";
      const path = parts.slice(1).join(" ");
      return { time: time.slice(11, 16), path };
    });
  } catch {
    return [];
  }
}
async function getTaskQueue() {
  const data = await readJsonFile(PATHS.tasks, null);
  if (!data) return null;
  const stats = {
    total: data.tasks.length,
    open: data.tasks.filter((t) => t.status === "open").length,
    claimed: data.tasks.filter((t) => t.status === "claimed").length,
    completed: data.tasks.filter((t) => t.status === "completed").length,
    blocked: data.tasks.filter((t) => t.status === "blocked").length,
    by_type: {}
  };
  for (const task of data.tasks) {
    stats.by_type[task.type] = (stats.by_type[task.type] || 0) + 1;
  }
  return { ...data, stats };
}
async function getBlackboard() {
  const data = await readJsonFile(PATHS.blackboard, null);
  if (!data) return null;
  const messages = [...data.messages].sort((a, b) => b.time.localeCompare(a.time)).slice(0, 50);
  const stats = {
    total: data.messages.length,
    by_topic: {},
    by_agent: {}
  };
  for (const msg of data.messages) {
    stats.by_topic[msg.topic] = (stats.by_topic[msg.topic] || 0) + 1;
    stats.by_agent[msg.agent] = (stats.by_agent[msg.agent] || 0) + 1;
  }
  return { messages, stats };
}
async function getFullStatus() {
  const results = await Promise.allSettled([
    getKralikiStats(),
    getActivityHeatMap(),
    getRecentFiles(),
    getLinearData(),
    getLeaderboard(),
    getSocialFeed(),
    getTaskQueue(),
    getBlackboard(),
    getAgentAnalytics(),
    getAgentStatus(),
    getRecallData(),
    getCircuitBreakers(),
    getCrashAnalytics(),
    getFitnessData(),
    getMemoryStats(),
    getDecisionTraceStats(),
    getGenomeStats(),
    getOrchestratorsState(),
    getCostAnalytics(),
    getPendingLinearIssues()
  ]);
  const [kraliki, heatMap, recentFiles, linear, leaderboard, social, tasks, blackboard, analytics, agentStatus, recall, circuitBreakers, crashAnalytics, fitness, memoryStats, decisionTraces, genomeStats, orchestrators, costAnalytics, pendingLinear] = results.map((r) => r.status === "fulfilled" ? r.value : null);
  return {
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    kraliki,
    heatMap: heatMap || [],
    recentFiles: recentFiles || [],
    linear,
    pendingLinear,
    leaderboard,
    social: social || [],
    tasks,
    blackboard,
    analytics,
    agentStatus: agentStatus || [],
    recall,
    circuitBreakers,
    crashAnalytics,
    fitness,
    memoryStats,
    decisionTraces,
    genomeStats,
    orchestrators,
    costAnalytics
  };
}
async function getKralikiStats() {
  return await readJsonFile(PATHS.kralikiStats, null);
}
async function getLeaderboard() {
  return await readJsonFile(PATHS.leaderboard, null);
}
const LAB_NAMES = {
  CC: "Claude Code",
  OC: "OpenCode",
  CX: "Codex",
  GE: "Gemini",
  GR: "Grok"
};
function parseAgentId(agentId) {
  const parts = agentId.split("-");
  if (parts.length >= 3 && LAB_NAMES[parts[0]]) {
    return { lab: parts[0], role: parts[1] };
  }
  if (agentId.startsWith("darwin-") && parts.length >= 3) {
    const cli = parts[1];
    const cliToLab = { claude: "CC", gemini: "GE", codex: "CX", opencode: "OC" };
    return { lab: cliToLab[cli] || null, role: parts.slice(2).join("-") };
  }
  return { lab: null, role: null };
}
async function getAgentAnalytics() {
  const leaderboard = await getLeaderboard();
  if (!leaderboard) return null;
  const analytics = {
    by_lab: {},
    by_role: {},
    total_agents: leaderboard.rankings.length,
    total_points: leaderboard.rankings.reduce((sum, a) => sum + (a.points || 0), 0)
  };
  for (const agent of leaderboard.rankings) {
    const parsed = parseAgentId(agent.id);
    const lab = parsed.lab || "unknown";
    const role = parsed.role || "unknown";
    const points = agent.points || 0;
    if (!analytics.by_lab[lab]) {
      analytics.by_lab[lab] = { agents: 0, points: 0, lab_name: LAB_NAMES[lab] || null };
    }
    analytics.by_lab[lab].agents += 1;
    analytics.by_lab[lab].points += points;
    if (!analytics.by_role[role]) {
      analytics.by_role[role] = { agents: 0, points: 0 };
    }
    analytics.by_role[role].agents += 1;
    analytics.by_role[role].points += points;
  }
  return analytics;
}
async function getSocialFeed() {
  const [socialData, blackboardData] = await Promise.all([
    readJsonFile(PATHS.socialFeed, null),
    readJsonFile(PATHS.blackboard, null)
  ]);
  const allPosts = [];
  if (socialData?.posts) {
    allPosts.push(...socialData.posts);
  }
  if (blackboardData?.messages) {
    for (const msg of blackboardData.messages) {
      allPosts.push({
        id: `bb-${msg.id}`,
        timestamp: msg.time,
        time: msg.time,
        agent: msg.agent,
        author: msg.agent,
        channel: msg.topic,
        content: msg.message,
        message: msg.message,
        type: "blackboard"
      });
    }
  }
  allPosts.sort((a, b) => {
    const timeA = a.timestamp || a.time || "";
    const timeB = b.timestamp || b.time || "";
    return timeB.localeCompare(timeA);
  });
  return allPosts.slice(0, 30);
}
function formatDateTime(timestamp) {
  if (!timestamp) return "--";
  const year = timestamp.getFullYear();
  const month = String(timestamp.getMonth() + 1).padStart(2, "0");
  const day = String(timestamp.getDate()).padStart(2, "0");
  const hour = String(timestamp.getHours()).padStart(2, "0");
  const minute = String(timestamp.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day} ${hour}:${minute}`;
}
function formatDuration(ms) {
  if (ms === null || Number.isNaN(ms) || ms < 0) return "--";
  const totalMinutes = Math.floor(ms / 6e4);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  if (minutes > 0) {
    return `${minutes}m`;
  }
  const seconds = Math.floor(ms / 1e3);
  return `${seconds}s`;
}
const LAB_PREFIXES = {
  CC: "claude",
  OC: "opencode",
  CX: "codex",
  GE: "gemini",
  GR: "grok"
};
function detectCliFromAgentId(agentId, command) {
  if (agentId) {
    const prefix = agentId.split("-")[0];
    if (LAB_PREFIXES[prefix]) return LAB_PREFIXES[prefix];
  }
  if (command) {
    if (command.includes("codex")) return "codex";
    if (command.includes("claude")) return "claude";
    if (command.includes("gemini")) return "gemini";
    if (command.includes("opencode")) return "opencode";
  }
  return null;
}
function parseAgentLogName(fileName, fileMtime) {
  const baseName = fileName.replace(/\.log$/, "");
  if (baseName.startsWith("CC-") || baseName.startsWith("OC-") || baseName.startsWith("CX-") || baseName.startsWith("GE-") || baseName.startsWith("GR-")) {
    const [lab, role, timePart] = baseName.split("-", 3);
    const cli = LAB_PREFIXES[lab] || null;
    const genome = role || null;
    let startTime = null;
    if (timePart) {
      const [time, day, month] = timePart.split(".");
      if (time && day && month) {
        const [hour, minute] = time.split(":");
        const year = fileMtime.getFullYear();
        startTime = new Date(year, Number(month) - 1, Number(day), Number(hour), Number(minute));
      }
    }
    return { id: baseName, genome, cli, startTime };
  }
  const legacyMatch = baseName.match(/^(?<genome>[a-z0-9_]+)_(?<date>\d{8})_(?<time>\d{6})$/);
  if (legacyMatch?.groups) {
    const genome = legacyMatch.groups.genome;
    const datePart = legacyMatch.groups.date;
    const timePart = legacyMatch.groups.time;
    const year = Number(datePart.slice(0, 4));
    const month = Number(datePart.slice(4, 6));
    const day = Number(datePart.slice(6, 8));
    const hour = Number(timePart.slice(0, 2));
    const minute = Number(timePart.slice(2, 4));
    const startTime = new Date(year, month - 1, day, hour, minute);
    const cli = genome.split("_")[0] || null;
    return { id: baseName, genome, cli, startTime };
  }
  return { id: baseName, genome: null, cli: null, startTime: null };
}
async function readTail(path, maxBytes = 65536) {
  try {
    const handle = await open(path, "r");
    const fileStats = await handle.stat();
    const size = fileStats.size;
    if (size <= 0) {
      await handle.close();
      return "";
    }
    const readSize = Math.min(size, maxBytes);
    const buffer = Buffer.alloc(readSize);
    await handle.read(buffer, 0, readSize, size - readSize);
    await handle.close();
    return buffer.toString("utf-8");
  } catch {
    return "";
  }
}
function parseCompletionStatus(tail) {
  const match = tail.match(/status:\s*([A-Za-z_-]+)/);
  if (!match) return "completed";
  const status = match[1].toLowerCase();
  if (status === "failed" || status === "error" || status === "timeout") {
    return "failed";
  }
  return "completed";
}
async function getRunningAgentProcesses(pointsByAgent) {
  const entries = [];
  const CONTROL_DIR = `${KRALIKI_BASE}/control`;
  try {
    const controlFiles = await readdir(CONTROL_DIR).catch(() => []);
    const stateFiles = controlFiles.filter((f) => f.startsWith("orchestrator_state_") && f.endsWith(".json"));
    for (const stateFile of stateFiles) {
      try {
        const content = await readFile(`${CONTROL_DIR}/${stateFile}`, "utf-8");
        const state = JSON.parse(content);
        const pid = state.pid;
        const agentId = state.agent_id;
        const cli = state.cli;
        if (!pid || !agentId) continue;
        try {
          await execAsync(`ps -p ${pid} -o pid=`);
        } catch {
          continue;
        }
        let startTime = "--";
        let duration = "--";
        try {
          const { stdout: startStdout } = await execAsync(`ps -p ${pid} -o lstart=`);
          startTime = formatDateTime(new Date(startStdout.trim()));
          const { stdout: elapsedStdout } = await execAsync(`ps -p ${pid} -o etimes=`);
          const elapsedSeconds = Number(elapsedStdout.trim());
          const durationMs = Number.isNaN(elapsedSeconds) ? null : elapsedSeconds * 1e3;
          duration = formatDuration(durationMs);
        } catch {
          if (state.spawned_at) {
            startTime = formatDateTime(new Date(state.spawned_at));
            const durationMs = Date.now() - new Date(state.spawned_at).getTime();
            duration = formatDuration(durationMs);
          }
        }
        const parts = agentId.split("-");
        const genome = parts.length >= 2 ? `${cli}_${parts[1]}` : null;
        entries.push({
          id: agentId,
          genome,
          cli,
          status: "running",
          pid,
          startTime,
          duration,
          points: pointsByAgent.get(agentId) ?? null
        });
      } catch {
        continue;
      }
    }
    const logFiles = await readdir(AGENT_LOGS_DIR).catch(() => []);
    const now = Date.now();
    const FIVE_MINUTES = 5 * 60 * 1e3;
    for (const logFile of logFiles) {
      if (!logFile.endsWith(".log")) continue;
      const logPath = `${AGENT_LOGS_DIR}/${logFile}`;
      const logStat = await stat(logPath).catch(() => null);
      if (!logStat) continue;
      if (now - logStat.mtime.getTime() < FIVE_MINUTES) {
        const { id, genome, cli, startTime: parsedStart } = parseAgentLogName(logFile, logStat.mtime);
        if (entries.some((e) => e.id === id)) continue;
        const durationMs = parsedStart ? now - parsedStart.getTime() : null;
        entries.push({
          id,
          genome,
          cli,
          status: "running",
          pid: null,
          startTime: formatDateTime(parsedStart),
          duration: formatDuration(durationMs),
          points: pointsByAgent.get(id) ?? null
        });
      }
    }
  } catch {
    return entries;
  }
  return entries;
}
async function getCrashAnalytics() {
  if (!existsSync(AGENT_LOGS_DIR)) return null;
  const analytics = {
    summary: {
      total_spawns_today: 0,
      total_crashes_today: 0,
      crash_rate_percent: 0,
      zero_byte_crashes: 0
    },
    by_cli: {},
    recent_crashes: [],
    error_patterns: {}
  };
  try {
    const logEntries = await readdir(AGENT_LOGS_DIR, { withFileTypes: true });
    const logFiles = logEntries.filter((entry) => entry.isFile() && entry.name.endsWith(".log"));
    const today = /* @__PURE__ */ new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
    const fileStats = await Promise.all(
      logFiles.map(async (entry) => {
        const filePath = `${AGENT_LOGS_DIR}/${entry.name}`;
        const stats = await stat(filePath);
        return { entry, filePath, stats };
      })
    );
    fileStats.sort((a, b) => b.stats.mtime.getTime() - a.stats.mtime.getTime());
    for (const fileInfo of fileStats) {
      const { entry, filePath, stats: fileStat } = fileInfo;
      const { id, genome, cli, startTime } = parseAgentLogName(entry.name, fileStat.mtime);
      const fileDate = fileStat.mtime.toISOString().slice(0, 10);
      const isToday = fileDate === todayStr;
      const cliKey = cli || "unknown";
      if (!analytics.by_cli[cliKey]) {
        analytics.by_cli[cliKey] = { spawns: 0, crashes: 0, zero_byte: 0, crash_rate: 0 };
      }
      if (isToday) {
        analytics.summary.total_spawns_today++;
        analytics.by_cli[cliKey].spawns++;
      }
      const isZeroByte = fileStat.size === 0;
      let crashType = null;
      let errorSnippet;
      if (isZeroByte) {
        crashType = "zero_byte";
        if (isToday) {
          analytics.summary.zero_byte_crashes++;
          analytics.by_cli[cliKey].zero_byte++;
        }
      } else {
        const tail = await readTail(filePath, 8192);
        if (tail) {
          const errorPatterns = [
            { pattern: /NotFoundError/i, key: "NotFoundError" },
            { pattern: /RATE_LIMIT/i, key: "RateLimit" },
            { pattern: /timeout/i, key: "Timeout" },
            { pattern: /connection refused/i, key: "ConnectionRefused" },
            { pattern: /authentication failed/i, key: "AuthFailed" },
            { pattern: /Error:\s*(.{0,50})/i, key: "GenericError" },
            { pattern: /status:\s*failed/i, key: "StatusFailed" },
            { pattern: /exit code:\s*[1-9]/i, key: "NonZeroExit" }
          ];
          for (const { pattern, key } of errorPatterns) {
            const match = tail.match(pattern);
            if (match) {
              crashType = key === "Timeout" ? "timeout" : "error";
              analytics.error_patterns[key] = (analytics.error_patterns[key] || 0) + 1;
              errorSnippet = match[0].slice(0, 80);
              break;
            }
          }
        }
      }
      if (crashType && isToday) {
        analytics.summary.total_crashes_today++;
        analytics.by_cli[cliKey].crashes++;
        if (analytics.recent_crashes.length < 20) {
          analytics.recent_crashes.push({
            id,
            cli,
            genome,
            time: formatDateTime(fileStat.mtime),
            type: crashType,
            error_snippet: errorSnippet
          });
        }
      }
    }
    if (analytics.summary.total_spawns_today > 0) {
      analytics.summary.crash_rate_percent = Math.round(
        analytics.summary.total_crashes_today / analytics.summary.total_spawns_today * 100
      );
    }
    for (const cliKey of Object.keys(analytics.by_cli)) {
      const cliStats = analytics.by_cli[cliKey];
      if (cliStats.spawns > 0) {
        cliStats.crash_rate = Math.round(cliStats.crashes / cliStats.spawns * 100);
      }
    }
    return analytics;
  } catch {
    return null;
  }
}
async function getAgentStatus() {
  if (!existsSync(AGENT_LOGS_DIR)) return [];
  const [logEntries, leaderboard] = await Promise.all([
    readdir(AGENT_LOGS_DIR, { withFileTypes: true }),
    getLeaderboard()
  ]);
  const pointsByAgent = /* @__PURE__ */ new Map();
  if (leaderboard?.rankings) {
    for (const agent of leaderboard.rankings) {
      pointsByAgent.set(agent.id, agent.points || 0);
    }
  }
  const runningEntries = await getRunningAgentProcesses(pointsByAgent);
  const runningIds = new Set(runningEntries.map((entry) => entry.id));
  const logFiles = logEntries.filter((entry) => entry.isFile() && entry.name.endsWith(".log"));
  const fileStats = await Promise.all(
    logFiles.map(async (entry) => {
      const filePath = `${AGENT_LOGS_DIR}/${entry.name}`;
      return {
        entry,
        filePath,
        stats: await stat(filePath)
      };
    })
  );
  const completedCandidates = [];
  for (const fileInfo of fileStats) {
    const { entry, filePath, stats: fileStat } = fileInfo;
    const { id, genome, cli, startTime } = parseAgentLogName(entry.name, fileStat.mtime);
    if (runningIds.has(id)) continue;
    const endTime = fileStat.mtime;
    const durationMs = startTime ? endTime.getTime() - startTime.getTime() : null;
    const entryBase = {
      id,
      genome,
      cli,
      status: "completed",
      pid: null,
      startTime: formatDateTime(startTime),
      duration: formatDuration(durationMs),
      points: pointsByAgent.get(id) ?? null
    };
    completedCandidates.push({ entry: entryBase, endTime, filePath });
  }
  completedCandidates.sort((a, b) => b.endTime.getTime() - a.endTime.getTime());
  const completedEntries = completedCandidates.slice(0, 10);
  const completedWithStatus = [];
  for (const completed of completedEntries) {
    const tail = await readTail(completed.filePath);
    const status = parseCompletionStatus(tail);
    const genomeMatch = tail.match(/genome:\s*([A-Za-z0-9_-]+)/);
    const nameMatch = tail.match(/name:\s*([A-Za-z0-9_-]+)/);
    const genome = genomeMatch?.[1] || nameMatch?.[1] || completed.entry.genome;
    const cli = detectCliFromAgentId(completed.entry.id, tail) || completed.entry.cli;
    completedWithStatus.push({
      ...completed.entry,
      status,
      genome,
      cli
    });
  }
  runningEntries.sort((a, b) => a.startTime.localeCompare(b.startTime));
  return [...runningEntries, ...completedWithStatus];
}
async function getOrchestratorsState() {
  const CONTROL_DIR = `${KRALIKI_BASE}/control`;
  const CLIS = ["claude", "codex", "opencode", "gemini"];
  try {
    const orchestrators = [];
    let totalRuntimeMs = 0;
    let activeCount = 0;
    for (const cli of CLIS) {
      const stateFile = `${CONTROL_DIR}/orchestrator_state_${cli}.json`;
      try {
        if (!existsSync(stateFile)) {
          orchestrators.push({
            cli,
            pid: null,
            agent_id: null,
            spawned_at: null,
            duration: "--",
            is_running: false
          });
          continue;
        }
        const content = await readFile(stateFile, "utf-8");
        const state = JSON.parse(content);
        const pid = state.pid;
        const agentId = state.agent_id;
        const spawnedAt = state.spawned_at;
        let isRunning = false;
        if (pid) {
          try {
            await execAsync(`ps -p ${pid} -o pid=`);
            isRunning = true;
            activeCount++;
          } catch {
            isRunning = false;
          }
        }
        let duration = "--";
        if (spawnedAt) {
          const startTime = new Date(spawnedAt);
          const durationMs = Date.now() - startTime.getTime();
          if (isRunning) {
            totalRuntimeMs += durationMs;
          }
          duration = formatDuration(durationMs);
        }
        orchestrators.push({
          cli,
          pid,
          agent_id: agentId,
          spawned_at: spawnedAt,
          duration,
          is_running: isRunning
        });
      } catch {
        orchestrators.push({
          cli,
          pid: null,
          agent_id: null,
          spawned_at: null,
          duration: "--",
          is_running: false
        });
      }
    }
    return {
      orchestrators,
      active_count: activeCount,
      total_runtime_minutes: Math.floor(totalRuntimeMs / 6e4)
    };
  } catch {
    return null;
  }
}
async function getCostAnalytics() {
  if (!existsSync(AGENT_LOGS_DIR)) return null;
  const analytics = {
    summary: {
      total_cost_today: 0,
      total_cost_week: 0,
      total_tokens_today: 0,
      total_agents_today: 0,
      avg_cost_per_agent: 0
    },
    by_cli: {},
    by_model: {},
    top_agents: [],
    hourly_costs: []
  };
  try {
    const logEntries = await readdir(AGENT_LOGS_DIR, { withFileTypes: true });
    const logFiles = logEntries.filter((entry) => entry.isFile() && entry.name.endsWith(".log"));
    const today = /* @__PURE__ */ new Date();
    const todayStr = today.toISOString().slice(0, 10);
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1e3);
    const fileStats = await Promise.all(
      logFiles.map(async (entry) => {
        const filePath = `${AGENT_LOGS_DIR}/${entry.name}`;
        const stats = await stat(filePath);
        return { entry, filePath, stats };
      })
    );
    fileStats.sort((a, b) => b.stats.mtime.getTime() - a.stats.mtime.getTime());
    const hourlyCosts = {};
    const agentCosts = [];
    for (const fileInfo of fileStats.slice(0, 100)) {
      const { entry, filePath, stats: fileStat } = fileInfo;
      const { id, cli } = parseAgentLogName(entry.name, fileStat.mtime);
      const fileDate = fileStat.mtime.toISOString().slice(0, 10);
      const isToday = fileDate === todayStr;
      const isThisWeek = fileStat.mtime >= weekAgo;
      if (!isThisWeek) continue;
      try {
        const content = await readTail(filePath, 32768);
        const lines = content.split("\n").filter((l) => l.trim());
        const lastLine = lines[lines.length - 1];
        if (!lastLine) continue;
        const result = JSON.parse(lastLine);
        const cost = result.total_cost_usd || 0;
        const durationMs = result.duration_ms || 0;
        const usage = result.usage || {};
        const modelUsage = result.modelUsage || {};
        let points = null;
        const resultText = result.result || "";
        const pointsMatch = resultText.match(/points[_\s]*(?:earned)?[:\s]*(\d+)/i);
        if (pointsMatch) {
          points = parseInt(pointsMatch[1], 10);
        }
        if (isToday) {
          analytics.summary.total_cost_today += cost;
          analytics.summary.total_agents_today++;
          analytics.summary.total_tokens_today += (usage.input_tokens || 0) + (usage.output_tokens || 0);
        }
        analytics.summary.total_cost_week += cost;
        const cliKey = cli || "unknown";
        if (!analytics.by_cli[cliKey]) {
          analytics.by_cli[cliKey] = { agents: 0, cost: 0, tokens: 0 };
        }
        if (isToday) {
          analytics.by_cli[cliKey].agents++;
          analytics.by_cli[cliKey].cost += cost;
          analytics.by_cli[cliKey].tokens += (usage.input_tokens || 0) + (usage.output_tokens || 0);
        }
        for (const [model, modelData] of Object.entries(modelUsage)) {
          const data = modelData;
          if (!analytics.by_model[model]) {
            analytics.by_model[model] = { requests: 0, cost: 0, input_tokens: 0, output_tokens: 0 };
          }
          if (isToday) {
            analytics.by_model[model].requests++;
            analytics.by_model[model].cost += data.costUSD || 0;
            analytics.by_model[model].input_tokens += data.inputTokens || 0;
            analytics.by_model[model].output_tokens += data.outputTokens || 0;
          }
        }
        if (isToday) {
          const hour = fileStat.mtime.toISOString().slice(11, 13) + ":00";
          if (!hourlyCosts[hour]) {
            hourlyCosts[hour] = { cost: 0, agents: 0 };
          }
          hourlyCosts[hour].cost += cost;
          hourlyCosts[hour].agents++;
        }
        if (isToday && cost > 0) {
          agentCosts.push({
            id,
            cli,
            cost,
            duration_ms: durationMs,
            points,
            time: fileStat.mtime
          });
        }
      } catch {
      }
    }
    if (analytics.summary.total_agents_today > 0) {
      analytics.summary.avg_cost_per_agent = analytics.summary.total_cost_today / analytics.summary.total_agents_today;
    }
    analytics.hourly_costs = Object.entries(hourlyCosts).map(([hour, data]) => ({ hour, ...data })).sort((a, b) => a.hour.localeCompare(b.hour));
    analytics.top_agents = agentCosts.sort((a, b) => b.cost - a.cost).slice(0, 10).map((a) => ({
      id: a.id,
      cli: a.cli,
      cost: Math.round(a.cost * 100) / 100,
      duration_ms: a.duration_ms,
      points: a.points,
      efficiency: a.points && a.cost > 0 ? Math.round(a.points / a.cost * 10) / 10 : null
    }));
    analytics.summary.total_cost_today = Math.round(analytics.summary.total_cost_today * 100) / 100;
    analytics.summary.total_cost_week = Math.round(analytics.summary.total_cost_week * 100) / 100;
    analytics.summary.avg_cost_per_agent = Math.round(analytics.summary.avg_cost_per_agent * 100) / 100;
    return analytics;
  } catch {
    return null;
  }
}
export {
  getCostAnalytics as a,
  getFullStatus as b,
  getAgentStatus as g
};
