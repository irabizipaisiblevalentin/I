import { useIde, type SidebarView } from "../store";

const ITEMS: { id: SidebarView; icon: string; label: string }[] = [
  { id: "explorer", icon: "📁", label: "Explorer" },
  { id: "docs", icon: "📖", label: "Documentation" },
  { id: "git", icon: "🌿", label: "Source Control" },
  { id: "packages", icon: "📦", label: "Packages" },
  { id: "extensions", icon: "🧩", label: "Extensions" },
  { id: "debug", icon: "🐞", label: "Run & Debug" },
];

export default function ActivityBar() {
  const sidebar = useIde((s) => s.sidebar);
  const setSidebar = useIde((s) => s.setSidebar);
  const panelVisible = useIde((s) => s.panelVisible);
  const togglePanel = useIde((s) => s.togglePanel);
  const setSettingsOpen = useIde((s) => s.setSettingsOpen);
  const togglePalette = useIde((s) => s.togglePalette);

  return (
    <div className="flex w-12 shrink-0 flex-col items-center border-r border-[#333] bg-[#252526] py-2">
      {ITEMS.map((item) => (
        <button
          key={item.id}
          title={item.label}
          onClick={() => setSidebar(item.id)}
          className={`mb-1 flex h-10 w-10 items-center justify-center rounded text-lg transition-colors ${
            sidebar === item.id
              ? "border-l-2 border-blue-400 bg-[#37373d] text-white"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <span aria-hidden>{item.icon}</span>
        </button>
      ))}
      <div className="flex-1" />
      <button
        title="Command Palette (Ctrl+Shift+P)"
        onClick={() => togglePalette()}
        className="flex h-10 w-10 items-center justify-center rounded text-lg text-gray-400 hover:text-white"
      >
        <span aria-hidden>⌘</span>
      </button>
      <button
        title="Settings"
        onClick={() => setSettingsOpen(true)}
        className="flex h-10 w-10 items-center justify-center rounded text-lg text-gray-400 hover:text-white"
      >
        <span aria-hidden>⚙️</span>
      </button>
      <button
        title="Output"
        onClick={() => togglePanel("output")}
        className={`flex h-10 w-10 items-center justify-center rounded text-lg ${
          panelVisible ? "text-white" : "text-gray-400 hover:text-white"
        }`}
      >
        <span aria-hidden>⏳</span>
      </button>
    </div>
  );
}
