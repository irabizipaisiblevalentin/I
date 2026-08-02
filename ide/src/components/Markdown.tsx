import { useMemo } from "react";

function inline(text: string): string {
  return text
    .replace(/`([^`]+)`/g, '<code class="istudio-md-code">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
}

function renderMarkdown(md: string): string {
  const lines = md.split(/\r?\n/);
  const out: string[] = [];
  let inCode = false;
  let code: string[] = [];
  let inList = false;
  let table: string[] = [];

  const flushList = () => {
    if (inList) {
      out.push("</ul>");
      inList = false;
    }
  };
  const flushTable = () => {
    if (table.length) {
      const rows = table.map(
        (r) => `<tr>${r.split("|").filter((c) => c !== "").map((c) => `<td>${inline(c.trim())}</td>`).join("")}</tr>`,
      );
      out.push(`<table>${rows.join("")}</table>`);
      table = [];
    }
  };
  const flushCode = () => {
    if (inCode) {
      out.push(`<pre class="istudio-md-pre"><code>${code.join("\n").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre>`);
      code = [];
      inCode = false;
    }
  };

  for (const raw of lines) {
    const line = raw;
    const fence = line.match(/^```(\w*)/);
    if (fence) {
      if (inCode) {
        flushCode();
      } else {
        flushList();
        flushTable();
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      code.push(line);
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      flushList();
      flushTable();
      const level = heading[1].length;
      out.push(`<h${level} class="istudio-md-h istudio-md-h${level}">${inline(heading[2])}</h${level}>`);
      continue;
    }
    if (/^\s*[-*]\s+/.test(line)) {
      if (!inList) {
        flushTable();
        out.push("<ul>");
        inList = true;
      }
      out.push(`<li>${inline(line.replace(/^\s*[-*]\s+/, ""))}</li>`);
      continue;
    }
    if (line.trim() === "") {
      flushList();
      flushTable();
      continue;
    }
    if (line.trim().startsWith("|")) {
      flushList();
      table.push(line);
      continue;
    }
    if (/^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+$/.test(line.trim())) {
      continue;
    }
    flushList();
    flushTable();
    if (line.startsWith("> ")) {
      out.push(`<blockquote class="istudio-md-blockquote">${inline(line.slice(2))}</blockquote>`);
    } else {
      out.push(`<p class="istudio-md-p">${inline(line)}</p>`);
    }
  }
  flushList();
  flushTable();
  flushCode();
  return out.join("\n");
}

export default function Markdown({ content }: { content: string }) {
  const html = useMemo(() => renderMarkdown(content), [content]);
  return (
    <div
      className="istudio-md overflow-y-auto px-4 py-3 text-[13px] leading-relaxed"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
