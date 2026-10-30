import { React, e } from "../ui/react.js";
import { callClass } from "../lib/bridge.js";
import {
  completeScannerReport, copyScannerReport, deleteScannerReport,
  listScannerReports, readScannerReport, scannerRunStatus, startScannerRun,
  stopScannerRun,
} from "../api/gibleApi.js";
import {
  DEFAULT_THRESHOLDS, filterProcessGroups, filterScannerGroups,
  groupCategories, pairFlags, pairMatches, paginateGroups,
  processBoardCount, processCategories, processFlags,
  processWorstFailure, selectPairForGroup, wrongGameScores,
} from "../lib/ivScanner.js";

const CATEGORY = {
  block: { title: "裁 / TD", detail: "Auction has no supported next call" },
  missed: { title: "丢 / LOSE", detail: "Game or slam was available" },
  down: { title: "宕 / SET", detail: "Selected contract sets too often" },
  wrong: { title: "错 / WRONG", detail: "chosen / best-other success ratio below threshold" },
};
const FLAG = {
  contract_failure: "SET · chosen contract fails",
  missed_game: "LOSE · game available",
  missed_small_slam: "LOSE · small slam available",
  missed_grand_slam: "LOSE · grand slam available",
  wrong_game: "WRONG · chosen / best-other success ratio",
};
const SUITS = [["S", "♠"], ["H", "♥"], ["D", "♦"], ["C", "♣"]];
const FULL_SCAN_SHAPES = 23;
const OVERVIEW_PAGE_SIZE = 100;

const pct = (value) => value == null ? "—" : `${(value * 100).toFixed(0)}%`;

const THRESHOLD_CONTROLS = [
  { key: "set", label: "SET 宕 failure", min: 0.4, max: 0.8, step: 0.01,
    inputStep: 0.01, unit: "percent" },
  { key: "missed", label: "LOSE 丢 availability", min: 0.1, max: 0.5, step: 0.01,
    inputStep: 0.01, unit: "percent" },
  { key: "wrong", label: "WRONG 错 success ratio", min: 0.5, max: 1, step: 0.01,
    inputStep: 0.01, unit: "ratio" },
  { key: "wrongFloor", label: "WRONG best-other floor", min: 0.2, max: 0.6,
    step: 0.01, inputStep: 0.01, unit: "percent" },
];

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function thresholdDisplay(control, value) {
  return control.unit === "percent"
    ? Math.round(value * 100)
    : Number(value).toFixed(2);
}

function thresholdValue(control, raw) {
  const parsed = Number(raw);
  if (!Number.isFinite(parsed)) return null;
  const value = control.unit === "percent" ? parsed / 100 : parsed;
  return Number(clamp(value, control.min, control.max).toFixed(4));
}

function ThresholdControl({ control, value, onUpdate }) {
  const [draft, setDraft] = React.useState(() => thresholdDisplay(control, value));
  React.useEffect(() => {
    setDraft(thresholdDisplay(control, value));
  }, [control, value]);
  const commit = (raw) => {
    const next = thresholdValue(control, raw);
    if (next != null) onUpdate(control.key, next);
    setDraft(thresholdDisplay(control, next == null ? value : next));
  };
  const step = (direction) => {
    const next = Number(clamp(
      value + direction * control.inputStep, control.min, control.max).toFixed(4));
    onUpdate(control.key, next);
  };
  return e("div", { className: "iv-threshold" },
    e("span", null, control.label),
    e("input", {
      type: "range", min: control.min, max: control.max, step: control.step,
      value, "aria-label": control.label,
      onChange: (event) => onUpdate(control.key, Number(event.target.value)),
    }),
    e("div", { className: "iv-threshold-value" },
      e("button", {
        type: "button", className: "iv-step",
        "aria-label": `Decrease ${control.label}`,
        onClick: () => step(-1),
      }, "←"),
      e("input", {
        type: "number",
        min: control.unit === "percent" ? Math.round(control.min * 100) : control.min,
        max: control.unit === "percent" ? Math.round(control.max * 100) : control.max,
        step: control.unit === "percent" ? 1 : 0.01,
        value: draft, "aria-label": `${control.label} value`,
        onChange: (event) => setDraft(event.target.value),
        onBlur: (event) => commit(event.target.value),
        onKeyDown: (event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            commit(event.currentTarget.value);
          }
        },
      }),
      e("button", {
        type: "button", className: "iv-step",
        "aria-label": `Increase ${control.label}`,
        onClick: () => step(1),
      }, "→"),
      e("em", null, control.unit === "percent" ? "%" : "ratio"),
    ),
  );
}

function compactSuits(hand = "") {
  const fields = hand.match(/^S(.*?)H(.*?)D(.*?)C(.*)$/);
  return fields
    ? fields.slice(1).map((holding) => (
      holding && holding !== "-" ? holding : "—"))
    : ["—", "—", "—", "—"];
}

const HAND_POINTS = { A: 4, K: 3, Q: 2, J: 1 };

function makeRate(rates) {
  const failure = rates?.contract_failure;
  return typeof failure === "number" && Number.isFinite(failure)
    ? 1 - failure
    : null;
}

function handStats(hand = "") {
  const holdings = compactSuits(hand);
  const shape = holdings.map((holding) => (
    holding === "—" ? 0 : holding.length));
  const hcp = holdings.reduce((sum, holding) => sum + [...holding]
    .reduce((points, rank) => points + (HAND_POINTS[rank] || 0), 0), 0);
  return { shape, hcp };
}

function miniHand(hand, title, tone = "") {
  const holdings = compactSuits(hand);
  const stats = handStats(hand);
  return e("section", { className: `iv-hand iv-mini-hand ${tone}` },
    e("div", { className: "iv-hand-heading" },
      e("strong", null, title),
      e("span", null, `${stats.hcp} HCP · ${stats.shape.join("–")}`)),
    SUITS.map(([suit, symbol], index) => e("div", {
      className: `iv-suit iv-suit-${suit.toLowerCase()}`, key: suit,
    }, e("span", null, symbol), e("b", null, holdings[index]))),
  );
}

function bestProcessMake(process = {}) {
  const values = (process.contracts || []).map((item) => makeRate(item.rates))
    .filter((value) => value != null);
  return values.length ? Math.max(...values) : null;
}

