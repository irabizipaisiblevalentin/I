import { useIde } from "../../store";
import { debugActiveFile, debugCommand } from "../../commands";

export default function DebugPanel() {
  const running = useIde((s) => s.debugRunning);
  const stopped = useIde((s) => s.debugStopped);
  const ended = useIde((s) => s.debugEnded);
  const output = useIde((s) => s.debugOutput);

  if (!running && !ended) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-xs text-gray-500">
        <p>Set breakpoints by clicking a line number, then press Debug in the editor toolbar.</p>
        <button
          onClick={() => void debugActiveFile()}
          className="rounded bg-[#0e639c] px-3 py-1 text-white hover:bg-[#1177bb]"
        >
          🐞 Start Debugging
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col p-2 text-xs">
      <div className="mb-2 flex items-center gap-2">
        <button
          onClick={() => void debugActiveFile()}
          className="rounded bg-[#0e639c] px-2 py-1 text-white hover:bg-[#1177bb]"
        >
          ↻ Restart
        </button>
        <button
          onClick={() => debugCommand("continue")}
          disabled={!stopped}
          className="rounded bg-[#3c3c3c] px-2 py-1 text-gray-200 hover:bg-[#4c4c4c] disabled:opacity-40"
        >
          ▶ Continue
        </button>
        <button
          onClick={() => debugCommand("step")}
          disabled={!stopped}
          className="rounded bg-[#3c3c3c] px-2 py-1 text-gray-200 hover:bg-[#4c4c4c] disabled:opacity-40"
        >
          ⤵ Step
        </button>
        <button
          onClick={() => debugCommand("stop")}
          className="rounded bg-[#a1260d] px-2 py-1 text-white hover:bg-[#c43e1e]"
        >
          ■ Stop
        </button>
        <span className="ml-2 text-gray-500">
          {running ? "running" : ended ? "ended" : ""}
        </span>
      </div>

      {stopped && (
        <div className="grid min-h-0 flex-1 grid-cols-2 gap-2">
          <section className="min-h-0 overflow-auto">
            <h4 className="mb-1 font-semibold text-gray-400">
              Variables · line {stopped.line}
            </h4>
            <table className="w-full text-left">
              <tbody>
                {Object.entries(stopped.globals).map(([name, value]) => (
                  <tr key={name} className="border-b border-[#2a2d2e]">
                    <td className="py-0.5 pr-2 text-gray-300">{name}</td>
                    <td className="py-0.5 font-mono text-blue-300">{value}</td>
                  </tr>
                ))}
                {Object.keys(stopped.globals).length === 0 && (
                  <tr>
                    <td className="py-0.5 text-gray-500">(no variables)</td>
                  </tr>
                )}
              </tbody>
            </table>
          </section>
          <section className="min-h-0 overflow-auto">
            <h4 className="mb-1 font-semibold text-gray-400">Stack (top)</h4>
            {stopped.stack_top.length > 0 ? (
              stopped.stack_top.map((v, i) => (
                <div key={i} className="py-0.5 font-mono text-blue-300">
                  {i === 0 ? "↘ " : "  "}
                  {v}
                </div>
              ))
            ) : (
              <p className="text-gray-500">(empty)</p>
            )}
          </section>
        </div>
      )}

      {output && (
        <pre className="mt-2 max-h-32 min-h-0 flex-1 overflow-auto whitespace-pre-wrap border-t border-[#2a2d2e] pt-2 text-gray-200">
          {output}
        </pre>
      )}

      {!stopped && !running && (
        <p className="text-gray-500">
          {ended ? "Debug session ended." : "Waiting…"}
        </p>
      )}
    </div>
  );
}
