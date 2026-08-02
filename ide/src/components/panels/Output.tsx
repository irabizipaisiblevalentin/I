import { useEffect, useRef } from "react";
import { useIde } from "../../store";

export default function Output() {
  const runOutput = useIde((s) => s.runOutput);
  const runExit = useIde((s) => s.runExit);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [runOutput]);

  return (
    <div ref={ref} className="h-full overflow-auto p-2 font-mono text-xs text-gray-300">
      <pre className="whitespace-pre-wrap">{runOutput || "— no output yet —"}</pre>
      {runExit && (
        <p
          className={`mt-1 border-t border-[#333] pt-1 ${
            runExit.ok ? "text-green-400" : "text-red-400"
          }`}
        >
          Process exited with code {runExit.code} ({runExit.ok ? "OK" : "error"})
        </p>
      )}
    </div>
  );
}
