import { React, e } from "../ui/react.js";
import {
  appendCall,
  emptyCallDraft,
  extractMetadata,
  parseBslFile,
  parsePolicyFile,
  removeObject,
  replaceSourceBlock,
  setKeywordValue,
  updateCall,
} from "../lib/bsl.js";
import { callClass, callLabel, suitSymbol } from "../lib/bridge.js";
import { classifyPath } from "../lib/files.js";

const ACTIONS = [
  "describe_hand",
  "opening",
  "response",
  "one_level_response",
  "transfer",
  "transfer_completion",
  "superaccept",
  "relay",
  "ask",
  "answer_frame",
  "control_bid",
  "place_contract",
  "invite_game",
  "invite_slam",
  "keycard_ask",
  "keycard_response",
  "rkcb_1430",
  "kickback_1430",
  "minorwood_1430",
  "gerber_ace_ask",
  "final_placement",
];

export function StructuredEditor({ content, path, diagnostics, onChange, onOpenCode }) {
  const fileKind = classifyPath(path);
  const parsed = React.useMemo(() => parseBslFile(content), [content]);
  const policy = React.useMemo(() => parsePolicyFile(content), [content]);
  const metadata = React.useMemo(() => extractMetadata(content, fileKind), [content, fileKind]);
  const [addingCall, setAddingCall] = React.useState(false);
  const [newCall, setNewCall] = React.useState(emptyCallDraft());

  function updateMetadata(key, value) {
    onChange(setKeywordValue(content, key, value));
  }

  function updateCallField(index, patch) {
    onChange(updateCall(content, index, patch));
  }

  function updateObjectSource(object, nextBlock) {
    onChange(replaceSourceBlock(content, object, nextBlock));
  }

  function deleteCall(call) {
    if (!window.confirm(`Delete call specification ${call.id}?`)) return;
    onChange(removeObject(content, call));
  }

  function addCall(event) {
    event.preventDefault();
    onChange(appendCall(content, newCall));
    setNewCall(emptyCallDraft());
    setAddingCall(false);
  }

  return e("div", { className: "structured-editor" },
    e("div", { className: "structured-main" },
      fileKind === "policy" && e(PolicyOverview, {
        policy,
        content,
        onChange,
        onOpenCode,
      }),
      fileKind !== "policy" && e(React.Fragment, null,
      e(FileOutline, { parsed }),
      e("section", { className: "guide-section" },
        e("div", { className: "section-title" },
          e("h3", null, "File Properties"),
          e("button", { className: "ghost", onClick: onOpenCode }, "Code View"),
        ),
        metadata.length
          ? e("div", { className: "metadata-grid" },
              metadata.map((field) => e("label", { key: field.key },
                e("span", null, field.label),
                e("input", {
                  value: field.value,
                  onChange: (event) => updateMetadata(field.key, event.target.value),
                }),
              )),
            )
          : e("p", { className: "empty-note" }, "No profile or gadget metadata object was found in this file."),
      ),
      e(CallSpecificationsSection, {
        calls: parsed.calls,
        addingCall,
        newCall,
        setNewCall,
        setAddingCall,
        addCall,
        updateCallField,
        updateObjectSource,
        deleteCall,
      }),
      e(FrameSection, { frames: parsed.frames, onUpdateSource: updateObjectSource }),
      e(PrivateRouteSection, { routes: parsed.privateRoutes, onUpdateSource: updateObjectSource }),
      e(EvaluatorSection, { evaluators: parsed.evaluators, onUpdateSource: updateObjectSource }),
      ),
    ),
  );
}

function PolicyOverview({ policy, content, onChange, onOpenCode }) {
  function updateFunctionSource(fn, nextBlock) {
    onChange(replaceSourceBlock(content, fn, nextBlock));
  }

  return e(React.Fragment, null,
    e("section", { className: "guide-section policy-overview" },
      e("div", { className: "section-title" },
        e("h3", null, "Policy Functions"),
        e("button", { className: "ghost", onClick: onOpenCode }, "Code View"),
      ),
      e("div", { className: "policy-summary-grid" },
        e("div", { className: "outline-tile active" },
          e("strong", null, policy.publicFunctions.length),
          e("span", null, "public functions"),
        ),
        e("div", { className: "outline-tile" },
          e("strong", null, policy.helperFunctions.length),
          e("span", null, "helpers"),
        ),
        e("div", { className: "outline-tile active" },
          e("strong", null, policy.exported.length),
          e("span", null, "registered"),
        ),
      ),
    ),
    e("section", { className: "guide-section" },
      e("div", { className: "section-title" },
        e("h3", null, "Registered Policy Order"),
        e("small", null, "policy_functions"),
      ),
      policy.exported.length
        ? e("div", { className: "policy-order" },
            policy.exported.map((name, index) => e("span", { key: name }, `${index + 1}. ${name}`)),
          )
        : e("p", { className: "empty-note" }, "No registered policy functions found."),
    ),
    e("section", { className: "guide-section" },
      e("div", { className: "section-title" },
        e("h3", null, "Decision Logic"),
        e("small", null, `${policy.functions.length} functions`),
      ),
      policy.functions.length
        ? e("div", { className: "policy-function-list" },
            policy.functions.map((fn) => e(PolicyFunctionCard, {
              key: `${fn.name}-${fn.start}`,
              fn,
              onUpdateSource: (nextBlock) => updateFunctionSource(fn, nextBlock),
            })),
          )
        : e("p", { className: "empty-note" }, "No Python policy functions found."),
    ),
  );
}

