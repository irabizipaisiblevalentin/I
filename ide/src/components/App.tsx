import { useEffect, useState } from "react";
import { useIde } from "../store";
import { applyDocumentTheme } from "../settings";
import { runActiveFile, debugActiveFile } from "../commands";
import { api } from "../api";
import ActivityBar from "./ActivityBar";
import SideBar from "./SideBar";
import EditorArea from "./EditorArea";
import BottomPanel from "./BottomPanel";
import StatusBar from "./StatusBar";
import Welcome from "./Welcome";
import CommandPalette from "./CommandPalette";
import SettingsPane from "./SettingsPane";
import { updateBreakpointDecorations } from "./MonacoEditor";

export default function App() {
  const project = useIde((s) => s.project);
  const loadTemplates = useIde((s) => s.loadTemplates);
  const settings = useIde((s) => s.settings);
  const paletteOpen = useIde((s) => s.paletteOpen);
  const togglePalette = useIde((s) => s.togglePalette);
  const setPaletteOpen = useIde((s) => s.setPaletteOpen);
  const settingsOpen = useIde((s) => s.settingsOpen);
  const setSettingsOpen = useIde((s) => s.setSettingsOpen);
  const togglePanel = useIde((s) => s.togglePanel);
  const saveFile = useIde((s) => s.saveFile);

  useEffect(() => {
    applyDocumentTheme(settings.theme);
  }, [settings.theme]);

  useEffect(() => {
    void loadTemplates();
    void (async () => {
      const state = useIde.getState();
      if (state.project) return;
      try {
        const current = await api<{ name: string; path: string } | null>(
          "/api/projects/current",
        );
        if (current) await useIde.getState().openProject(current.path);
      } catch {
        // no project to restore
      }
    })();
  }, [loadTemplates]);

  const [dropActive, setDropActive] = useState(false);

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
    if (!dropActive) setDropActive(true);
  };

  const onDragLeave = (e: React.DragEvent) => {
    if (e.currentTarget.contains(e.relatedTarget as Node)) return;
    setDropActive(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDropActive(false);
    const files = Array.from(e.dataTransfer.files ?? []);
    if (files.length === 0) return;
    const state = useIde.getState();
    if (!state.project) return;
    void Promise.all(
      files.map((f) => f.text().then((text) => state.importDroppedFile(f.name, text))),
    );
  };

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;
      const tag = (e.target as HTMLElement | null)?.tagName;

      if (mod && e.shiftKey && e.key.toLowerCase() === "p") {
        e.preventDefault();
        togglePalette();
        return;
      }
      if (e.key === "Escape") {
        if (useIde.getState().paletteOpen) setPaletteOpen(false);
        else if (useIde.getState().settingsOpen) setSettingsOpen(false);
        return;
      }
      if (tag === "INPUT" || tag === "TEXTAREA") return;

      if (mod && e.key.toLowerCase() === "s") {
        e.preventDefault();
        const active = useIde.getState().activeFile;
        if (active) void saveFile(active);
        return;
      }
      if (mod && e.key === "`") {
        e.preventDefault();
        togglePanel("terminal");
        return;
      }
      if (e.key === "F5") {
        e.preventDefault();
        void runActiveFile();
        return;
      }
      if (e.key === "F9") {
        e.preventDefault();
        const active = useIde.getState().activeFile;
        const cursor = useIde.getState().cursor;
        if (active) {
          useIde.getState().toggleBreakpoint(active, cursor.line);
          updateBreakpointDecorations(active);
        }
        return;
      }
      if (e.key === "F1") {
        e.preventDefault();
        togglePalette();
        return;
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [togglePalette, setPaletteOpen, setSettingsOpen, togglePanel, saveFile]);

  if (!project) {
    return (
      <div
        className="relative h-full bg-[#1e1e1e] text-gray-200"
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <Welcome />
        {dropActive && <DropOverlay />}
      </div>
    );
  }

  return (
    <div
      className="relative flex h-full flex-col bg-[#1e1e1e] text-gray-200"
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <div className="flex min-h-0 flex-1">
        <ActivityBar />
        <SideBar />
        <div className="flex min-w-0 flex-1 flex-col">
          <EditorArea />
          <BottomPanel />
        </div>
      </div>
      <StatusBar />
      {dropActive && <DropOverlay />}
      {paletteOpen && (
        <CommandPalette
          onClose={() => setPaletteOpen(false)}
          onRun={() => void runActiveFile()}
          onDebug={() => void debugActiveFile()}
          onSave={() => {
            const active = useIde.getState().activeFile;
            if (active) void saveFile(active);
          }}
        />
      )}
      {settingsOpen && <SettingsPane onClose={() => setSettingsOpen(false)} />}
    </div>
  );
}

function DropOverlay() {
  return (
    <div className="pointer-events-none absolute inset-0 z-40 flex items-center justify-center border-2 border-dashed border-[#0e639c] bg-[#0e639c]/10">
      <p className="rounded bg-[#252526] px-4 py-2 text-sm text-gray-100 shadow">
        Drop files into the project
      </p>
    </div>
  );
}