function handCard(seat, caseData) {
  const holdings = compactSuits(caseData.hands[seat]);
  const name = seat === "n" ? "North" : "South";
  const shape = caseData[`${name.toLowerCase()}_shape`]?.join("–") ?? "";
  return e("section", { className: "iv-hand", key: seat },
    e("div", { className: "iv-hand-heading" },
      e("strong", null, name),
      e("span", null, `${caseData[`${seat === "n" ? "north" : "south"}_hcp`]} HCP · ${caseData[`${seat === "n" ? "north" : "south"}_kr`]} K–R · ${shape}`),
    ),
    SUITS.map(([suit, symbol], index) => e("div", {
      className: `iv-suit iv-suit-${suit.toLowerCase()}`, key: suit,
    }, e("span", null, symbol), e("b", null, holdings[index]))),
  );
}

function auctionRows(pair) {
  const tiles = (pair.calls || []).map((call) => ({ call }));
  if (pair.status === "blocked") {
    tiles.push({ td: true, seat: pair.blocked?.seat });
  }
  const rows = [];
  for (let index = 0; index < tiles.length; index += 4) rows.push(tiles.slice(index, index + 4));
  return rows;
}

function auctionTile(tile, index) {
  if (tile.td) {
    const seat = tile.seat?.toUpperCase() || "?";
    return e("span", {
      key: index, className: "iv-call-td",
      "aria-label": `TD at ${seat}`, title: `TD · ${seat} to call`,
    }, "TD");
  }
  return e("span", { key: index, className: `iv-call ${callClass(tile.call)}` }, tile.call);
}

function warningDetail(flag, pair, thresholds) {
  const rates = pair.rates || {};
  if (flag === "contract_failure") {
    return `${pct(rates.contract_failure)} set · alert above ${pct(thresholds.set)}`;
  }
  if (flag === "wrong_game") {
    const { ratio, bestOther } = wrongGameScores(pair);
    const ratioText = ratio == null ? "—" : Number(ratio).toFixed(2);
    return `RATIO ${ratioText} · below ${Number(thresholds.wrong).toFixed(2)}; best-other ${pct(bestOther)} above ${pct(thresholds.wrongFloor)}`;
  }
  return `${pct(rates[flag])} available · alert above ${pct(thresholds.missed)}`;
}

function pairRailButton(pair, selected, onSelect) {
  return e("button", {
    key: pair.id, type: "button",
    className: `iv-pair-button ${selected ? "selected" : ""}`,
    "aria-pressed": selected,
    onClick: () => onSelect(pair.id),
  },
    e("span", { className: "iv-pair-top" },
      e("strong", null, `#${pair.id} · P${(pair.pair_slot ?? 0) + 1}`),
      e("span", null, pair.contract
        || (pair.status === "blocked" ? "TD" : pair.status === "limit" ? "LIMIT" : "—"))),
    e("span", { className: "iv-pair-auction" }, pair.auction || "No calls recorded"),
  );
}

function ewResultStrip(pair) {
  const results = pair.ew_results || [];
  if (!results.length) return null;
  return e("div", { className: "iv-detail-section" },
    e("h4", null, `E/W results · ${pair.contract} by ${pair.declarer?.toUpperCase()}`),
    e("div", { className: "iv-ew-strip" },
      e("div", { className: "iv-ew-scroll" },
        e("table", null,
          e("thead", null, e("tr", null,
            results.map((_, index) => e("th", { scope: "col", key: index }, `EW ${index + 1}`)))),
          e("tbody", null, e("tr", null,
            results.map((result, index) => e("td", {
              key: index, className: `iv-ew-outcome ${result.outcome === "MAKE" ? "make" : "set"}`,
            },
              result.outcome,
              result.lose && e("em", {
                className: "iv-ew-lose",
                title: `Missed ${result.missed_target || "target"}`,
              }, "LOSE")))))))));
}

function pairDetail(pair, group, thresholds) {
  if (!pair) return e("div", { className: "iv-empty-detail" },
    "Select a sampling cell, then pick one of its N/S pairs to inspect that pair's hands and auction.");
  const rates = pair.rates || {};
  const make = makeRate(rates);
  const flags = pairFlags(pair, thresholds);
  const alternatives = Object.entries(pair.alternative_game_rates || {})
    .filter(([, rate]) => rate > 0);
  const slot = (pair.pair_slot ?? 0) + 1;
  const title = pair.status === "limit"
    ? "Call limit reached"
    : pair.status === "blocked"
      ? `TD · ${pair.blocked?.seat?.toUpperCase() || "?"}`
      : pair.contract
        ? `${pair.contract} · ${pair.declarer?.toUpperCase()} declares`
        : "No contract";
  return e("div", { className: "iv-detail-body" },
    e("div", { className: "iv-detail-heading" },
      e("span", { className: "iv-eyebrow" },
        `DEAL #${pair.id} · PAIR ${slot}/${group?.actual_pair_count ?? 1}`),
      e("h3", null, title),
      e("p", null, pair.auction || "No calls recorded"),
      make != null && e("div", {
        className: `iv-make-badge ${make < 1 - thresholds.set ? "bad" : "good"}`,
      }, "CONTRACT MAKE ", e("strong", null, pct(make)),
      e("small", null, `${pair.dds_boards ?? "—"} DDS boards`)),
    ),
    e("div", { className: "iv-hands" }, handCard("n", pair), handCard("s", pair)),
    e("div", { className: "iv-detail-section" },
      e("h4", null, "Auction"),
      e("div", { className: "iv-auction-rows" },
        auctionRows(pair).map((row, rowIndex) => e("div", {
          className: "iv-auction-row", key: rowIndex,
        }, row.map((tile, index) => auctionTile(tile, index))))),
    ),
    pair.status === "limit" && e("div", { className: "iv-detail-section iv-block-diagnostic" },
      e("h4", null, "Call limit"),
      e("p", null, "The auction reached the maximum number of calls, so no contract or DDS evidence was recorded for this pair.")),
    pair.status === "blocked" && e("div", { className: "iv-detail-section iv-block-diagnostic" },
      e("h4", null, `TD · ${pair.blocked?.seat?.toUpperCase() || "?"}`),
      (pair.blocked?.diagnostics || []).map((line, index) => e("p", { key: index }, line))),
    flags.length > 0 && e("div", { className: "iv-detail-section" },
      e("h4", null, "Warnings"),
      e("div", { className: "iv-warning-list" },
        flags.map((flag) => e("div", { key: flag },
          e("strong", null, FLAG[flag] || flag),
          e("span", null, warningDetail(flag, pair, thresholds)),
        )),
      ),
      alternatives.length > 0 && e("p", { className: "iv-alternatives" },
        "Other-game success rates: ",
        alternatives.map(([name, rate]) => `${name} ${pct(rate)}`).join(" · "),
      ),
      e("p", { className: "iv-evidence" },
        `${pair.class_pairs ?? "—"} N/S pairs in this auction group · ${pair.dds_boards ?? "—"} DDS boards. Rates use all pooled boards.`),
    ),
    ewResultStrip(pair),
  );
}

