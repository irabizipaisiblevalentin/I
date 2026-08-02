const KNOWN_EVENTS = [
  "output",
  "done",
  "started",
  "stopped",
  "ended",
  "error",
  "breakpoints",
  "exit",
];

export type SSEHandler = (event: string, data: unknown) => void;

export function openSSE(path: string, onEvent: SSEHandler): EventSource {
  const es = new EventSource(path);
  for (const name of KNOWN_EVENTS) {
    es.addEventListener(name, (e: MessageEvent) => {
      let data: unknown = e.data;
      try {
        data = JSON.parse(String(e.data));
      } catch {
        // keep raw text
      }
      onEvent(name, data);
    });
  }
  return es;
}

export function closeSSE(es: EventSource | null): void {
  if (es) {
    es.close();
  }
}
