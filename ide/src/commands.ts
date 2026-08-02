import { api } from "./api";
import { closeSSE, openSSE } from "./sse";
import { useIde } from "./store";
import { scrollToLine } from "./components/MonacoEditor";
import type { DebugStopped } from "./types";

let runSSE: EventSource | null = null;
let debugSSE: EventSource | null = null;
let debugSessionId: string | null = null;

function isDebugStopped(value: unknown): value is DebugStopped {
  const v = value as DebugStopped;
  return typeof v === "object" && v !== null && typeof v.line === "number";
}

export async function runActiveFile(): Promise<void> {
  const state = useIde.getState();
  const { project, activeFile } = state;
  if (!project || !activeFile) return;
  if (runSSE) {
    closeSSE(runSSE);
    runSSE = null;
  }
  state.clearRun();
  state.setRunRunning(true);
  state.setRunExit(null);
  state.showPanel("output");

  let data: { job_id: string } | null = null;
  try {
    data = await api<{ job_id: string }>("/api/run", {
      method: "POST",
      body: { root: project.path, file: activeFile },
    });
  } catch (err) {
    state.appendRun(`[error] could not start run: ${String(err)}\n`);
    state.setRunRunning(false);
    state.setRunExit({ ok: false, code: -1 });
    return;
  }
  runSSE = openSSE(`/sse/run/${data.job_id}`, (event, payload) => {
    const s = useIde.getState();
    if (event === "output") {
      const line = (payload as { line?: string })?.line ?? "";
      s.appendRun(line);
    } else if (event === "done") {
      const done = payload as { ok?: boolean; code?: number };
      s.setRunExit({ ok: Boolean(done.ok), code: done.code ?? -1 });
      s.setRunRunning(false);
    } else if (event === "error") {
      s.appendRun(`[error] ${String(payload)}\n`);
      s.setRunRunning(false);
    }
  });
}

export async function debugActiveFile(): Promise<void> {
  const state = useIde.getState();
  const { project, activeFile } = state;
  if (!project || !activeFile) return;
  if (debugSSE) {
    closeSSE(debugSSE);
    debugSSE = null;
  }
  debugSessionId = null;
  const file = activeFile;
  state.setDebugRunning(true);
  state.setDebugEnded(false);
  state.setDebugStopped(null);
  useIde.setState({ debugOutput: "" });
  state.showPanel("debug");

  const data = await api<{ session_id: string }>("/api/debug/start", {
    method: "POST",
    body: { root: project.path, file },
  });
  debugSessionId = data.session_id;
  const lines = state.breakpoints[file] ?? [];
  if (lines.length > 0) {
    void api("/api/debug/command", {
      method: "POST",
      body: { session_id: data.session_id, command: "breakpoints", lines },
    });
  }
  debugSSE = openSSE(`/sse/debug/${data.session_id}`, (event, payload) => {
    const s = useIde.getState();
    if (event === "stopped" && isDebugStopped(payload)) {
      s.setDebugStopped(payload);
      scrollToLine(payload.line);
    } else if (event === "output") {
      const line = (payload as { line?: string })?.line ?? "";
      s.appendDebugOutput(line);
    } else if (event === "ended") {
      s.setDebugEnded(true);
      s.setDebugRunning(false);
    } else if (event === "error") {
      s.setDebugEnded(true);
      s.setDebugRunning(false);
    }
  });
}

export function debugCommand(command: "continue" | "step" | "stop"): void {
  if (!debugSessionId) return;
  void api("/api/debug/command", {
    method: "POST",
    body: { session_id: debugSessionId, command },
  });
}

export function syncBreakpointsForDebug(file: string): void {
  if (!debugSessionId) return;
  const lines = useIde.getState().breakpoints[file] ?? [];
  void api("/api/debug/command", {
    method: "POST",
    body: { session_id: debugSessionId, command: "breakpoints", lines },
  });
}

export function stopDebugSession(): void {
  if (debugSessionId) {
    void api("/api/debug/stop", { method: "POST", body: { session_id: debugSessionId } });
  }
  if (debugSSE) {
    closeSSE(debugSSE);
    debugSSE = null;
  }
  debugSessionId = null;
  useIde.getState().setDebugRunning(false);
}
