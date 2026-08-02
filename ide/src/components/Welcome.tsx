import { useRef, useState, type FormEvent } from "react";
import { useIde } from "../store";
import { isDesktop, pickAndOpenFolder, pickFolderForImport } from "../desktop";
import type { ProjectInfo, TemplateInfo } from "../types";
import { readFolderFiles } from "../upload";

export default function Welcome() {
  const templates = useIde((s) => s.templates);
  const createProject = useIde((s) => s.createProject);
  const importAsProject = useIde((s) => s.importAsProject);
  const importAsProjectFromFolder = useIde((s) => s.importAsProjectFromFolder);
  const openProject = useIde((s) => s.openProject);
  const [name, setName] = useState("");
  const [template, setTemplate] = useState<string | null>(null);
  const [openPath, setOpenPath] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const folderRef = useRef<HTMLInputElement>(null);

  const recent = JSON.parse(localStorage.getItem("istudio.recent") ?? "[]") as string[];

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !template) return;
    setBusy(true);
    setError(null);
    try {
      const created = await createProject(name.trim(), template);
      addRecent(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const open = async (path: string) => {
    setBusy(true);
    setError(null);
    try {
      const proj = await openProject(path);
      addRecent(proj);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const addRecent = (proj: ProjectInfo) => {
    const next = [
      proj.path,
      ...recent.filter((p: string) => p !== proj.path),
    ].slice(0, 5);
    localStorage.setItem("istudio.recent", JSON.stringify(next));
  };

  const browse = async () => {
    setBusy(true);
    setError(null);
    try {
      const picked = await pickAndOpenFolder();
      if (picked) {
        const proj = await openProject(picked);
        addRecent(proj);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const importFolder = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      const map = await readFolderFiles(files);
      const first = files[0] as File & { webkitRelativePath?: string };
      const rootName =
        (first.webkitRelativePath ?? "").split("/")[0] ||
        first.name.replace(/\.[^.]+$/, "") ||
        "imported-project";
      const safe = rootName.replace(/[^a-zA-Z0-9_-]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
      const proj = await importAsProject(safe || "imported-project", map);
      addRecent(proj);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  };

  const startFolderImport = async () => {
    setBusy(true);
    setError(null);
    try {
      if (isDesktop()) {
        const source = await pickFolderForImport();
        if (source) {
          const proj = await importAsProjectFromFolder(source);
          addRecent(proj);
        }
      } else {
        folderRef.current?.click();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col items-center overflow-auto bg-[#1e1e1e] text-white">
      <div className="mt-16 w-full max-w-3xl px-6">
        <div className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="I Studio IDE logo"
            className="h-12 w-12 rounded object-cover"
          />
          <h1 className="text-2xl font-semibold">
            I <span className="text-[#0e639c]">Studio</span> IDE
          </h1>
        </div>
        <p className="mt-1 text-sm text-gray-400">
          Start a new project or open an existing one.
        </p>

        {error && (
          <p className="mt-3 rounded bg-red-900/40 px-3 py-2 text-xs text-red-300">
            {error}
          </p>
        )}

        <section className="mt-8">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-400">
            New project
          </h2>
          <form onSubmit={submit} className="space-y-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Project name"
              className="w-full max-w-sm rounded border border-[#333] bg-[#252526] px-3 py-2 text-sm outline-none focus:border-[#0e639c]"
            />
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
              {templates.map((t: TemplateInfo) => (
                <button
                  key={t.key}
                  type="button"
                  onClick={() => setTemplate(t.key)}
                  className={`rounded border p-3 text-left transition ${
                    template === t.key
                      ? "border-[#0e639c] bg-[#0e639c]/20"
                      : "border-[#333] bg-[#252526] hover:border-[#555]"
                  }`}
                >
                  <span className="text-sm font-semibold">{t.name}</span>
                  <span className="mt-1 block text-[11px] text-gray-400">
                    {t.description}
                  </span>
                  <span className="mt-1 block text-[10px] uppercase text-gray-500">
                    {t.category}
                  </span>
                </button>
              ))}
            </div>
            <button
              type="submit"
              disabled={!name.trim() || !template || busy}
              className="rounded bg-[#0e639c] px-4 py-2 text-sm text-white hover:bg-[#1177bb] disabled:opacity-40"
            >
              {busy ? "Creating…" : "Create project"}
            </button>
          </form>
        </section>

        <section className="mt-6">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-400">
            Import
          </h2>
          <input
            ref={folderRef}
            type="file"
            webkitdirectory
            multiple
            className="hidden"
            onChange={(e) => void importFolder(e)}
          />
          <button
            onClick={() => void startFolderImport()}
            disabled={busy}
            className="rounded bg-[#3c3c3c] px-4 py-2 text-sm text-white hover:bg-[#4c4c4c] disabled:opacity-40"
          >
            {busy ? "Importing…" : "Import Folder as Project…"}
          </button>
          <p className="mt-1 text-[11px] text-gray-500">
            Creates a new project from the selected folder — no template files added.
          </p>
        </section>

        <section className="mt-8 pb-16">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-400">
            Recent
          </h2>
          {recent.length === 0 ? (
            <p className="text-sm text-gray-500">No recent projects.</p>
          ) : (
            <ul className="space-y-1">
              {recent.map((path: string) => (
                <li key={path}>
                  <button
                    onClick={() => void open(path)}
                    disabled={busy}
                    className="text-sm text-[#4daafc] hover:underline disabled:opacity-40"
                  >
                    {path}
                  </button>
                </li>
              ))}
            </ul>
          )}

        <div className="mt-4 flex max-w-sm gap-2">
          <input
            value={openPath}
            onChange={(e) => setOpenPath(e.target.value)}
            placeholder="Open a folder path…"
            className="min-w-0 flex-1 rounded border border-[#333] bg-[#252526] px-3 py-2 text-sm outline-none focus:border-[#0e639c]"
          />
          <button
            onClick={() => void open(openPath)}
            disabled={!openPath.trim() || busy}
            className="shrink-0 rounded bg-[#3c3c3c] px-3 py-2 text-sm text-white hover:bg-[#4c4c4c] disabled:opacity-40"
          >
            Open
          </button>
          {isDesktop() && (
            <button
              onClick={() => void browse()}
              disabled={busy}
              className="shrink-0 rounded bg-[#0e639c] px-3 py-2 text-sm text-white hover:bg-[#1177bb] disabled:opacity-40"
            >
              {busy ? "Opening…" : "Open Folder…"}
            </button>
          )}
        </div>
        {isDesktop() && (
          <p className="mt-2 text-[11px] text-gray-500">
            Tip: right-click any folder in File Explorer and choose
            <span className="text-gray-300"> “Open with I Studio”</span>, or drag a
            folder from Explorer onto the window.
          </p>
        )}
      </section>
      </div>
    </div>
  );
}
