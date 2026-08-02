export interface IdeSettings {
  theme: "dark" | "light";
  fontSize: number;
  tabSize: number;
  minimap: boolean;
  wordWrap: boolean;
  renderWhitespace: "selection" | "all" | "none";
}

export const DEFAULT_SETTINGS: IdeSettings = {
  theme: "dark",
  fontSize: 14,
  tabSize: 4,
  minimap: true,
  wordWrap: false,
  renderWhitespace: "selection",
};

const STORAGE_KEY = "istudio.settings";

export function loadSettings(): IdeSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_SETTINGS };
    return { ...DEFAULT_SETTINGS, ...(JSON.parse(raw) as Partial<IdeSettings>) };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

export function saveSettings(settings: IdeSettings): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch {
    // storage unavailable; settings apply for the session only
  }
}

export function monacoThemeFor(settings: IdeSettings): string {
  return settings.theme === "light" ? "istudio-light" : "istudio-dark";
}

export function applyDocumentTheme(theme: IdeSettings["theme"]): void {
  document.documentElement.setAttribute("data-theme", theme);
}
