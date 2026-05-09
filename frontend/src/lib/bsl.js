const OBJECT_TYPES = ["Profile", "Gadget", "Call", "Frame", "PrivateRoute", "Evaluator", "Relay"];

export function parseBslFile(content) {
  const objects = [];
  for (const type of OBJECT_TYPES) {
    objects.push(...extractBlocks(content, type).map((entry) => ({
      ...entry,
      type,
      style: "constructor",
      id: stringArgument(entry.block, "id") || `${type.toLowerCase()}_${entry.start}`,
      description: stringArgument(entry.block, "description"),
      systemNotes: stringArgument(entry.block, "system_notes"),
    })));
  }
  for (const type of ["Profile", "Gadget"]) {
    objects.push(...extractClassBlocks(content, type).map((entry) => ({
      ...entry,
      type,
      style: "class",
      id: stringAttribute(entry.block, "id") || `${type.toLowerCase()}_${entry.start}`,
      description: stringAttribute(entry.block, "description"),
      systemNotes: stringAttribute(entry.block, "system_notes"),
    })));
  }
  const builderTypes = [
    ["call", "Call"],
    ["frame", "Frame"],
    ["route", "PrivateRoute"],
    ["evaluator", "Evaluator"],
    ["relay", "Relay"],
  ];
  for (const [builder, type] of builderTypes) {
    objects.push(...extractBuilderBlocks(content, builder).map((entry) => ({
      ...entry,
      type,
      style: "builder",
      id: entry.id,
      description: assignmentString(entry.block, `${builder}.description`),
      systemNotes: assignmentString(entry.block, `${builder}.system_notes`),
    })));
  }
  objects.sort((left, right) => left.start - right.start);
  return {
    objects,
    profile: objects.find((object) => object.type === "Profile") || null,
    gadget: objects.find((object) => object.type === "Gadget") || null,
    calls: objects.filter((object) => object.type === "Call").map(summarizeCallObject),
    frames: objects.filter((object) => object.type === "Frame").map(summarizeFrameObject),
    privateRoutes: objects.filter((object) => object.type === "PrivateRoute").map(summarizePrivateRouteObject),
    evaluators: objects.filter((object) => object.type === "Evaluator").map(summarizeEvaluatorObject),
    relays: objects.filter((object) => object.type === "Relay"),
  };
}

export function parsePolicyFile(content) {
  const text = String(content || "");
  const functionMatches = Array.from(text.matchAll(/^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*:/gm));
  const functions = functionMatches.map((match, index) => {
    const start = match.index;
    const nextDef = index + 1 < functionMatches.length ? functionMatches[index + 1].index : text.length;
    const end = functionBlockEnd(text, start, nextDef);
    const body = text.slice(start, end);
    return {
      name: match[1],
      start,
      end,
      block: body.trimEnd(),
      args: match[2].split(",").map((arg) => arg.trim()).filter(Boolean),
      exported: policyFunctionNames(text).includes(match[1]),
      helper: match[1].startsWith("_"),
      docstring: functionDocstring(body),
      candidateCalls: candidateCalls(body),
      candidateMethods: candidateMethods(body),
      branches: (body.match(/\bif\b|\belif\b/g) || []).length,
      returns: (body.match(/\breturn\b/g) || []).length,
    };
  });
  const exported = policyFunctionNames(text);
  return {
    functions,
    exported,
    publicFunctions: functions.filter((fn) => !fn.helper),
    helperFunctions: functions.filter((fn) => fn.helper),
  };
}

export function replaceSourceBlock(content, object, nextBlock) {
  if (!object || !Number.isInteger(object.start) || !Number.isInteger(object.end)) return content;
  const prior = String(content || "");
  const suffix = prior.slice(object.end).startsWith("\n") ? "" : "\n";
  return `${prior.slice(0, object.start)}${String(nextBlock).trimEnd()}${suffix}${prior.slice(object.end)}`;
}

export function extractMetadata(content, fileKind) {
  const parsed = parseBslFile(content);
  const object = fileKind === "profile" ? parsed.profile : parsed.gadget;
  if (!object) return [];
  const keysByKind = {
    profile: ["id", "name", "version"],
    gadget: ["id", "namespace", "name", "version"],
  };
  return (keysByKind[fileKind] || []).map((key) => ({
    key,
    label: key.replaceAll("_", " "),
    value: object.style === "class" ? stringAttribute(object.block, key) : stringArgument(object.block, key),
  }));
}

