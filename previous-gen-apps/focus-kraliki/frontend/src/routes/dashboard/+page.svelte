<script lang="ts">
  import { onMount } from "svelte";
  import CommandCenterCanvas from "$lib/components/assistant/CommandCenterCanvas.svelte";
  import { assistantStore } from "$lib/stores/assistant";
  import { api } from "$lib/api/client";

  interface Project {
    id: string;
    name: string;
    description?: string;
    status: "active" | "archived" | "completed";
    task_count: number;
    completed_count: number;
    created_at?: string;
  }

  interface Task {
    id: string;
    title: string;
    description?: string;
    status: "todo" | "in_progress" | "done" | "archived";
    priority: "low" | "medium" | "high" | "urgent";
    project_id?: string;
    linear_id?: string;
    linear_url?: string;
    created_at?: string;
    due_date?: string;
  }

  interface KnowledgeSummary {
    total_items: number;
    types: Array<{
      type: string;
      typeId: string;
      icon?: string;
      color?: string;
      count: number;
      recent: Array<{ id: string; title: string }>;
    }>;
  }

  let focusStatus = $state<"online" | "offline" | "checking">("checking");
  let authStatus = $state<"authenticated" | "unauthenticated" | "unknown">("unknown");
  let focusUrl = $state("https://focus.verduona.dev");
  let localUrl = "http://127.0.0.1:3017";

  const productName = "Focus by Kraliki";

  let projects = $state<Project[]>([]);
  let tasks = $state<Task[]>([]);
  let selectedProjectId = $state<string | null>(null);
  let tasksScope = $state<"all" | "project">("all");
  let loading = $state(true);
  let activeTab = $state<"overview" | "projects" | "tasks" | "sync" | "brain">(
    "overview",
  );

  interface BrainResponse {
    success: boolean;
    message: string;
    data?: Record<string, unknown>;
  }

  interface DailyPlan {
    greeting: string;
    priorities: Array<{ title: string; priority: string }>;
    overdue: number;
    due_today: number;
    insight?: string;
  }

  let brainLoading = $state(false);
  let dailyPlan = $state<DailyPlan | null>(null);
  let nextAction = $state<{
    action: string;
    task?: unknown;
    reason?: string;
  } | null>(null);
  let brainInput = $state("");
  let brainResponse = $state<BrainResponse | null>(null);
  let captureInput = $state("");
  let captureResponse = $state<BrainResponse | null>(null);
  let summaryLoading = $state(false);
  let brainSummary = $state<KnowledgeSummary | null>(null);
  let summaryError = $state<string | null>(null);

  const commandPrompts = [
    "I have an idea for...",
    "Note to self:",
    "What should I do next?",
    "My goal is to...",
  ];
  const localCliTools = [
    { name: "OpenCode CLI", model: "GLM-4.7", note: "Default" },
    { name: "Claude Code CLI", model: "GLM-4.7", note: "Z.AI plan" },
    { name: "Cline", model: "GLM-4.7", note: "Local" },
    { name: "Agentic coding", model: "Grok Code Fast", note: "Speed" },
  ];
  let commandInput = $state("");
  let captureDraft = $state("");
  let supportsRecording = $state(false);
  let isRecording = $state(false);
  let isProcessingAudio = $state(false);
  let recordingError = $state<string | null>(null);
  let uploadError = $state<string | null>(null);
  let voiceProvider = $state("gemini-native");
  let voiceStatus = $state<{ providers: Record<string, boolean> } | null>(null);
  let mediaRecorder: MediaRecorder | null = $state(null);
  let recordingStream: MediaStream | null = $state(null);
  let audioChunks: Blob[] = $state([]);

  const STATUS_MAP: Record<string, Task["status"]> = {
    pending: "todo",
    todo: "todo",
    in_progress: "in_progress",
    inprogress: "in_progress",
    started: "in_progress",
    completed: "done",
    done: "done",
    archived: "archived",
    canceled: "archived",
    cancelled: "archived",
  };

  const demoProjects: Project[] = [
    {
      id: "demo-1",
      name: "Kraliki Integration",
      description: "Connect swarm agents to Focus",
      status: "active",
      task_count: 5,
      completed_count: 2,
    },
    {
      id: "demo-2",
      name: "Revenue Q1 2026",
      description: "Hit 3-5K MRR target",
      status: "active",
      task_count: 8,
      completed_count: 3,
    },
    {
      id: "demo-3",
      name: "AI Academy Launch",
      description: "L1-L4 training curriculum",
      status: "active",
      task_count: 12,
      completed_count: 1,
    },
  ];

  const demoTasks: Task[] = [
    {
      id: "t1",
      title: "Build Focus by Kraliki API proxy",
      status: "done",
      priority: "high",
      project_id: "demo-1",
      linear_id: "KRA-101",
    },
    {
      id: "t2",
      title: "Create projects UI component",
      status: "in_progress",
      priority: "high",
      project_id: "demo-1",
    },
    {
      id: "t3",
      title: "Implement task sync to Linear",
      status: "todo",
      priority: "medium",
      project_id: "demo-1",
    },
    {
      id: "t4",
      title: "SenseIt first paying customer",
      status: "in_progress",
      priority: "urgent",
      project_id: "demo-2",
      linear_id: "BIZ-001",
    },
    {
      id: "t5",
      title: "Voice by Kraliki demo ready",
      status: "todo",
      priority: "high",
      project_id: "demo-2",
    },
  ];

  function normalizePriority(rawPriority: unknown): Task["priority"] {
    if (typeof rawPriority === "number") {
      if (rawPriority <= 1) return "urgent";
      if (rawPriority === 2) return "high";
      if (rawPriority === 3) return "medium";
      return "low";
    }

    const value = String(rawPriority || "").toLowerCase();
    if (value === "urgent" || value === "critical" || value === "p1")
      return "urgent";
    if (value === "high" || value === "p2") return "high";
    if (value === "medium" || value === "normal" || value === "p3")
      return "medium";
    if (value === "low" || value === "p4") return "low";
    return "medium";
  }

  function normalizeTask(raw: Record<string, any>): Task {
    const statusKey = String(raw.status || raw.state || "todo").toLowerCase();
    const status = STATUS_MAP[statusKey] || "todo";

    return {
      id: raw.id,
      title: raw.title,
      description: raw.description || undefined,
      status,
      priority: normalizePriority(raw.priority),
      project_id: raw.project_id || raw.projectId || raw.projectID || raw.project?.id,
      linear_id: raw.linear_id || raw.linearId,
      linear_url: raw.linear_url || raw.linearUrl,
      created_at: raw.created_at || raw.createdAt,
      due_date: raw.due_date || raw.dueDate,
    };
  }

  function normalizeProject(raw: Record<string, any>): Project {
    const statusRaw = String(raw.status || "active").toLowerCase();
    const status: Project["status"] =
      statusRaw === "archived"
        ? "archived"
        : statusRaw === "completed"
          ? "completed"
          : "active";

    return {
      id: raw.id,
      name: raw.name,
      description: raw.description || undefined,
      status,
      task_count: raw.task_count ?? raw.taskCount ?? 0,
      completed_count: raw.completed_count ?? raw.completedCount ?? 0,
      created_at: raw.created_at || raw.createdAt,
    };
  }

  function extractList(data: any, key: "projects" | "tasks"): any[] {
    if (Array.isArray(data)) return data;
    if (data?.[key]) return data[key];
    return [];
  }

  function priorityFromScore(score?: number) {
    if (score === undefined || score === null) return "medium";
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    return "low";
  }

  function normalizeDailyPlan(raw: Record<string, any> | null): DailyPlan | null {
    if (!raw) return null;
    const source = raw.priorities || raw.top_tasks || [];
    const priorities = source.map((item: Record<string, any>) => {
      const rawPriority = item.priority ?? item.priority_score;
      const priority =
        typeof rawPriority === "number" && rawPriority > 4
          ? priorityFromScore(rawPriority)
          : normalizePriority(rawPriority);

      return {
        title: item.title || item.task?.title || "Untitled task",
        priority,
      };
    });

    return {
      greeting: raw.greeting || "Ready to focus?",
      priorities,
      overdue: raw.overdue ?? raw.overdue_count ?? 0,
      due_today: raw.due_today ?? raw.due_today_count ?? 0,
      insight: raw.insight || raw.shadow_insight || raw.reasoning || raw.recommendation,
    };
  }

  function normalizeNextAction(raw: Record<string, any> | null) {
    if (!raw) return null;
    const action = raw.message || raw.action || "Next action ready";
    const reason = raw.reason || raw.reasoning || raw.suggestion;
    return { action, task: raw.task, reason };
  }

  function isCapturableInput(input: string): boolean {
    const trimmed = input.trim();
    if (!trimmed) return false;
    const lowerInput = trimmed.toLowerCase();

    const questionPatterns = [
      /\?$/,
      /^(what|when|where|who|why|how|can you|could you|please|show|find|search|help)/i,
      /^(do |does |is |are |was |were |will |would |should i)/i,
    ];

    for (const pattern of questionPatterns) {
      if (pattern.test(lowerInput)) return false;
    }

    const capturePatterns = [
      /^(idea|note|task|plan|goal|strategy|remember|don't forget|need to|should|must|todo)/i,
      /^(i have an? |my |the |a |an )/i,
    ];

    for (const pattern of capturePatterns) {
      if (pattern.test(lowerInput)) return true;
    }

    return trimmed.length < 120 && !trimmed.includes("?");
  }

  function getAuthHeaders(): Record<string, string> {
    const token = api.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function authFetch(url: string, options: RequestInit = {}) {
    const headers = {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    };
    return fetch(url, {
      ...options,
      headers,
    });
  }

  async function postBrainAction(
    action: "ask" | "capture",
    payload: Record<string, unknown>,
  ) {
    const res = await authFetch(`/api/brain/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(20000),
    });

    const data = await res.json().catch(() => null);
    if (!res.ok) {
      return {
        success: false,
        message: data?.message || data?.error || "Focus Brain unavailable",
      };
    }

    return data as BrainResponse;
  }

  async function handleCommandMessage(
    message: string,
    options?: { addUserMessage?: boolean; source?: "text" | "voice" },
  ) {
    const trimmed = message.trim();
    if (!trimmed) return;

    if (options?.addUserMessage) {
      assistantStore.addMessage({
        role: "user",
        content: trimmed,
        source: options.source || "text",
      });
    }

    assistantStore.setProcessing(true);
    try {
      const capture = isCapturableInput(trimmed);
      const response = capture
        ? await postBrainAction("capture", { input: trimmed, create: true })
        : await postBrainAction("ask", { question: trimmed });

      assistantStore.addMessage({
        role: response.success ? "assistant" : "system",
        content:
          response.message ||
          (capture ? "Captured in Focus." : "Focus Brain replied."),
        source: "text",
      });

      if (capture) {
        await fetchBrainSummary();
      }
    } catch (error) {
      assistantStore.addMessage({
        role: "system",
        content:
          error instanceof Error ? error.message : "Focus Brain request failed.",
        source: "text",
      });
    } finally {
      assistantStore.setProcessing(false);
    }
  }

  async function submitCaptureDraft() {
    const draft = captureDraft.trim();
    if (!draft) return;
    captureDraft = "";
    await handleCommandMessage(draft, { addUserMessage: true, source: "text" });
  }

  async function handleCommandSend(event: { detail: { message: string } }) {
    await handleCommandMessage(event.detail.message);
  }

  async function checkFocus() {
    focusStatus = "checking";
    try {
      const res = await authFetch("/api/brain/health", {
        signal: AbortSignal.timeout(5000),
      });
      if (res.ok) {
        const data = await res.json();
        focusStatus = data.status === "ok" || data.status === "healthy" ? "online" : "offline";
      } else {
        focusStatus = "offline";
      }
    } catch {
      focusStatus = "offline";
    }
  }

  async function fetchProjects() {
    try {
      const res = await authFetch("/api/projects", {
        signal: AbortSignal.timeout(10000),
      });

      if (res.status === 401 || res.status === 403) {
        authStatus = "unauthenticated";
        projects = demoProjects.map(normalizeProject);
        return;
      }

      if (res.ok) {
        const data = await res.json();
        const rawProjects = extractList(data, "projects");
        projects = rawProjects.map(normalizeProject);
        authStatus = "authenticated";
      } else {
        projects = demoProjects.map(normalizeProject);
        authStatus = "unauthenticated";
      }
    } catch {
      projects = demoProjects.map(normalizeProject);
      authStatus = "unauthenticated";
    }
  }

  async function fetchTasks(projectId?: string) {
    tasksScope = projectId ? "project" : "all";
    try {
      const url = projectId ? `/api/tasks?projectId=${projectId}` : "/api/tasks";
      const res = await authFetch(url, {
        signal: AbortSignal.timeout(10000),
      });

      if (res.status === 401 || res.status === 403) {
        authStatus = "unauthenticated";
        const demoList = projectId
          ? demoTasks.filter((t) => t.project_id === projectId)
          : demoTasks;
        tasks = demoList.map(normalizeTask);
        return;
      }

      if (res.ok) {
        const data = await res.json();
        const rawTasks = extractList(data, "tasks");
        tasks = rawTasks.map(normalizeTask);
        if (authStatus === "unknown") authStatus = "authenticated";
      } else {
        const demoList = projectId
          ? demoTasks.filter((t) => t.project_id === projectId)
          : demoTasks;
        tasks = demoList.map(normalizeTask);
      }
    } catch {
      const demoList = projectId
        ? demoTasks.filter((t) => t.project_id === projectId)
        : demoTasks;
      tasks = demoList.map(normalizeTask);
    }
  }

  function selectProject(projectId: string | null) {
    selectedProjectId = projectId;
    if (projectId) {
      fetchTasks(projectId);
    } else {
      fetchTasks();
    }
  }

  async function fetchDailyPlan() {
    brainLoading = true;
    try {
      const res = await authFetch("/api/brain/daily-plan", {
        signal: AbortSignal.timeout(15000),
      });
      if (res.ok) {
        const data = await res.json();
        dailyPlan = normalizeDailyPlan(data.data || data);
      }
    } catch {
      // ignore
    } finally {
      brainLoading = false;
    }
  }

  async function fetchNextAction() {
    try {
      const res = await authFetch("/api/brain/next-action", {
        signal: AbortSignal.timeout(15000),
      });
      if (res.ok) {
        const data = await res.json();
        nextAction = normalizeNextAction(data.data || data);
      }
    } catch {
      // ignore
    }
  }

  async function refreshBrainPulse() {
    await fetchDailyPlan();
    await fetchNextAction();
    await fetchBrainSummary();
  }

  async function askBrain() {
    if (!brainInput.trim()) return;
    brainLoading = true;
    brainResponse = null;
    try {
      const response = await postBrainAction("ask", { question: brainInput });
      brainResponse = response;
    } catch (error) {
      brainResponse = {
        success: false,
        message: error instanceof Error ? error.message : "Focus Brain unavailable",
      };
    } finally {
      brainLoading = false;
    }
  }

  async function captureToBrain() {
    if (!captureInput.trim()) return;
    brainLoading = true;
    captureResponse = null;
    try {
      const response = await postBrainAction("capture", {
        input: captureInput,
        create: true,
      });
      captureResponse = response;
      if (captureResponse?.success) {
        captureInput = "";
      }
    } catch (error) {
      captureResponse = {
        success: false,
        message: error instanceof Error ? error.message : "Capture failed",
      };
    } finally {
      brainLoading = false;
    }
  }

  async function fetchBrainSummary() {
    summaryLoading = true;
    summaryError = null;
    try {
      const res = await authFetch("/api/brain/summary", {
        signal: AbortSignal.timeout(15000),
      });
      if (res.status === 401 || res.status === 403) {
        authStatus = "unauthenticated";
        summaryError = "Authentication required";
        return;
      }
      if (res.ok) {
        const data = await res.json();
        const summary = data.data || data;
        if (summary?.types) {
          brainSummary = summary as KnowledgeSummary;
        } else {
          brainSummary = null;
          summaryError = "Summary unavailable";
        }
      } else {
        summaryError = "Failed to load summary";
      }
    } catch (error) {
      summaryError = error instanceof Error ? error.message : "Summary error";
    } finally {
      summaryLoading = false;
    }
  }

  async function syncTaskToLinear(taskId: string) {
    try {
      const res = await authFetch(`/api/linear/sync-task/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          labels: ["GIN", "GIN-DEV"],
          priority: "medium",
          team_key: "PRO",
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          const taskIndex = tasks.findIndex((t) => t.id === taskId);
          if (taskIndex !== -1) {
            tasks[taskIndex].linear_id = data.linear_id;
            tasks[taskIndex].linear_url = data.linear_url;
          }
          alert(`Synced to Linear: ${data.message}`);
        } else {
          alert(`Sync failed: ${data.message}`);
        }
      } else {
        alert("Failed to sync to Linear");
      }
    } catch {
      alert("Error syncing to Linear");
    }
  }

  async function checkVoiceProviders() {
    try {
      const data = await api.assistant.getProviders() as { providers?: Record<string, boolean>; data?: { providers?: Record<string, boolean> } };
      const providers = data.providers || data.data?.providers || {};
      voiceStatus = { providers };
    } catch {
      voiceStatus = null;
    }
  }

  function handleVoiceProviderChange(value: string) {
    voiceProvider = value;
  }

  function startRecording() {
    if (!supportsRecording || isRecording) return;
    recordingError = null;
    uploadError = null;

    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        recordingStream = stream;
        isRecording = true;
        audioChunks = [];

        const options: MediaRecorderOptions = { mimeType: "audio/webm" };
        mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks = [...audioChunks, event.data];
          }
        };
        mediaRecorder.onstop = () => {
          processRecording();
        };
        mediaRecorder.start();
      })
      .catch(() => {
        recordingError = "Microphone access denied";
        isRecording = false;
      });
  }

  function stopRecording() {
    if (!isRecording || !mediaRecorder) return;
    isRecording = false;
    mediaRecorder.stop();

    if (recordingStream) {
      recordingStream.getTracks().forEach((track) => track.stop());
      recordingStream = null;
    }
  }

  async function processRecording() {
    if (audioChunks.length === 0) return;

    isProcessingAudio = true;
    uploadError = null;

    try {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      audioChunks = [];

      const result: any = await api.assistant.transcribeAudio(
        audioBlob,
        "en",
        voiceProvider,
      );
      const transcript = result.transcript || "";
      if (!transcript) {
        throw new Error("No transcript returned");
      }

      await handleCommandMessage(transcript, {
        addUserMessage: true,
        source: "voice",
      });
    } catch (error) {
      uploadError = error instanceof Error ? error.message : "Voice processing failed";
    } finally {
      isProcessingAudio = false;
    }
  }

  async function uploadCaptureFile(file: File) {
    uploadError = null;
    try {
      const formData = new FormData();
      formData.append("file", file, file.name);

      const res = await authFetch("/api/captures/upload", {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(30000),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Upload failed");
      }

      const data = await res.json();
      assistantStore.addMessage({
        role: "assistant",
        content: `Captured: ${data.title || file.name}`,
        source: "text",
      });
      await fetchBrainSummary();
    } catch (error) {
      uploadError =
        error instanceof Error ? error.message : "Capture upload failed";
    }
  }

  async function handleCommandUpload(event: Event) {
    const target = event.currentTarget as HTMLInputElement | null;
    const file = target?.files?.[0];
    if (!file) return;
    await uploadCaptureFile(file);
    if (target) target.value = "";
  }

  function handleCommandDragOver(event: DragEvent) {
    event.preventDefault();
  }

  async function handleCommandDrop(event: DragEvent) {
    event.preventDefault();
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      await uploadCaptureFile(file);
      return;
    }
    const text = event.dataTransfer?.getData("text/plain");
    if (text) {
      await handleCommandMessage(text, { addUserMessage: true, source: "text" });
    }
  }

  async function handleCommandPaste(event: ClipboardEvent) {
    const items = event.clipboardData?.items;
    if (!items) return;

    for (const item of items) {
      if (item.type.startsWith("image/")) {
        event.preventDefault();
        const file = item.getAsFile();
        if (file) {
          await uploadCaptureFile(file);
        }
        return;
      }
    }
  }

  onMount(() => {
    focusUrl = window.location.origin;
    supportsRecording = !!navigator?.mediaDevices?.getUserMedia;
    checkVoiceProviders();

    const init = async () => {
      await Promise.all([checkFocus(), fetchProjects(), fetchTasks()]);
      loading = false;
    };
    init();

    const interval = setInterval(checkFocus, 30000);
    const pasteHandler = (event: ClipboardEvent) => {
      handleCommandPaste(event);
    };
    window.addEventListener("paste", pasteHandler);

    return () => {
      clearInterval(interval);
      window.removeEventListener("paste", pasteHandler);
    };
  });

  const projectStats = $derived.by(() => {
    const stats = new Map<string, { total: number; completed: number }>();

    for (const project of projects) {
      stats.set(project.id, {
        total: project.task_count || 0,
        completed: project.completed_count || 0,
      });
    }

    if (tasksScope === "all") {
      for (const [projectId] of stats) {
        stats.set(projectId, { total: 0, completed: 0 });
      }

      for (const task of tasks) {
        if (!task.project_id) continue;
        const current = stats.get(task.project_id) || {
          total: 0,
          completed: 0,
        };
        current.total += 1;
        if (task.status === "done") {
          current.completed += 1;
        }
        stats.set(task.project_id, current);
      }
    } else if (tasksScope === "project" && selectedProjectId) {
      const current = stats.get(selectedProjectId) || { total: 0, completed: 0 };
      if (current.total === 0 && current.completed === 0) {
        for (const task of tasks) {
          if (task.project_id !== selectedProjectId) continue;
          current.total += 1;
          if (task.status === "done") current.completed += 1;
        }
        stats.set(selectedProjectId, current);
      }
    }

    return stats;
  });

  const projectsWithStats = $derived(
    projects.map((project) => {
      const stats = projectStats.get(project.id);
      return {
        ...project,
        task_count: stats?.total ?? project.task_count ?? 0,
        completed_count: stats?.completed ?? project.completed_count ?? 0,
      };
    }),
  );

  const selectedProject = $derived(
    projectsWithStats.find((p) => p.id === selectedProjectId),
  );
  const filteredTasks = $derived(
    selectedProjectId
      ? tasks.filter((t) => t.project_id === selectedProjectId)
      : tasks,
  );

  const totalProjects = $derived(projectsWithStats.length);
  const activeProjects = $derived(
    projectsWithStats.filter((p) => p.status === "active").length,
  );
  const totalTasks = $derived(tasks.length);
  const completedTasks = $derived(tasks.filter((t) => t.status === "done").length);
  const inProgressTasks = $derived(
    tasks.filter((t) => t.status === "in_progress").length,
  );
  const syncedToLinear = $derived(tasks.filter((t) => t.linear_id).length);

  function getPriorityClass(priority: string): string {
    switch (priority) {
      case "urgent":
        return "priority-urgent";
      case "high":
        return "priority-high";
      case "medium":
        return "priority-medium";
      default:
        return "priority-low";
    }
  }

  function getStatusClass(status: string): string {
    switch (status) {
      case "done":
        return "status-done";
      case "in_progress":
        return "status-progress";
      case "archived":
        return "status-archived";
      default:
        return "status-todo";
    }
  }

  $effect(() => {
    if ((activeTab === "brain" || activeTab === "overview") && !dailyPlan) {
      fetchDailyPlan();
      fetchNextAction();
    }
    if ((activeTab === "brain" || activeTab === "overview") && !brainSummary && !summaryLoading) {
      fetchBrainSummary();
    }
    if (activeTab === "sync" && tasksScope !== "all") {
      selectedProjectId = null;
      fetchTasks();
    }
  });
