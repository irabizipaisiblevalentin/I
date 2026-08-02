import { useIde, type PanelView } from "../store";
import Problems from "./panels/Problems";
import Output from "./panels/Output";
import TerminalPanel from "./panels/TerminalPanel";
import DebugPanel from "./panels/DebugPanel";

const TABS: { id: PanelView; label: string }[] = [
  { id: "problems", label: "Problems" },
  { id: "output", label: "Output" },
  { id: "terminal", label: "Terminal" },
  { id: "debug", label: "Debug" },
];

export default function BottomPanel() {
  const panel = useIde((s) => s.panel);
  const panelVisible = useIde((s) => s.panelVisible);
  const setPanel = useIde((s) => s.setPanel);
  const togglePanel = useIde((s) => s.togglePanel);
  const diagnostics = useIde((s) => s.diagnostics);

  const problemCount = Object.values(diagnostics).reduce(
    (sum, list) => sum + list.length,
    0,
  );

  if (!panelVisible) {
    return (
      <div className="flex h-6 shrink-0 items-center gap-1 border-t border-[#333] bg-[#1e1e1e] px-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => togglePanel(tab.id)}
            className="px-2 text-xs text-gray-400 hover:text-white"
          >
            {tab.label}
            {tab.id === "problems" && problemCount > 0 && (
              <span className="ml-1 rounded bg-red-500 px-1 text-[10px] text-white">
                {problemCount}
              </span>
            )}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="flex h-56 shrink-0 flex-col border-t border-[#333] bg-[#1e1e1e]">
      <div className="flex shrink-0 items-center border-b border-[#333] bg-[#252526]">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setPanel(tab.id)}
            className={`border-r border-[#333] px-3 py-1 text-xs ${
              panel === tab.id
                ? "bg-[#1e1e1e] text-white"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {tab.label}
            {tab.id === "problems" && problemCount > 0 && (
              <span className="ml-1 rounded bg-red-500 px-1 text-[10px] text-white">
                {problemCount}
              </span>
            )}
          </button>
        ))}
        <div className="flex-1" />
        <button
          onClick={() => togglePanel(panel)}
          className="px-3 py-1 text-xs text-gray-400 hover:text-white"
        >
          ▾
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-auto">
        {panel === "problems" && <Problems />}
        {panel === "output" && <Output />}
        {panel === "terminal" && <TerminalPanel />}
        {panel === "debug" && <DebugPanel />}
      </div>
    </div>
  );
}
