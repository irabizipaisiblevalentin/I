import { useMemo } from "react";
import { useIde } from "../../store";
import type { Diagnostic } from "../../types";
import { getEditor } from "../MonacoEditor";

const SEVERITY_LABEL: Record<number, { label: string; cls: string }> = {
  1: { label: "error", cls: "text-red-400" },
  2: { label: "warning", cls: "text-yellow-400" },
  3: { label: "info", cls: "text-blue-400" },
  4: { label: "hint", cls: "text-gray-400" },
};

export default function Problems() {
  const diagnostics = useIde((s) => s.diagnostics);
  const setActiveFile = useIde((s) => s.setActiveFile);

  const all = useMemo(() => {
    const rows: { file: string; diag: Diagnostic }[] = [];
    for (const [file, list] of Object.entries(diagnostics)) {
      for (const diag of list) {
        rows.push({ file, diag });
      }
    }
    return rows;
  }, [diagnostics]);

  const goto = (file: string, diag: Diagnostic) => {
    setActiveFile(file);
    const ed = getEditor();
    if (ed) {
      ed.revealLineInCenter(diag.range.start.line);
      ed.setPosition({ lineNumber: diag.range.start.line, column: 1 });
      ed.focus();
    }
  };

  if (all.length === 0) {
    return (
      <div className="p-3 text-xs text-gray-500">
        No problems detected.
      </div>
    );
  }

  return (
    <div className="p-2">
      {all.map((row, i) => {
        const sev = SEVERITY_LABEL[row.diag.severity] ?? SEVERITY_LABEL[1];
        const shortFile = row.file.split("/").pop() ?? row.file;
        return (
          <button
            key={i}
            onClick={() => goto(row.file, row.diag)}
            className="flex w-full items-start gap-2 px-1 py-0.5 text-left text-xs hover:bg-[#2a2d2e]"
          >
            <span className={`shrink-0 font-semibold ${sev.cls}`}>{sev.label}</span>
            <span className="min-w-0 flex-1 truncate text-gray-300">{row.diag.message}</span>
            <span className="shrink-0 text-gray-500">
              [{shortFile}] ({row.diag.range.start.line},{row.diag.range.start.character})
            </span>
          </button>
        );
      })}
    </div>
  );
}