export function setKeywordValue(content, key, value) {
  const parsed = parseBslFile(content);
  const target = parsed.profile || parsed.gadget;
  if (!target) return content;
  if (target.style === "class") {
    const block = setClassAttribute(target.block, key, value);
    return replaceObject(content, target, block);
  }
  const block = setKeywordInBlock(target.block, key, value, { beforeClose: true });
  return replaceObject(content, target, block);
}

export function summarizeCalls(content) {
  return parseBslFile(content).calls;
}

export function updateCall(content, callIndex, updates) {
  const calls = summarizeCalls(content);
  const call = calls[callIndex];
  if (!call) return content;
  let block = call.block;
  if (call.style === "builder") {
    if ("id" in updates) block = replaceBuilderId(block, "call", updates.id);
    if ("description" in updates) block = setBuilderAssignment(block, "call.description", updates.description);
    if ("systemNotes" in updates) block = setBuilderAssignment(block, "call.system_notes", updates.systemNotes);
    if ("auction" in updates) block = setBuilderAssignment(block, "call.when", updates.auction || "");
    if ("seatPositions" in updates) block = setBuilderAssignment(block, "call.seats", parseSeatPositions(updates.seatPositions), { raw: true });
    if ("bid" in updates) block = setBuilderAssignment(block, "call.bid", renderBuilderBidValue(updates.bid), { raw: true });
    if ("action" in updates) block = setBuilderAssignment(block, "call.meaning.action", updates.action);
    if ("targetSuit" in updates) block = setBuilderAssignment(block, "call.meaning.target_suit", updates.targetSuit && updates.targetSuit !== "none" ? updates.targetSuit : "");
    if ("alertable" in updates) block = setBuilderAssignment(block, "call.meaning.alertable", Boolean(updates.alertable), { raw: true });
    return replaceObject(content, call, block);
  }
  if ("id" in updates) block = setKeywordInBlock(block, "id", updates.id, { beforeClose: true });
  if ("description" in updates) block = setKeywordInBlock(block, "description", updates.description, { beforeClose: true });
  if ("systemNotes" in updates) block = setKeywordInBlock(block, "system_notes", updates.systemNotes, { beforeClose: true });
  if ("auction" in updates || "seatPositions" in updates) {
    block = setAuctionInBlock(
      block,
      "auction" in updates ? updates.auction : call.auction,
      "seatPositions" in updates ? updates.seatPositions : call.seatPositions,
    );
  }
  if ("bid" in updates) block = setKeywordInBlock(block, "bid", renderBidExpression(updates.bid), { beforeClose: true, raw: true });
  if ("action" in updates) block = setMeaningConstructorField(block, "action", updates.action);
  if ("targetSuit" in updates) block = setMeaningConstructorField(block, "target_suit", updates.targetSuit && updates.targetSuit !== "none" ? updates.targetSuit : "");
  if ("alertable" in updates) block = setMeaningConstructorField(block, "alertable", Boolean(updates.alertable), { raw: true });
  return replaceObject(content, call, block);
}

export function removeObject(content, object) {
  const start = includeLeadingBlankLine(content, object.start);
  let end = object.end;
  if (content.slice(end, end + 2) === "\n\n") end += 1;
  return `${content.slice(0, start)}${content.slice(end)}`.replace(/\n{4,}/g, "\n\n\n");
}

export function appendCall(content, draft) {
  const callText = renderCall(draft);
  return `${String(content || "").replace(/\s*$/, "")}\n\n${callText}\n`;
}

export function renderCall(draft) {
  const appliesName = `${sanitizeIdentifier(draft.id || "new_call")}_applies`;
  const seats = parseSeatPositions(draft.seatPositions);
  const lines = [
    `def ${appliesName}(ctx):`,
    "    return True",
    "",
    `        call = self.call(${pyString(draft.id || "new_call")})`,
    `        call.when = ${pyString(draft.auction || "")}`,
  ];
  if (seats.length) lines.push(`        call.seats = [${seats.join(", ")}]`);
  lines.push(`        call.bid = ${renderBuilderBidValue(draft.bid || "P")}`);
  lines.push(`        call.applies = ${appliesName}`);
  lines.push(`        call.meaning.action = ${pyString(draft.action || "describe_hand")}`);
  if (draft.targetSuit && draft.targetSuit !== "none") {
    lines.push(`        call.meaning.target_suit = ${pyString(draft.targetSuit)}`);
  }
  if (draft.alertable) lines.push("        call.meaning.alertable = True");
  if (draft.description) lines.push(`        call.description = ${pyString(draft.description)}`);
  if (draft.systemNotes) lines.push(`        call.system_notes = ${pyString(draft.systemNotes)}`);
  return lines.join("\n");
}

