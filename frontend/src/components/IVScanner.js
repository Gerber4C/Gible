import { React, e } from "../ui/react.js";
import {
  listScannerReports, readScannerReport, scannerRunStatus, startScannerRun,
} from "../api/gibleApi.js";
import {
  DEFAULT_THRESHOLDS, filterScannerGroups, groupCategories,
  pairFlags, pairMatches, paginateGroups, selectPairForGroup, wrongGameScores,
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
  return fields ? fields.slice(1).map((holding) => holding || "—") : ["—", "—", "—", "—"];
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
  return e("span", { key: index }, tile.call);
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

export function IVScanner({ profileId }) {
  const [reports, setReports] = React.useState([]);
  const [reportId, setReportId] = React.useState("");
  const [report, setReport] = React.useState(null);
  const [run, setRun] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState("");
  const [category, setCategory] = React.useState("all");
  const [view, setView] = React.useState("findings");
  const [page, setPage] = React.useState(1);
  const [selectedGroupId, setSelectedGroupId] = React.useState(null);
  const [selectedPairId, setSelectedPairId] = React.useState(null);
  const [search, setSearch] = React.useState("");
  const [thresholds, setThresholds] = React.useState(DEFAULT_THRESHOLDS);
  const [hcpMin, setHcpMin] = React.useState(0);
  const [hcpMax, setHcpMax] = React.useState(22);
  const [pairs, setPairs] = React.useState(2);
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

  async function startScan() {
    setError("");
    manualReport.current = false;
    loadedRun.current = null;
    try {
      const result = await startScannerRun({
        profile: profileId, seed: Number(seed),
        hcp_min: Number(hcpMin), hcp_max: Number(hcpMax),
        pairs_per_cell: Number(pairs), ew_samples: Number(ewSamples),
      });
      setRun(result.run);
    } catch (failure) {
      setError(failure.message);
    }
  }

  const counts = React.useMemo(() => {
    const result = { block: 0, missed: 0, down: 0, wrong: 0 };
    (report?.groups || []).forEach((group) => {
      groupCategories(group, thresholds).forEach((key) => { result[key] += 1; });
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
  const overviewSource = React.useMemo(() => {
    if (view !== "overview") return [];
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
  const visibleGroups = view === "overview" ? pagination.items : findingsGroups;
  const matchingPairs = React.useMemo(
    () => findingsGroups.reduce((sum, group) => sum + (group.pairs || []).filter(
      (pair) => pairMatches(pair, category, search, thresholds)).length, 0),
    [findingsGroups, category, search, thresholds]);
  const selectedGroup = visibleGroups.find((group) => group.id === selectedGroupId)
    || visibleGroups[0] || null;
  const selectionCategory = view === "overview" ? "all" : category;
  const selectedPair = selectedGroup
    ? (selectedGroup.pairs || []).find((pair) => pair.id === selectedPairId)
      || selectPairForGroup(selectedGroup, selectionCategory, search, thresholds)
    : null;

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

  const running = run?.status === "running" || run?.status === "queued";
  const planned = (Number(hcpMax) - Number(hcpMin) + 1) * FULL_SCAN_SHAPES * Number(pairs);

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
          e("label", null, "N/S pairs per cell", e("input", { type: "number", min: 1, max: 20, value: pairs,
            onChange: (event) => setPairs(event.target.value) })),
          e("label", null, "E/W deals per pair", e("input", { type: "number", min: 1, max: 20, value: ewSamples,
            onChange: (event) => setEwSamples(event.target.value) })),
          e("label", null, "Seed", e("input", { type: "number", min: 0, value: seed,
            onChange: (event) => setSeed(event.target.value) })),
        ),
        e("div", { className: "iv-run-row" },
          e("button", { className: "primary", onClick: startScan, disabled: running },
            running ? "Scan running…" : "Start scan"),
          e("span", null, `North 1NT · all ${FULL_SCAN_SHAPES} South shapes · opponents pass · DDS evaluates completed auctions`),
        ),
        run && e("div", { className: `iv-progress iv-progress-${run.status}`, role: "status" },
          e("div", null,
            e("strong", null, run.status === "completed" ? "Scan complete" :
              run.status === "failed" ? "Scan failed" : "Scanning deals"),
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
        ),
        report && e("div", { className: "iv-summary-line" },
          `${report.summary?.pairs ?? 0} N/S pairs · ${report.summary?.dds_boards ?? 0} DDS boards · `,
          `${report.summary?.unassessed ?? 0} completed cases without enough comparable boards`),
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
          "aria-label": "Findings view" },
          e("button", {
            type: "button", className: view === "findings" ? "active" : "",
            "aria-pressed": view === "findings",
            onClick: () => setView("findings"),
          }, "Findings"),
          e("button", {
            type: "button", className: view === "overview" ? "active" : "",
            "aria-pressed": view === "overview",
            onClick: () => { setView("overview"); setCategory("all"); },
          }, "Overview · 总览"),
        ),
        e("div", { className: "iv-categories" },
          Object.entries(CATEGORY).map(([key, item], index) => e("button", {
            key, className: `iv-category iv-category-${key} ${category === key ? "selected" : ""}`,
            onClick: () => {
              setView("findings");
              setCategory(category === key ? "all" : key);
            },
            "aria-pressed": category === key,
          }, e("span", null, `0${index + 1} / ${item.title}`),
          e("strong", null, counts[key]),
          e("small", null, item.detail))),
        ),
        e("div", { className: "iv-inspection" },
          e("div", { className: "iv-list" },
            e("div", { className: "iv-list-tools" },
              e("span", null, busy ? "Loading…" : (
                view === "overview"
                  ? `all ${pagination.total} cell·process groups · page ${pagination.page}/${pagination.pages}`
                  : `${findingsGroups.length} findings · ${matchingPairs} N/S pairs`)),
              e("input", { type: "search", placeholder: "Find deal #, auction, hand", value: search,
                "aria-label": "Search scanner findings", onChange: (event) => setSearch(event.target.value) }),
              category !== "all" && view === "findings" && e("button", {
                onClick: () => setCategory("all"),
              }, "Show all"),
            ),
            view === "overview" && e("div", { className: "iv-pager" },
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
                  ? (view === "overview"
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
                    e("span", null, `${report?.budget?.ew_samples ?? "—"} EW samples`)),
                  e("span", { className: "iv-case-tags" },
                    categories.map((key) => e("b", { key, className: `iv-tag iv-tag-${key}` }, CATEGORY[key]?.title || key)),
                    categories.length === 0 && view === "overview" && e("b", {
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
