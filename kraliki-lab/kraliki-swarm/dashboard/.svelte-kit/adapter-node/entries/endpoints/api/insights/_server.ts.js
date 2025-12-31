import { json } from "@sveltejs/kit";
import { exec } from "child_process";
import { promisify } from "util";
import * as fs from "fs/promises";
promisify(exec);
const DARWIN2_DIR = process.env.DARWIN2_PATH || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm";
const BOARD_FILE = `${DARWIN2_DIR}/arena/data/board.json`;
const GET = async () => {
  try {
    let insights = [];
    try {
      const data = await fs.readFile(BOARD_FILE, "utf-8");
      const board = JSON.parse(data);
      if (board.posts) {
        insights = board.posts.slice(0, 50).map((post) => ({
          id: post.id || Math.random().toString(36).substr(2, 9),
          agent: post.author || "unknown",
          category: post.category || "general",
          title: post.title || post.content?.substring(0, 50) || "Untitled",
          content: post.content || "",
          importance: post.importance || "medium",
          timestamp: post.timestamp || (/* @__PURE__ */ new Date()).toISOString(),
          upvotes: post.upvotes || 0
        }));
      }
    } catch {
    }
    return json({
      insights,
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString(),
      categories: ["revenue", "technical", "strategy", "blockers", "general"]
    });
  } catch (e) {
    console.error("Failed to get insights:", e);
    return json({
      insights: [],
      error: e instanceof Error ? e.message : "Unknown error",
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString()
    }, { status: 500 });
  }
};
const POST = async ({ request }) => {
  try {
    const insight = await request.json();
    let board = { posts: [] };
    try {
      const data = await fs.readFile(BOARD_FILE, "utf-8");
      board = JSON.parse(data);
    } catch {
    }
    const newInsight = {
      id: Math.random().toString(36).substr(2, 9),
      ...insight,
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      upvotes: 0
    };
    board.posts = [newInsight, ...board.posts];
    await fs.writeFile(BOARD_FILE, JSON.stringify(board, null, 2));
    return json({ success: true, insight: newInsight });
  } catch (e) {
    console.error("Failed to post insight:", e);
    return json({
      error: "Failed to post insight",
      details: e instanceof Error ? e.message : "Unknown error"
    }, { status: 500 });
  }
};
export {
  GET,
  POST
};
