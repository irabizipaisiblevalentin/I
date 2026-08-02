import { useIde } from "../store";

interface SettingsPaneProps {
  onClose: () => void;
}

export default function SettingsPane({ onClose }: SettingsPaneProps) {
  const settings = useIde((s) => s.settings);
  const updateSettings = useIde((s) => s.updateSettings);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[10vh]"
      onMouseDown={onClose}
    >
      <div
        className="w-[480px] overflow-hidden rounded-md border border-[#454545] bg-[#252526] shadow-2xl"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#454545] px-4 py-3">
          <h2 className="text-sm font-medium text-gray-100">Settings</h2>
          <button onClick={onClose} className="rounded px-2 text-gray-400 hover:text-white">
            ×
          </button>
        </div>
        <div className="max-h-80 space-y-4 overflow-y-auto p-4 text-sm">
          <label className="block">
            <span className="mb-1 block text-gray-400">Theme</span>
            <select
              value={settings.theme}
              onChange={(e) =>
                updateSettings({ theme: e.target.value as "dark" | "light" })
              }
              className="w-full rounded border border-[#454545] bg-[#1e1e1e] px-2 py-1.5 text-gray-100 outline-none"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </label>
          <label className="block">
            <span className="mb-1 block text-gray-400">Font size</span>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min={10}
                max={24}
                value={settings.fontSize}
                onChange={(e) => updateSettings({ fontSize: Number(e.target.value) })}
                className="flex-1"
              />
              <span className="w-8 text-right text-gray-100">{settings.fontSize}</span>
            </div>
          </label>
          <label className="block">
            <span className="mb-1 block text-gray-400">Tab size</span>
            <select
              value={settings.tabSize}
              onChange={(e) => updateSettings({ tabSize: Number(e.target.value) })}
              className="w-full rounded border border-[#454545] bg-[#1e1e1e] px-2 py-1.5 text-gray-100 outline-none"
            >
              <option value={2}>2</option>
              <option value={4}>4</option>
              <option value={8}>8</option>
            </select>
          </label>
          <label className="flex items-center justify-between">
            <span className="text-gray-400">Minimap</span>
            <input
              type="checkbox"
              checked={settings.minimap}
              onChange={(e) => updateSettings({ minimap: e.target.checked })}
            />
          </label>
          <label className="flex items-center justify-between">
            <span className="text-gray-400">Word wrap</span>
            <input
              type="checkbox"
              checked={settings.wordWrap}
              onChange={(e) => updateSettings({ wordWrap: e.target.checked })}
            />
          </label>
        </div>
      </div>
    </div>
  );
}
