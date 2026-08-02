import { useEffect } from "react";
import { useIde } from "../store";

export default function StatusBar() {
  const project = useIde((s) => s.project);
  const cursor = useIde((s) => s.cursor);
  const refreshGit = useIde((s) => s.refreshGit);
  const settings = useIde((s) => s.settings);
  const updateSettings = useIde((s) => s.updateSettings);

  useEffect(() => {
    if (project) void refreshGit();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project?.path]);

  const branch =
    useIde((s) => s.gitStatus)?.branch ??
    (project ? "no repository" : "no project");

  return (
    <footer className="flex h-6 shrink-0 items-center gap-3 border-t border-[#333] bg-[#0e639c] px-2 text-[11px] text-white">
      <span className="flex items-center gap-1">
        <span className="inline-block h-2 w-2 rounded-full bg-green-300" />
        I Studio
      </span>
      <span>⎇ {branch}</span>
      <div className="flex-1" />
      <span>
        Ln {cursor.line}, Col {cursor.column}
      </span>
      <span>Spaces: {settings.tabSize}</span>
      <select
        value={settings.theme}
        onChange={(e) =>
          updateSettings({ theme: e.target.value as "dark" | "light" })
        }
        title="Theme"
        className="cursor-pointer rounded border border-white/20 bg-transparent px-1 text-white outline-none [&>option]:bg-[#252526]"
      >
        <option value="dark">Dark</option>
        <option value="light">Light</option>
      </select>
      <span>I Language</span>
    </footer>
  );
}