function PolicyFunctionCard({ fn, onUpdateSource }) {
  return e("article", { className: fn.exported ? "policy-function-card exported" : "policy-function-card" },
    e("div", { className: "policy-function-head" },
      e("strong", null, fn.name),
      e("span", null, fn.exported ? "registered" : fn.helper ? "helper" : "available"),
    ),
    e("div", { className: "object-detail-grid" },
      e(DetailChip, { label: "Arguments", value: fn.args.join(", ") || "none" }),
      e(DetailChip, { label: "Branches", value: String(fn.branches) }),
      e(DetailChip, { label: "Returns", value: String(fn.returns) }),
      e(DetailChip, { label: "Candidate API", value: fn.candidateMethods.join(", ") || "none" }),
    ),
    fn.candidateCalls.length
      ? e("div", { className: "candidate-call-row" },
          fn.candidateCalls.map((call) => e("span", { key: call }, call)),
        )
      : null,
    fn.docstring && e("p", { className: "object-description" }, fn.docstring),
    e(SourceBlockEditor, {
      label: "Function code",
      value: fn.block,
      onChange: onUpdateSource,
      rows: Math.min(18, Math.max(6, fn.block.split("\n").length + 1)),
    }),
  );
}

function FileOutline({ parsed }) {
  const counts = [
    ["Calls", parsed.calls.length],
    ["Frames", parsed.frames.length],
    ["Private routes", parsed.privateRoutes.length],
    ["Evaluators", parsed.evaluators.length],
    ["Relays", parsed.relays.length],
  ];
  return e("section", { className: "guide-section outline-section" },
    e("div", { className: "section-title" },
      e("h3", null, "File Outline"),
      e("small", null, `${parsed.objects.length} objects`),
    ),
    e("div", { className: "outline-grid" },
      counts.map(([label, count]) => e("div", { className: count ? "outline-tile active" : "outline-tile", key: label },
        e("strong", null, count),
        e("span", null, label),
      )),
    ),
  );
}

function CallSpecificationsSection({
  calls,
  addingCall,
  newCall,
  setNewCall,
  setAddingCall,
  addCall,
  updateCallField,
  updateObjectSource,
  deleteCall,
}) {
  return e("section", { className: "guide-section" },
    e("div", { className: "section-title" },
      e("h3", null, "Call Specifications"),
      e("button", { className: "primary", onClick: () => setAddingCall(!addingCall) }, addingCall ? "Close" : "New Call"),
    ),
    addingCall && e("div", { className: "new-object-panel" },
      e("h4", null, "Create Call Specification"),
      e(CallForm, {
        value: newCall,
        onChange: setNewCall,
        onSubmit: addCall,
        submitLabel: "Add Call",
      }),
    ),
    calls.length
      ? e("div", { className: "call-editor-list" },
          calls.map((call) => e(CallEditorCard, {
            key: `${call.id}-${call.start}`,
            call,
            onUpdate: (patch) => updateCallField(call.index, patch),
            onUpdateSource: (nextBlock) => updateObjectSource(call, nextBlock),
            onDelete: () => deleteCall(call),
          })),
        )
      : e("p", { className: "empty-note" }, "No Call(...) objects found."),
  );
}

