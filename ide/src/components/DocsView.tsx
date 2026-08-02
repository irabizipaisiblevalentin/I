import { useEffect, useState } from "react";
import { useIde } from "../store";
import Markdown from "./Markdown";

const DOC_INDEX: { path: string; title: string }[] = [
  { path: "docs/getting-started.md", title: "Getting Started" },
  { path: "docs/language-guide.md", title: "Language Guide" },
  { path: "docs/stdlib-reference.md", title: "Standard Library Reference" },
  { path: "docs/LANGUAGE_SPECIFICATION.md", title: "Language Specification" },
  { path: "docs/error-reference.md", title: "Error Reference" },
  { path: "docs/migration-guide.md", title: "Migration Guide" },
  { path: "docs/faq.md", title: "FAQ" },
];

export default function DocsView() {
  const docsPath = useIde((s) => s.docsPath);
  const openDocs = useIde((s) => s.openDocs);
  const [content, setContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!docsPath) {
      setContent(null);
      return;
    }
    let cancelled = false;
    setContent(null);
    setError(null);
    fetch(`/${docsPath}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then((text) => {
        if (!cancelled) setContent(text);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load this document.");
      });
    return () => {
      cancelled = true;
    };
  }, [docsPath]);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="border-b border-[#333] px-3 py-2 text-[11px] font-medium uppercase tracking-wide text-gray-500">
        Documentation
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        {content !== null ? (
          <Markdown content={content} />
        ) : error ? (
          <div className="px-3 py-2 text-xs text-red-400">{error}</div>
        ) : (
          <div className="p-2">
            {DOC_INDEX.map((doc) => (
              <button
                key={doc.path}
                onClick={() => openDocs(doc.path)}
                className={`block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-[#37373d] ${
                  docsPath === doc.path ? "bg-[#37373d] text-white" : "text-gray-300"
                }`}
              >
                {doc.title}
              </button>
            ))}
            <p className="mt-3 px-2 text-[11px] text-gray-500">
              Select a document to browse the reference in the editor area.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