function processKey(process) {
  return (process.process || []).join(" ") || process.auction
    || `${process.cases} cases`;
}

function processRate(value, threshold, inverse = false) {
  if (value == null) return { text: "—", bad: false, width: 0 };
  const bad = inverse ? value < threshold : value > threshold;
  return {
    text: inverse ? Number(value).toFixed(2) : pct(value),
    bad,
    width: Math.max(0, Math.min(1, Number(value))) * 100,
  };
}

function rateMeter(label, value, threshold, inverse = false) {
  const rate = processRate(value, threshold, inverse);
  return e("div", { className: `iv-rate ${rate.bad ? "bad" : "ok"}` },
    e("span", { className: "iv-rate-label" }, label),
    e("span", { className: "iv-rate-track" },
      e("i", { style: { width: `${rate.width}%` } })),
    e("b", null, rate.text),
  );
}

function processFlagTags(process, thresholds) {
  const categories = processCategories(process, thresholds);
  const flags = processFlags(process, thresholds);
  return e("span", { className: "iv-case-tags" },
    categories.map((key) => e("b", {
      key, className: `iv-tag iv-tag-${key}`,
    }, CATEGORY[key]?.title || key)),
    categories.length === 0 && e("b", { className: "iv-tag iv-tag-clean" },
      "CLEAN"),
    flags.includes("wrong_game") && e("b", {
      className: "iv-tag iv-tag-wrong", title: "chosen / best-other ratio",
    }, "RATIO"),
  );
}

function contractCard(item, thresholds) {
  const rates = item.rates || {};
  const missed = Math.max(
    rates.missed_game ?? 0, rates.missed_small_slam ?? 0,
    rates.missed_grand_slam ?? 0);
  const flags = processCategories({ contracts: [item] }, thresholds);
  return e("article", { className: "iv-contract-card", key: `${item.contract}-${item.declarer}` },
    e("header", null,
      e("strong", null, item.contract || "—"),
      e("span", null, `${String(item.declarer || "").toUpperCase()} declares`),
      e("em", null, `${item.boards ?? 0} boards`)),
    e("div", { className: "iv-contract-rates" },
      rateMeter("MAKE", makeRate(rates), 1 - thresholds.set, true),
      rateMeter("LOSE", missed, thresholds.missed),
      rateMeter("WRONG", rates.wrong_game, thresholds.wrong, true)),
    flags.length > 0 && e("div", { className: "iv-contract-flags" },
      flags.map((key) => e("b", {
        key, className: `iv-tag iv-tag-${key}`,
      }, CATEGORY[key]?.title || key))),
  );
}

function poolTable(title, groups, kind, thresholds, selectedIndex, onSelect) {
  if (!groups?.length) {
    return e("div", { className: "iv-pool-block" },
      e("h4", null, title),
      e("p", { className: "iv-empty-list" }, "No hands in this pool."));
  }
  return e("div", { className: "iv-pool-block" },
    e("div", { className: "iv-pool-heading" },
      e("h4", null, title),
      e("span", null, `${groups.length} shape·band pools`)),
    e("div", { className: "iv-pool-scroll" },
      e("table", { className: "iv-pool-table" },
        e("thead", null, e("tr", null,
          ["Shape", kind === "north" ? "Mode" : "HCP",
            ...(kind === "north" ? ["HCP", "K–R"] : []),
            "Hands", "Dropped", "Flags"].map((label) => e("th", {
              key: label, scope: "col",
            }, label)))),
        e("tbody", null, groups.map((group, index) => {
          const categories = Object.entries(group.categories || {})
            .filter(([, count]) => count > 0).map(([key]) => key);
          return e("tr", {
            key: `${group.north_shape || group.south_shape}-${index}`,
            className: `iv-pool-row ${selectedIndex === index ? "selected" : ""}`,
            onClick: () => onSelect?.(index),
            title: "Use this shape·band pool as the primary view",
          },
            e("td", null,
              e("span", { className: "iv-shape-chip" },
                (group.north_shape || group.south_shape || []).join("–") || "?")),
            e("td", null, kind === "north" ? group.opener_mode : group.south_hcp),
            ...(kind === "north" ? [
              e("td", null, group.hcp_band),
              e("td", null, group.kr_band),
            ] : []),
            e("td", null, `${group.stored ?? 0}/${group.cases ?? 0}`),
            e("td", null, group.dropped ?? 0),
            e("td", null, categories.length
              ? e("span", { className: "iv-pool-flags" },
                categories.map((key) => e("b", {
                  key, className: `iv-tag iv-tag-${key}`,
                }, CATEGORY[key]?.title || key)))
              : e("span", { className: "iv-pool-clean" }, "—")),
          );
        })))));
}

function processCard(process, selected, thresholds, onSelect) {
  const categories = processCategories(process, thresholds);
  return e("button", {
    key: processKey(process), type: "button",
    className: `iv-case iv-process-card ${selected ? "selected" : ""}`,
    onClick: () => onSelect(processKey(process)),
    "aria-pressed": selected,
  },
    e("span", { className: "iv-case-top" },
      e("strong", null, `${process.cases ?? 0} N/S pairs`),
      e("span", null, `${processBoardCount(process)} DDS boards`)),
    processFlagTags(process, thresholds),
    e("span", { className: "iv-case-auction" }, process.auction || "—"),
    e("span", { className: "iv-process-contracts" },
      (process.contracts || []).slice(0, 4).map((item) => e("em", {
        key: `${item.contract}-${item.declarer}`,
      }, `${item.contract} ${String(item.declarer || "").toUpperCase()}`)),
      (process.contracts || []).length > 4 && e("em", null, "+ more")),
    bestProcessMake(process) != null && e("span", {
      className: "iv-process-worst",
    }, `best MAKE ${pct(bestProcessMake(process))}`),
    process.overflow > 0 && e("span", { className: "iv-process-overflow" },
      `+${process.overflow} overflowed`),
  );
}