export function emptyCallDraft() {
  return {
    id: "new_call",
    auction: "",
    seatPositions: "1,2,3,4",
    bid: "P",
    action: "describe_hand",
    targetSuit: "none",
    alertable: false,
    description: "",
    systemNotes: "",
  };
}

export function lintText(content, path) {
  const diagnostics = [];
  const stack = [];
  const pairs = { "(": ")", "[": "]", "{": "}" };
  const closers = new Set(Object.values(pairs));
  let quote = "";
  let escaped = false;
  let line = 1;
  let column = 0;

  for (let index = 0; index < content.length; index += 1) {
    const char = content[index];
    column += 1;
    if (char === "\n") {
      line += 1;
      column = 0;
      continue;
    }
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "#") {
      while (index < content.length && content[index] !== "\n") index += 1;
      index -= 1;
      continue;
    }
    if (char === "'" || char === '"') {
      quote = char;
      continue;
    }
    if (pairs[char]) {
      stack.push({ expected: pairs[char], line, column });
    } else if (closers.has(char)) {
      const prior = stack.pop();
      if (!prior || prior.expected !== char) {
        diagnostics.push({ severity: "error", line, column, message: `Unexpected closing bracket ${char}` });
      }
    }
  }
  if (quote) {
    diagnostics.push({ severity: "error", line, column: Math.max(1, column), message: "Unclosed string literal" });
  }
  for (const item of stack.slice(-3)) {
    diagnostics.push({ severity: "error", line: item.line, column: item.column, message: `Missing closing bracket ${item.expected}` });
  }
  return diagnostics;
}

