import { useEffect, useState } from "react";
import { useIde } from "../store";

export default function GitPanel() {
  const gitStatus = useIde((s) => s.gitStatus);
  const gitLog = useIde((s) => s.gitLog);
  const refreshGit = useIde((s) => s.refreshGit);
  const gitCommit = useIde((s) => s.gitCommit);
  const gitInit = useIde((s) => s.gitInit);
  const [message, setMessage] = useState("");

  useEffect(() => {
    void refreshGit();
  }, [refreshGit]);

  const commit = () => {
    if (!message.trim()) return;
    void gitCommit(message.trim());
    setMessage("");
  };

  if (!gitStatus?.is_repo) {
    return (
      <div className="p-3">
        <p className="mb-2 text-xs text-gray-400">This project is not a Git repository.</p>
        <button
          onClick={() => void gitInit()}
          className="rounded bg-[#0e639c] px-3 py-1 text-xs text-white hover:bg-[#1177bb]"
        >
          Initialize Repository
        </button>
      </div>
    );
  }

  const changes = [...gitStatus.staged, ...gitStatus.changed];
  return (
    <div className="p-2">
      <div className="mb-2 flex items-center justify-between px-1">
        <span className="text-xs font-semibold text-gray-300">SOURCE CONTROL</span>
        <button
          onClick={() => void refreshGit()}
          className="text-xs text-gray-400 hover:text-white"
        >
          ↻
        </button>
      </div>
      <div className="mb-2 flex gap-1">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") commit();
          }}
          placeholder="Commit message"
          className="min-w-0 flex-1 rounded border border-[#3c3c3c] bg-[#1e1e1e] px-2 py-1 text-xs text-gray-200 outline-none focus:border-blue-500"
        />
        <button
          onClick={commit}
          disabled={!message.trim()}
          className="rounded bg-[#0e639c] px-2 text-xs text-white disabled:opacity-40"
        >
          ✓
        </button>
      </div>
      <p className="mb-1 px-1 text-[11px] text-gray-500">
        {gitStatus.branch || "detached"} · {changes.length} change{changes.length === 1 ? "" : "s"}
      </p>
      <div className="mb-3 space-y-0.5">
        {changes.map((c) => (
          <div
            key={c.path + c.code}
            className="flex items-center gap-2 px-1 text-xs text-gray-300"
          >
            <span className="w-5 text-[10px] text-gray-500">{c.code.trim()}</span>
            <span className="truncate">{c.path}</span>
          </div>
        ))}
        {changes.length === 0 && (
          <p className="px-1 text-xs text-gray-500">No changes.</p>
        )}
      </div>
      <span className="text-[11px] font-semibold uppercase text-gray-400">Recent</span>
      <div className="mt-1 space-y-0.5">
        {gitLog.map((entry) => (
          <div key={entry.hash} className="px-1 text-xs text-gray-400">
            <span className="text-gray-500">{entry.hash}</span> {entry.message}
          </div>
        ))}
        {gitLog.length === 0 && <p className="px-1 text-xs text-gray-500">No commits yet.</p>}
      </div>
    </div>
  );
}