function CallEditorCard({ call, onUpdate, onUpdateSource, onDelete }) {
  const [open, setOpen] = React.useState(false);
  const current = {
    id: call.id || "",
    auction: call.auction || "",
    seatPositions: call.seatPositions.length ? call.seatPositions.join(",") : "",
    bid: call.bid.kind === "absolute" ? call.bid.label : call.bidRaw,
    action: call.action || "describe_hand",
    targetSuit: call.targetSuit || "none",
    alertable: Boolean(call.alertable),
    description: call.description || "",
    systemNotes: call.systemNotes || "",
  };

  return e("article", { className: "call-edit-card" },
    e("div", { className: "call-summary-row" },
      e("button", { className: "call-summary", onClick: () => setOpen(!open) },
        e("strong", { className: `call-badge ${call.bid.kind} ${displayBidClass(call)}` }, displayBidLabel(call)),
        e("span", null, call.id || "unnamed"),
        e("small", null, callSubtitle(call)),
      ),
      e("button", { className: "ghost danger-button", onClick: onDelete }, "Delete"),
    ),
    e("div", { className: "call-details" },
      e(DetailChip, { label: "Auction", value: call.auction || "any" }),
      e(DetailChip, { label: "Action", value: call.action || "not specified" }),
      call.targetSuit && e(DetailChip, { label: "Suit", value: suitSymbol(call.targetSuit) }),
      e(DetailChip, { label: "Applies", value: call.appliesText ? "function" : "none" }),
      e(DetailChip, { label: "Effects", value: String(call.effectsCount) }),
      call.alertable && e(DetailChip, { label: "Alert", value: "Yes" }),
    ),
    call.description && e("p", { className: "object-description" }, call.description),
    call.bid.detail && e("p", { className: "object-raw" }, call.bid.detail),
    call.requiresText && e("p", { className: "object-raw" }, `requires: ${call.requiresText}`),
    call.appliesText && e("p", { className: "object-raw" }, `applies: ${call.appliesText}`),
    call.effectsText && e("p", { className: "object-raw" }, `effects: ${call.effectsText}`),
    open && e(CallForm, {
      value: current,
      onChange: onUpdate,
      submitLabel: null,
    }),
    open && e(SourceBlockEditor, {
      label: "Complete Call source",
      value: call.block,
      onChange: onUpdateSource,
      rows: Math.min(18, Math.max(8, call.block.split("\n").length + 1)),
    }),
  );
}

function FrameSection({ frames, onUpdateSource }) {
  return e(ObjectSection, {
    title: "Frames",
    empty: "No Frame(...) objects found.",
    objects: frames,
    render: (frame) => e(GenericObjectCard, {
      key: frame.start,
      title: frame.frameType || frame.id,
      badge: frame.sourceCall || frame.auction || "frame",
      description: frame.description,
      details: [
        ["ID", frame.id],
        ["Auction", frame.auction || "any"],
        ["Stages", frame.stages.join(", ") || "none listed"],
        ["Close", frame.closeOnActions.join(", ") || "not listed"],
      ],
      raw: frame.variablesText,
      source: frame.block,
      onUpdateSource: (nextBlock) => onUpdateSource(frame, nextBlock),
    }),
  });
}

function PrivateRouteSection({ routes, onUpdateSource }) {
  return e(ObjectSection, {
    title: "Private Routes",
    empty: "No PrivateRoute(...) objects found.",
    objects: routes,
    render: (route) => e(GenericObjectCard, {
      key: route.start,
      title: route.goal || route.id,
      badge: route.entryCall || "route",
      description: route.description,
      details: [
        ["ID", route.id],
        ["Owner", route.owner || "not listed"],
        ["Auction", route.auction || "any"],
        ["Entry", route.entryCall || "not listed"],
      ],
      raw: route.preconditionsText || route.workflowText,
      source: route.block,
      onUpdateSource: (nextBlock) => onUpdateSource(route, nextBlock),
    }),
  });
}

function EvaluatorSection({ evaluators, onUpdateSource }) {
  return e(ObjectSection, {
    title: "Evaluators",
    empty: "No Evaluator(...) objects found.",
    objects: evaluators,
    render: (evaluator) => e(GenericObjectCard, {
      key: evaluator.start,
      title: evaluator.id,
      badge: evaluator.evaluatorType || "evaluator",
      description: evaluator.description,
      details: [["Type", evaluator.evaluatorType || "not listed"]],
      raw: evaluator.definitionText,
      source: evaluator.block,
      onUpdateSource: (nextBlock) => onUpdateSource(evaluator, nextBlock),
    }),
  });
}

function ObjectSection({ title, empty, objects, render }) {
  if (!objects.length) {
    return e("section", { className: "guide-section compact-section" },
      e("div", { className: "section-title" }, e("h3", null, title), e("small", null, "0")),
      e("p", { className: "empty-note" }, empty),
    );
  }
  return e("section", { className: "guide-section compact-section" },
    e("div", { className: "section-title" }, e("h3", null, title), e("small", null, objects.length)),
    e("div", { className: "generic-object-list" }, objects.map(render)),
  );
}