export function mergeDiagnostics(localDiagnostics, serverDiagnostics) {
  const seen = new Set();
  return [...localDiagnostics, ...serverDiagnostics].filter((diagnostic) => {
    const key = `${diagnostic.severity}:${diagnostic.line}:${diagnostic.column}:${diagnostic.message}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function highlightCode(content, path) {
  const lines = String(content || "").split("\n");
  return lines.map((line) => {
    const highlighted = path?.endsWith(".md") ? highlightMarkdownLine(line) : highlightPythonLine(line);
    return highlighted || "&nbsp;";
  }).join("\n");
}

function summarizeCallObject(object, index) {
  if (object.style === "builder") return summarizeBuilderCallObject(object, index);
  const contextRaw = argumentRaw(object.block, "when") || argumentRaw(object.block, "context");
  const meaningRaw = argumentRaw(object.block, "meaning");
  const requiresRaw = argumentRaw(object.block, "requires");
  const appliesRaw = argumentRaw(object.block, "applies") || argumentRaw(object.block, "applicability");
  const effectsRaw = argumentRaw(object.block, "effects");
  const bid = bidSummary(argumentRaw(object.block, "bid"));
  return {
    ...object,
    index,
    bid,
    auction: auctionPatternFromContext(contextRaw),
    seatPositions: seatPositionsFromContext(contextRaw),
    action: fieldFromDict(meaningRaw, "action_type") || fieldFromConstructor(meaningRaw, "action") || fieldFromConstructor(meaningRaw, "action_type"),
    targetSuit: fieldFromDict(meaningRaw, "target_suit") || fieldFromConstructor(meaningRaw, "target_suit"),
    alertable: booleanFieldFromDict(meaningRaw, "alertable") || booleanFieldFromConstructor(meaningRaw, "alertable"),
    callActTypes: listFieldFromDict(meaningRaw, "call_act_types").concat(listFieldFromConstructor(meaningRaw, "acts")),
    natureLabels: listFieldFromDict(meaningRaw, "nature_labels").concat(listFieldFromConstructor(meaningRaw, "nature")),
    effectsCount: countTopLevelListItems(effectsRaw),
    requiresText: compactRaw(requiresRaw),
    appliesText: compactRaw(appliesRaw),
    effectsText: compactRaw(effectsRaw),
    meaningText: compactRaw(meaningRaw),
    bidRaw: compactRaw(argumentRaw(object.block, "bid")),
  };
}

function summarizeBuilderCallObject(object, index) {
  const bidRaw = assignmentRaw(object.block, "call.bid");
  const requiresRaw = assignmentRaw(object.block, "call.requires");
  const appliesRaw = assignmentRaw(object.block, "call.applies");
  const natureLabels = assignmentList(object.block, "call.meaning.nature").concat(assignmentList(object.block, "call.meaning.nature_labels"));
  const callActTypes = assignmentList(object.block, "call.meaning.acts").concat(assignmentList(object.block, "call.meaning.call_act_types"));
  return {
    ...object,
    index,
    bid: bidSummary(bidRaw),
    auction: assignmentString(object.block, "call.when"),
    seatPositions: assignmentList(object.block, "call.seats").map(Number).filter(Boolean),
    action: assignmentString(object.block, "call.meaning.action") || assignmentString(object.block, "call.meaning.action_type"),
    targetSuit: assignmentString(object.block, "call.meaning.target_suit"),
    alertable: assignmentBoolean(object.block, "call.meaning.alertable"),
    callActTypes,
    natureLabels,
    effectsCount: countWord(object.block, "call.effect("),
    requiresText: compactRaw(requiresRaw),
    appliesText: compactRaw(appliesRaw),
    effectsText: `${countWord(object.block, "call.effect(")} effect assignments`,
    meaningText: compactRaw(builderMeaningAssignments(object.block)),
    bidRaw: compactRaw(bidRaw),
  };
}

function summarizeFrameObject(object) {
  if (object.style === "builder") {
    return {
      ...object,
      frameType: assignmentString(object.block, "frame.frame_type"),
      auction: assignmentString(object.block, "frame.when"),
      sourceCall: assignmentString(object.block, "frame.source_call"),
      stages: assignmentList(object.block, "frame.stages"),
      closeOnActions: assignmentList(object.block, "frame.close_on_actions"),
      variablesText: compactRaw(assignmentRaw(object.block, "frame.variables")),
    };
  }
  const variablesRaw = argumentRaw(object.block, "variables");
  const contextRaw = argumentRaw(object.block, "when") || argumentRaw(object.block, "context");
  return {
    ...object,
    frameType: stringArgument(object.block, "frame_type"),
    auction: auctionPatternFromContext(contextRaw),
    sourceCall: stringArgument(object.block, "source_call"),
    stages: listArgument(object.block, "stages"),
    closeOnActions: listArgument(object.block, "close_on_actions"),
    variablesText: compactRaw(variablesRaw),
  };
}

function summarizePrivateRouteObject(object) {
  if (object.style === "builder") {
    return {
      ...object,
      owner: assignmentString(object.block, "route.owner"),
      goal: assignmentString(object.block, "route.goal"),
      auction: assignmentString(object.block, "route.when"),
      entryCall: assignmentString(object.block, "route.entry_call"),
      workflowText: compactRaw(assignmentRaw(object.block, "route.workflow")),
      preconditionsText: compactRaw(assignmentRaw(object.block, "route.preconditions")),
    };
  }
  const contextRaw = argumentRaw(object.block, "when") || argumentRaw(object.block, "context");
  return {
    ...object,
    owner: stringArgument(object.block, "owner"),
    goal: stringArgument(object.block, "goal"),
    auction: auctionPatternFromContext(contextRaw),
    entryCall: stringArgument(object.block, "entry_call"),
    workflowText: compactRaw(argumentRaw(object.block, "workflow")),
    preconditionsText: compactRaw(argumentRaw(object.block, "preconditions")),
  };
}

function summarizeEvaluatorObject(object) {
  if (object.style === "builder") {
    return {
      ...object,
      evaluatorType: "python_function",
      definitionText: compactRaw(assignmentRaw(object.block, "evaluator.function")),
    };
  }
  const functionRaw = argumentRaw(object.block, "function") || argumentRaw(object.block, "definition");
  return {
    ...object,
    evaluatorType: stringArgument(object.block, "evaluator_type"),
    definitionText: compactRaw(functionRaw),
  };
}

function replaceObject(content, object, block) {
  return `${content.slice(0, object.start)}${block}${content.slice(object.end)}`;
}

function setClassAttribute(block, key, value) {
  const pattern = new RegExp(`^(\\s*)${escapeRegex(key)}\\s*=\\s*([^\\n]*)`, "m");
  const rendered = pyString(value);
  if (pattern.test(block)) return block.replace(pattern, `$1${key} = ${rendered}`);
  return block.replace(/(\n\s+def\s+build\s*\()/, `\n    ${key} = ${rendered}\n$1`);
}

function setBuilderAssignment(block, path, value, options = {}) {
  const pattern = new RegExp(`^(\\s*)${escapeRegex(path)}\\s*=\\s*([^\\n]*)`, "m");
  const rendered = options.raw ? rawAssignmentValue(value) : pyString(value);
  if (pattern.test(block)) return block.replace(pattern, `$1${path} = ${rendered}`);
  return `${block.trimEnd()}\n        ${path} = ${rendered}`;
}

function rawAssignmentValue(value) {
  if (typeof value === "string") return value;
  return rawValue(value);
}

function replaceBuilderId(block, builder, value) {
  const pattern = new RegExp(`self\\.${escapeRegex(builder)}\\(\\s*(['\"])(.*?)\\1\\s*\\)`);
  return block.replace(pattern, `self.${builder}(${pyString(value)})`);
}

function assignmentRaw(block, path) {
  const pattern = new RegExp(`^\\s*${escapeRegex(path)}\\s*=\\s*([^\\n]*)`, "m");
  const match = String(block || "").match(pattern);
  return match ? match[1].trim() : "";
}

function assignmentString(block, path) {
  return stringFromRaw(assignmentRaw(block, path));
}

function assignmentBoolean(block, path) {
  const raw = assignmentRaw(block, path).toLowerCase();
  return raw === "true";
}

function assignmentList(block, path) {
  const raw = assignmentRaw(block, path);
  const quoted = listFromRaw(raw);
  if (quoted.length) return quoted;
  return Array.from(String(raw || "").matchAll(/\b\d+\b/g)).map((item) => item[0]);
}

function builderMeaningAssignments(block) {
  return String(block || "")
    .split("\n")
    .filter((line) => /call\.meaning\./.test(line))
    .map((line) => line.trim())
    .join("; ");
}

function setContextField(block, field, value, options = {}) {
  return setDictKeywordField(block, "context", field, value, options);
}

function setMeaningField(block, field, value, options = {}) {
  return setDictKeywordField(block, "meaning", field, value, options);
}

function setAuctionInBlock(block, auction, seatPositions) {
  const seats = parseSeatPositions(seatPositions);
  const rendered = `Auction(${pyString(auction || "")}${seats.length ? `, seats=[${seats.join(", ")}]` : ""})`;
  const entry = argumentEntry(block, "when") || argumentEntry(block, "context");
  if (entry) return `${block.slice(0, entry.start)}${rendered}${block.slice(entry.end)}`;
  return setKeywordInBlock(block, "when", rendered, { beforeClose: true, raw: true });
}

function setMeaningConstructorField(block, field, value, options = {}) {
  const entry = argumentEntry(block, "meaning");
  const rendered = options.raw ? rawValue(value) : pythonValue(value);
  if (!entry) {
    return setKeywordInBlock(block, "meaning", `Meaning(${field}=${rendered})`, { beforeClose: true, raw: true });
  }

  let raw = entry.raw.trim();
  if (!raw.startsWith("Meaning(")) {
    raw = `Meaning(${field}=${rendered})`;
    return `${block.slice(0, entry.start)}${raw}${block.slice(entry.end)}`;
  }

  const pattern = new RegExp(`\\b${escapeRegex(field)}\\s*=\\s*([^,\\)\\n]+)`, "s");
  if (pattern.test(raw)) {
    raw = raw.replace(pattern, `${field}=${rendered}`);
  } else {
    raw = raw.replace(/\)\s*$/, `, ${field}=${rendered})`);
  }
  return `${block.slice(0, entry.start)}${raw}${block.slice(entry.end)}`;
}

function setDictKeywordField(block, keyword, field, value, options = {}) {
  const entry = argumentEntry(block, keyword);
  if (!entry || !entry.raw.trim().startsWith("{")) return block;
  const rendered = options.raw ? rawValue(value) : pyString(value);
  let raw = entry.raw;
  const pattern = new RegExp(`(['"]${escapeRegex(field)}['"]\\s*:\\s*)([^,}\\n]+)`, "s");
  if (pattern.test(raw)) {
    raw = raw.replace(pattern, `$1${rendered}`);
  } else {
    raw = raw.replace(/\}\s*$/, `, ${pyString(field)}: ${rendered}}`);
  }
  return `${block.slice(0, entry.start)}${raw}${block.slice(entry.end)}`;
}

function setKeywordInBlock(block, key, value, options = {}) {
  const entry = argumentEntry(block, key);
  const rendered = options.raw ? String(value) : pyString(value);
  if (entry) {
    return `${block.slice(0, entry.start)}${rendered}${block.slice(entry.end)}`;
  }
  if (!options.beforeClose) return block;
  return block.replace(/\)\s*$/, `    ${key}=${rendered},\n)`);
}

function argumentRaw(block, key) {
  return argumentEntry(block, key)?.raw || "";
}

function stringArgument(block, key) {
  const raw = argumentRaw(block, key).trim();
  return stringFromRaw(raw);
}

function listArgument(block, key) {
  return listFromRaw(argumentRaw(block, key));
}

function argumentEntry(block, key) {
  const pattern = new RegExp(`\\b${escapeRegex(key)}\\s*=`);
  const match = pattern.exec(block);
  if (!match) return null;
  const start = match.index + match[0].length;
  const end = scanArgumentEnd(block, start);
  return { start, end, raw: block.slice(start, end).trim() };
}

function scanArgumentEnd(text, start) {
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = start; index < text.length; index += 1) {
    const char = text[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"') {
      quote = char;
      continue;
    }
    if ("([{".includes(char)) depth += 1;
    else if (")]}'".includes(char)) depth = Math.max(0, depth - 1);
    else if (char === "," && depth === 0) return index;
  }
  return text.length;
}

function bidSummary(raw) {
  const trimmed = raw.trim();
  const stringValue = stringFromRaw(trimmed);
  if (stringValue) return { kind: "absolute", label: stringValue, detail: "" };
  const bidValue = constructorStringArgument(trimmed, "Bid");
  if (bidValue) return { kind: "absolute", label: bidValue, detail: "" };
  if (trimmed.startsWith("StepAfterState(")) {
    return {
      kind: "relative",
      label: "Relative step",
      detail: compactRaw(trimmed),
    };
  }
  if (!trimmed) return { kind: "missing", label: "No bid parsed", detail: "" };
  return { kind: "expression", label: "Bid expression", detail: compactRaw(trimmed) };
}

function renderBidExpression(value) {
  const text = String(value || "P").trim();
  if (!text) return "Bid('P')";
  if (looksLikeExpression(text)) return text;
  return `Bid(${pyString(text.toUpperCase())})`;
}

function renderBuilderBidValue(value) {
  const text = String(value || "P").trim();
  if (!text) return pyString("P");
  if (looksLikeExpression(text) || text.startsWith("{")) return text;
  return pyString(text.toUpperCase());
}

function stringFromRaw(raw) {
  const match = raw.match(/^(['"])([\s\S]*?)\1$/);
  return match ? match[2] : "";
}

function constructorStringArgument(raw, constructor) {
  const pattern = new RegExp(`^${escapeRegex(constructor)}\\(\\s*(['"])([\\s\\S]*?)\\1`);
  const match = String(raw || "").trim().match(pattern);
  return match ? match[2] : "";
}

function auctionPatternFromContext(raw) {
  return constructorStringArgument(raw, "Auction") || fieldFromDict(raw, "auction_pattern");
}

function seatPositionsFromContext(raw) {
  const constructorSeats = listFieldFromConstructor(raw, "seats").concat(listFieldFromConstructor(raw, "seat_positions"));
  if (constructorSeats.length) return constructorSeats.map(Number).filter(Boolean);
  return listFieldFromDict(raw, "seat_positions").map(Number).filter(Boolean);
}

function fieldFromDict(raw, field) {
  const pattern = new RegExp(`['"]${escapeRegex(field)}['"]\\s*:\\s*(['"])([\\s\\S]*?)\\1`);
  const match = raw.match(pattern);
  if (match) return match[2];
  const barePattern = new RegExp(`['"]${escapeRegex(field)}['"]\\s*:\\s*([A-Za-z_][A-Za-z0-9_]*)`);
  const bareMatch = raw.match(barePattern);
  return bareMatch ? bareMatch[1] : "";
}

function booleanFieldFromDict(raw, field) {
  const pattern = new RegExp(`['"]${escapeRegex(field)}['"]\\s*:\\s*(True|False|true|false)`);
  const match = raw.match(pattern);
  if (!match) return false;
  return match[1].toLowerCase() === "true";
}

function booleanFieldFromConstructor(raw, field) {
  const pattern = new RegExp(`\\b${escapeRegex(field)}\\s*=\\s*(True|False|true|false)`);
  const match = String(raw || "").match(pattern);
  if (!match) return false;
  return match[1].toLowerCase() === "true";
}

function listFieldFromDict(raw, field) {
  const pattern = new RegExp(`['"]${escapeRegex(field)}['"]\\s*:\\s*(\\[[\\s\\S]*?\\])`);
  const match = raw.match(pattern);
  return match ? listFromRaw(match[1]) : [];
}

function listFieldFromConstructor(raw, field) {
  const pattern = new RegExp(`\\b${escapeRegex(field)}\\s*=\\s*(\\[[\\s\\S]*?\\])`);
  const match = String(raw || "").match(pattern);
  if (!match) return [];
  const quoted = listFromRaw(match[1]);
  if (quoted.length) return quoted;
  return Array.from(match[1].matchAll(/\b\d+\b/g)).map((item) => item[0]);
}

function fieldFromConstructor(raw, field) {
  const pattern = new RegExp(`${escapeRegex(field)}\\s*=\\s*(['"])([\\s\\S]*?)\\1`);
  const match = raw.match(pattern);
  return match ? match[2] : "";
}

function listFromRaw(raw) {
  return Array.from(String(raw || "").matchAll(/(['"])(.*?)\1/g)).map((match) => match[2]);
}

function parseSeatPositions(value) {
  if (Array.isArray(value)) return value;
  return String(value || "")
    .split(/[,\s]+/)
    .map((item) => Number(item.trim()))
    .filter((item) => Number.isInteger(item) && item >= 1 && item <= 4);
}

function rawValue(value) {
  if (typeof value === "boolean") return value ? "True" : "False";
  if (Array.isArray(value)) return `[${value.join(", ")}]`;
  if (value === "none" || value === "") return "None";
  return pyString(value);
}

function pythonValue(value) {
  if (value === "" || value === "none" || value === null || value === undefined) return "None";
  if (typeof value === "boolean") return value ? "True" : "False";
  if (Array.isArray(value)) return `[${value.map(pythonValue).join(", ")}]`;
  return pyString(value);
}

function pyString(value) {
  return `'${String(value ?? "").replace(/\\/g, "\\\\").replace(/'/g, "\\'")}'`;
}

function sanitizeIdentifier(value) {
  const text = String(value || "new_call").replace(/[^A-Za-z0-9_]/g, "_");
  return /^[A-Za-z_]/.test(text) ? text : `call_${text}`;
}

function countWord(raw, word) {
  if (!raw) return 0;
  return (raw.match(new RegExp(escapeRegex(word), "g")) || []).length;
}

function countTopLevelListItems(raw) {
  const trimmed = String(raw || "").trim();
  if (!trimmed.startsWith("[")) return 0;
  let count = 0;
  let depth = 0;
  let quote = "";
  for (const char of trimmed) {
    if (quote) {
      if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"') {
      quote = char;
    } else if ("[{(".includes(char)) {
      depth += 1;
      if (depth === 2) count += 1;
    } else if ("]})".includes(char)) {
      depth = Math.max(0, depth - 1);
    }
  }
  return count;
}

function compactRaw(raw) {
  return String(raw || "").replace(/\s+/g, " ").trim();
}

function looksLikeExpression(value) {
  return /^[A-Za-z_][A-Za-z0-9_]*\(/.test(String(value || "").trim());
}

function includeLeadingBlankLine(content, start) {
  if (start >= 2 && content.slice(start - 2, start) === "\n\n") return start - 1;
  return start;
}

function extractBlocks(content, name) {
  const blocks = [];
  const marker = `${name}(`;
  let searchFrom = 0;
  while (searchFrom < content.length) {
    const start = content.indexOf(marker, searchFrom);
    if (start === -1) break;
    let depth = 1;
    let quote = "";
    let escaped = false;
    for (let index = start + marker.length; index < content.length; index += 1) {
      const char = content[index];
      if (quote) {
        if (escaped) escaped = false;
        else if (char === "\\") escaped = true;
        else if (char === quote) quote = "";
        continue;
      }
      if (char === "'" || char === '"') {
        quote = char;
        continue;
      }
      if (char === "(") depth += 1;
      if (char === ")") depth -= 1;
      if (depth === 0) {
        blocks.push({ block: content.slice(start, index + 1), start, end: index + 1 });
        searchFrom = index + 1;
        break;
      }
    }
    if (searchFrom <= start) break;
  }
  return blocks;
}

function extractClassBlocks(content, baseName) {
  const text = String(content || "");
  const matches = Array.from(text.matchAll(new RegExp(`^class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\(\\s*${escapeRegex(baseName)}\\s*\\)\\s*:`, "gm")));
  return matches.map((match, index) => {
    const start = match.index;
    const next = index + 1 < matches.length ? matches[index + 1].index : text.length;
    return {
      block: text.slice(start, next).trimEnd(),
      start,
      end: next,
      className: match[1],
    };
  });
}

function extractBuilderBlocks(content, builderName) {
  const text = String(content || "");
  const marker = /^\s{8}(call|frame|route|evaluator|relay)\s*=\s*self\.(call|frame|route|evaluator|relay)\(\s*(['"])(.*?)\3\s*\)/gm;
  const matches = Array.from(text.matchAll(marker)).filter((match) => match[1] === match[2]);
  return matches.filter((match) => match[1] === builderName).map((match) => {
    const start = match.index;
    const nextMatch = matches.find((item) => item.index > start);
    const next = nextMatch ? nextMatch.index : text.length;
    let end = next;
    const slice = text.slice(start, next);
    const methodBoundary = slice.search(/\n    def\s+/);
    if (methodBoundary > 0) end = start + methodBoundary;
    return {
      block: text.slice(start, end).trimEnd(),
      start,
      end,
      id: match[4],
    };
  });
}

function stringAttribute(block, key) {
  const raw = assignmentRaw(block, key);
  return stringFromRaw(raw);
}

function highlightMarkdownLine(line) {
  const escaped = escapeHtml(line);
  if (/^\s*#/.test(line)) return `<span class="tok-heading">${escaped}</span>`;
  if (/^\s*[-*]\s/.test(line)) return `<span class="tok-keyword">${escaped}</span>`;
  return escaped;
}

function highlightPythonLine(line) {
  const keywords = new Set(["class", "def", "return", "if", "elif", "else", "for", "in", "and", "or", "not", "None", "True", "False"]);
  const constructors = new Set([...OBJECT_TYPES, "Author", "Meaning", "State", "StepAfterState", "self"]);
  const suits = new Set(["S", "H", "D", "C", "N", "P", "X", "R"]);
  let output = "";
  let index = 0;
  let bracketDepth = 0;

  while (index < line.length) {
    const char = line[index];
    if (char === "#") {
      output += `<span class="tok-comment">${escapeHtml(line.slice(index))}</span>`;
      break;
    }
    if (char === "'" || char === '"') {
      const quote = char;
      let end = index + 1;
      let escaped = false;
      while (end < line.length) {
        const next = line[end];
        if (escaped) escaped = false;
        else if (next === "\\") escaped = true;
        else if (next === quote) {
          end += 1;
          break;
        }
        end += 1;
      }
      output += `<span class="tok-string">${escapeHtml(line.slice(index, end))}</span>`;
      index = end;
      continue;
    }
    if (/[A-Za-z_]/.test(char)) {
      let end = index + 1;
      while (end < line.length && /[A-Za-z0-9_]/.test(line[end])) end += 1;
      const word = line.slice(index, end);
      let className = "";
      if (keywords.has(word)) className = "tok-keyword";
      else if (constructors.has(word)) className = "tok-constructor";
      else if (suits.has(word)) className = "tok-suit";
      output += className ? `<span class="${className}">${word}</span>` : escapeHtml(word);
      index = end;
      continue;
    }
    if (/[0-9]/.test(char)) {
      let end = index + 1;
      while (end < line.length && /[0-9.]/.test(line[end])) end += 1;
      output += `<span class="tok-number">${escapeHtml(line.slice(index, end))}</span>`;
      index = end;
      continue;
    }
    if ("()[]{}".includes(char)) {
      const className = `tok-bracket depth-${bracketDepth % 4}`;
      if ("([{".includes(char)) bracketDepth += 1;
      if (")]}".includes(char)) bracketDepth = Math.max(0, bracketDepth - 1);
      output += `<span class="${className}">${escapeHtml(char)}</span>`;
      index += 1;
      continue;
    }
    output += escapeHtml(char);
    index += 1;
  }
  return output;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function policyFunctionNames(text) {
  const match = String(text || "").match(/policy_functions\s*=\s*\[([\s\S]*?)\]/m);
  if (!match) return [];
  return Array.from(match[1].matchAll(/\b([A-Za-z_][A-Za-z0-9_]*)\b/g))
    .map((entry) => entry[1])
    .filter((name) => !["None", "True", "False"].includes(name));
}

function functionDocstring(body) {
  const match = String(body || "").match(/^\s*def[\s\S]*?:\s*\n\s*(["']{3})([\s\S]*?)\1/m);
  return match ? match[2].trim() : "";
}

function functionBlockEnd(text, start, fallbackEnd) {
  const slice = text.slice(start, fallbackEnd);
  const lineMatches = Array.from(slice.matchAll(/\n(?=\S)/g));
  for (const match of lineMatches) {
    const absolute = start + match.index + 1;
    if (absolute === start) continue;
    const line = text.slice(absolute, text.indexOf("\n", absolute) === -1 ? text.length : text.indexOf("\n", absolute));
    if (!line.startsWith("def ")) return absolute;
  }
  return fallbackEnd;
}

function candidateCalls(body) {
  const calls = new Set();
  for (const match of String(body || "").matchAll(/candidates\.(?:get|for_call)\(\s*(['"])(.*?)\1/g)) {
    calls.add(match[2]);
  }
  for (const match of String(body || "").matchAll(/candidates\.first_available\(([\s\S]*?)\)/g)) {
    for (const call of match[1].matchAll(/(['"])(.*?)\1/g)) {
      calls.add(call[2]);
    }
  }
  return Array.from(calls);
}

function candidateMethods(body) {
  return Array.from(new Set(
    Array.from(String(body || "").matchAll(/candidates\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g)).map((match) => match[1]),
  ));
}

function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
