import { React, e } from "../ui/react.js";
import { highlightCode } from "../lib/bsl.js";

export function CodeEditor({ content, path, diagnostics, onChange }) {
  const [scroll, setScroll] = React.useState({ top: 0, left: 0 });
  const lineCount = Math.max(1, content.split("\n").length);
  const highlighted = React.useMemo(() => highlightCode(content, path), [content, path]);

  function handleScroll(event) {
    setScroll({ top: event.currentTarget.scrollTop, left: event.currentTarget.scrollLeft });
  }

  return e("div", { className: "code-editor-workspace" },
    e("div", { className: "editor-shell source-editor" },
      e("div", { className: "line-number-viewport" },
        e("div", {
          className: "line-numbers",
          style: { transform: `translateY(${-scroll.top}px)` },
        }, Array.from({ length: lineCount }, (_, index) => e("span", { key: index }, index + 1))),
      ),
      e("div", { className: "editor-codebox" },
        e("pre", {
          className: "highlight-layer",
          style: { transform: `translate(${-scroll.left}px, ${-scroll.top}px)` },
          "aria-hidden": "true",
          dangerouslySetInnerHTML: { __html: highlighted },
        }),
        e("textarea", {
          className: "code-editor",
          value: content,
          spellCheck: false,
          wrap: "off",
          "aria-label": "Code editor",
          onScroll: handleScroll,
          onChange: (event) => onChange(event.target.value),
        }),
      ),
    ),
    e(EditorDiagnosticsBar, { diagnostics }),
  );
}

function EditorDiagnosticsBar({ diagnostics }) {
  const errors = diagnostics.filter((diagnostic) => diagnostic.severity === "error");
  const warnings = diagnostics.filter((diagnostic) => diagnostic.severity !== "error");
  const firstDiagnostic = diagnostics[0];

  return e("div", { className: diagnostics.length ? "editor-diagnostics-bar active" : "editor-diagnostics-bar" },
    e("span", { className: "editor-mode-label" }, "Source"),
    diagnostics.length
      ? e(React.Fragment, null,
          e("strong", null, `${errors.length} error${errors.length === 1 ? "" : "s"}`),
          e("span", null, `${warnings.length} warning${warnings.length === 1 ? "" : "s"}`),
          firstDiagnostic && e("span", null, `Line ${firstDiagnostic.line}: ${firstDiagnostic.message}`),
        )
      : e("span", null, "No syntax issues detected"),
  );
}
