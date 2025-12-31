import { json } from "@sveltejs/kit";
import { readFile, stat, readdir } from "fs/promises";
import { join } from "path";
import "../../../../../chunks/scopes.js";
const BRAIN_PATH = "/home/adminmatej/github/brain-2026";
function parseMarkdown(content, filename) {
  content.split("\n");
  let title = filename.replace(".md", "").replace(/-/g, " ");
  let status = "unknown";
  let summary = "";
  const phases = [];
  const tasks = [];
  const h1Match = content.match(/^#\s+(.+)$/m);
  if (h1Match) {
    title = h1Match[1].trim();
  }
  const statusMatch = content.match(/\*\*Status:\*\*\s*(\w+)/i) || content.match(/Status:\s*(\w+)/i);
  if (statusMatch) {
    status = statusMatch[1];
  }
  const summaryMatch = content.match(/^#[^#].*\n\n([^#\n].+)/m);
  if (summaryMatch) {
    summary = summaryMatch[1].slice(0, 200);
  }
  const phaseRegex = /###\s+(Phase|Step)\s+(\d+[\.\d]*)[:\s]+(.+)/gi;
  let phaseMatch;
  while ((phaseMatch = phaseRegex.exec(content)) !== null) {
    const phaseId = phaseMatch[2];
    const phaseName = phaseMatch[3].trim();
    const phaseStatusMatch = phaseName.match(/(✅|DONE|COMPLETE|✓)/i);
    const phaseStatus = phaseStatusMatch ? "complete" : "pending";
    phases.push({
      id: phaseId,
      name: phaseName.replace(/\s*(✅|DONE|COMPLETE|✓).*/i, ""),
      status: phaseStatus,
      tasks: []
    });
  }
  const taskRegex = /^[-*]\s*\[([ xX✓])\]\s*(.+)$/gm;
  let taskMatch;
  let taskId = 1;
  while ((taskMatch = taskRegex.exec(content)) !== null) {
    const isComplete = taskMatch[1] !== " ";
    const taskTitle = taskMatch[2].trim();
    tasks.push({
      id: `task-${taskId++}`,
      title: taskTitle,
      status: isComplete ? "complete" : "pending"
    });
  }
  return { title, status, summary, phases, tasks };
}
async function scanDirectory(dirPath, type) {
  const docs = [];
  try {
    const files = await readdir(dirPath);
    for (const file of files) {
      if (!file.endsWith(".md")) continue;
      const filePath = join(dirPath, file);
      const fileStat = await stat(filePath);
      if (!fileStat.isFile()) continue;
      try {
        const content = await readFile(filePath, "utf-8");
        const parsed = parseMarkdown(content, file);
        const dateMatch = file.match(/(\d{4}-\d{2}-\d{2})/);
        const date = dateMatch ? dateMatch[1] : fileStat.mtime.toISOString().split("T")[0];
        docs.push({
          id: file.replace(".md", ""),
          title: parsed.title || file,
          path: filePath,
          type,
          date,
          status: parsed.status,
          summary: parsed.summary,
          phases: parsed.phases,
          tasks: parsed.tasks
        });
      } catch (e) {
        console.error(`Error parsing ${filePath}:`, e);
      }
    }
  } catch (e) {
    console.error(`Error scanning ${dirPath}:`, e);
  }
  return docs;
}
const GET = async ({ url }) => {
  try {
    const typeFilter = url.searchParams.get("type");
    const docs = [];
    const decisions = await scanDirectory(join(BRAIN_PATH, "decisions"), "decision");
    docs.push(...decisions);
    const plans = await scanDirectory(join(BRAIN_PATH, "plans"), "plan");
    docs.push(...plans);
    const roadmapFiles = ["2026_ROADMAP.md", "revenue_plan.md", "implementation_plan.md", "swarm-alignment.md"];
    for (const file of roadmapFiles) {
      try {
        const filePath = join(BRAIN_PATH, file);
        const content = await readFile(filePath, "utf-8");
        const parsed = parseMarkdown(content, file);
        const fileStat = await stat(filePath);
        docs.push({
          id: file.replace(".md", ""),
          title: parsed.title || file,
          path: filePath,
          type: "roadmap",
          date: fileStat.mtime.toISOString().split("T")[0],
          status: parsed.status,
          summary: parsed.summary,
          phases: parsed.phases,
          tasks: parsed.tasks
        });
      } catch (e) {
      }
    }
    const filtered = typeFilter ? docs.filter((d) => d.type === typeFilter) : docs;
    filtered.sort((a, b) => b.date.localeCompare(a.date));
    return json({
      strategies: filtered,
      count: filtered.length,
      types: {
        decision: docs.filter((d) => d.type === "decision").length,
        plan: docs.filter((d) => d.type === "plan").length,
        roadmap: docs.filter((d) => d.type === "roadmap").length
      }
    });
  } catch (e) {
    console.error("Error loading strategies:", e);
    return json({ error: "Failed to load strategies", details: e instanceof Error ? e.message : "Unknown" }, { status: 500 });
  }
};
const POST = async ({ request }) => {
  try {
    const { strategyId, strategyPath } = await request.json();
    if (!strategyPath) {
      return json({ error: "strategyPath required" }, { status: 400 });
    }
    const content = await readFile(strategyPath, "utf-8");
    const parsed = parseMarkdown(content, strategyPath.split("/").pop() || "strategy");
    const FOCUS_URL = process.env.FOCUS_URL || process.env.FOCUS_URL || "http://127.0.0.1:8095";
    const projectData = {
      name: parsed.title || "Imported Strategy",
      description: parsed.summary || `Imported from ${strategyPath}`,
      source_doc: strategyPath,
      status: "active"
    };
    const projectRes = await fetch(`${FOCUS_URL}/api/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectData)
    });
    if (!projectRes.ok) {
      const errorText = await projectRes.text();
      return json({ error: "Failed to create project in Focus", details: errorText }, { status: 500 });
    }
    const project = await projectRes.json();
    const createdTasks = [];
    const allTasks = [
      ...parsed.tasks || [],
      ...parsed.phases?.flatMap((p) => p.tasks) || []
    ];
    for (const task of allTasks) {
      try {
        const taskRes = await fetch(`${FOCUS_URL}/api/tasks`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: project.id,
            title: task.title,
            description: task.description || "",
            status: task.status === "complete" ? "done" : "todo",
            priority: task.priority || "medium"
          })
        });
        if (taskRes.ok) {
          createdTasks.push(await taskRes.json());
        }
      } catch (e) {
        console.error("Error creating task:", e);
      }
    }
    return json({
      success: true,
      project,
      tasksCreated: createdTasks.length,
      message: `Created project "${project.name}" with ${createdTasks.length} tasks`
    });
  } catch (e) {
    console.error("Error sending to Focus:", e);
    return json({ error: "Failed to send to Focus", details: e instanceof Error ? e.message : "Unknown" }, { status: 500 });
  }
};
export {
  GET,
  POST
};
