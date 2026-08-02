import { monaco } from "./setup";
import type { CompletionItem, Diagnostic } from "../types";

const KEYWORDS = [
  "andika",
  "soma",
  "subira",
  "niba",
  "cyangwa",
  "cyangwa_niba",
  "iherezo",
  "wihuse",
  "kuri",
  "buri",
  "muri",
  "kugeza",
  "umurimo",
  "shyira",
  "shyira_ko",
  "igiceri",
  "ukuri",
  "ikinyoma",
  "kora",
  "nga",
  "kubika",
];

export function registerILanguage(): void {
  if (monaco.languages.getLanguages().some((l) => l.id === "i")) {
    return;
  }

  monaco.languages.register({ id: "i", extensions: [".i"], aliases: ["I", "i"] });

  monaco.languages.setMonarchTokensProvider("i", {
    defaultToken: "",
    ignoreCase: true,
    tokenPostfix: ".i",

    keywords: KEYWORDS,
    types: ["int", "float", "string", "bool", "ubwoko"],
    escapes: /\\(?:[abfnrtv\\"'0-7])/,

    tokenizer: {
      root: [
        [/#.*/, "comment"],
        [/#\[[^\]]*\]/, "comment"],
        [/[a-zA-Z_]\w*(?=\s*\()/, "identifier.function"],
        [/[a-zA-Z_]\w*/, { cases: { "@keywords": "keyword", "@types": "type", "@default": "identifier" } }],
        [/\d+(\.\d+)?/, "number"],
        [/"(?:[^"\\]|\\.)*"/, "string"],
        [/'(?:[^'\\]|\\.)*'/, "string"],
        [/[{}()[\]]/, "@brackets"],
        [/[+\-*/%=<>!&|]+/, "operator"],
        [/[;,]/, "delimiter"],
      ],
    },
  });

  monaco.languages.setLanguageConfiguration("i", {
    comments: { lineComment: "#" },
    brackets: [
      ["{", "}"],
      ["(", ")"],
      ["[", "]"],
    ],
    autoClosingPairs: [
      { open: "{", close: "}" },
      { open: "(", close: ")" },
      { open: "[", close: "]" },
      { open: '"', close: '"' },
    ],
    surroundingPairs: [
      { open: "{", close: "}" },
      { open: "(", close: ")" },
      { open: "[", close: "]" },
      { open: '"', close: '"' },
    ],
  });

  monaco.editor.defineTheme("istudio-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "c586c0", fontStyle: "bold" },
      { token: "type", foreground: "4ec9b0" },
      { token: "string", foreground: "ce9178" },
      { token: "number", foreground: "b5cea8" },
      { token: "comment", foreground: "6a9955", fontStyle: "italic" },
      { token: "identifier", foreground: "d4d4d4" },
      { token: "identifier.function", foreground: "dcdcaa" },
      { token: "operator", foreground: "d4d4d4" },
      { token: "delimiter", foreground: "d4d4d4" },
      { token: "bracket", foreground: "d4d4d4" },
    ],
    colors: {
      "editor.background": "#1e1e1e",
      "editor.foreground": "#d4d4d4",
      "editor.lineHighlightBackground": "#2d2d2d",
      "editorCursor.foreground": "#aeafad",
      "editor.selectionBackground": "#264f78",
      "editorIndentGuide.background1": "#333333",
    },
  });

  monaco.editor.defineTheme("istudio-light", {
    base: "vs",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "0000ff", fontStyle: "bold" },
      { token: "type", foreground: "267f99" },
      { token: "string", foreground: "a31515" },
      { token: "number", foreground: "098658" },
      { token: "comment", foreground: "008000", fontStyle: "italic" },
      { token: "identifier", foreground: "000000" },
      { token: "identifier.function", foreground: "795e26" },
      { token: "operator", foreground: "000000" },
      { token: "delimiter", foreground: "000000" },
      { token: "bracket", foreground: "000000" },
    ],
    colors: {
      "editor.background": "#ffffff",
      "editor.foreground": "#000000",
    },
  });
}

export function registerCompletionProvider(
  provider: (content: string, line: number, character: number) => Promise<CompletionItem[]>,
): void {
  monaco.languages.registerCompletionItemProvider("i", {
    triggerCharacters: [".", "_"],
    provideCompletionItems: async (model, position) => {
      const items = await provider(model.getValue(), position.lineNumber, position.column - 1);
      return {
        suggestions: items.map((item) => ({
          label: item.label,
          kind: item.kind as monaco.languages.CompletionItemKind,
          detail: item.detail,
          documentation: item.documentation,
          insertText: item.insertText ?? item.label,
          range: {
            startLineNumber: position.lineNumber,
            startColumn: position.column,
            endLineNumber: position.lineNumber,
            endColumn: position.column,
          },
        })),
      };
    },
  });
}

export function registerHoverProvider(
  provider: (content: string, line: number, character: number) => Promise<string | null>,
): void {
  monaco.languages.registerHoverProvider("i", {
    provideHover: async (model, position) => {
      const value = await provider(model.getValue(), position.lineNumber, position.column - 1);
      if (!value) return null;
      return {
        range: {
          startLineNumber: position.lineNumber,
          startColumn: position.column,
          endLineNumber: position.lineNumber,
          endColumn: position.column + 1,
        },
        contents: [{ value }],
      };
    },
  });
}

const BLOCK_END = /^\s*(iherezo|cyangwa|cyangwa_niba)\b/;
const BLOCK_OPEN = /(\bkora\s*|\s*:\s*)$/;

export function formatICode(code: string): string {
  const lines = code.split(/\r?\n/);
  const out: string[] = [];
  const indentUnit = "    ";
  let indent = 0;

  for (const raw of lines) {
    const stripped = raw.trim();
    if (!stripped) {
      out.push("");
      continue;
    }
    if (BLOCK_END.test(stripped)) {
      indent = Math.max(0, indent - 1);
    }
    out.push(indentUnit.repeat(indent) + stripped);
    if (BLOCK_OPEN.test(stripped)) {
      indent += 1;
    }
  }

  return out.join("\n") + "\n";
}

export function registerFormattingProvider(): void {
  monaco.languages.registerDocumentFormattingEditProvider("i", {
    provideDocumentFormattingEdits(model) {
      const text = model.getValue();
      const formatted = formatICode(text);
      if (formatted === text) return [];
      return [{ range: model.getFullModelRange(), text: formatted }];
    },
  });
}

export function setDiagnostics(file: string, diagnostics: Diagnostic[]): void {
  const uri = monaco.Uri.parse(file);
  const model = monaco.editor.getModel(uri);
  if (!model) return;
  const markers: monaco.editor.IMarkerData[] = diagnostics.map((d) => ({
    startLineNumber: d.range.start.line,
    startColumn: Math.max(1, d.range.start.character + 1),
    endLineNumber: d.range.end.line,
    endColumn: Math.max(1, d.range.end.character + 1),
    message: d.message,
    severity:
      d.severity === 1
        ? monaco.MarkerSeverity.Error
        : d.severity === 2
          ? monaco.MarkerSeverity.Warning
          : monaco.MarkerSeverity.Info,
  }));
  monaco.editor.setModelMarkers(model, "istudio", markers);
}
