interface PywebviewApi {
  open_folder: () => Promise<string>;
  pick_folder: () => Promise<string>;
  open_path: (path: string) => Promise<string>;
}

declare global {
  interface Window {
    pywebview?: {
      api: PywebviewApi;
    };
  }
}

export function isDesktop(): boolean {
  return typeof window !== "undefined" && !!window.pywebview?.api;
}

export async function pickAndOpenFolder(): Promise<string> {
  if (!isDesktop()) return "";
  const result = await window.pywebview!.api.open_folder();
  return result || "";
}

export async function pickFolderForImport(): Promise<string> {
  if (!isDesktop()) return "";
  const result = await window.pywebview!.api.pick_folder();
  return result || "";
}
