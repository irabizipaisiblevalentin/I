import { create } from "zustand";
import { api } from "./api";
import type {
  DebugStopped,
  Diagnostic,
  ExtensionInfo,
  FileNode,
  GitLogEntry,
  GitStatus,
  PackageResult,
  ProjectInfo,
  TemplateInfo,
} from "./types";
import {
  applyDocumentTheme,
  loadSettings,
  saveSettings,
  type IdeSettings,
} from "./settings";

export type SidebarView = "explorer" | "git" | "packages" | "debug" | "docs" | "extensions";
export type PanelView = "problems" | "output" | "terminal" | "debug";

interface IdeState {
  project: ProjectInfo | null;
  templates: TemplateInfo[];
  tree: FileNode[];
  openFiles: string[];
  activeFile: string | null;
  content: Record<string, string>;
  diagnostics: Record<string, Diagnostic[]>;
  sidebar: SidebarView;
  panel: PanelView;
  panelVisible: boolean;
  gitStatus: GitStatus | null;
  gitLog: GitLogEntry[];
  packages: PackageResult[];
  installed: PackageResult[];
  extensions: ExtensionInfo[];
  marketplace: ExtensionInfo[];
  runOutput: string;
  runRunning: boolean;
  runExit: { ok: boolean; code: number } | null;
  debugRunning: boolean;
  debugStopped: DebugStopped | null;
  debugEnded: boolean;
  debugOutput: string;
  breakpoints: Record<string, number[]>;
  cursor: { line: number; column: number };
  settings: IdeSettings;
  paletteOpen: boolean;
  settingsOpen: boolean;
  docsPath: string | null;

  loadTemplates: () => Promise<void>;
  createProject: (name: string, template: string) => Promise<ProjectInfo>;
  importAsProject: (name: string, files: Record<string, string>) => Promise<ProjectInfo>;
  importAsProjectFromFolder: (source: string) => Promise<ProjectInfo>;
  importIntoProject: (files: Record<string, string>) => Promise<void>;
  importIntoProjectFromFolder: (source: string) => Promise<void>;
  openProject: (path: string) => Promise<ProjectInfo>;
  loadTree: () => Promise<void>;
  openFile: (path: string) => Promise<void>;
  closeFile: (path: string) => void;
  setActiveFile: (path: string) => void;
  setContent: (path: string, value: string) => void;
  saveFile: (path: string) => Promise<void>;
  createFile: (path: string) => Promise<void>;
  setDiagnostics: (path: string, diags: Diagnostic[]) => void;
  analyzeFile: (path: string) => Promise<void>;
  setSidebar: (v: SidebarView) => void;
  setPanel: (v: PanelView) => void;
  togglePanel: (v: PanelView) => void;
  showPanel: (v: PanelView) => void;
  refreshGit: () => Promise<void>;
  gitCommit: (message: string) => Promise<void>;
  gitInit: () => Promise<void>;
  searchPackages: (q: string) => Promise<void>;
  installPackage: (name: string, version?: string) => Promise<void>;
  uninstallPackage: (name: string) => Promise<void>;
  refreshExtensions: () => Promise<void>;
  browseExtensions: (q: string) => Promise<void>;
  installExtension: (name: string, version?: string) => Promise<void>;
  uninstallExtension: (name: string) => Promise<void>;
  appendRun: (text: string) => void;
  setRunRunning: (running: boolean) => void;
  setRunExit: (exit: { ok: boolean; code: number } | null) => void;
  clearRun: () => void;
  setDebugRunning: (v: boolean) => void;
  setDebugStopped: (s: DebugStopped | null) => void;
  setDebugEnded: (v: boolean) => void;
  appendDebugOutput: (text: string) => void;
  toggleBreakpoint: (file: string, line: number) => void;
  setBreakpoints: (file: string, lines: number[]) => void;
  setCursor: (line: number, column: number) => void;
  updateSettings: (patch: Partial<IdeSettings>) => void;
  togglePalette: () => void;
  setPaletteOpen: (open: boolean) => void;
  setSettingsOpen: (open: boolean) => void;
  openDocs: (path: string) => void;
  importDroppedFile: (name: string, content: string) => Promise<string | null>;
}

