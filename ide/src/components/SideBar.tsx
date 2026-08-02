import { useIde } from "../store";
import Explorer from "./Explorer";
import ExtensionsPanel from "./ExtensionsPanel";
import GitPanel from "./GitPanel";
import PackagesPanel from "./PackagesPanel";
import DebugSidebar from "./DebugSidebar";
import DocsView from "./DocsView";

export default function SideBar() {
  const sidebar = useIde((s) => s.sidebar);
  const project = useIde((s) => s.project);

  return (
    <div className="flex w-64 shrink-0 flex-col border-r border-[#333] bg-[#252526]">
      <div className="border-b border-[#333] px-3 py-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
        {project?.name ?? "I Studio"}
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        {sidebar === "explorer" && <Explorer />}
        {sidebar === "git" && <GitPanel />}
        {sidebar === "packages" && <PackagesPanel />}
        {sidebar === "debug" && <DebugSidebar />}
        {sidebar === "docs" && <DocsView />}
        {sidebar === "extensions" && <ExtensionsPanel />}
      </div>
    </div>
  );
}
