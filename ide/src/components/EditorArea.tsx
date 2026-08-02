import { useIde } from "../store";
import MonacoEditor, { updateBreakpointDecorations } from "./MonacoEditor";
import { debugActiveFile, runActiveFile } from "../commands";
import { useEffect } from "react";

export default function EditorArea() {
  const openFiles = useIde((s) => s.openFiles);
  const activeFile = useIde((s) => s.activeFile);
  const content = useIde((s) => s.content);
  const setContent = useIde((s) => s.setContent);
  const setActiveFile = useIde((s) => s.setActiveFile);
  const closeFile = useIde((s) => s.closeFile);
  const runRunning = useIde((s) => s.runRunning);
  const debugRunning = useIde((s) => s.debugRunning);

  useEffect(() => {
    if (activeFile) updateBreakpointDecorations(activeFile);
  }, [activeFile]);

  if (!activeFile) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-gray-500">
        Open a file from the Explorer to start editing.
      </div>
    );
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-[#333] bg-[#252526]">
        <div className="flex min-w-0 flex-1 overflow-x-auto">
          {openFiles.map((path) => {
            const name = path.split("/").pop() ?? path;
            const isActive = path === activeFile;
            return (
              <div
                key={path}
                onClick={() => setActiveFile(path)}
                className={`flex shrink-0 cursor-pointer items-center gap-1 border-r border-[#333] px-3 py-1.5 text-xs ${
                  isActive
                    ? "bg-[#1e1e1e] text-white"
                    : "bg-[#2d2d2d] text-gray-400 hover:text-white"
                }`}
                title={path}
              >
                <span>{name}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    closeFile(path);
                  }}
                  className="rounded px-1 text-gray-500 hover:bg-[#3c3c3c] hover:text-white"
                >
                  ×
                </button>
              </div>
            );
          })}
        </div>
        <div className="flex shrink-0 items-center gap-1 px-2">
          <button
            title="Run"
            onClick={() => void runActiveFile()}
            className="flex items-center gap-1 rounded bg-[#0e639c] px-3 py-1 text-xs text-white hover:bg-[#1177bb]"
          >
            {runRunning ? "⏳ Running…" : "▶ Run"}
          </button>
          <button
            title="Debug"
            onClick={() => void debugActiveFile()}
            className="rounded bg-[#3c3c3c] px-3 py-1 text-xs text-gray-200 hover:bg-[#4c4c4c]"
          >
            🐞 Debug
          </button>
        </div>
      </div>
      <div className="min-h-0 flex-1">
        <MonacoEditor
          file={activeFile}
          value={content[activeFile] ?? ""}
          onChange={(v) => setContent(activeFile, v)}
        />
      </div>
      {debugRunning && <DebugHint />}
    </div>
  );
}

function DebugHint() {
  return (
    <div className="border-t border-[#333] bg-[#1e1e1e] px-3 py-1 text-[11px] text-gray-400">
      Debugging — set breakpoints by clicking line numbers, then control from the Debug panel.
    </div>
  );
}