export const useIde = create<IdeState>((set, get) => ({
  project: null,
  templates: [],
  tree: [],
  openFiles: [],
  activeFile: null,
  content: {},
  diagnostics: {},
  sidebar: "explorer",
  panel: "output",
  panelVisible: false,
  gitStatus: null,
  gitLog: [],
  packages: [],
  installed: [],
  extensions: [],
  marketplace: [],
  runOutput: "",
  runRunning: false,
  runExit: null,
  debugRunning: false,
  debugStopped: null,
  debugEnded: false,
  debugOutput: "",
  breakpoints: {},
  cursor: { line: 1, column: 1 },
  settings: loadSettings(),
  paletteOpen: false,
  settingsOpen: false,
  docsPath: null,

  loadTemplates: async () => {
    const data = await api<{ key: string; name: string; description: string; category: string }[]>("/api/templates");
    set({ templates: data });
  },

  createProject: async (name, template) => {
    const project = await api<ProjectInfo>("/api/projects/create", {
      method: "POST",
      body: { name, template },
    });
    set({ project, openFiles: [], activeFile: null, content: {}, runOutput: "" });
    await get().loadTree();
    await get().openFile("src/main.i");
    return project;
  },

  importAsProject: async (name, files) => {
    const project = await api<ProjectInfo>("/api/projects/import", {
      method: "POST",
      body: { name, files },
    });
    set({ project, openFiles: [], activeFile: null, content: {}, runOutput: "" });
    await get().loadTree();
    const first = Object.keys(files)[0];
    if (first) await get().openFile(first);
    return project;
  },

  importAsProjectFromFolder: async (source) => {
    const raw = source.split(/[\\/]/).filter(Boolean).pop() ?? "imported-project";
    const name = raw.replace(/[^a-zA-Z0-9_-]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "") || "imported-project";
    const project = await api<ProjectInfo>("/api/projects/import", {
      method: "POST",
      body: { name, source },
    });
    set({ project, openFiles: [], activeFile: null, content: {}, runOutput: "" });
    await get().loadTree();
    return project;
  },

  importIntoProject: async (files) => {
    const project = get().project;
    if (!project) return;
    await api<{ ok: boolean }>("/api/project/import", {
      method: "POST",
      body: { root: project.path, files },
    });
    set({ openFiles: [], activeFile: null, content: {}, runOutput: "" });
    await get().loadTree();
    const first = Object.keys(files)[0];
    if (first) await get().openFile(first);
  },

  importIntoProjectFromFolder: async (source) => {
    const project = get().project;
    if (!project) return;
    await api<{ ok: boolean }>("/api/project/import", {
      method: "POST",
      body: { root: project.path, source },
    });
    set({ openFiles: [], activeFile: null, content: {}, runOutput: "" });
    await get().loadTree();
  },

  openProject: async (path) => {
    const project = await api<ProjectInfo>("/api/projects/open", {
      method: "POST",
      body: { path },
    });
    set({ project, openFiles: [], activeFile: null, content: {}, runOutput: "" });
    await get().loadTree();
    try {
      await get().openFile("src/main.i");
    } catch {
      // no main file; leave explorer open
    }
    return project;
  },

  loadTree: async () => {
    const project = get().project;
    if (!project) return;
    const data = await api<{ root: string; tree: FileNode[] }>(
      `/api/project/tree?root=${encodeURIComponent(project.path)}`,
    );
    set({ tree: data.tree });
  },

  openFile: async (path) => {
    const project = get().project;
    if (!project) return;
    const cached = get().content[path];
    let text = cached ?? "";
    if (cached === undefined) {
      const data = await api<{ content: string }>(
        `/api/project/file?root=${encodeURIComponent(project.path)}&path=${encodeURIComponent(path)}`,
      );
      text = data.content;
    }
    set((s) => ({
      content: { ...s.content, [path]: text },
      openFiles: s.openFiles.includes(path) ? s.openFiles : [...s.openFiles, path],
      activeFile: path,
    }));
    if (cached === undefined) void get().analyzeFile(path);
  },

  closeFile: (path) => {
    set((s) => {
      const openFiles = s.openFiles.filter((p) => p !== path);
      const activeFile =
        s.activeFile === path
          ? (openFiles[openFiles.length - 1] ?? null)
          : s.activeFile;
      return { openFiles, activeFile };
    });
  },

  setActiveFile: (path) => {
    set({ activeFile: path });
  },

  setContent: (path, value) => {
    set((s) => ({ content: { ...s.content, [path]: value } }));
    void get().analyzeFile(path);
  },

  saveFile: async (path) => {
    const project = get().project;
    if (!project) return;
    const value = get().content[path] ?? "";
    await api<{ ok: boolean }>("/api/project/file", {
      method: "POST",
      body: { root: project.path, path, content: value },
    });
    await get().analyzeFile(path);
  },

  createFile: async (path) => {
    await get().saveFile(path);
    await get().loadTree();
    await get().openFile(path);
  },

  setDiagnostics: (path, diags) => {
    set((s) => ({ diagnostics: { ...s.diagnostics, [path]: diags } }));
  },

  analyzeFile: async (path: string) => {
    const project = get().project;
    if (!project) return;
    const value = get().content[path] ?? "";
    try {
      const data = await api<{ diagnostics: Diagnostic[] }>("/api/diagnostics", {
        method: "POST",
        body: { content: value, filename: path },
      });
      get().setDiagnostics(path, data.diagnostics);
    } catch {
      get().setDiagnostics(path, []);
    }
  },

  setSidebar: (v) => set({ sidebar: v }),
  setPanel: (v) => set({ panel: v }),
  togglePanel: (v) =>
    set((s) => ({
      panel: v,
      panelVisible: s.panel === v ? !s.panelVisible : true,
    })),
  showPanel: (v) => set({ panel: v, panelVisible: true }),

  refreshGit: async () => {
    const project = get().project;
    if (!project) return;
    try {
      const status = await api<GitStatus>(
        `/api/project/git/status?root=${encodeURIComponent(project.path)}`,
      );
      const log = await api<{ log: GitLogEntry[] }>(
        `/api/project/git/log?root=${encodeURIComponent(project.path)}`,
      );
      set({ gitStatus: status, gitLog: log.log });
    } catch {
      set({ gitStatus: null, gitLog: [] });
    }
  },

  gitCommit: async (message) => {
    const project = get().project;
    if (!project) return;
    await api<{ ok: boolean }>("/api/project/git/commit", {
      method: "POST",
      body: { root: project.path, message },
    });
    await get().refreshGit();
  },

  gitInit: async () => {
    const project = get().project;
    if (!project) return;
    await api<{ ok: boolean }>("/api/project/git/init", {
      method: "POST",
      body: { root: project.path },
    });
    await get().refreshGit();
  },

  searchPackages: async (q) => {
    const data = await api<PackageResult[]>(`/api/packages/search?q=${encodeURIComponent(q)}`);
    set({ packages: data });
  },

  installPackage: async (name, version) => {
    const project = get().project;
    if (!project) return;
    await api<{ ok: boolean }>("/api/project/install", {
      method: "POST",
      body: { root: project.path, name, version },
    });
  },

  uninstallPackage: async (name) => {
    const project = get().project;
    if (!project) return;
    await api<{ ok: boolean }>("/api/project/uninstall", {
      method: "POST",
      body: { root: project.path, name },
    });
  },

  refreshExtensions: async () => {
    const data = await api<{ extensions: ExtensionInfo[] }>("/api/extensions");
    set({ extensions: data.extensions });
  },

  browseExtensions: async (q) => {
    const data = await api<{ extensions: ExtensionInfo[] }>(
      `/api/extensions/browse?q=${encodeURIComponent(q)}`,
    );
    set({ marketplace: data.extensions });
  },

  installExtension: async (name, version) => {
    await api<ExtensionInfo>("/api/extensions/install", {
      method: "POST",
      body: { name, version },
    });
    await get().refreshExtensions();
    await get().browseExtensions("");
  },

  uninstallExtension: async (name) => {
    await api<{ ok: boolean }>("/api/extensions/uninstall", {
      method: "POST",
      body: { name },
    });
    await get().refreshExtensions();
    await get().browseExtensions("");
  },

  appendRun: (text) => set((s) => ({ runOutput: s.runOutput + text })),
  setRunRunning: (runRunning) => set({ runRunning }),
  setRunExit: (runExit) => set({ runExit }),
  clearRun: () => set({ runOutput: "", runExit: null }),

  setDebugRunning: (debugRunning) => set({ debugRunning }),
  setDebugStopped: (debugStopped) => set({ debugStopped }),
  setDebugEnded: (debugEnded) => set({ debugEnded }),
  appendDebugOutput: (text) => set((s) => ({ debugOutput: s.debugOutput + text })),

  toggleBreakpoint: (file, line) => {
    set((s) => {
      const current = s.breakpoints[file] ?? [];
      const next = current.includes(line)
        ? current.filter((l) => l !== line)
        : [...current, line].sort((a, b) => a - b);
      return { breakpoints: { ...s.breakpoints, [file]: next } };
    });
  },
  setBreakpoints: (file, lines) => {
    set((s) => ({ breakpoints: { ...s.breakpoints, [file]: lines } }));
  },
  setCursor: (line, column) => set({ cursor: { line, column } }),

  updateSettings: (patch) =>
    set((s) => {
      const settings = { ...s.settings, ...patch };
      saveSettings(settings);
      applyDocumentTheme(settings.theme);
      return { settings };
    }),
  togglePalette: () => set((s) => ({ paletteOpen: !s.paletteOpen })),
  setPaletteOpen: (paletteOpen) => set({ paletteOpen }),
  setSettingsOpen: (settingsOpen) => set({ settingsOpen }),
  openDocs: (docsPath) => set({ docsPath, sidebar: "docs" }),
  importDroppedFile: async (name, content) => {
    const project = get().project;
    if (!project) return null;
    const safe = name.replace(/\\/g, "/").split("/").pop() ?? name;
    const rel = safe.replace(/^[^a-zA-Z0-9._-]+/, "");
    if (!rel) return null;
    await api<{ ok: boolean }>("/api/project/file", {
      method: "POST",
      body: { root: project.path, path: rel, content },
    });
    await get().openFile(rel);
    return rel;
  },
}));
