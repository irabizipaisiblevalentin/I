import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";

import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";

// Use OUR bundled monaco instance instead of lazy-loading from a CDN.
// Without this, languages/themes registered in this app are applied to a
// different monaco instance than the one the <Editor> component renders,
// so tokenization/colors/diagnostics never show up.
loader.config({ monaco });

self.MonacoEnvironment = {
  getWorker(_workerId: string, label: string) {
    if (label === "json") {
      return new jsonWorker();
    }
    return new editorWorker();
  },
};

export { monaco };
