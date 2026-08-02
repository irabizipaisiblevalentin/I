import { useState } from "react";
import { useIde } from "../store";

export default function PackagesPanel() {
  const packages = useIde((s) => s.packages);
  const searchPackages = useIde((s) => s.searchPackages);
  const installPackage = useIde((s) => s.installPackage);
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");

  const search = () => {
    void searchPackages(query.trim()).catch((e) => setStatus(String(e)));
  };

  const install = async (name: string, version?: string) => {
    setBusy(name);
    setStatus("");
    try {
      await installPackage(name, version);
      setStatus(`Installed ${name}.`);
    } catch (e) {
      setStatus(`Failed: ${e}`);
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="p-2">
      <div className="mb-2 flex gap-1">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") search();
          }}
          placeholder="Search isoko packages"
          className="min-w-0 flex-1 rounded border border-[#3c3c3c] bg-[#1e1e1e] px-2 py-1 text-xs text-gray-200 outline-none focus:border-blue-500"
        />
        <button
          onClick={search}
          className="rounded bg-[#3c3c3c] px-2 text-xs text-gray-200 hover:bg-[#4c4c4c]"
        >
          🔍
        </button>
      </div>
      {status && <p className="mb-2 px-1 text-xs text-yellow-300">{status}</p>}
      <div className="space-y-0.5">
        {packages.map((pkg) => (
          <div
            key={pkg.name}
            className="flex items-center justify-between rounded px-1 py-0.5 text-xs text-gray-300 hover:bg-[#2a2d2e]"
          >
            <div className="min-w-0">
              <div className="truncate font-medium text-gray-200">
                {pkg.name}
                {pkg.version ? <span className="ml-1 text-gray-500">@{pkg.version}</span> : null}
              </div>
              {pkg.description && (
                <div className="truncate text-[11px] text-gray-500">{pkg.description}</div>
              )}
            </div>
            <button
              onClick={() => void install(pkg.name, pkg.version)}
              disabled={busy === pkg.name}
              className="ml-2 shrink-0 rounded bg-[#0e639c] px-2 py-0.5 text-[11px] text-white disabled:opacity-40"
            >
              {busy === pkg.name ? "…" : "Install"}
            </button>
          </div>
        ))}
        {packages.length === 0 && (
          <p className="px-1 text-xs text-gray-500">No results. Try &quot;utility&quot; or &quot;web&quot;.</p>
        )}
      </div>
    </div>
  );
}
