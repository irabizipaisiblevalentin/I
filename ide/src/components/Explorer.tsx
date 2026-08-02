import { useRef, useState } from "react";
import { useIde } from "../store";
import { isDesktop, pickFolderForImport } from "../desktop";
import type { FileNode } from "../types";
import { readFolderFiles } from "../upload";

function FileTree({ node }: { node: FileNode }) {
  const openFile = useIde((s) => s.openFile);
  const [collapsed, setCollapsed] = useState(false);

  if (node.type === "file") {
    return (
      <button
        onClick={() => void openFile(node.path)}
        title={node.path}
        className="flex w-full items-center gap-2 px-2 py-1 text-left text-[13px] text-gray-300 hover:bg-[#2a2d2e]"
      >
        <span className="text-xs">📄</span>
        <span className="truncate">{node.name}</span>
      </button>
    );
  }

  return (
    <div>
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="flex w-full items-center gap-1 px-1 py-1 text-left text-[13px] font-medium text-gray-200 hover:bg-[#2a2d2e]"
      >
        <span className="text-xs">{collapsed ? "▸" : "▾"}</span>
        <span className="text-xs">📁</span>
        <span>{node.name}</span>
      </button>
      {!collapsed && (
        <div className="ml-3 border-l border-[#333] pl-1">
          {(node.children ?? []).map((child) => (
            <FileTree key={child.path} node={child} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Explorer() {
  const tree = useIde((s) => s.tree);
  const loadTree = useIde((s) => s.loadTree);
  const createFile = useIde((s) => s.createFile);
  const importIntoProject = useIde((s) => s.importIntoProject);
  const importIntoProjectFromFolder = useIde((s) => s.importIntoProjectFromFolder);
  const project = useIde((s) => s.project);
  const [newName, setNewName] = useState("");
  const [importing, setImporting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleCreate = () => {
    const name = newName.trim();
    if (!name || !project) return;
    void createFile(name.startsWith("src/") ? name : `src/${name}`);
    setNewName("");
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setImporting(true);
    try {
      const map = await readFolderFiles(files);
      await importIntoProject(map);
    } finally {
      setImporting(false);
      e.target.value = "";
    }
  };

  const startImport = async () => {
    setImporting(true);
    try {
      if (isDesktop()) {
        const source = await pickFolderForImport();
        if (source) await importIntoProjectFromFolder(source);
      } else {
        inputRef.current?.click();
      }
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="p-2">
      <div className="mb-2 flex items-center justify-between px-1">
        <span className="text-xs font-semibold text-gray-300">EXPLORER</span>
        <div className="flex items-center gap-1">
          <button
            title="Import folder (replaces project files)"
            onClick={() => void startImport()}
            disabled={importing}
            className="text-xs text-gray-400 hover:text-white disabled:opacity-40"
          >
            {importing ? "…" : "⬆"}
          </button>
          <button
            title="Refresh"
            onClick={() => void loadTree()}
            className="text-xs text-gray-400 hover:text-white"
          >
            ↻
          </button>
        </div>
      </div>
      <input
        ref={inputRef}
        type="file"
        webkitdirectory
        multiple
        className="hidden"
        onChange={(e) => void handleImport(e)}
      />
      <button
        onClick={() => void startImport()}
        disabled={importing}
        className="mb-2 w-full rounded border border-[#3c3c3c] bg-[#252526] px-2 py-1 text-xs text-gray-300 hover:border-[#0e639c] hover:text-white disabled:opacity-40"
      >
        {importing ? "Importing folder…" : "Import Folder…"}
      </button>
      <div className="mb-2 flex gap-1">
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleCreate();
          }}
          placeholder="new file (src/…)"
          className="min-w-0 flex-1 rounded border border-[#3c3c3c] bg-[#1e1e1e] px-2 py-1 text-xs text-gray-200 outline-none focus:border-blue-500"
        />
        <button
          onClick={handleCreate}
          className="rounded bg-[#3c3c3c] px-2 text-xs text-gray-200 hover:bg-[#4c4c4c]"
        >
          +
        </button>
      </div>
      <div className="space-y-0.5">
        {tree.map((node) => (
          <FileTree key={node.path} node={node} />
        ))}
      </div>
    </div>
  );
}
