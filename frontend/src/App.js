import { React, e } from "./ui/react.js";
import {
  deleteProfileFile,
  generateTrainingDeal,
  listProfileFiles,
  listProfiles,
  readProfileFile,
  simulateAuction,
  writeProfileFile,
} from "./api/gibleApi.js";
import { CodeEditor } from "./components/CodeEditor.js";
import { FileTree } from "./components/FileTree.js";
import { StructuredEditor } from "./components/StructuredEditor.js";
import { BridgePanel } from "./components/BridgeTools.js";
import { IVScanner } from "./components/IVScanner.js";
import { fileKindLabel, displayFileName } from "./lib/files.js";
import { lintText } from "./lib/bsl.js";
import { parseHand, seatName } from "./lib/bridge.js";
import { clearOpponents, compactHand, completeOpponents, initialDeal, randomDeal, validateDeal } from "./lib/deal.js";

export default function App() {
  const [profiles, setProfiles] = React.useState([]);
  const [profileId, setProfileId] = React.useState("daqiush_2over1");
  const [files, setFiles] = React.useState([]);
  const [selectedFile, setSelectedFile] = React.useState("");
  const [originalContent, setOriginalContent] = React.useState("");
  const [fileContent, setFileContent] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [workspaceView, setWorkspaceView] = React.useState("table");
  const [viewMode, setViewMode] = React.useState("guide");
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [deal, setDeal] = React.useState(initialDeal);
  const [showOpponents, setShowOpponents] = React.useState(false);
  const dealValidation = React.useMemo(() => validateDeal(deal), [deal]);
  const northSouthValidation = React.useMemo(() => validateDeal(deal, ["n", "s"]), [deal]);
  const [dealer, setDealer] = React.useState("n");
  const [vulnerability, setVulnerability] = React.useState("none");
  const [simulation, setSimulation] = React.useState(null);
  const [visibleCallCount, setVisibleCallCount] = React.useState(0);
  const [simulationLoading, setSimulationLoading] = React.useState(false);
  const [trainingMode, setTrainingMode] = React.useState("off");
  const [targetOpening, setTargetOpening] = React.useState("1NT");
  const [targetResponse, setTargetResponse] = React.useState("4C");
  const [targetOpener, setTargetOpener] = React.useState("ns");
  const [trainingSeed, setTrainingSeed] = React.useState("");
  const [responderHcpMin, setResponderHcpMin] = React.useState("");
  const [responderHcpMax, setResponderHcpMax] = React.useState("");
  const [responderLengths, setResponderLengths] = React.useState({ S: "", H: "", D: "", C: "" });
  const [trainingResult, setTrainingResult] = React.useState(null);
  const [trainingLoading, setTrainingLoading] = React.useState(false);
  const trainingAbort = React.useRef(null);
  const simulationRequestId = React.useRef(0);
  const auctionRequested = React.useRef(false);
  const replayCount = React.useRef(0);

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
    simulationRequestId.current += 1;
    setSimulation(null);
    setVisibleCallCount(0);
    setSimulationLoading(false);
    if (!dealValidation.valid || !auctionRequested.current) return;
    setSimulationLoading(true);
    const timer = window.setTimeout(() => {
      refreshSimulation("count", replayCount.current);
    }, 250);
    return () => window.clearTimeout(timer);
  }, [profileId, deal, dealer, vulnerability, trainingResult]);

  function setHolding(seat, suit, value) {
    if (deal[seat][suit] === value) return;
    simulationRequestId.current += 1;
    invalidateTrainingSearch();
    setDeal((prior) => ({ ...prior, [seat]: { ...prior[seat], [suit]: value } }));
  }

  function dealRandomHands() {
    invalidateTrainingSearch();
    simulationRequestId.current += 1;
    auctionRequested.current = false;
    replayCount.current = 0;
    setSimulation(null);
    setVisibleCallCount(0);
    setSimulationLoading(false);
    setDeal(randomDeal());
    setStatus("New deal ready. Press play to begin the auction.");
  }

  function invalidateTrainingSearch() {
    trainingAbort.current?.abort();
    trainingAbort.current = null;
    setTrainingLoading(false);
    setTrainingResult(null);
  }

  function cancelTrainingSearch() {
    invalidateTrainingSearch();
    setStatus("Training deal search cancelled.");
  }

  async function generateMatchingDeal() {
    trainingAbort.current?.abort();
    const controller = new AbortController();
    trainingAbort.current = controller;
    setTrainingLoading(true);
    setStatus("Searching for a deal that produces the selected calls...");
    try {
      const seedText = trainingSeed.trim();
      if (seedText && !/^-?\d+$/.test(seedText)) throw new Error("Seed must be an integer.");
      if (seedText && !Number.isSafeInteger(Number(seedText))) throw new Error("Seed must be a safe integer.");
      const parseLength = (text) => {
        const value = (text || "").trim();
        if (!value) return null;
        const pair = value.match(/^(\d+)\s*-\s*(\d+)$/);
        if (pair) return [Number(pair[1]), Number(pair[2])];
        if (/^\d+$/.test(value)) { const single = Number(value); return [single, single]; }
        throw new Error(`Length range "${text}" must be a number or min-max.`);
      };
      const responder = {};
      const hcpMin = responderHcpMin.trim();
      const hcpMax = responderHcpMax.trim();
      if (hcpMin) responder.min_hcp = Number(hcpMin);
      if (hcpMax) responder.max_hcp = Number(hcpMax);
      const minLengths = {};
      const maxLengths = {};
      for (const suit of ["S", "H", "D", "C"]) {
        const range = parseLength(responderLengths[suit]);
        if (range) { minLengths[suit] = range[0]; maxLengths[suit] = range[1]; }
      }
      if (Object.keys(minLengths).length) responder.min_lengths = minLengths;
      if (Object.keys(maxLengths).length) responder.max_lengths = maxLengths;
      const result = await generateTrainingDeal({
        profile: { id: profileId }, opening: targetOpening,
        response: trainingMode === "response" ? targetResponse : null,
        opener: targetOpener, vulnerability,
        responder: Object.keys(responder).length ? responder : null,
        seed: seedText ? Number(seedText) : null, max_attempts: 2000,
      }, controller.signal);
      if (trainingAbort.current !== controller) return;
      if (result.status !== "matched") {
        setStatus(`${result.message} Tried ${result.attempts} deals (seed ${result.seed}).`);
        return;
      }
      const nextDeal = Object.fromEntries(Object.entries(result.hands).map(
        ([seat, cards]) => [seat, parseHand(cards)]));
      const checked = validateDeal(nextDeal);
      if (!checked.valid) throw new Error(`Generated deal was invalid: ${checked.errors.join(" ")}`);
      auctionRequested.current = false;
      replayCount.current = 0;
      simulationRequestId.current += 1;
      setSimulation(null);
      setVisibleCallCount(0);
      setSimulationLoading(false);
      setTrainingResult(result);
      setDeal(nextDeal);
      setDealer(result.dealer);
      if (result.opener === "e" || result.opener === "w") setShowOpponents(true);
      setStatus(`Matched ${result.calls.map((call) => call === "P" ? "Pass" : call.replace("N", "NT")).join(" · ")} after ${result.attempts} deals. Seed ${result.seed}. Press play to replay.`);
    } catch (error) {
      if (trainingAbort.current === controller && error?.name !== "AbortError") {
        setStatus(`Training deal search failed: ${error.message}`);
      }
    } finally {
      if (trainingAbort.current === controller) {
        trainingAbort.current = null;
        setTrainingLoading(false);
      }
    }
  }

  function revealCalls(count) {
    replayCount.current = count;
    setVisibleCallCount(count);
  }

  function fillOpponents() {
    try {
      const completed = completeOpponents(deal);
      simulationRequestId.current += 1;
      invalidateTrainingSearch();
      setDeal(completed);
      setStatus("E/W hands filled randomly from the remaining 26 cards. N/S hands preserved.");
    } catch (error) {
      setStatus(`Cannot fill E/W hands: ${error.message}`);
    }
  }

  function clearEastWestHands() {
    simulationRequestId.current += 1;
    invalidateTrainingSearch();
    auctionRequested.current = false;
    replayCount.current = 0;
    setSimulation(null);
    setVisibleCallCount(0);
    setSimulationLoading(false);
    setDeal((prior) => clearOpponents(prior));
    setShowOpponents(true);
    setStatus("E/W hands cleared. N/S hands preserved.");
  }

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
    if (!dealValidation.valid) return;
    auctionRequested.current = true;
    const requestId = simulationRequestId.current + 1;
    simulationRequestId.current = requestId;
    setSimulationLoading(true);
    setStatus("Building auction...");
    try {
      const activeSeats = trainingResult?.status === "matched"
        ? [trainingResult.opener, { n: "s", s: "n", e: "w", w: "e" }[trainingResult.opener]]
        : ["n", "s"];
      const result = await simulateAuction({
        profile: { id: profileId },
        hands: Object.fromEntries(activeSeats.map((seat) => [seat, compactHand(deal[seat])])),
        environment: { dealer, vulnerability, scoring: "IMP" },
        max_calls: 60,
      });
      if (requestId !== simulationRequestId.current) return;
      setSimulation(result);
      const total = result.records?.length ?? result.calls?.length ?? 0;
      const count = revealMode === "all" ? total
        : revealMode === "first" ? Math.min(1, total)
        : revealMode === "none" ? 0
        : Math.min(revealMode === "count" ? requestedCount : replayCount.current, total);
      revealCalls(count);
      setSimulationLoading(false);
      setStatus(result.status === "blocked"
        ? `TD${result.blocked?.seat ? ` · ${seatName(result.blocked.seat)}` : ""}. Review the auction diagnostics.`
        : result.status === "limit" ? "Auction stopped at the call limit. Replay available calls."
        : "Auction ready.");
    } catch (error) {
      if (requestId !== simulationRequestId.current) return;
      setSimulationLoading(false);
      setStatus(`Auction failed: ${error.message}`);
    }
  }

  async function stepForward() {
    if (!simulation) {
      await refreshSimulation("first");
      return;
    }
    revealCalls(Math.min(visibleCallCount + 1, simulation.records?.length ?? 0));
  }

  function stepBackward() {
    revealCalls(Math.max(0, visibleCallCount - 1));
  }

  async function showEntireAuction() {
    if (!simulation) {
      await refreshSimulation("all");
      return;
    }
    revealCalls(simulation.records?.length ?? 0);
  }

  async function showFirstCall() {
    if (!simulation) {
      await refreshSimulation("first");
      return;
    }
    revealCalls(Math.min(1, simulation.records?.length ?? 0));
  }

  return e("div", { className: sidebarCollapsed ? "app sidebar-collapsed" : "app" },
    e("aside", { className: sidebarCollapsed ? "sidebar collapsed" : "sidebar" },
      e("div", { className: "sidebar-top" },
        e("div", { className: "brand" },
          e("div", { className: "brand-mark" }, "G"),
          !sidebarCollapsed && e("div", null,
            e("h1", null, "Gible"),
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
              className: workspaceView === "table" ? "rail-tab active" : "rail-tab",
              title: "Table",
              onClick: () => setWorkspaceView("table"),
            }, "T"),
            e("button", {
              className: workspaceView === "scanner" ? "rail-tab active" : "rail-tab",
              title: "IV Scanner",
              onClick: () => setWorkspaceView("scanner"),
            }, "IV"),
            e("button", {
              className: workspaceView === "editor" ? "rail-tab active" : "rail-tab",
              title: "System Editor",
              onClick: () => setWorkspaceView("editor"),
            }, "E"),
          )
        : e(React.Fragment, null,
            e("label", { className: "field-label" }, "Profile"),
            e("select", { value: profileId, onChange: (event) => { invalidateTrainingSearch(); setProfileId(event.target.value); } },
              profiles.map((profile) => e("option", { key: profile.id, value: profile.id }, profile.name || profile.id)),
            ),
            e("div", { className: "workspace-switcher" },
              e("button", {
                className: workspaceView === "table" ? "nav-tab active" : "nav-tab",
                onClick: () => setWorkspaceView("table"),
              }, "Table"),
              e("button", {
                className: workspaceView === "scanner" ? "nav-tab active" : "nav-tab",
                onClick: () => setWorkspaceView("scanner"),
              }, "IV Scanner"),
              e("button", {
                className: workspaceView === "editor" ? "nav-tab active" : "nav-tab",
                onClick: () => setWorkspaceView("editor"),
              }, "System Editor"),
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
    e("main", { className: `workspace ${workspaceView === "editor" ? "editor-workspace" : workspaceView === "scanner" ? "scanner-workspace" : "table-workspace"}` },
      workspaceView === "scanner" && e(IVScanner, { profileId }),
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
        profileId,
        deal,
        setHolding,
        validation: dealValidation,
        showOpponents,
        setShowOpponents,
        onRandomDeal: dealRandomHands,
        trainingMode, setTrainingMode: (value) => { invalidateTrainingSearch(); setTrainingMode(value); },
        targetOpening, setTargetOpening: (value) => { invalidateTrainingSearch(); setTargetOpening(value); },
        targetResponse, setTargetResponse: (value) => { invalidateTrainingSearch(); setTargetResponse(value); },
        targetOpener, setTargetOpener: (value) => { invalidateTrainingSearch(); setTargetOpener(value); },
        responderHcpMin, setResponderHcpMin: (value) => { invalidateTrainingSearch(); setResponderHcpMin(value); },
        responderHcpMax, setResponderHcpMax: (value) => { invalidateTrainingSearch(); setResponderHcpMax(value); },
        responderLengths, setResponderLengths: (value) => { invalidateTrainingSearch(); setResponderLengths(value); },
        trainingSeed, setTrainingSeed: (value) => { if (trainingLoading) invalidateTrainingSearch(); setTrainingSeed(value); }, trainingResult, trainingLoading,
        onGenerateTraining: generateMatchingDeal, onCancelTraining: cancelTrainingSearch,
        onCompleteOpponents: fillOpponents,
        onClearOpponents: clearEastWestHands,
        canCompleteOpponents: northSouthValidation.valid,
        dealer,
        setDealer: (value) => { invalidateTrainingSearch(); setDealer(value); },
        vulnerability,
        setVulnerability: (value) => { invalidateTrainingSearch(); setVulnerability(value); },
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