const PROCESS_SEATS = ["N", "E", "S", "W"];

function processAuction(process, td) {
  const calls = process.process || [];
  const tiles = calls.map((call, index) => ({
    call, seat: PROCESS_SEATS[index % 4],
  }));
  if (td?.seat) tiles.push({ td: true, seat: td.seat.toUpperCase() });
  const rows = [];
  for (let index = 0; index < tiles.length; index += 4) {
    rows.push(tiles.slice(index, index + 4));
  }
  return rows;
}

function metricValue(value) {
  return value == null ? "— %" : pct(value);
}

function processMetric(title, value, detail, tone = "") {
  return e("div", { className: `iv-process-metric ${tone}` },
    e("span", { className: "iv-process-metric-title" }, title),
    e("strong", null, value),
    detail && e("small", null, detail));
}

function primaryMetricCards(primary, thresholds) {
  const metrics = primary?.metrics || {};
  const contract = metrics.contract || "—";
  const level = Number(String(contract).replace(/[^0-9]/g, "").slice(0, 1));
  const sameLevel = level >= 7 ? "GRAND SLAM"
    : level === 6 ? "SMALL SLAM" : "GAME";
  const ratio = metrics.make_ratio;
  return e("div", { className: "iv-primary-metrics" },
    processMetric(
      `CURRENT ${contract}`,
      metricValue(metrics.make),
      "MAKE",
      metrics.make == null ? "empty" : "make"),
    processMetric("LOSE", metricValue(metrics.lose_game), "GAME",
                  metrics.lose_game == null ? "empty" : ""),
    processMetric("LOSE", metricValue(metrics.lose_small_slam), "SMALL SLAM",
                  metrics.lose_small_slam == null ? "empty" : ""),
    processMetric("LOSE", metricValue(metrics.lose_grand_slam), "GRAND SLAM",
                  metrics.lose_grand_slam == null ? "empty" : ""),
    processMetric(
      `BEST ${sameLevel}`,
      metrics.best_other?.contract
        ? `${metrics.best_other.contract} ${pct(metrics.best_other.make)}`
        : "—",
      "other contract",
      metrics.best_other ? "" : "empty"),
    processMetric(
      "CURRENT / BEST",
      ratio == null ? "—" : Number(ratio).toFixed(2),
      `below ${Number(thresholds.wrong).toFixed(2)}`,
      ratio != null && ratio < thresholds.wrong ? "bad" : ""));
}

function ProcessView({ processes, thresholds, selectedKey, onSelect, search, onSearch }) {
  const [primarySide, setPrimarySide] = React.useState("north");
  const [primaryIndex, setPrimaryIndex] = React.useState(0);
  const [partnerIndex, setPartnerIndex] = React.useState(0);
  React.useEffect(() => {
    setPrimaryIndex(0);
    setPartnerIndex(0);
  }, [selectedKey, primarySide]);
  if (!processes.length) {
    return e("div", { className: "iv-inspection" },
      e("div", { className: "iv-list" },
        e("div", { className: "iv-list-tools" },
          e("span", null, "0 process·groups"),
          e("span", { className: "iv-process-list-note" },
            "one row = one fixed public auction process"),
          e("input", {
            type: "search", placeholder: "Find auction, contract, shape",
            value: search,
            "aria-label": "Search process groups",
            onChange: (event) => onSearch(event.target.value),
          })),
        e("p", { className: "iv-empty-list" },
          "No process groups match the current filters and thresholds. "
          + "Clear the search or switch to Process Overview.")));
  }
  const selected = processes.find((process) => processKey(process) === selectedKey)
    || processes[0];
  const primaryHands = selected.primary_hands?.[
    primarySide === "north" ? "n" : "s"] || [];
  const activePrimaryIndex = Math.min(
    primaryIndex, Math.max(0, primaryHands.length - 1));
  const primary = primaryHands[activePrimaryIndex];
  const partners = primary?.partners || [];
  const activePartnerIndex = Math.min(
    partnerIndex, Math.max(0, partners.length - 1));
  const partner = partners[activePartnerIndex];
  const partnerLabel = primarySide === "north" ? "South" : "North";
  const primaryLabel = primarySide === "north" ? "North" : "South";
  const blocked = partners.find((item) => item.status === "blocked");
  const rows = processAuction(selected, blocked?.td);
  return e("div", { className: "iv-inspection iv-process-inspection" },
    e("div", { className: "iv-list" },
      e("div", { className: "iv-list-tools" },
        e("span", null, `${processes.length} process·groups`),
        e("span", { className: "iv-process-list-note" },
          "one row = one fixed public auction process"),
        e("input", {
          type: "search", placeholder: "Find auction, contract, shape",
          value: search,
          "aria-label": "Search process groups",
          onChange: (event) => onSearch(event.target.value),
        })),
      e("div", { className: "iv-list-scroll" },
        processes.map((process) => processCard(
          process, processKey(selected) === processKey(process),
          thresholds, onSelect)))),
    e("div", { className: "iv-process-main" },
      e("section", { className: "iv-process-auction" },
        e("div", { className: "iv-process-section-head" },
          e("span", { className: "iv-eyebrow" },
            "PROCESS · SAME FOR EVERY HAND IN THIS BUCKET"),
          e("span", null, `${selected.cases ?? 0} N/S pairs · `
            + `${processBoardCount(selected)} DDS boards`
            + (selected.overflow > 0
              ? ` · +${selected.overflow} overflowed` : ""))),
        e("div", { className: "iv-process-call-rows" },
          rows.map((row, rowIndex) => e("div", {
            className: "iv-process-call-row", key: rowIndex,
          }, row.map((tile, index) => e("div", {
            key: index,
            className: `iv-process-call ${tile.td ? "td" : callClass(tile.call)}`,
          }, e("span", null, tile.seat),
          e("strong", null, tile.td ? "TD" : tile.call)))))),
      e("div", { className: "iv-process-workbench" },
        e("aside", { className: "iv-primary-list" },
          e("div", { className: "iv-primary-list-head" },
            e("h4", null, "Primary Hands"),
            e("div", { className: "iv-primary-toggle", role: "group",
              "aria-label": "Primary hand perspective" },
              e("button", {
                type: "button",
                className: primarySide === "north" ? "active" : "",
                "aria-pressed": primarySide === "north",
                onClick: () => setPrimarySide("north"),
              }, "North"),
              e("button", {
                type: "button",
                className: primarySide === "south" ? "active" : "",
                "aria-pressed": primarySide === "south",
                onClick: () => setPrimarySide("south"),
              }, "South"))),
          e("div", { className: "iv-primary-scroll" },
            primaryHands.length === 0 && e("p", { className: "iv-empty-list" },
              `No stored ${primaryLabel} primary hand in this process.`),
            primaryHands.map((item, index) => e("button", {
              key: item.hand, type: "button",
              className: `iv-primary-item ${activePrimaryIndex === index ? "selected" : ""}`,
              onClick: () => {
                setPrimaryIndex(index);
                setPartnerIndex(0);
              },
            },
              e("strong", null, `#${item.label}`),
              e("span", null,
                `${(item.shape || []).join("–") || "?"} · `
                + `${item.hcp ?? "?"} HCP · ${item.kr ?? "?"} KR`),
              e("small", null, `${item.partner_count ?? 0} partner hands · `
                + `${item.boards ?? 0} boards`
                + (item.overflow > 0
                  ? ` · +${item.overflow} overflowed` : "")))))),
        e("section", { className: "iv-primary-inspect" },
          e("div", { className: "iv-primary-inspect-head" },
            e("h3", null, primary
              ? `PRIMARY #${primary.label} · 全部匹配牌加权汇总`
              : "PRIMARY HAND"),
            e("span", null, primary
              ? `${primary.partner_count ?? 0} partner hands · `
                + `${primary.boards ?? 0} EW boards`
              : "")),
          primary && primaryMetricCards(primary, thresholds),
          primary && e("section", { className: "iv-partner-panel" },
            e("div", { className: "iv-partner-panel-head" },
              e("h4", null, `同伴实例 ${activePartnerIndex + 1} / ${partners.length}`),
              e("div", { className: "iv-partner-nav" },
                e("button", {
                  type: "button", "aria-label": "Previous partner hand",
                  disabled: activePartnerIndex <= 0,
                  onClick: () => setPartnerIndex(
                    Math.max(0, activePartnerIndex - 1)),
                }, "◀"),
                e("button", {
                  type: "button", "aria-label": "Next partner hand",
                  disabled: activePartnerIndex >= partners.length - 1,
                  onClick: () => setPartnerIndex(
                    Math.min(partners.length - 1, activePartnerIndex + 1)),
                }, "▶"))),
            e("div", { className: "iv-hand-pair" },
              miniHand(primary.hand, `${primaryLabel} · Primary`, "is-primary"),
              partner
                ? miniHand(partner.hand,
                  `${partnerLabel} · Partner #${activePartnerIndex + 1}`)
                : e("p", { className: "iv-empty-list" },
                  `No matched ${partnerLabel} hand.`)),
            partner?.status === "blocked" && e("div", {
              className: "iv-process-td",
            },
              e("strong", null, `TD · ${String(partner.td?.seat || "?").toUpperCase()} to call`),
              (partner.td?.diagnostics || []).map((line, index) => e("p", {
                key: index,
              }, line))),
            partner?.status === "limit" && e("div", {
              className: "iv-process-td limit",
            }, e("strong", null, "LIMIT · call limit reached"))))))));
}

