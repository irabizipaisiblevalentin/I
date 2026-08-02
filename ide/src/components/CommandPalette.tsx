import { useEffect, useMemo, useRef, useState } from "react";
import { useIde } from "../store";

interface CommandPaletteProps {
  onClose: () => void;
  onRun: () => void;
  onDebug: () => void;
  onSave: () => void;
}

interface PaletteItem {
  label: string;
  detail?: string;
  run: () => void;
}

export default function CommandPalette({ onClose, onRun, onDebug, onSave }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const togglePanel = useIde((s) => s.togglePanel);
  const updateSettings = useIde((s) => s.updateSettings);
  const settings = useIde((s) => s.settings);
  const setSettingsOpen = useIde((s) => s.setSettingsOpen);
  const openDocs = useIde((s) => s.openDocs);

  const items = useMemo<PaletteItem[]>(() => {
    const docs: { label: string; detail: string; path: string }[] = [
      { label: "Docs: Language Guide", detail: "grammar, operators, built-ins", path: "docs/language-guide.md" },
      { label: "Docs: Getting Started", detail: "15-minute path", path: "docs/getting-started.md" },
      { label: "Docs: Standard Library", detail: "all 44 modules", path: "docs/stdlib-reference.md" },
      { label: "Docs: Language Specification", detail: "Version 1.0 LANGUAGE FREEZE", path: "docs/LANGUAGE_SPECIFICATION.md" },
      { label: "Docs: Error Reference", detail: "PARS/SEM/E-codes", path: "docs/error-reference.md" },
      { label: "Docs: Migration Guide", detail: "0.1.0 → 1.0.0", path: "docs/migration-guide.md" },
      { label: "Docs: FAQ", detail: "frequently asked questions", path: "docs/faq.md" },
    ];
    const base: PaletteItem[] = [
      { label: "Run active file", detail: "F5", run: onRun },
      { label: "Debug active file", detail: "", run: onDebug },
      { label: "Save active file", detail: "Ctrl+S", run: onSave },
      { label: "Toggle terminal", detail: "Ctrl+`", run: () => togglePanel("terminal") },
      { label: "Toggle output", detail: "", run: () => togglePanel("output") },
      { label: "Toggle problems", detail: "", run: () => togglePanel("problems") },
      { label: "Open settings", detail: "", run: () => setSettingsOpen(true) },
      ...(settings.theme === "dark"
        ? [{ label: "Switch to light theme", detail: "", run: () => updateSettings({ theme: "light" }) }]
        : [{ label: "Switch to dark theme", detail: "", run: () => updateSettings({ theme: "dark" }) }]),
      ...docs.map((d) => ({ label: d.label, detail: d.detail, run: () => openDocs(d.path) })),
    ];
    return base;
  }, [onRun, onDebug, onSave, togglePanel, setSettingsOpen, settings.theme, updateSettings, openDocs]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter(
      (i) => i.label.toLowerCase().includes(q) || (i.detail ?? "").toLowerCase().includes(q),
    );
  }, [items, query]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  const execute = (item: PaletteItem) => {
    onClose();
    item.run();
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && filtered[activeIndex]) {
      e.preventDefault();
      execute(filtered[activeIndex]);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[12vh]"
      onMouseDown={onClose}
    >
      <div
        className="w-[560px] overflow-hidden rounded-md border border-[#454545] bg-[#252526] shadow-2xl"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type a command…"
          className="w-full border-b border-[#454545] bg-transparent px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-500"
        />
        <div className="max-h-72 overflow-y-auto py-1">
          {filtered.length === 0 && (
            <div className="px-4 py-3 text-sm text-gray-500">No matching commands</div>
          )}
          {filtered.map((item, index) => (
            <button
              key={item.label}
              onClick={() => execute(item)}
              onMouseEnter={() => setActiveIndex(index)}
              className={`flex w-full items-center justify-between px-4 py-1.5 text-left text-sm ${
                index === activeIndex ? "bg-[#0e639c] text-white" : "text-gray-300"
              }`}
            >
              <span>{item.label}</span>
              {item.detail && <span className="text-xs text-gray-500">{item.detail}</span>}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
