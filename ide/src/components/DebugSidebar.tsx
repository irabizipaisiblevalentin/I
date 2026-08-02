import { useIde } from "../store";
import { debugActiveFile, debugCommand, stopDebugSession } from "../commands";
import { updateBreakpointDecorations } from "./MonacoEditor";

export default function DebugSidebar() {
  const project = useIde((s) => s.project);
  const breakpoints = useIde((s) => s.breakpoints);
  const running = useIde((s) => s.debugRunning);
  const stopped = useIde((s) => s.debugStopped);

  if (!project) return null;

  const lines = Object.entries(breakpoints).flatMap(([file, ls]) =>
    ls.map((line) => ({ file, line })),
  );

  return (
    <div className="p-2">
      <span className="px-1 text-xs font-semibold text-gray-300">RUN &amp; DEBUG</span>
      <div className="mt-2 flex gap-1">
        <button
          onClick={() => void debugActiveFile()}
          className="flex-1 rounded bg-[#0e639c] px-2 py-1 text-xs text-white hover:bg-[#1177bb]"
        >
          ▶ Start
        </button>
        <button
          onClick={() => debugCommand("continue")}
          disabled={!stopped}
          className="rounded bg-[#3c3c3c] px-2 py-1 text-xs text-gray-200 hover:bg-[#4c4c4c] disabled:opacity-40"
        >
          ▶
        </button>
        <button
          onClick={() => debugCommand("step")}
          disabled={!stopped}
          className="rounded bg-[#3c3c3c] px-2 py-1 text-xs text-gray-200 hover:bg-[#4c4c4c] disabled:opacity-40"
        >
          ⤵
        </button>
        <button
          onClick={stopDebugSession}
          disabled={!running}
          className="rounded bg-[#a1260d] px-2 py-1 text-xs text-white hover:bg-[#c43e1e] disabled:opacity-40"
        >
          ■
        </button>
      </div>

      <div className="mt-3">
        <span className="px-1 text-[11px] font-semibold uppercase text-gray-400">
          Breakpoints
        </span>
        <div className="mt-1 space-y-0.5">
          {lines.map((bp) => (
            <div
              key={bp.file + bp.line}
              className="flex items-center justify-between px-1 text-xs text-gray-300"
            >
              <span className="truncate">
                {bp.file.split("/").pop()}:{bp.line}
              </span>
              <button
                onClick={() => {
                  useIde.getState().toggleBreakpoint(bp.file, bp.line);
                  updateBreakpointDecorations(bp.file);
                }}
                className="text-gray-500 hover:text-white"
              >
                ×
              </button>
            </div>
          ))}
          {lines.length === 0 && (
            <p className="px-1 text-xs text-gray-500">
              None — click a line number in the editor.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