export function IVScanner({ profileId }) {
  const [reports, setReports] = React.useState([]);
  const [reportId, setReportId] = React.useState("");
  const [report, setReport] = React.useState(null);
  const [run, setRun] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState("");
  const [category, setCategory] = React.useState("all");
  const [view, setView] = React.useState("process-findings");
  const [page, setPage] = React.useState(1);
  const [selectedGroupId, setSelectedGroupId] = React.useState(null);
  const [selectedPairId, setSelectedPairId] = React.useState(null);
  const [selectedProcessKey, setSelectedProcessKey] = React.useState(null);
  const [search, setSearch] = React.useState("");
  const [thresholds, setThresholds] = React.useState(DEFAULT_THRESHOLDS);
  const [hcpMin, setHcpMin] = React.useState(0);
  const [hcpMax, setHcpMax] = React.useState(22);
  const [northCap, setNorthCap] = React.useState(2);
  const [southCap, setSouthCap] = React.useState(2);
  const [linkCaps, setLinkCaps] = React.useState(true);
  const [ewSamples, setEwSamples] = React.useState(10);
  const [seed, setSeed] = React.useState(23);
  const loadedRun = React.useRef(null);
  const loadedRunId = React.useRef(null);
  const reportIdRef = React.useRef("");
  const manualReport = React.useRef(false);

  async function refreshReports(preferredId) {
    const result = await listScannerReports();
    const matching = (result.reports || []).filter((item) => item.profile?.id === profileId);
    setReports(matching);
    const nextId = (preferredId && matching.some((item) => item.id === preferredId) ? preferredId : null)
      || (matching.some((item) => item.id === reportId) ? reportId : matching[0]?.id || "");
    setReportId(nextId);
  }

  React.useEffect(() => {
    setError("");
    setReport(null);
    setReportId("");
    refreshReports().catch((failure) => setError(failure.message));
  }, [profileId]);

  React.useEffect(() => {
    if (!reportId) { setReport(null); return; }
    let active = true;
    setBusy(true);
    readScannerReport(reportId)
      .then((data) => {
        if (!active) return;
        setReport(data);
        setSelectedGroupId(null);
        setSelectedPairId(null);
        setBusy(false);
      })
      .catch((failure) => { if (active) { setError(failure.message); setBusy(false); } });
    return () => { active = false; };
  }, [reportId]);

  React.useEffect(() => { reportIdRef.current = reportId; }, [reportId]);

  React.useEffect(() => {
    let active = true;
    async function poll() {
      try {
        const result = await scannerRunStatus();
        if (!active) return;
        const next = result.run;
        setRun(next);
        // Load the report as soon as the backend publishes a (partial) one,
        // and refresh it as the run advances, so findings stream in live.
        if (next?.profile === profileId && next.report_id) {
          const key = `${next.id}:${next.snapshot_pairs || 0}`;
          const following = !manualReport.current
            || reportIdRef.current === next.report_id;
          if (following && loadedRun.current !== key) {
            loadedRun.current = key;
            const data = await readScannerReport(next.report_id);
            if (!active) return;
            if (loadedRunId.current !== next.id) {
              loadedRunId.current = next.id;
              setSelectedGroupId(null);
              setSelectedPairId(null);
            }
            setReport(data);
            setReportId(next.report_id);
            refreshReports(next.report_id).catch(() => {});
          }
        }
      } catch (failure) {
        if (active) setError(failure.message);
      }
    }
    poll();
    const timer = window.setInterval(poll, 2000);
    return () => { active = false; window.clearInterval(timer); };
  }, [profileId]);

  async function stopScan() {
    setError("");
    try {
      const result = await stopScannerRun();
      setRun(result.run);
    } catch (failure) {
      setError(failure.message);
    }
  }

  async function completeReport() {
    if (!reportId) return;
    setError("");
    manualReport.current = true;
    loadedRun.current = null;
    try {
      const result = await completeScannerReport(reportId, {
        north_cap: Number(northCap), south_cap: Number(southCap),
        ew_samples: Number(ewSamples), seed: Number(seed),
      });
      setRun(result.run);
    } catch (failure) {
      setError(failure.message);
    }
  }

  async function copyReport() {
    if (!reportId) return;
    if (!window.confirm(`Copy report ${reportId}?`)) return;
    setError("");
    try {
      const result = await copyScannerReport(reportId);
      const copiedId = result.report?.id;
      await refreshReports(copiedId);
      if (copiedId) setReportId(copiedId);
      setCategory("all");
      setSearch("");
    } catch (failure) {
      setError(failure.message);
    }
  }

  async function deleteReport() {
    if (!reportId) return;
    if (!window.confirm(`Delete report ${reportId}?`)) return;
    if (!window.confirm(
      "This is the second confirmation. Delete the report and its HTML viewer permanently?")) return;
    setError("");
    try {
      await deleteScannerReport(reportId);
      setSelectedGroupId(null);
      setSelectedPairId(null);
      setSelectedProcessKey(null);
      await refreshReports();
    } catch (failure) {
      setError(failure.message);
    }
  }

  async function startScan() {
    setError("");
    manualReport.current = false;
    loadedRun.current = null;
    try {
      const result = await startScannerRun({
        profile: profileId, seed: Number(seed),
        hcp_min: Number(hcpMin), hcp_max: Number(hcpMax),
        // Caps are the stored-hand budget per North/South process pool. The
        // scan still needs a pair-slot count per cell; the larger cap is the
        // only value that can fill both pools, so the two settings cannot
        // contradict each other.
        pairs_per_cell: Math.max(Number(northCap), Number(southCap)),
        ew_samples: Number(ewSamples),
        north_cap: Number(northCap), south_cap: Number(southCap),
      });
      setRun(result.run);
    } catch (failure) {
      setError(failure.message);
    }
  }

  const isProcessView = view.startsWith("process");
  const counts = React.useMemo(() => {
    const result = { block: 0, missed: 0, down: 0, wrong: 0 };
    (report?.groups || []).forEach((group) => {
      groupCategories(group, thresholds).forEach((key) => { result[key] += 1; });
    });
    return result;
  }, [report, thresholds]);
  const processCounts = React.useMemo(() => {
    const result = { block: 0, missed: 0, down: 0, wrong: 0 };
    (report?.process_groups || []).forEach((process) => {
      processCategories(process, thresholds).forEach((key) => {
        result[key] += 1;
      });
    });
    return result;
  }, [report, thresholds]);
  const flaggedGroups = React.useMemo(
    () => (report?.groups || []).filter(
      (group) => groupCategories(group, thresholds).length > 0),
    [report, thresholds]);
  const findingsGroups = React.useMemo(
    () => filterScannerGroups(flaggedGroups, category, search, thresholds),
    [flaggedGroups, category, search, thresholds]);
  const processSource = React.useMemo(() => {
    if (!isProcessView) return [];
    let items = filterProcessGroups(
      report?.process_groups || [], category, search, thresholds);
    if (view === "process-findings") {
      items = items.filter(
        (process) => processCategories(process, thresholds).length > 0);
    }
    return [...items].sort((left, right) => (
      (view === "process-findings"
        ? processCategories(right, thresholds).length
          - processCategories(left, thresholds).length
        : 0)
      || (right.cases || 0) - (left.cases || 0)
      || String(left.auction || "").localeCompare(String(right.auction || ""))));
  }, [report, view, category, search, thresholds, isProcessView]);
  const overviewSource = React.useMemo(() => {
    if (view !== "cell-overview") return [];
    const groups = filterScannerGroups(
      report?.groups || [], "all", search, thresholds);
    return [...groups].sort((left, right) => (
      String(left.parent_id).localeCompare(String(right.parent_id))
      || String(left.auction).localeCompare(String(right.auction))
      || left.id.localeCompare(right.id)));
  }, [report, view, search, thresholds]);
  const pagination = React.useMemo(
    () => paginateGroups(overviewSource, page, OVERVIEW_PAGE_SIZE),
    [overviewSource, page]);
  const visibleGroups = view === "cell-overview"
    ? pagination.items
    : (view === "cell-findings" ? findingsGroups : []);
  const matchingPairs = React.useMemo(
    () => findingsGroups.reduce((sum, group) => sum + (group.pairs || []).filter(
      (pair) => pairMatches(pair, category, search, thresholds)).length, 0),
    [findingsGroups, category, search, thresholds]);
  const selectedGroup = visibleGroups.find((group) => group.id === selectedGroupId)
    || visibleGroups[0] || null;
  const selectionCategory = view === "cell-overview" ? "all" : category;
  const selectedPair = selectedGroup
    ? (selectedGroup.pairs || []).find((pair) => pair.id === selectedPairId)
      || selectPairForGroup(selectedGroup, selectionCategory, search, thresholds)
    : null;
  const displayCounts = isProcessView ? processCounts : counts;

  React.useEffect(() => {
    setPage(1);
  }, [report, view, category, search, thresholds]);

  React.useEffect(() => {
    const group = visibleGroups.find((item) => item.id === selectedGroupId)
      || visibleGroups[0] || null;
    setSelectedPairId(selectPairForGroup(
      group, selectionCategory, search, thresholds)?.id ?? null);
    if (group && group.id !== selectedGroupId) setSelectedGroupId(group.id);
  }, [visibleGroups, selectedGroupId, selectionCategory, search, thresholds]);

  React.useEffect(() => {
    const keys = processSource.map(processKey);
    if (keys.includes(selectedProcessKey)) return;
    setSelectedProcessKey(keys[0] || null);
  }, [processSource, selectedProcessKey]);

  const running = ["running", "queued", "stopping"].includes(run?.status);
  const plannedPairsPerCell = Math.max(Number(northCap), Number(southCap));
  const planned = (Number(hcpMax) - Number(hcpMin) + 1) * FULL_SCAN_SHAPES * plannedPairsPerCell;

  return e("section", { className: "iv-scanner" },
    e("header", { className: "iv-header" },
      e("div", null,
        e("span", { className: "iv-eyebrow" }, "GIBLE / DIAGNOSTICS"),
        e("h2", null, "IV Scanner"),
        e("p", null, "Find TD calls, missed contracts, failing contracts, and WRONG games."),
      ),
      e("span", { className: "iv-scope-chip" }, "NORTH OPENS 1NT"),
    ),
    e("div", { className: "iv-main" },
      e("section", { className: "iv-control" },
        e("div", { className: "iv-control-title" },
          e("div", null, e("span", { className: "iv-eyebrow" }, "01 / SAMPLE"),
            e("h3", null, "Set the scan")),
          e("span", null, `${Number.isFinite(planned) ? planned : "—"} N/S pairs planned`),
        ),
        e("div", { className: "iv-fields" },
          e("label", null, "South HCP from", e("input", { type: "number", min: 0, max: 22, value: hcpMin,
            onChange: (event) => setHcpMin(event.target.value) })),
          e("label", null, "to", e("input", { type: "number", min: 0, max: 22, value: hcpMax,
            onChange: (event) => setHcpMax(event.target.value) })),
          e("label", { className: "iv-cap-field" }, "North cap",
            e("input", { type: "number", min: 1, max: 20, value: northCap,
              onChange: (event) => {
                const next = event.target.value;
                setNorthCap(next);
                if (linkCaps) setSouthCap(next);
              } })),
          e("label", { className: "iv-cap-field" }, "South cap",
            e("input", { type: "number", min: 1, max: 20, value: southCap,
              onChange: (event) => {
                const next = event.target.value;
                setSouthCap(next);
                if (linkCaps) setNorthCap(next);
              } })),
          e("label", { className: "iv-cap-link" },
            e("input", { type: "checkbox", checked: linkCaps,
              onChange: (event) => {
                const linked = event.target.checked;
                setLinkCaps(linked);
                if (linked) setSouthCap(northCap);
              } }),
            e("span", null, "🔗 Link caps"),
            e("small", null, "both change together")),
          e("label", null, "E/W deals per pair", e("input", { type: "number", min: 1, max: 20, value: ewSamples,
            onChange: (event) => setEwSamples(event.target.value) })),
          e("label", null, "Seed", e("input", { type: "number", min: 0, value: seed,
            onChange: (event) => setSeed(event.target.value) })),
        ),
        e("div", { className: "iv-run-row" },
          e("button", { className: "primary", onClick: startScan, disabled: running },
            running ? "Scan running…" : "Start scan"),
          e("button", {
            className: "iv-stop-button", onClick: stopScan,
            disabled: !running || run?.mode === "complete" || run?.stop_requested,
          }, run?.stop_requested ? "Stopping…" : "Stop scan"),
          e("button", {
            className: "iv-complete-button", onClick: completeReport,
            disabled: running || !reportId,
            title: "Re-bid every stored hand, update changed processes, then fill N/S caps",
          }, "Complete report"),
          e("span", null, `North 1NT · all ${FULL_SCAN_SHAPES} South shapes · opponents pass · DDS evaluates completed auctions`),
        ),
        run && e("div", { className: `iv-progress iv-progress-${run.status}`, role: "status" },
          e("div", null,
            e("strong", null, run.status === "completed"
              ? (run.mode === "complete" ? "Report complete" : "Scan complete")
              : run.status === "stopped" ? "Scan stopped"
              : run.status === "failed" ? (run.mode === "complete"
                ? "Report completion failed" : "Scan failed")
              : run.mode === "complete" ? "Completing report" : "Scanning deals"),
            e("span", null, `${run.completed_pairs}/${run.planned_pairs} pairs · ${run.dds_boards} DDS boards`),
          ),
          e("div", { className: "iv-progress-track" },
            e("div", { style: { width: `${run.planned_pairs ? 100 * run.completed_pairs / run.planned_pairs : 0}%` } })),
          run.error && e("p", null, run.error),
        ),
        error && e("p", { className: "iv-error", role: "alert" }, error),
      ),
      e("section", { className: "iv-results" },
        e("div", { className: "iv-results-top" },
          e("div", null, e("span", { className: "iv-eyebrow" }, "02 / INSPECT"), e("h3", null, "Findings")),
          e("label", null, "Report", e("select", { value: reportId,
            onChange: (event) => { manualReport.current = true; setReportId(event.target.value); setCategory("all"); setSearch(""); } },
            reports.length === 0 && e("option", { value: "" }, "No saved scans"),
            reports.map((item) => e("option", { key: item.id, value: item.id },
              `${item.id} · ${item.summary?.pairs ?? 0} pairs`)),
          )),
          e("div", { className: "iv-report-actions" },
            e("button", {
              type: "button", onClick: copyReport,
              disabled: running || !reportId,
              title: "Duplicate this report and its HTML viewer",
            }, "Copy report"),
            e("button", {
              type: "button", className: "danger", onClick: deleteReport,
              disabled: running || !reportId,
              title: "Delete this report after two confirmations",
            }, "Delete report")),
        ),
        report && e("div", { className: "iv-summary-line" },
          `${report.summary?.pairs ?? 0} N/S pairs · ${report.summary?.dds_boards ?? 0} DDS boards · `,
          `${report.summary?.overflow ?? 0} overflow hands (weighted, not stored) · `,
          `${report.summary?.unassessed ?? 0} completed cases without enough comparable boards`),
        report && !report.partner_matching && e("p", {
          className: "iv-completion-note warn",
        }, "This report predates process partner matching. "
          + "Restart the backend if needed, rerun the scan, or use "
          + "Complete report to add the missing partner matches."),
        report?.completion && e("p", { className: "iv-completion-note" },
          `Completed report · ${report.completion.rebidded_pairs ?? 0} hands re-bid · `
          + `${report.completion.changed_pairs ?? 0} process changes · `
          + `${report.completion.added_pairs ?? 0} hands added · `
          + `${report.completion.remaining_deficits?.length ?? 0} cap deficits remain`),
        report && e("div", { className: "iv-thresholds", role: "group",
          "aria-label": "Alarm thresholds" },
          e("div", { className: "iv-thresholds-head" },
            e("span", { className: "iv-eyebrow" }, "ALARM THRESHOLDS"),
            e("span", null, "TD has no threshold"),
            e("button", { type: "button",
              onClick: () => setThresholds(DEFAULT_THRESHOLDS) }, "Reset")),
          e("div", { className: "iv-threshold-grid" },
            THRESHOLD_CONTROLS.map((control) => e(ThresholdControl, {
              key: control.key, control,
              value: thresholds[control.key],
              onUpdate: (key, next) => setThresholds((current) => ({
                ...current, [key]: next,
              })),
            }))),
        ),
        report && e("div", { className: "iv-view-switch", role: "group",
          "aria-label": "Scanner view" },
          e("button", {
            type: "button",
            className: view === "process-findings" ? "active" : "",
            "aria-pressed": view === "process-findings",
            onClick: () => { setView("process-findings"); setCategory("all"); },
          }, "Process · Findings"),
          e("button", {
            type: "button",
            className: view === "process-overview" ? "active" : "",
            "aria-pressed": view === "process-overview",
            onClick: () => { setView("process-overview"); setCategory("all"); },
          }, "Process · Overview 总览"),
          e("button", {
            type: "button",
            className: view === "cell-findings" ? "active" : "",
            "aria-pressed": view === "cell-findings",
            onClick: () => { setView("cell-findings"); setCategory("all"); },
          }, "Cell · Findings"),
          e("button", {
            type: "button",
            className: view === "cell-overview" ? "active" : "",
            "aria-pressed": view === "cell-overview",
            onClick: () => { setView("cell-overview"); setCategory("all"); },
          }, "Cell · Overview 总览"),
        ),
        e("div", { className: "iv-categories" },
          Object.entries(CATEGORY).map(([key, item], index) => e("button", {
            key, className: `iv-category iv-category-${key} ${category === key ? "selected" : ""}`,
            onClick: () => {
              setView(isProcessView ? "process-findings" : "cell-findings");
              setCategory(category === key ? "all" : key);
            },
            "aria-pressed": category === key,
          }, e("span", null, `0${index + 1} / ${item.title}`),
          e("strong", null, displayCounts[key]),
          e("small", null, item.detail))),
        ),
        isProcessView
          ? e(ProcessView, {
            processes: processSource, thresholds,
            selectedKey: selectedProcessKey,
            onSelect: setSelectedProcessKey,
            search, onSearch: setSearch,
          })
          : e("div", { className: "iv-inspection" },
          e("div", { className: "iv-list" },
            e("div", { className: "iv-list-tools" },
              e("span", null, busy ? "Loading…" : (
                view === "cell-overview"
                  ? `all ${pagination.total} cell·process groups · page ${pagination.page}/${pagination.pages}`
                  : `${findingsGroups.length} findings · ${matchingPairs} N/S pairs`)),
              e("input", { type: "search", placeholder: "Find deal #, auction, hand", value: search,
                "aria-label": "Search scanner findings", onChange: (event) => setSearch(event.target.value) }),
              category !== "all" && view === "cell-findings" && e("button", {
                onClick: () => setCategory("all"),
              }, "Show all"),
            ),
            view === "cell-overview" && e("div", { className: "iv-pager" },
              e("button", {
                type: "button", "aria-label": "Previous overview page",
                disabled: pagination.page <= 1,
                onClick: () => setPage((current) => Math.max(1, current - 1)),
              }, "‹ Prev"),
              e("span", null,
                `Page ${pagination.page} / ${pagination.pages} · `
                + `${pagination.start}–${pagination.end} of ${pagination.total}`),
              e("button", {
                type: "button", "aria-label": "Next overview page",
                disabled: pagination.page >= pagination.pages,
                onClick: () => setPage((current) => (
                  Math.min(pagination.pages, current + 1))),
              }, "Next ›"),
            ),
            e("div", { className: "iv-list-scroll" },
              visibleGroups.length === 0 && e("p", { className: "iv-empty-list" },
                report
                  ? (view === "cell-overview"
                    ? "No cell·process groups match this search."
                    : "No findings match the current filters and thresholds.")
                  : "Choose or run a scan to see findings."),
              visibleGroups.map((group) => {
                const categories = groupCategories(group, thresholds);
                const first = group.pairs?.[0];
                return e("button", {
                  key: group.id,
                  className: `iv-case ${selectedGroup?.id === group.id ? "selected" : ""}`,
                  onClick: () => setSelectedGroupId(group.id),
                },
                  e("span", { className: "iv-case-top" },
                    e("strong", null, `${group.actual_pair_count} NS pair${group.actual_pair_count === 1 ? "" : "s"}`),
                    e("span", null,
                      `${report?.budget?.ew_samples ?? "—"} EW samples`
                      + (makeRate(first?.rates) == null ? ""
                        : ` · MAKE ${pct(makeRate(first.rates))}`))),
                  e("span", { className: "iv-case-tags" },
                    categories.map((key) => e("b", { key, className: `iv-tag iv-tag-${key}` }, CATEGORY[key]?.title || key)),
                    categories.length === 0 && view === "cell-overview" && e("b", {
                      className: "iv-tag iv-tag-clean",
                    }, "CLEAN"),
                    group.incomplete && e("b", { className: "iv-tag iv-tag-block" },
                      `CELL ${group.actual_pair_count}/${group.expected_pair_count}`)),
                  e("span", { className: "iv-case-auction" },
                    `South ${group.south_hcp ?? "?"} HCP · ${(group.south_shape || []).join("–") || "?"} · ${group.auction || first?.auction || "—"}`),
                );
              }),
            ),
          ),
          e("div", { className: "iv-pair-workspace" },
            selectedGroup && e("div", {
              className: "iv-pair-rail", role: "group",
              "aria-label": "N/S pairs in the selected cell",
            },
              selectedGroup.pairs.map((pair) => pairRailButton(
                pair, pair.id === selectedPair?.id,
                (pairId) => setSelectedPairId(pairId)))),
            e("div", { className: "iv-pair-detail" },
              pairDetail(selectedPair, selectedGroup, thresholds)),
          ),
        ),
        e("p", { className: "iv-method" },
          "DDS compares complete four-hand deals. Pairs in one sampling cell with the same complete auction pool their DDS boards; different auctions become separate cells. These rates are diagnostic samples, not estimates of actual declarer play."),
      ),
    ),
  );
}
