import { React, e } from "../ui/react.js";
import { buildFileTree, defaultNewFile, displayFileName, fileExtension, pathForNewFile } from "../lib/files.js";

export function FileTree({ files, selectedFile, dirty, onSelect, onCreate, onDelete }) {
  const tree = React.useMemo(() => buildFileTree(files), [files]);
  const [dialog, setDialog] = React.useState(null);

  function openNew(kind) {
    setDialog(defaultNewFile(kind));
  }

  async function createFromDialog(event) {
    event.preventDefault();
    if (!dialog) return;
    const path = pathForNewFile(dialog);
    if (!path) return;
    await onCreate(path, dialog.content);
    setDialog(null);
  }

  return e("nav", { className: "file-tree" },
    e("div", { className: "file-tree-title" },
      e("span", null, "Workspace Files"),
      dirty && e("small", null, "unsaved"),
    ),
    e("div", { className: "file-tree-scroll" },
      tree.map((group) =>
        e("details", { className: "tree-group", key: group.id, open: true },
          e("summary", null,
            e("span", null, group.label),
            e("button", {
              className: "mini-action",
              onClick: (event) => {
                event.preventDefault();
                event.stopPropagation();
                openNew(group.id);
              },
              title: `New ${group.label.toLowerCase()} file`,
            }, "+"),
          ),
          group.items.map((item) => item.children
            ? e("details", { className: "tree-folder", key: item.id, open: false },
                e("summary", null,
                  e("span", null, item.label),
                  e("small", null, item.children.length),
                ),
                item.children.map((child) => e(FileButton, {
                  key: child.path,
                  file: child,
                  selectedFile,
                  onSelect,
                  onDelete,
                })),
              )
            : e(FileButton, {
                key: item.path,
                file: item,
                selectedFile,
                onSelect,
                onDelete,
              }),
          ),
        ),
      ),
      dialog && e(NewFileDialog, {
        draft: dialog,
        setDraft: setDialog,
        onSubmit: createFromDialog,
        onCancel: () => setDialog(null),
      }),
    ),
  );
}

function FileButton({ file, selectedFile, onSelect, onDelete }) {
  return e("div", { className: file.path === selectedFile ? "file-row active" : "file-row" },
    e("button", {
      className: "file",
      onClick: () => onSelect(file.path),
      title: file.path,
    },
      e("span", null, file.label || displayFileName(file.path)),
      e("small", null, file.badge || fileExtension(file.path)),
    ),
    file.path !== "profile.bsl.py" && e("button", {
      className: "icon-action danger",
      onClick: () => onDelete(file.path),
      title: `Delete ${file.path}`,
    }, "Del"),
  );
}

function NewFileDialog({ draft, setDraft, onSubmit, onCancel }) {
  const path = pathForNewFile(draft);
  return e("form", { className: "new-file-form", onSubmit },
    e("div", { className: "section-title" },
      e("h3", null, "New File"),
      e("button", { className: "icon-action", type: "button", onClick: onCancel }, "Close"),
    ),
    e("label", null,
      e("span", null, "Kind"),
      e("select", {
        value: draft.kind,
        onChange: (event) => setDraft(defaultNewFile(event.target.value)),
      },
        e("option", { value: "gadgets" }, "Gadget"),
        e("option", { value: "policies" }, "Policy"),
        e("option", { value: "tests" }, "Test"),
        e("option", { value: "documents" }, "Document"),
      ),
    ),
    draft.kind !== "policies" && e("label", null,
      e("span", null, draft.kind === "gadgets" ? "Gadget folder" : "Folder"),
      e("input", {
        value: draft.folder,
        onChange: (event) => setDraft({ ...draft, folder: event.target.value }),
      }),
    ),
    e("label", null,
      e("span", null, "File name"),
      e("input", {
        value: draft.fileName,
        onChange: (event) => setDraft({ ...draft, fileName: event.target.value }),
      }),
    ),
    e("div", { className: "path-preview" }, path),
    e("button", { className: "primary", type: "submit" }, "Create"),
  );
}
