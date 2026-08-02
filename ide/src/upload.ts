declare module "react" {
  interface HTMLAttributes<T> {
    webkitdirectory?: boolean;
  }
}

export async function readFolderFiles(files: FileList): Promise<Record<string, string>> {
  const map: Record<string, string> = {};
  const all = Array.from(files);
  for (const file of all) {
    const rel = (file as File & { webkitRelativePath?: string }).webkitRelativePath ?? file.name;
    const parts = rel.split("/");
    parts.shift();
    if (parts.length === 0 || !parts[parts.length - 1]) continue;
    map[parts.join("/")] = await file.text();
  }
  return map;
}