function GenericObjectCard({ title, badge, description, details, raw, source, onUpdateSource }) {
  const [open, setOpen] = React.useState(false);
  return e("article", { className: "generic-object-card" },
    e("button", { className: "generic-summary", onClick: () => setOpen(!open) },
      e("strong", null, title || "Unnamed"),
      e("small", null, badge),
    ),
    description && e("p", { className: "object-description" }, description),
    open && e("div", { className: "generic-details" },
      details.map(([label, value]) => e(DetailChip, { key: label, label, value })),
      raw && e("p", { className: "object-raw" }, raw),
      source && e(SourceBlockEditor, {
        label: "Complete source",
        value: source,
        onChange: onUpdateSource,
        rows: Math.min(18, Math.max(8, source.split("\n").length + 1)),
      }),
    ),
  );
}

function SourceBlockEditor({ label, value, onChange, rows = 8 }) {
  return e("label", { className: "source-block-editor" },
    e("span", null, label),
    e("textarea", {
      value,
      rows,
      spellCheck: false,
      onChange: (event) => onChange(event.target.value),
    }),
  );
}

function DetailChip({ label, value }) {
  return e("span", { className: "detail-chip" },
    e("b", null, label),
    e("span", null, value),
  );
}

function CallForm({ value, onChange, onSubmit, submitLabel }) {
  const form = e("div", { className: "call-form" },
    e("label", null,
      e("span", null, "ID"),
      e("input", {
        value: value.id,
        onChange: (event) => onChange({ ...value, id: event.target.value }),
      }),
    ),
    e("label", null,
      e("span", null, "Auction context"),
      e("input", {
        value: value.auction,
        placeholder: "1NP2DP",
        onChange: (event) => onChange({ ...value, auction: event.target.value.toUpperCase() }),
      }),
    ),
    e("label", null,
      e("span", null, "Seats"),
      e("input", {
        value: value.seatPositions,
        placeholder: "1,2,3,4",
        onChange: (event) => onChange({ ...value, seatPositions: event.target.value }),
      }),
    ),
    e("label", null,
      e("span", null, "Bid"),
      e("input", {
        value: value.bid,
        placeholder: "2H or StepAfterState(...)",
        onChange: (event) => onChange({ ...value, bid: normalizeBidInput(event.target.value) }),
      }),
    ),
    e("label", null,
      e("span", null, "Action"),
      e("select", {
        value: value.action,
        onChange: (event) => onChange({ ...value, action: event.target.value }),
      }, ACTIONS.map((action) => e("option", { key: action, value: action }, action))),
    ),
    e("label", null,
      e("span", null, "Target suit"),
      e("select", {
        value: value.targetSuit || "none",
        onChange: (event) => onChange({ ...value, targetSuit: event.target.value }),
      },
        e("option", { value: "none" }, "None"),
        e("option", { value: "S" }, "Spades"),
        e("option", { value: "H" }, "Hearts"),
        e("option", { value: "D" }, "Diamonds"),
        e("option", { value: "C" }, "Clubs"),
        e("option", { value: "N" }, "NT"),
      ),
    ),
    e("label", { className: "check-row" },
      e("input", {
        type: "checkbox",
        checked: Boolean(value.alertable),
        onChange: (event) => onChange({ ...value, alertable: event.target.checked }),
      }),
      e("span", null, "Alertable"),
    ),
    e("label", { className: "wide" },
      e("span", null, "Description"),
      e("textarea", {
        value: value.description,
        rows: 3,
        onChange: (event) => onChange({ ...value, description: event.target.value }),
      }),
    ),
    e("label", { className: "wide" },
      e("span", null, "System notes"),
      e("textarea", {
        value: value.systemNotes,
        rows: 3,
        onChange: (event) => onChange({ ...value, systemNotes: event.target.value }),
      }),
    ),
  );

  if (!onSubmit) return form;
  return e("form", { onSubmit },
    form,
    submitLabel && e("button", { className: "primary", type: "submit" }, submitLabel),
  );
}

function callSubtitle(call) {
  const parts = [];
  parts.push(call.auction ? `after ${call.auction}` : "any auction");
  if (call.action) parts.push(call.action);
  if (call.targetSuit) parts.push(suitSymbol(call.targetSuit));
  if (call.bid.kind !== "absolute") parts.push(call.bid.kind);
  return parts.join(" / ");
}

function displayBidLabel(call) {
  return call.bid.kind === "absolute" ? callLabel(call.bid.label) : call.bid.label;
}

function displayBidClass(call) {
  return call.bid.kind === "absolute" ? callClass(call.bid.label) : "";
}

function normalizeBidInput(value) {
  return value.includes("(") ? value : value.toUpperCase();
}
