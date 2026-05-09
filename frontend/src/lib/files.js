export const FILE_GROUPS = [
  { id: "profile", label: "Profile" },
  { id: "gadgets", label: "Gadgets" },
  { id: "policies", label: "Policies" },
  { id: "tests", label: "Tests" },
  { id: "documents", label: "Documents" },
];

export function buildFileTree(files) {
  const groups = FILE_GROUPS.map((group) => ({ ...group, count: 0, items: [] }));
  const byId = Object.fromEntries(groups.map((group) => [group.id, group]));
  const gadgetFolders = new Map();
  const testFolders = new Map();

  for (const file of files) {
    const path = file.path;
    if (path === "profile.bsl.py") {
      byId.profile.items.push(withLabel(file, "profile.bsl.py", "BSL"));
      byId.profile.count += 1;
    } else if (path.startsWith("gadgets/")) {
      const parts = path.split("/");
      const folder = parts[1] || "misc";
      if (!gadgetFolders.has(folder)) {
        gadgetFolders.set(folder, { id: `gadget:${folder}`, label: folder, children: [] });
        byId.gadgets.items.push(gadgetFolders.get(folder));
      }
      gadgetFolders.get(folder).children.push(withLabel(file, parts.slice(2).join("/") || file.name, fileExtension(path)));
      byId.gadgets.count += 1;
    } else if (path.startsWith("policies/")) {
      byId.policies.items.push(withLabel(file, displayFileName(path), "PY"));
      byId.policies.count += 1;
    } else if (path.startsWith("tests/")) {
      const parts = path.split("/");
      const folder = parts.length > 2 ? parts[1] : "docs";
      if (!testFolders.has(folder)) {
        testFolders.set(folder, { id: `test:${folder}`, label: folder, children: [] });
        byId.tests.items.push(testFolders.get(folder));
      }
      testFolders.get(folder).children.push(withLabel(file, parts.slice(2).join("/") || displayFileName(path), fileExtension(path)));
      byId.tests.count += 1;
    } else {
      byId.documents.items.push(withLabel(file, displayFileName(path), fileExtension(path)));
      byId.documents.count += 1;
    }
  }

  return groups.filter((group) => group.count > 0);
}

export function defaultNewFile(kind) {
  if (kind === "gadgets") {
    return {
      kind,
      folder: "new_gadget",
      fileName: "gadget.bsl.py",
      content: [
        "class NewGadget(Gadget):",
        "    id = 'new_gadget'",
        "    namespace = 'meow'",
        "    name = 'New Gadget'",
        "    version = '0.1.0'",
        "    author = Author('Meow Li')",
        "",
        "    def build(self):",
        "        pass",
        "",
      ].join("\n"),
    };
  }
  if (kind === "policies") {
    return {
      kind,
      folder: "",
      fileName: "new_policy.policy.py",
      content: [
        "def new_policy(ctx, candidates):",
        "    return None",
        "",
        "",
        "policy_functions = [new_policy]",
        "",
      ].join("\n"),
    };
  }
  if (kind === "tests") {
    return {
      kind,
      folder: "cases",
      fileName: "new_cases.yaml",
      content: "cases:\n  - name: new_case\n",
    };
  }
  return {
    kind: "documents",
    folder: "",
    fileName: "notes.md",
    content: "# Notes\n",
  };
}

export function pathForNewFile(draft) {
  const fileName = cleanSegment(draft.fileName);
  const folder = cleanPath(draft.folder);
  if (!fileName) return "";
  if (draft.kind === "gadgets") {
    return ["gadgets", folder || "new_gadget", fileName].join("/");
  }
  if (draft.kind === "policies") {
    return ["policies", fileName].join("/");
  }
  if (draft.kind === "tests") {
    return ["tests", folder || "cases", fileName].join("/");
  }
  return [folder || "docs", fileName].join("/");
}

export function fileKindLabel(path) {
  if (!path) return "Choose a profile file";
  if (path.startsWith("gadgets/")) return "Gadget source";
  if (path.startsWith("policies/")) return "Policy Function";
  if (path.startsWith("tests/")) return "Fixture or readable test document";
  if (path === "profile.bsl.py") return "Partnership Profile";
  return "Profile document";
}

export function classifyPath(path) {
  if (!path) return "document";
  if (path === "profile.bsl.py") return "profile";
  if (path.includes("/gadget.bsl.py")) return "gadget";
  if (path.endsWith(".policy.py")) return "policy";
  if (path.startsWith("tests/")) return "test";
  return "source";
}

export function displayFileName(path) {
  if (!path) return "";
  return path.split("/").pop();
}

export function fileExtension(path) {
  const lower = String(path || "").toLowerCase();
  if (lower.endsWith(".bsl.py")) return "BSL";
  if (lower.endsWith(".policy.py")) return "PY";
  const match = lower.match(/\.([a-z0-9]+)$/);
  return match ? match[1].toUpperCase() : "";
}

function withLabel(file, label, badge) {
  return { ...file, label, badge };
}

function cleanSegment(value) {
  return String(value || "").replace(/[\\/:*?"<>|]/g, "_").trim();
}

function cleanPath(value) {
  return String(value || "")
    .split("/")
    .map(cleanSegment)
    .filter(Boolean)
    .join("/");
}
