import { useMemo } from "react";
import Editor, { type Monaco, type BeforeMount, type OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { api } from "../api";
import { useIde } from "../store";
import { monacoThemeFor } from "../settings";
import {
  registerCompletionProvider,
  registerFormattingProvider,
  registerHoverProvider,
  registerILanguage,
} from "../monaco/iLanguage";
import type { CompletionItem } from "../types";

interface MonacoEditorProps {
  file: string;
  value: string;
  onChange: (value: string) => void;
}

const editorRef: { current: editor.IStandaloneCodeEditor | null } = {
  current: null,
};

export function getEditor(): editor.IStandaloneCodeEditor | null {
  return editorRef.current;
}

export function scrollToLine(line: number): void {
  const ed = editorRef.current;
  if (!ed) return;
  ed.revealLineInCenter(line);
  ed.setPosition({ lineNumber: line, column: 1 });
}

export function updateBreakpointDecorations(file: string): void {
  const ed = editorRef.current;
  if (!ed) return;
  const { breakpoints } = useIde.getState();
  const lines = breakpoints[file] ?? [];
  ed.deltaDecorations(
    [],
    lines.map((line) => ({
      range: {
        startLineNumber: line,
        startColumn: 1,
        endLineNumber: line,
        endColumn: 1,
      },
      options: {
        isWholeLine: true,
        glyphMarginClassName: "istudio-breakpoint",
        glyphMarginHoverMessage: { value: "Breakpoint" },
      },
    })),
  );
}

async function fetchCompletions(
  content: string,
  line: number,
  character: number,
): Promise<CompletionItem[]> {
  const data = await api<{ completions: CompletionItem[] }>("/api/completion", {
    method: "POST",
    body: { content, line, column: character },
  });
  return data.completions;
}

async function fetchHover(
  content: string,
  line: number,
  character: number,
): Promise<string | null> {
  const data = await api<{ hover: { contents: { value: string }[] } | null }>("/api/hover", {
    method: "POST",
    body: { content, line, column: character },
  });
  if (!data.hover || !data.hover.contents?.length) return null;
  return data.hover.contents.map((c) => c.value).join("\n\n");
}

export default function MonacoEditor({ file, value, onChange }: MonacoEditorProps) {
  const uri = useMemo(() => ({ file }), [file]);
  const settings = useIde((s) => s.settings);
  const theme = monacoThemeFor(settings);

  const handleBeforeMount: BeforeMount = (_monaco) => {
    registerILanguage();
    registerCompletionProvider(fetchCompletions);
    registerHoverProvider(fetchHover);
    registerFormattingProvider();
  };

  const handleMount: OnMount = (editorInstance, monaco: Monaco) => {
    editorRef.current = editorInstance;
    registerILanguage();

    editorInstance.onMouseDown((e) => {
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_LINE_NUMBERS) {
        const line = e.target.position?.lineNumber;
        if (line) {
          useIde.getState().toggleBreakpoint(file, line);
          updateBreakpointDecorations(file);
        }
      }
    });

    editorInstance.onDidChangeModelContent(() => {
      const model = editorInstance.getModel();
      if (model) {
        monaco.editor.setModelMarkers(model, "istudio", []);
      }
    });

    editorInstance.onDidChangeCursorPosition((e) => {
      useIde.getState().setCursor(e.position.lineNumber, e.position.column);
    });

    const model = editorInstance.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model, "i");
    }
    setTimeout(() => updateBreakpointDecorations(file), 100);
  };

  const handleChange = (value: string | undefined) => {
    if (value !== undefined) onChange(value);
  };

  return (
    <Editor
      path={uri.file}
      language="i"
      theme={theme}
      value={value}
      onChange={handleChange}
      beforeMount={handleBeforeMount}
      onMount={handleMount}
      options={{
        fontSize: settings.fontSize,
        tabSize: settings.tabSize,
        fontFamily: "Cascadia Code, Consolas, monospace",
        minimap: { enabled: settings.minimap },
        glyphMargin: true,
        lineNumbersMinChars: 3,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        wordWrap: settings.wordWrap ? "on" : "off",
        renderWhitespace: settings.renderWhitespace,
        quickSuggestions: { other: true, comments: false, strings: false },
        suggestOnTriggerCharacters: true,
      }}
    />
  );
}
