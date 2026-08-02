import { useEffect, useState } from "react";
import { useIde } from "../store";

export default function ExtensionsPanel() {
  const extensions = useIde((s) => s.extensions);
  const marketplace = useIde((s) => s.marketplace);
  const refreshExtensions = useIde((s) => s.refreshExtensions);
  const browseExtensions = useIde((s) => s.browseExtensions);
  const installExtension = useIde((s) => s.installExtension);
  const uninstallExtension = useIde((s) => s.uninstallExtension);
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    void refreshExtensions();
    void browseExtensions("").catch(() => setStatus("Marketplace unavailable"));
  }, [refreshExtensions, browseExtensions]);

  const install = async (name: string, version?: string) => {
    setBusy(name);
    setStatus("");
    try {
      await installExtension(name, version);
      setStatus(`Installed ${name}.`);
    } catch (e) {
      setStatus(`Failed: ${e}`);
    } finally {
      setBusy(null);
    }
  };

  const uninstall = async (name: string) => {
    setBusy(name);
    setStatus("");
    try {
      await uninstallExtension(name);
      setStatus(`Uninstalled ${name}.`);
    } catch (e) {
      setStatus(`Failed: ${e}`);
    } finally {
      setBusy(null);
    }
  };

  const browse = () => {
    void browseExtensions(query.trim()).catch((e) => setStatus(String(e)));
  };

  return (
    <div className="p-2">
      <p className="mb-2 px-1 text-[11px] text-gray-500">
        Extensions live in ~/.istudio/extensions
      </p>
      {status && <p className="mb-2 px-1 text-xs text-yellow-300">{status}</p>}

      <div className="mb-3">
        <div className="mb-1 text-[11px] font-semibold uppercase text-gray-400">Installed</div>
        {extensions.length === 0 && (
          <p className="px-1 text-xs text-gray-500">No extensions installed.</p>
        )}
        {extensions.map((ext) => (
          <div
            key={ext.name}
            className="flex items-center justify-between rounded px-1 py-0.5 text-xs text-gray-300 hover:bg-[#2a2d2e]"
          >
            <div className="min-w-0">
              <div className="truncate font-medium text-gray-200">
                {ext.name}
                {ext.version ? <span className="ml-1 text-gray-500">@{ext.version}</span> : null}
              </div>
              {ext.description && (
                <div className="truncate text-[11px] text-gray-500">{ext.description}</div>
              )}
            </div>
            <button
              onClick={() => void uninstall(ext.name)}
              disabled={busy === ext.name}
              className="ml-2 shrink-0 rounded bg-[#3c3c3c] px-2 py-0.5 text-[11px] text-gray-300 hover:bg-[#4c4c4c] disabled:opacity-40"
            >
              Uninstall
            </button>
          </div>
        ))}
      </div>

      <div className="mb-1 text-[11px] font-semibold uppercase text-gray-400">Marketplace</div>
      <div className="mb-2 flex gap-1">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") browse();
          }}
          placeholder="Search extensions"
          className="min-w-0 flex-1 rounded border border-[#3c3c3c] bg-[#1e1e1e] px-2 py-1 text-xs text-gray-200 outline-none focus:border-blue-500"
        />
        <button
          onClick={browse}
          className="rounded bg-[#3c3c3c] px-2 text-xs text-gray-200 hover:bg-[#4c4c4c]"
        >
          Search
        </button>
      </div>
      <div className="space-y-0.5">
        {marketplace.map((ext) => (
          <div
            key={ext.name}
            className="flex items-center justify-between rounded px-1 py-0.5 text-xs text-gray-300 hover:bg-[#2a2d2e]"
          >
            <div className="min-w-0">
              <div className="truncate font-medium text-gray-200">
                {ext.name}
                {ext.version ? <span className="ml-1 text-gray-500">@{ext.version}</span> : null}
              </div>
              {ext.description && (
                <div className="truncate text-[11px] text-gray-500">{ext.description}</div>
              )}
            </div>
            {ext.installed ? (
              <span className="ml-2 shrink-0 text-[11px] text-gray-500">installed</span>
            ) : (
              <button
                onClick={() => void install(ext.name, ext.version)}
                disabled={busy === ext.name}
                className="ml-2 shrink-0 rounded bg-[#0e639c] px-2 py-0.5 text-[11px] text-white hover:bg-[#1177bb] disabled:opacity-40"
              >
                Install
              </button>
            )}
          </div>
        ))}
        {marketplace.length === 0 && (
          <p className="px-1 text-xs text-gray-500">No extensions found.</p>
        )}
      </div>
    </div>
  );
}