</script>

<div class="page">
  <div class="page-header">
    <h2 class="glitch">{productName} // Strategy to Execution</h2>
    <div class="header-badges">
      <span class="status-badge">{activeProjects} PROJECTS</span>
      <span class="focus-badge {focusStatus}">
        {#if focusStatus === "checking"}
          FOCUS: CHECKING...
        {:else if focusStatus === "online"}
          FOCUS: ONLINE
        {:else}
          FOCUS: OFFLINE
        {/if}
      </span>
    </div>
  </div>

  <div class="integration-banner" class:online={focusStatus === "online"} class:demo={authStatus === "unauthenticated"}>
    <div class="banner-content">
      <span class="banner-icon">&#9201;</span>
      <div class="banner-text">
        <strong>{productName}: AI Brain Organizer</strong>
        {#if authStatus === "unauthenticated"}
          <span class="demo-notice">Showing demo data - login to Focus for real data</span>
        {:else}
          <span>Capture anything, turn it into projects, sync to swarm execution.</span>
        {/if}
      </div>
      <div class="banner-actions">
        <a href={focusUrl} target="_blank" class="brutal-btn small">OPEN FOCUS</a>
        {#if focusStatus === "online"}
          <a href={localUrl} target="_blank" class="brutal-btn small outline">LOCAL</a>
        {/if}
      </div>
    </div>
  </div>

  <div class="focus-tabs">
    <button class="focus-tab" class:active={activeTab === "overview"} onclick={() => (activeTab = "overview")}>
      COMMAND
    </button>
    <button class="focus-tab" class:active={activeTab === "projects"} onclick={() => (activeTab = "projects")}>
      PROJECTS
    </button>
    <button class="focus-tab" class:active={activeTab === "tasks"} onclick={() => (activeTab = "tasks")}>
      TASKS
    </button>
    <button class="focus-tab" class:active={activeTab === "sync"} onclick={() => (activeTab = "sync")}>
      LINEAR SYNC
    </button>
    <button class="focus-tab brain-tab" class:active={activeTab === "brain"} onclick={() => (activeTab = "brain")}>
      AI BRAIN
    </button>
  </div>

  {#if loading}
    <div class="loading-state">
      <div class="loader"></div>
      <span>Loading {productName} data...</span>
    </div>
  {:else if activeTab === "overview"}
    <div class="command-hero">
      <div class="hero-top">
        <span class="hero-tag">FOCUS MODE</span>
        <span class="hero-status {focusStatus}">
          {#if focusStatus === "checking"}
            FOCUS: CHECKING...
          {:else if focusStatus === "online"}
            FOCUS: ONLINE
          {:else}
            FOCUS: OFFLINE
          {/if}
        </span>
      </div>
      <h3 class="command-title">COMMAND CENTER</h3>
      <p class="command-subtitle">Unified AI assistant with voice, text, and workflow orchestration.</p>
      <div class="hero-stats">
        <div class="hero-stat">
          <span class="stat-value">{totalProjects}</span>
          <span class="stat-label">PROJECTS</span>
        </div>
        <div class="hero-stat">
          <span class="stat-value">{totalTasks}</span>
          <span class="stat-label">TASKS</span>
        </div>
        <div class="hero-stat">
          <span class="stat-value">{inProgressTasks}</span>
          <span class="stat-label">IN_PROGRESS</span>
        </div>
        <div class="hero-stat">
          <span class="stat-value">{completedTasks}</span>
          <span class="stat-label">COMPLETED</span>
        </div>
      </div>
    </div>

    <div class="command-layout">
      <div class="command-main">
        <div class="command-panel">
          <CommandCenterCanvas
            title="Command Center"
            subtitle="Unified AI assistant with voice, text, and workflow orchestration"
            bind:inputMessage={commandInput}
            quickPrompts={commandPrompts}
            {isRecording}
            {isProcessingAudio}
            {supportsRecording}
            {voiceProvider}
            {voiceStatus}
            {recordingError}
            {uploadError}
            onsend={handleCommandSend}
            onrecord={startRecording}
            onstop={stopRecording}
            onupload={handleCommandUpload}
            onprovider={handleVoiceProviderChange}
          />
        </div>

        <div class="capture-zone" ondragover={handleCommandDragOver} ondrop={handleCommandDrop}>
          <div class="capture-header">
            <h4>SEAMLESS CAPTURE</h4>
            <p>Drop files, paste images, or dump raw text. The Brain auto-organizes.</p>
          </div>
          <div class="capture-input-row">
            <input
              type="text"
              class="capture-input"
              placeholder="Type anything to capture instantly..."
              bind:value={captureDraft}
              onkeydown={(e) => e.key === "Enter" && submitCaptureDraft()}
            />
            <button class="brutal-btn" onclick={submitCaptureDraft} disabled={!captureDraft.trim()}>
              CAPTURE
            </button>
          </div>
          <div class="capture-meta">
            <span>Supports images, text, and links. Paste anywhere.</span>
            {#if uploadError}
              <span class="capture-error">{uploadError}</span>
            {/if}
          </div>
        </div>
      </div>

      <div class="command-side">
        <div class="pulse-card">
          <div class="pulse-title">DAILY PLAN</div>
          {#if dailyPlan}
            <div class="pulse-greeting">{dailyPlan.greeting}</div>
            {#if dailyPlan.priorities?.length}
              <div class="pulse-priorities">
                {#each dailyPlan.priorities.slice(0, 3) as priority}
                  <div class="pulse-priority">
                    <span class="priority-dot {priority.priority}"></span>
                    <span>{priority.title}</span>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="pulse-muted">No priorities yet.</div>
            {/if}
            <div class="pulse-stats">
              <span class="pulse-stat danger">OVERDUE: {dailyPlan.overdue || 0}</span>
              <span class="pulse-stat">DUE TODAY: {dailyPlan.due_today || 0}</span>
            </div>
          {:else if brainLoading}
            <div class="pulse-muted">Loading daily plan...</div>
          {:else}
            <div class="pulse-muted">No daily plan yet.</div>
          {/if}
        </div>

        <div class="pulse-card">
          <div class="pulse-title">NEXT ACTION</div>
          {#if nextAction}
            <div class="pulse-action">{nextAction.action}</div>
            {#if nextAction.reason}
              <div class="pulse-reason">{nextAction.reason}</div>
            {/if}
          {:else if brainLoading}
            <div class="pulse-muted">Loading next action...</div>
          {:else}
            <div class="pulse-muted">No next action available.</div>
          {/if}
        </div>

        <div class="pulse-card">
          <div class="pulse-title">KNOWLEDGE SUMMARY</div>
          {#if brainSummary}
            <div class="summary-total">TOTAL ITEMS: {brainSummary.total_items}</div>
            <div class="summary-types">
              {#each brainSummary.types.slice(0, 5) as item}
                <div class="summary-type">
                  <span class="summary-dot" style="background-color: {item.color || 'var(--terminal-green)'}"></span>
                  <span class="summary-label">{item.type.toUpperCase()}</span>
                  <span class="summary-count">{item.count}</span>
                </div>
              {/each}
            </div>
          {:else if summaryLoading}
            <div class="pulse-muted">Loading summary...</div>
          {:else if summaryError}
            <div class="pulse-muted">{summaryError}</div>
          {:else}
            <div class="pulse-muted">Summary unavailable.</div>
          {/if}
        </div>

        <div class="pulse-actions">
          <button class="brutal-btn small outline" onclick={refreshBrainPulse} disabled={brainLoading || summaryLoading}>
            {brainLoading || summaryLoading ? "LOADING..." : "REFRESH"}
          </button>
          <button class="brutal-btn small" onclick={() => (activeTab = "brain")}>
            OPEN BRAIN
          </button>
        </div>
      </div>
    </div>

    <div class="snapshot-grid">
      <div class="snapshot-card">
        <div class="snapshot-header">
          <h4>PROJECTS SNAPSHOT</h4>
          <button class="brutal-btn small outline" onclick={() => (activeTab = "projects")}>
            VIEW ALL
          </button>
        </div>
        <div class="snapshot-list">
          {#each projectsWithStats.slice(0, 4) as project}
            <div class="snapshot-item">
              <div class="snapshot-title">{project.name}</div>
              <span class="snapshot-status {project.status}">{project.status.toUpperCase()}</span>
              <span class="snapshot-meta">{project.completed_count}/{project.task_count} tasks</span>
            </div>
          {/each}
          {#if projectsWithStats.length === 0}
            <div class="snapshot-empty">No projects yet.</div>
          {/if}
        </div>
      </div>

      <div class="snapshot-card">
        <div class="snapshot-header">
          <h4>TASKS SNAPSHOT</h4>
          <button class="brutal-btn small outline" onclick={() => (activeTab = "tasks")}>
            VIEW ALL
          </button>
        </div>
        <div class="snapshot-list">
          {#each tasks.slice(0, 6) as task}
            <div class="snapshot-item">
              <span class="task-status {getStatusClass(task.status)}">
                {task.status.replace("_", " ").toUpperCase()}
              </span>
              <span class="snapshot-title">{task.title}</span>
              <span class="task-priority {getPriorityClass(task.priority)}">
                {task.priority.toUpperCase()}
              </span>
            </div>
          {/each}
          {#if tasks.length === 0}
            <div class="snapshot-empty">No tasks yet.</div>
          {/if}
        </div>
      </div>

      <div class="snapshot-card">
        <div class="snapshot-header">
          <h4>LINEAR SYNC</h4>
          <button class="brutal-btn small outline" onclick={() => (activeTab = "sync")}>
            OPEN SYNC
          </button>
        </div>
        <div class="snapshot-list">
          <div class="snapshot-metric">
            <span class="metric-value">{syncedToLinear}</span>
            <span class="metric-label">SYNCED</span>
          </div>
          <div class="snapshot-metric">
            <span class="metric-value">{totalTasks - syncedToLinear}</span>
            <span class="metric-label">PENDING</span>
          </div>
          <div class="snapshot-metric">
            <span class="metric-value">{totalTasks > 0 ? Math.round((syncedToLinear / totalTasks) * 100) : 0}%</span>
            <span class="metric-label">RATE</span>
          </div>
        </div>
      </div>

      <div class="snapshot-card">
        <div class="snapshot-header">
          <h4>LOCAL CLI (LAB)</h4>
          <span class="snapshot-meta">CONTAINER</span>
        </div>
        <div class="snapshot-list cli-list">
          {#each localCliTools as tool}
            <div class="cli-row">
              <span class="cli-name">{tool.name}</span>
              <span class="cli-model">{tool.model}</span>
              <span class="cli-note">{tool.note}</span>
            </div>
          {/each}
        </div>
      </div>
    </div>

    {#if authStatus === "unauthenticated"}
      <div class="auth-notice">
        <span class="notice-icon">&#128274;</span>
        <span>Login to Focus by Kraliki for full Brain access. Demo data shown above.</span>
        <a href={focusUrl} target="_blank" class="brutal-btn small">LOGIN</a>
      </div>
    {/if}
  {:else if activeTab === "projects"}
    <div class="projects-section">
      <div class="section-header">
        <h3>PROJECTS</h3>
        <button
          class="brutal-btn small"
          disabled={authStatus === "unauthenticated"}
          title={authStatus === "unauthenticated" ? "Login to Focus to create projects" : ""}
        >
          + NEW PROJECT
        </button>
      </div>

      <div class="projects-grid">
        {#each projectsWithStats as project}
          <button
            class="project-card"
            class:selected={selectedProjectId === project.id}
            class:active={project.status === "active"}
            onclick={() =>
              selectProject(project.id === selectedProjectId ? null : project.id)}
            type="button"
          >
            <div class="project-header">
              <span class="project-name">{project.name}</span>
              <span class="project-status {project.status}">
                {project.status.toUpperCase()}
              </span>
            </div>
            {#if project.description}
              <p class="project-desc">{project.description}</p>
            {/if}
            <div class="project-progress">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  style="width: {project.task_count > 0
                    ? (project.completed_count / project.task_count) * 100
                    : 0}%"
                ></div>
              </div>
              <span class="progress-text">
                {project.completed_count}/{project.task_count} tasks
              </span>
            </div>
          </button>
        {/each}
      </div>
    </div>
  {:else if activeTab === "tasks"}
    <div class="tasks-section">
      <div class="section-header">
        <h3>
          {#if selectedProject}
            TASKS // {selectedProject.name}
          {:else}
            ALL TASKS
          {/if}
        </h3>
        <div class="task-filters">
          {#if selectedProjectId}
            <button class="brutal-btn small outline" onclick={() => selectProject(null)}>
              SHOW ALL
            </button>
          {/if}
          <button class="brutal-btn small" disabled={authStatus === "unauthenticated"}>
            + NEW TASK
          </button>
        </div>
      </div>

      <div class="status-filters">
        <span class="filter-label">Filter:</span>
        <button class="filter-btn active">ALL ({filteredTasks.length})</button>
        <button class="filter-btn">TODO ({filteredTasks.filter((t) => t.status === "todo").length})</button>
        <button class="filter-btn">
          IN PROGRESS ({filteredTasks.filter((t) => t.status === "in_progress").length})
        </button>
        <button class="filter-btn">DONE ({filteredTasks.filter((t) => t.status === "done").length})</button>
      </div>

      <div class="task-list detailed">
        {#each filteredTasks as task}
          <div class="task-card">
            <div class="task-main">
              <span class="task-status-dot {getStatusClass(task.status)}"></span>
              <div class="task-info">
                <span class="task-title">{task.title}</span>
                {#if task.description}
                  <span class="task-desc">{task.description}</span>
                {/if}
              </div>
            </div>
            <div class="task-meta">
              <span class="task-priority {getPriorityClass(task.priority)}">
                {task.priority.toUpperCase()}
              </span>
              <span class="task-status-badge {getStatusClass(task.status)}">
                {task.status.replace("_", " ").toUpperCase()}
              </span>
              {#if task.linear_id}
                <a href={task.linear_url || "#"} class="task-linear-link" target="_blank">
                  {task.linear_id}
                </a>
              {:else}
                <button
                  class="sync-btn"
                  disabled={authStatus === "unauthenticated"}
                  onclick={() => syncTaskToLinear(task.id)}
                >
                  SYNC TO LINEAR
                </button>
              {/if}
            </div>
          </div>
        {/each}

        {#if filteredTasks.length === 0}
          <div class="empty-state">
            <div class="empty-icon">&#128203;</div>
            <p>No tasks found</p>
          </div>
        {/if}
      </div>
    </div>
  {:else if activeTab === "sync"}
    <div class="sync-section">
      <div class="section">
        <h3>LINEAR SYNC STATUS</h3>

        <div class="sync-stats">
          <div class="sync-stat">
            <span class="sync-value">{syncedToLinear}</span>
            <span class="sync-label">Synced to Linear</span>
          </div>
          <div class="sync-stat">
            <span class="sync-value">{totalTasks - syncedToLinear}</span>
            <span class="sync-label">Not Synced</span>
          </div>
          <div class="sync-stat">
            <span class="sync-value">{totalTasks > 0 ? Math.round((syncedToLinear / totalTasks) * 100) : 0}%</span>
            <span class="sync-label">Sync Rate</span>
          </div>
        </div>

        <div class="sync-progress">
          <div class="sync-bar">
            <div
              class="sync-fill"
              style="width: {totalTasks > 0 ? (syncedToLinear / totalTasks) * 100 : 0}%"
            ></div>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>SYNCED TASKS</h3>
        <div class="synced-list">
          {#each tasks.filter((t) => t.linear_id) as task}
            <div class="synced-item">
              <span class="synced-title">{task.title}</span>
              <span class="synced-id">{task.linear_id}</span>
              <span class="synced-status {getStatusClass(task.status)}">
                {task.status.replace("_", " ").toUpperCase()}
              </span>
            </div>
          {/each}

          {#if syncedToLinear === 0}
            <div class="empty-state small">
              <p>No tasks synced to Linear yet</p>
            </div>
          {/if}
        </div>
      </div>

      <div class="section">
        <h3>UNSYNCED TASKS</h3>
        <div class="unsynced-list">
          {#each tasks.filter((t) => !t.linear_id) as task}
            <div class="unsynced-item">
              <span class="unsynced-title">{task.title}</span>
              <span class="unsynced-priority {getPriorityClass(task.priority)}">
                {task.priority.toUpperCase()}
              </span>
              <button class="brutal-btn small" disabled={authStatus === "unauthenticated"} onclick={() => syncTaskToLinear(task.id)}>
                SYNC NOW
              </button>
            </div>
          {/each}

          {#if totalTasks - syncedToLinear === 0}
            <div class="empty-state small">
              <p>All tasks are synced!</p>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {:else if activeTab === "brain"}
    <div class="brain-section">
      <div class="section brain-card">
        <div class="section-header">
          <h3>DAILY PLAN</h3>
          <button class="brutal-btn small outline" onclick={fetchDailyPlan} disabled={brainLoading}>
            {brainLoading ? "LOADING..." : "REFRESH"}
          </button>
        </div>

        {#if dailyPlan}
          <div class="daily-plan">
            <div class="greeting">{dailyPlan.greeting}</div>

            {#if dailyPlan.priorities && dailyPlan.priorities.length > 0}
              <div class="priorities">
                <h4>TOP PRIORITIES</h4>
                {#each dailyPlan.priorities as priority}
                  <div class="priority-item">
                    <span class="priority-dot {priority.priority}"></span>
                    <span class="priority-title">{priority.title}</span>
                  </div>
                {/each}
              </div>
            {/if}

            <div class="plan-stats">
              <div class="plan-stat">
                <span class="plan-stat-value danger">{dailyPlan.overdue || 0}</span>
                <span class="plan-stat-label">OVERDUE</span>
              </div>
              <div class="plan-stat">
                <span class="plan-stat-value">{dailyPlan.due_today || 0}</span>
                <span class="plan-stat-label">DUE TODAY</span>
              </div>
            </div>

            {#if dailyPlan.insight}
              <div class="plan-insight">
                <span class="insight-icon">&#128161;</span>
                <span>{dailyPlan.insight}</span>
              </div>
            {/if}
          </div>
        {:else if brainLoading}
          <div class="loading-state small">
            <div class="loader"></div>
            <span>Loading your daily plan...</span>
          </div>
        {:else}
          <div class="empty-state small">
            <p>No daily plan available</p>
          </div>
        {/if}
      </div>

      <div class="section brain-card next-action-card">
        <h3>NEXT ACTION</h3>
        {#if nextAction}
          <div class="next-action">
            <div class="action-text">{nextAction.action}</div>
            {#if nextAction.reason}
              <div class="action-reason">{nextAction.reason}</div>
            {/if}
          </div>
        {:else}
          <div class="empty-state small">
            <p>Loading next action...</p>
          </div>
        {/if}
      </div>

      <div class="section brain-card">
        <h3>ASK THE BRAIN</h3>
        <div class="brain-input-container">
          <input
            type="text"
            class="brain-input"
            placeholder="Ask anything about your work..."
            bind:value={brainInput}
            onkeydown={(e) => e.key === "Enter" && askBrain()}
            disabled={brainLoading || authStatus === "unauthenticated"}
          />
          <button
            class="brutal-btn"
            onclick={askBrain}
            disabled={brainLoading || !brainInput.trim() || authStatus === "unauthenticated"}
          >
            {brainLoading ? "THINKING..." : "ASK"}
          </button>
        </div>

        {#if brainResponse}
          <div class="brain-response" class:success={brainResponse.success} class:error={!brainResponse.success}>
            <div class="response-message">{brainResponse.message}</div>
            {#if brainResponse.data}
              <pre class="response-data">{JSON.stringify(brainResponse.data, null, 2)}</pre>
            {/if}
          </div>
        {/if}
      </div>

      <div class="section brain-card">
        <h3>QUICK CAPTURE</h3>
        <p class="brain-hint">Just type anything - the Brain will auto-categorize it as an idea, task, note, or plan.</p>
        <div class="brain-input-container">
          <textarea
            class="brain-textarea"
            placeholder="I have an idea... / Remember to... / My goal is..."
            bind:value={captureInput}
            disabled={brainLoading || authStatus === "unauthenticated"}
            rows="3"
          ></textarea>
          <button
            class="brutal-btn"
            onclick={captureToBrain}
            disabled={brainLoading || !captureInput.trim() || authStatus === "unauthenticated"}
          >
            {brainLoading ? "CAPTURING..." : "CAPTURE"}
          </button>
        </div>

        {#if captureResponse}
          <div class="brain-response" class:success={captureResponse.success} class:error={!captureResponse.success}>
            <div class="response-message">{captureResponse.message}</div>
          </div>
        {/if}
      </div>

      {#if authStatus === "unauthenticated"}
        <div class="auth-notice">
          <span class="notice-icon">&#128274;</span>
          <span>Login to Focus by Kraliki for full Brain access. Demo data shown above.</span>
          <a href={focusUrl} target="_blank" class="brutal-btn small">LOGIN</a>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  :global(:root) {
    --terminal-green: var(--color-terminal-green);
    --cyan-data: var(--color-cyan-data, #00ffff);
    --warning: #ffaa00;
    --magenta-pulse: #ff00ff;
    --text-main: hsl(var(--foreground));
    --text-muted: hsl(var(--muted-foreground));
    --surface: hsl(var(--card));
    --void: var(--color-void);
  }

  .page {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--border);
    padding-bottom: 16px;
  }

  .header-badges {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .status-badge {
    padding: 8px 16px;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-muted);
  }

  .focus-badge {
    padding: 8px 16px;
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
    border: 2px solid var(--border);
  }

  .focus-badge.checking {
    color: var(--text-muted);
  }

  .focus-badge.online {
    color: var(--terminal-green);
    border-color: var(--terminal-green);
    background: rgba(51, 255, 0, 0.1);
  }

  .focus-badge.offline {
    color: var(--text-muted);
    border-style: dashed;
  }

  .integration-banner {
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 16px 20px;
  }

  .integration-banner.online {
    border-color: var(--terminal-green);
  }

  .integration-banner.demo {
    border-color: var(--warning, #ffaa00);
  }

  .banner-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .banner-icon {
    font-size: 32px;
  }

  .banner-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .banner-text strong {
    font-size: 14px;
    color: var(--text-main);
  }

  .banner-text span {
    font-size: 12px;
    color: var(--text-muted);
  }

  .demo-notice {
    color: var(--warning, #ffaa00) !important;
    font-style: italic;
  }

  .banner-actions {
    display: flex;
    gap: 8px;
  }

  .focus-tabs {
    display: flex;
    gap: 8px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 12px;
  }

  .focus-tab {
    padding: 10px 20px;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-muted);
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .focus-tab:hover {
    border-color: var(--terminal-green);
    color: var(--terminal-green);
  }

  .focus-tab.active {
    background: var(--terminal-green);
    border-color: var(--terminal-green);
    color: var(--void);
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 48px;
    color: var(--text-muted);
  }

  .loader {
    width: 32px;
    height: 32px;
    border: 3px solid var(--border);
    border-top-color: var(--terminal-green);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }

  .stat-card {
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 20px;
    text-align: center;
    box-shadow: 4px 4px 0 0 var(--border);
  }

  .stat-value {
    display: block;
    font-family: "JetBrains Mono", monospace;
    font-size: 32px;
    font-weight: 700;
    color: var(--terminal-green);
  }

  .stat-label {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.05em;
  }

  .command-hero {
    background: linear-gradient(135deg, rgba(51, 255, 0, 0.08), rgba(0, 0, 0, 0.6));
    border: 2px solid var(--border);
    padding: 24px;
    box-shadow: 6px 6px 0 0 var(--border);
    display: flex;
    flex-direction: column;
    gap: 12px;
    position: relative;
  }

  .hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .hero-tag {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    padding: 6px 10px;
    border: 2px solid var(--border);
    background: var(--surface);
    color: var(--text-muted);
    font-weight: 700;
  }

  .hero-status {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 6px 10px;
    border: 2px solid var(--border);
  }

  .hero-status.online {
    border-color: var(--terminal-green);
    color: var(--terminal-green);
  }

  .hero-status.offline {
    color: var(--text-muted);
    border-style: dashed;
  }

  .command-title {
    font-size: 32px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--terminal-green);
  }

  .command-subtitle {
    font-size: 12px;
    color: var(--text-muted);
    max-width: 520px;
  }

  .hero-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }

  .hero-stat {
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 12px;
    text-align: left;
  }

  .command-layout {
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(240px, 1fr);
    gap: 20px;
  }

  .command-main {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .command-panel {
    border: 2px solid var(--border);
    box-shadow: 4px 4px 0 0 var(--border);
    background: var(--surface);
  }

  .capture-zone {
    border: 2px dashed var(--border);
    padding: 16px;
    background: rgba(255, 255, 255, 0.02);
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .capture-zone h4 {
    font-size: 11px;
    margin: 0 0 6px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
  }

  .capture-zone p {
    font-size: 11px;
    color: var(--text-muted);
    margin: 0;
  }

  .capture-input-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .capture-input {
    flex: 1;
    min-width: 220px;
    padding: 10px 12px;
    border: 2px solid var(--border);
    background: var(--void);
    color: var(--text-main);
    font-family: "JetBrains Mono", monospace;
  }

  .capture-input:focus {
    outline: none;
    border-color: var(--terminal-green);
  }

  .capture-meta {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--text-muted);
    gap: 12px;
    flex-wrap: wrap;
  }

  .capture-error {
    color: #ff0066;
    font-weight: 700;
  }

  .command-side {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .section {
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 20px;
    box-shadow: 4px 4px 0 0 var(--border);
  }

  .section h3 {
    font-size: 12px;
    font-weight: 700;
    margin: 0 0 16px 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .section-hint {
    margin: 4px 0 0;
    font-size: 11px;
    color: var(--text-muted);
  }

  .pulse-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .pulse-card {
    border: 2px solid var(--border);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: rgba(255, 255, 255, 0.02);
  }

  .pulse-title {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    font-weight: 700;
  }

  .pulse-greeting {
    font-size: 16px;
    font-weight: 600;
  }

  .pulse-priorities {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .pulse-priority {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
  }

  .pulse-muted {
    font-size: 12px;
    color: var(--text-muted);
  }

  .pulse-stats {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .pulse-stat {
    color: var(--text-muted);
  }

  .pulse-stat.danger {
    color: #ff0066;
  }

  .pulse-action {
    font-size: 14px;
    font-weight: 600;
  }

  .pulse-reason {
    font-size: 11px;
    color: var(--text-muted);
  }

  .summary-total {
    font-size: 12px;
    font-weight: 700;
    color: var(--terminal-green);
    letter-spacing: 0.05em;
  }

  .summary-types {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .summary-type {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
  }

  .summary-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .summary-label {
    flex: 1;
    color: var(--text-main);
  }

  .summary-count {
    font-family: "JetBrains Mono", monospace;
    color: var(--text-muted);
  }

  .snapshot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
  }

  .snapshot-card {
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 16px;
    box-shadow: 4px 4px 0 0 var(--border);
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .snapshot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }

  .snapshot-header h4 {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin: 0;
  }

  .snapshot-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .snapshot-item {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 8px;
    align-items: center;
    font-size: 11px;
  }

  .snapshot-title {
    color: var(--text-main);
  }

  .cli-list {
    gap: 10px;
  }

  .cli-row {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 8px;
    align-items: center;
    font-size: 11px;
  }

  .cli-name {
    font-weight: 700;
    color: var(--text-main);
  }

  .cli-model {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .cli-note {
    font-size: 9px;
    text-transform: uppercase;
    padding: 2px 6px;
    border: 1px solid var(--border);
    color: var(--text-muted);
  }

  .snapshot-status {
    font-size: 9px;
    padding: 2px 6px;
    border: 1px solid var(--border);
    text-transform: uppercase;
  }

  .snapshot-status.active {
    border-color: var(--terminal-green);
    color: var(--terminal-green);
  }

  .snapshot-status.completed {
    border-color: var(--cyan-data, #00d4ff);
    color: var(--cyan-data, #00d4ff);
  }

  .snapshot-status.archived {
    color: var(--text-muted);
    border-style: dashed;
  }

  .snapshot-meta {
    font-size: 10px;
    color: var(--text-muted);
    white-space: nowrap;
  }

  .snapshot-empty {
    font-size: 11px;
    color: var(--text-muted);
    padding: 8px 0;
  }

  .snapshot-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }

  .snapshot-metric:last-child {
    border-bottom: none;
  }

  .metric-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--terminal-green);
    font-family: "JetBrains Mono", monospace;
  }

  .metric-label {
    font-size: 9px;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .task-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .task-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border);
  }

  .task-status {
    font-size: 9px;
    padding: 4px 8px;
    font-weight: 700;
    min-width: 80px;
    text-align: center;
  }

  .task-title {
    flex: 1;
    font-size: 12px;
  }

  .task-priority {
    font-size: 9px;
    padding: 2px 8px;
    font-weight: 700;
  }

  .task-linear {
    font-size: 10px;
    color: var(--cyan-data, #00d4ff);
    font-family: "JetBrains Mono", monospace;
  }

  .status-done,
  .task-status.status-done {
    background: var(--terminal-green);
    color: var(--void);
  }

  .status-progress,
  .task-status.status-progress {
    background: var(--cyan-data, #00d4ff);
    color: var(--void);
  }

  .status-todo,
  .task-status.status-todo {
    background: var(--border);
    color: var(--text-main);
  }

  .status-archived,
  .task-status.status-archived {
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-muted);
    border: 1px dashed var(--border);
  }

  .priority-urgent {
    background: #ff0066;
    color: white;
  }

  .priority-high {
    background: var(--warning, #ffaa00);
    color: var(--void);
  }

  .priority-medium {
    background: var(--cyan-data, #00d4ff);
    color: var(--void);
  }

  .priority-low {
    background: var(--border);
    color: var(--text-main);
  }

  .projects-section,
  .tasks-section,
  .sync-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }

  .project-card {
    background: var(--surface);
    border: 2px solid var(--border);
    padding: 20px;
    cursor: pointer;
    transition: all 0.1s ease;
    text-align: left;
    width: 100%;
    font-family: inherit;
    color: inherit;
  }

  .project-card:hover {
    border-color: var(--terminal-green);
  }

  .project-card.selected {
    border-color: var(--terminal-green);
    box-shadow: 4px 4px 0 0 var(--terminal-green);
  }

  .project-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
  }

  .project-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-main);
  }

  .project-status {
    font-size: 9px;
    padding: 2px 8px;
    font-weight: 700;
  }

  .project-status.active {
    background: var(--terminal-green);
    color: var(--void);
  }

  .project-status.archived {
    background: var(--border);
    color: var(--text-muted);
  }

  .project-status.completed {
    background: var(--cyan-data, #00d4ff);
    color: var(--void);
  }

  .project-desc {
    font-size: 11px;
    color: var(--text-muted);
    margin: 0 0 12px 0;
    line-height: 1.4;
  }

  .project-progress {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--border);
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--terminal-green);
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: 10px;
    color: var(--text-muted);
    font-family: "JetBrains Mono", monospace;
  }

  .task-filters {
    display: flex;
    gap: 8px;
  }

  .status-filters {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }

  .filter-label {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .filter-btn {
    padding: 6px 12px;
    font-size: 10px;
    font-family: "JetBrains Mono", monospace;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-muted);
    cursor: pointer;
  }

  .filter-btn:hover,
  .filter-btn.active {
    border-color: var(--terminal-green);
    color: var(--terminal-green);
  }

  .task-list.detailed {
    gap: 12px;
  }

  .task-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: var(--surface);
    border: 2px solid var(--border);
    gap: 16px;
  }

  .task-main {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
  }

  .task-status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .task-status-dot.status-done {
    background: var(--terminal-green);
  }

  .task-status-dot.status-progress {
    background: var(--cyan-data, #00d4ff);
  }

  .task-status-dot.status-todo {
    background: var(--border);
  }

  .task-status-dot.status-archived {
    background: var(--text-muted);
  }

  .task-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .task-desc {
    font-size: 11px;
    color: var(--text-muted);
  }

  .task-meta {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .task-status-badge {
    font-size: 9px;
    padding: 4px 8px;
    font-weight: 700;
  }

  .task-linear-link {
    font-size: 10px;
    padding: 4px 8px;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid var(--cyan-data, #00d4ff);
    color: var(--cyan-data, #00d4ff);
    text-decoration: none;
    font-family: "JetBrains Mono", monospace;
  }

  .sync-btn {
    font-size: 9px;
    padding: 4px 8px;
    background: var(--surface);
    border: 1px dashed var(--border);
    color: var(--text-muted);
    cursor: pointer;
    font-family: "JetBrains Mono", monospace;
  }

  .sync-btn:hover:not(:disabled) {
    border-color: var(--terminal-green);
    color: var(--terminal-green);
  }

  .sync-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .sync-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }

  .sync-stat {
    text-align: center;
  }

  .sync-value {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: var(--terminal-green);
    font-family: "JetBrains Mono", monospace;
  }

  .sync-label {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .sync-progress {
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }

  .sync-bar {
    height: 8px;
    background: var(--border);
    overflow: hidden;
  }

  .sync-fill {
    height: 100%;
    background: var(--terminal-green);
    transition: width 0.3s ease;
  }

  .synced-list,
  .unsynced-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .synced-item,
  .unsynced-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border);
  }

  .synced-title,
  .unsynced-title {
    flex: 1;
    font-size: 12px;
  }

  .synced-id {
    font-size: 10px;
    color: var(--cyan-data, #00d4ff);
    font-family: "JetBrains Mono", monospace;
  }

  .synced-status {
    font-size: 9px;
    padding: 2px 8px;
    font-weight: 700;
  }

  .unsynced-priority {
    font-size: 9px;
    padding: 2px 8px;
    font-weight: 700;
  }

  .empty-state {
    text-align: center;
    padding: 48px;
  }

  .empty-state.small {
    padding: 24px;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .empty-state p {
    color: var(--text-muted);
    margin: 0;
  }

  .brain-tab {
    background: linear-gradient(135deg, var(--surface) 0%, rgba(255, 0, 255, 0.1) 100%);
  }

  .brain-tab:hover {
    border-color: var(--magenta-pulse, #ff00ff);
    color: var(--magenta-pulse, #ff00ff);
  }

  .brain-tab.active {
    background: var(--magenta-pulse, #ff00ff);
    border-color: var(--magenta-pulse, #ff00ff);
  }

  .brain-section {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .brain-card {
    border-color: var(--magenta-pulse, #ff00ff);
  }

  .brain-card h3 {
    color: var(--magenta-pulse, #ff00ff);
  }

  .daily-plan {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .greeting {
    font-size: 18px;
    color: var(--text-main);
    font-weight: 500;
  }

  .priorities h4 {
    font-size: 10px;
    color: var(--text-muted);
    margin: 0 0 8px 0;
    letter-spacing: 0.05em;
  }

  .priority-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .priority-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .priority-dot.high,
  .priority-dot.urgent {
    background: var(--warning, #ffaa00);
  }

  .priority-dot.medium {
    background: var(--cyan-data, #00d4ff);
  }

  .priority-dot.low {
    background: var(--border);
  }

  .priority-title {
    font-size: 13px;
  }

  .plan-stats {
    display: flex;
    gap: 24px;
    padding: 12px 0;
  }

  .plan-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .plan-stat-value {
    font-size: 24px;
    font-weight: 700;
    font-family: "JetBrains Mono", monospace;
    color: var(--terminal-green);
  }

  .plan-stat-value.danger {
    color: #ff0066;
  }

  .plan-stat-label {
    font-size: 9px;
    color: var(--text-muted);
    letter-spacing: 0.05em;
  }

  .plan-insight {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px;
    background: rgba(255, 0, 255, 0.05);
    border: 1px dashed var(--magenta-pulse, #ff00ff);
    font-size: 12px;
  }

  .insight-icon {
    font-size: 16px;
  }

  .next-action-card {
    border-color: var(--terminal-green);
  }

  .next-action-card h3 {
    color: var(--terminal-green);
  }

  .next-action {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .action-text {
    font-size: 16px;
    color: var(--text-main);
    font-weight: 500;
  }

  .action-reason {
    font-size: 12px;
    color: var(--text-muted);
  }

  .brain-input-container {
    display: flex;
    gap: 12px;
    margin-top: 12px;
  }

  .brain-input {
    flex: 1;
    padding: 12px 16px;
    background: var(--void);
    border: 2px solid var(--border);
    color: var(--text-main);
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
  }

  .brain-input:focus {
    outline: none;
    border-color: var(--magenta-pulse, #ff00ff);
  }

  .brain-textarea {
    flex: 1;
    padding: 12px 16px;
    background: var(--void);
    border: 2px solid var(--border);
    color: var(--text-main);
    font-family: inherit;
    font-size: 13px;
    resize: vertical;
    min-height: 80px;
  }

  .brain-textarea:focus {
    outline: none;
    border-color: var(--magenta-pulse, #ff00ff);
  }

  .brain-hint {
    font-size: 11px;
    color: var(--text-muted);
    margin: 4px 0 8px 0;
  }

  .brain-response {
    margin-top: 16px;
    padding: 16px;
    border: 2px solid var(--border);
  }

  .brain-response.success {
    border-color: var(--terminal-green);
    background: rgba(51, 255, 0, 0.05);
  }

  .brain-response.error {
    border-color: #ff0066;
    background: rgba(255, 0, 102, 0.05);
  }

  .response-message {
    font-size: 13px;
    line-height: 1.5;
  }

  .response-data {
    margin-top: 12px;
    padding: 12px;
    background: var(--void);
    font-size: 11px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .auth-notice {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: rgba(255, 170, 0, 0.1);
    border: 2px dashed var(--warning, #ffaa00);
  }

  .notice-icon {
    font-size: 20px;
  }

  .loading-state.small {
    padding: 24px;
  }

  .brutal-btn {
    background: var(--surface);
    border: 2px solid var(--terminal-green);
    color: var(--terminal-green);
    padding: 10px 20px;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: all 0.1s ease;
  }

  .brutal-btn:hover:not(:disabled) {
    background: var(--terminal-green);
    color: var(--void);
  }

  .brutal-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .brutal-btn.small {
    padding: 6px 12px;
    font-size: 10px;
  }

  .brutal-btn.outline {
    border-style: dashed;
  }

  @media (max-width: 768px) {
    .stats-row {
      grid-template-columns: repeat(2, 1fr);
    }

    .command-layout {
      grid-template-columns: 1fr;
    }

    .hero-stats {
      grid-template-columns: repeat(2, 1fr);
    }

    .command-title {
      font-size: 24px;
    }

    .projects-grid {
      grid-template-columns: 1fr;
    }

    .task-card {
      flex-direction: column;
      align-items: flex-start;
    }

    .task-meta {
      flex-wrap: wrap;
    }

    .sync-stats {
      grid-template-columns: 1fr;
    }

    .banner-content {
      flex-direction: column;
      text-align: center;
    }

    .focus-tabs {
      flex-wrap: wrap;
    }

    .brain-input-container {
      flex-direction: column;
      align-items: stretch;
    }

    .snapshot-item {
      grid-template-columns: 1fr;
      align-items: flex-start;
    }
  }
</style>
