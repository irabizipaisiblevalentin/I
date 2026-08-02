import { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { api } from "../../api";
import { closeSSE, openSSE } from "../../sse";
import { useIde } from "../../store";

export default function TerminalPanel() {
  const containerRef = useRef<HTMLDivElement>(null);
  const projectPath = useIde((s) => s.project?.path);
  const termRef = useRef<Terminal | null>(null);
  const esRef = useRef<EventSource | null>(null);
  const termIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!projectPath || !containerRef.current || termRef.current) return;

    const term = new Terminal({
      convertEol: true,
      fontSize: 12,
      fontFamily: "Cascadia Code, Consolas, monospace",
      theme: { background: "#1e1e1e" },
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current);
    fit.fit();
    termRef.current = term;

    term.onData((data) => {
      if (termIdRef.current) {
        void api("/api/terminal/input", {
          method: "POST",
          body: { term_id: termIdRef.current, data },
        });
      }
    });

    let cancelled = false;
    void (async () => {
      try {
        const res = await api<{ term_id: string }>("/api/terminal", {
          method: "POST",
          body: { root: projectPath },
        });
        if (cancelled) return;
        termIdRef.current = res.term_id;
        esRef.current = openSSE(`/sse/terminal/${res.term_id}`, (event, payload) => {
          if (event === "output") {
            const data = (payload as { data?: string } | string | undefined) ?? "";
            term.write(typeof data === "string" ? data : data?.data ?? "");
          } else if (event === "exit") {
            term.write("\r\n[terminal closed]\r\n");
          }
        });
      } catch (e) {
        term.write(`[terminal error] ${String(e)}\r\n`);
      }
    })();

    const onResize = () => fit.fit();
    window.addEventListener("resize", onResize);
    return () => {
      cancelled = true;
      window.removeEventListener("resize", onResize);
      if (esRef.current) closeSSE(esRef.current);
      if (termIdRef.current) {
        void api(`/api/terminal/${termIdRef.current}`, { method: "DELETE" });
      }
      term.dispose();
      termRef.current = null;
      termIdRef.current = null;
    };
  }, [projectPath]);

  return <div ref={containerRef} className="h-full w-full p-1" />;
}
