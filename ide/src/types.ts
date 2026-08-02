export interface ProjectInfo {
  name: string;
  path: string;
  template: string;
  description: string;
}

export interface TemplateInfo {
  key: string;
  name: string;
  description: string;
  category: string;
}

export interface FileNode {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
}

export interface Position {
  line: number;
  character: number;
}

export interface Diagnostic {
  range: { start: Position; end: Position };
  severity: number;
  message: string;
  source: string;
  code: string;
}

export interface CompletionItem {
  label: string;
  kind: number;
  detail?: string;
  documentation?: string;
  insertText?: string;
}

export interface SymbolInfo {
  name: string;
  kind: number;
  range: { start: Position; end: Position };
  selectionRange: { start: Position; end: Position };
}

export interface GitStatus {
  is_repo: boolean;
  branch: string;
  changed: { path: string; code: string }[];
  staged: { path: string; code: string }[];
}

export interface GitLogEntry {
  hash: string;
  author: string;
  message: string;
}

export interface PackageResult {
  name: string;
  version?: string;
  description?: string;
}

export interface ExtensionInfo {
  name: string;
  version: string;
  description?: string;
  author?: string;
  path?: string;
  installed?: boolean;
}

export interface RunEvent {
  event: "output" | "done" | "error";
  data: unknown;
}

export interface DebugStopped {
  line: number;
  function: string;
  globals: Record<string, string>;
  stack_top: string[];
  breakpoints: number[];
}

export interface DebugEvent {
  event: "started" | "stopped" | "ended" | "error" | "breakpoints";
  data: unknown;
}
