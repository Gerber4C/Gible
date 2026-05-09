import { React, e } from "./ui/react.js";
import {
  deleteProfileFile,
  listProfileFiles,
  listProfiles,
  readProfileFile,
  simulateAuction,
  writeProfileFile,
} from "./api/partnerApi.js";
import { CodeEditor } from "./components/CodeEditor.js";
import { FileTree } from "./components/FileTree.js";
import { StructuredEditor } from "./components/StructuredEditor.js";
import { BridgePanel } from "./components/BridgeTools.js";
import { fileKindLabel, displayFileName } from "./lib/files.js";
import { lintText } from "./lib/bsl.js";
import { parseHand } from "./lib/bridge.js";

export default function App() {
  const [profiles, setProfiles] = React.useState([]);
  const [profileId, setProfileId] = React.useState("meow_2over1");
  const [files, setFiles] = React.useState([]);
  const [selectedFile, setSelectedFile] = React.useState("");
  const [originalContent, setOriginalContent] = React.useState("");
  const [fileContent, setFileContent] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [workspaceView, setWorkspaceView] = React.useState("editor");
  const [viewMode, setViewMode] = React.useState("guide");
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [northHand, setNorthHand] = React.useState("SAQ7HKJ8DA762CQ54");
  const [southHand, setSouthHand] = React.useState("S72HAQJ987D53CK42");
  const [dealer, setDealer] = React.useState("n");
  const [vulnerability, setVulnerability] = React.useState("none");
  const [simulation, setSimulation] = React.useState(null);
  const [visibleCallCount, setVisibleCallCount] = React.useState(0);
  const [simulationLoading, setSimulationLoading] = React.useState(false);
  const simulationRequestId = React.useRef(0);

  const dirty = fileContent !== originalContent;
  const diagnostics = React.useMemo(() => lintText(fileContent, selectedFile), [fileContent, selectedFile]);

  React.useEffect(() => {
    listProfiles()
      .then((data) => {
        setProfiles(data.profiles ?? []);
        if (data.profiles?.length && !data.profiles.some((profile) => profile.id === profileId)) {
          setProfileId(data.profiles[0].id);
        }
      })
      .catch((error) => setStatus(`Backend unavailable: ${error.message}`));
  }, []);

  React.useEffect(() => {
    if (!profileId) return;
    refreshFiles(profileId);
  }, [profileId]);

  React.useEffect(() => {
    if (!profileId || !selectedFile) return;
    loadFile(selectedFile);
  }, [profileId, selectedFile]);

  React.useEffect(() => {
    if (!isCompleteHand(northHand) || !isCompleteHand(southHand)) {
      simulationRequestId.current += 1;
      setSimulation(null);
      setVisibleCallCount(0);
      setSimulationLoading(false);
      return;
    }
    if (!simulation && !simulationLoading) {
      setVisibleCallCount(0);
      return;
    }
    const revealCount = visibleCallCount;
    simulationRequestId.current += 1;
    setSimulation(null);
    setVisibleCallCount(0);
    setSimulationLoading(true);
    const timer = window.setTimeout(() => {
      refreshSimulation("count", revealCount);
    }, 250);
    return () => window.clearTimeout(timer);
  }, [profileId, northHand, southHand, dealer, vulnerability]);

  async function refreshFiles(activeProfileId = profileId) {
    try {
      const data = await listProfileFiles(activeProfileId);
      const nextFiles = data.files ?? [];
      setFiles(nextFiles);
      if (!selectedFile || !nextFiles.some((file) => file.path === selectedFile)) {
        const preferred = nextFiles.find((file) => file.path === "profile.bsl.py") ?? nextFiles[0];
        setSelectedFile(preferred?.path ?? "");
      }
    } catch (error) {
      setStatus(`Could not load files: ${error.message}`);
    }
  }

  async function loadFile(path) {
    try {
      const data = await readProfileFile(profileId, path);
      setOriginalContent(data.content ?? "");
      setFileContent(data.content ?? "");
      setStatus(`Loaded ${path}`);
    } catch (error) {
      setStatus(`Could not read file: ${error.message}`);
    }
  }

  function updateContent(nextContent) {
    setFileContent(nextContent);
  }

  async function selectFile(path) {
    if (dirty && !window.confirm("Discard unsaved changes before opening another file?")) return;
    setSelectedFile(path);
  }

  async function saveFile() {
    try {
      await writeProfileFile(profileId, selectedFile, fileContent);
      setOriginalContent(fileContent);
      await refreshFiles();
      setStatus(`Saved ${selectedFile}`);
    } catch (error) {
      setStatus(`Save failed: ${error.message}`);
    }
  }

  function discardChanges() {
    if (!dirty) return;
    if (!window.confirm("Discard unsaved changes in this file?")) return;
    setFileContent(originalContent);
    setStatus(`Discarded changes in ${selectedFile}`);
  }

  async function reloadFile() {
    if (dirty && !window.confirm("Reload from disk and discard unsaved changes?")) return;
    await loadFile(selectedFile);
  }

  async function createFile(path, content) {
    if (dirty && !window.confirm("Discard unsaved changes before creating a new file?")) return;
    try {
      await writeProfileFile(profileId, path, content);
      await refreshFiles();
      setSelectedFile(path);
      setStatus(`Created ${path}`);
    } catch (error) {
      setStatus(`Create failed: ${error.message}`);
    }
  }

  async function deleteFile(path) {
    if (path === selectedFile && dirty && !window.confirm("This file has unsaved changes. Delete it anyway?")) return;
    if (!window.confirm(`Delete ${path}?`)) return;
    try {
      await deleteProfileFile(profileId, path);
      if (path === selectedFile) {
        setSelectedFile("");
        setOriginalContent("");
        setFileContent("");
      }
      await refreshFiles();
      setStatus(`Deleted ${path}`);
    } catch (error) {
      setStatus(`Delete failed: ${error.message}`);
    }
  }

  async function refreshSimulation(revealMode = "preserve", requestedCount = 0) {
    const requestId = simulationRequestId.current + 1;
    simulationRequestId.current = requestId;
    setSimulationLoading(true);
    setStatus("Building auction...");
    try {
      const result = await simulateAuction({
        profile: { id: profileId },
        hands: { n: northHand, s: southHand },
        environment: { dealer, vulnerability, scoring: "IMP" },
        max_calls: 60,
      });
      if (requestId !== simulationRequestId.current) return;
      setSimulation(result);
      const total = result.records?.length ?? result.calls?.length ?? 0;
      setVisibleCallCount((prior) => {
        if (revealMode === "all") return total;
        if (revealMode === "first") return Math.min(1, total);
        if (revealMode === "none") return 0;
        if (revealMode === "count") return Math.min(requestedCount, total);
        return Math.min(prior, total);
      });
      setSimulationLoading(false);
      setStatus("Auction ready.");
    } catch (error) {
      if (requestId !== simulationRequestId.current) return;
      setSimulationLoading(false);
      setStatus(`Auction failed: ${error.message}`);
    }
  }

  async function stepForward() {
    if (!simulation || visibleCallCount === 0) {
      await refreshSimulation("first");
      return;
    }
    setVisibleCallCount((count) => Math.min(count + 1, simulation.records?.length ?? 0));
  }

  function stepBackward() {
    setVisibleCallCount((count) => Math.max(0, count - 1));
  }

  async function showEntireAuction() {
    if (!simulation) {
      await refreshSimulation("all");
      return;
    }
    setVisibleCallCount(simulation.records?.length ?? 0);
  }

  async function showFirstCall() {
    if (!simulation) {
      await refreshSimulation("first");
      return;
    }
    setVisibleCallCount(Math.min(1, simulation.records?.length ?? 0));
  }

  return e("div", { className: sidebarCollapsed ? "app sidebar-collapsed" : "app" },
    e("aside", { className: sidebarCollapsed ? "sidebar collapsed" : "sidebar" },
      e("div", { className: "sidebar-top" },
        e("div", { className: "brand" },
          e("div", { className: "brand-mark" }, "P"),
          !sidebarCollapsed && e("div", null,
            e("h1", null, "Partner"),
            e("p", null, "Partnership Profile workspace"),
          ),
        ),
        e("button", {
          className: "sidebar-toggle",
          title: sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar",
          onClick: () => setSidebarCollapsed(!sidebarCollapsed),
        }, sidebarCollapsed ? ">" : "<"),
      ),
      sidebarCollapsed
        ? e("div", { className: "sidebar-rail" },
            e("button", {
              className: workspaceView === "editor" ? "rail-tab active" : "rail-tab",
              title: "System Editor",
              onClick: () => setWorkspaceView("editor"),
            }, "E"),
            e("button", {
              className: workspaceView === "table" ? "rail-tab active" : "rail-tab",
              title: "Table",
              onClick: () => setWorkspaceView("table"),
            }, "T"),
          )
        : e(React.Fragment, null,
            e("label", { className: "field-label" }, "Profile"),
            e("select", { value: profileId, onChange: (event) => setProfileId(event.target.value) },
              profiles.map((profile) => e("option", { key: profile.id, value: profile.id }, profile.name || profile.id)),
            ),
            e("div", { className: "workspace-switcher" },
              e("button", {
                className: workspaceView === "editor" ? "nav-tab active" : "nav-tab",
                onClick: () => setWorkspaceView("editor"),
              }, "System Editor"),
              e("button", {
                className: workspaceView === "table" ? "nav-tab active" : "nav-tab",
                onClick: () => setWorkspaceView("table"),
              }, "Table"),
            ),
            workspaceView === "editor" && e(FileTree, {
              files,
              selectedFile,
              dirty,
              onSelect: selectFile,
              onCreate: createFile,
              onDelete: deleteFile,
            }),
          ),
    ),
    e("main", { className: workspaceView === "editor" ? "workspace editor-workspace" : "workspace table-workspace" },
      workspaceView === "editor" && e("section", { className: "editor-panel" },
        e("div", { className: "panel-header" },
          e("div", null,
            e("h2", null, displayFileName(selectedFile) || "No file selected"),
            e("p", null, selectedFile ? fileKindLabel(selectedFile) : "Choose a profile file"),
          ),
          e("div", { className: "header-actions" },
            dirty && e("span", { className: "dirty-pill" }, "Unsaved"),
            e("div", { className: "mode-tabs", role: "tablist", "aria-label": "Editor mode" },
              e("button", {
                className: viewMode === "guide" ? "mode active" : "mode",
                onClick: () => setViewMode("guide"),
              }, "Guide"),
              e("button", {
                className: viewMode === "code" ? "mode active" : "mode",
                onClick: () => setViewMode("code"),
              }, "Code"),
            ),
            e("button", { className: "ghost", disabled: !selectedFile, onClick: reloadFile }, "Reload"),
            e("button", { className: "ghost", disabled: !dirty, onClick: discardChanges }, "Discard"),
            e("button", { className: "primary", disabled: !dirty || !selectedFile, onClick: saveFile }, "Save"),
          ),
        ),
        selectedFile && (viewMode === "guide"
          ? e(StructuredEditor, {
              content: fileContent,
              path: selectedFile,
              onChange: updateContent,
              onOpenCode: () => setViewMode("code"),
            })
          : e(CodeEditor, {
              content: fileContent,
              path: selectedFile,
              diagnostics,
              onChange: updateContent,
            })),
      ),
      workspaceView === "table" && e(BridgePanel, {
        northHand,
        setNorthHand,
        southHand,
        setSouthHand,
        dealer,
        setDealer,
        vulnerability,
        setVulnerability,
        simulation,
        simulationLoading,
        visibleCallCount,
        onShowFirst: showFirstCall,
        onStepForward: stepForward,
        onStepBackward: stepBackward,
        onShowAll: showEntireAuction,
      }),
    ),
    e("footer", { className: "statusbar" }, status || "Ready"),
  );
}

function isCompleteHand(text) {
  const hand = parseHand(text);
  return Object.values(hand).join("").length === 13;
}
