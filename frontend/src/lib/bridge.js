export function parseAuction(text) {
  const value = String(text || "").toUpperCase().replace(/\s+/g, "");
  const calls = [];
  for (let index = 0; index < value.length;) {
    const char = value[index];
    if (char === "P" || char === "X" || char === "R") {
      calls.push(char);
      index += 1;
      continue;
    }
    if ("1234567".includes(char) && index + 1 < value.length) {
      calls.push(`${char}${value[index + 1]}`);
      index += 2;
      continue;
    }
    index += 1;
  }
  return calls;
}

export function parseHand(text) {
  const result = { S: "", H: "", D: "", C: "" };
  let suit = null;
  const value = String(text || "").toUpperCase();
  for (let index = 0; index < value.length; index += 1) {
    const raw = value[index];
    if (raw in result) {
      suit = raw;
      continue;
    }
    if (!suit || /\s/.test(raw)) continue;
    if (raw === "1" && value[index + 1] === "0") {
      result[suit] += "T";
      index += 1;
      continue;
    }
    if ("AKQJT98765432X".includes(raw)) result[suit] += raw;
  }
  return result;
}

export function suitSymbol(suit) {
  return { S: "\u2660", H: "\u2665", D: "\u2666", C: "\u2663" }[suit] || suit;
}

export function suitClass(suit) {
  return {
    S: "suit-spades",
    H: "suit-hearts",
    D: "suit-diamonds",
    C: "suit-clubs",
    N: "strain-notrump",
  }[String(suit || "").toUpperCase()] || "";
}

export function callLabel(call) {
  const normalized = String(call || "").toUpperCase();
  if (normalized === "P") return "Pass";
  if (normalized === "X") return "X";
  if (normalized === "R" || normalized === "XX") return "XX";
  const match = normalized.match(/^([1-7])([CDHSN])$/);
  if (!match) return normalized;
  if (match[2] === "N") return `${match[1]}NT`;
  return `${match[1]}${suitSymbol(match[2])}`;
}

export function callClass(call) {
  const normalized = String(call || "").toUpperCase();
  if (normalized === "P") return "call-pass";
  if (normalized === "X") return "call-double";
  if (normalized === "R" || normalized === "XX") return "call-redouble";
  const match = normalized.match(/^([1-7])([CDHSN])$/);
  return match ? suitClass(match[2]) : "";
}

export function auctionFromRecords(records) {
  return (records || []).map((record) => callLabel(record.call)).join(" ");
}

export function seatName(seat) {
  return { n: "North", e: "East", s: "South", w: "West" }[String(seat || "").toLowerCase()] || seat;
}

export function handSummary(text) {
  const hand = parseHand(text);
  const shape = ["S", "H", "D", "C"].map((suit) => hand[suit].length).join("-");
  const hcp = estimateHcp(hand);
  return `${hcp} HCP / ${shape}`;
}

export function rankLabel(rank) {
  return String(rank || "").toUpperCase() === "T" ? "10" : rank;
}

export function meaningText(result) {
  const meaning = result?.public_meaning?.meaning ?? {};
  const parts = [meaning.action_type, meaning.target_suit].filter(Boolean);
  return parts.length ? parts.join(" / ") : "No public meaning";
}

export function logicHint(record) {
  const seat = seatName(record?.seat);
  const call = callLabel(record?.call);
  const explanation = record?.explanation;
  if (!explanation) return `${seat}: ${call}\nAutomatic opponent call in the local simulator.`;

  const meaning = explanation.public_meaning?.meaning ?? {};
  const origin = explanation.public_meaning?.origin ?? {};
  const internal = explanation.internal_origin ?? {};
  const policy = internal.selection_policy ?? {};
  const compared = (internal.compared_candidates ?? []).map((candidate) => callLabel(candidate.call));
  const diagnostics = explanation.diagnostics ?? [];
  const lines = [`${seat}: ${call}`];

  const action = meaning.action_type || meaning.action || "";
  if (action) lines.push(`Meaning: ${humanize(action)}${meaning.target_suit ? `, ${suitWord(meaning.target_suit)}` : ""}`);
  if (meaning.alertable) lines.push("Alert: yes");
  if (origin.gadget_id || origin.object_id) {
    lines.push(`Origin: ${[origin.gadget_id, origin.object_id].filter(Boolean).join(" / ")}`);
  }
  if (policy.object_id) lines.push(`Policy: ${policy.object_id}`);
  if (compared.length > 1) lines.push(`Compared: ${compared.join(", ")}`);
  if (diagnostics.length) lines.push(`Diagnostics: ${diagnostics.join("; ")}`);
  return lines.join("\n");
}

function estimateHcp(hand) {
  const values = { A: 4, K: 3, Q: 2, J: 1 };
  return Object.values(hand).join("").split("").reduce((sum, rank) => sum + (values[rank] || 0), 0);
}

function suitWord(suit) {
  return { S: "spades", H: "hearts", D: "diamonds", C: "clubs", N: "notrump" }[String(suit || "").toUpperCase()] || suit;
}

function humanize(value) {
  return String(value || "").replaceAll("_", " ");
}
