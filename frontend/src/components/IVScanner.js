import { React, e } from "../ui/react.js";
import {
  listScannerReports, readScannerReport, scannerRunStatus, startScannerRun,
} from "../api/gibleApi.js";

const CATEGORY = {
  block: { title: "卡 / BLOCKED", detail: "Auction has no supported next call" },
  missed: { title: "丢 / LOSE", detail: "Game or slam was available" },
  down: { title: "宕 / SET", detail: "Chosen contract fails too often" },
  wrong: { title: "错 / WRONG", detail: "Selected/alternative success odds ratio < 0.8" },
};
const FLAG = {
  contract_failure: "Down > 50%",
  missed_game: "Missed game > 30%",
  missed_small_slam: "Missed small slam > 30%",
  missed_grand_slam: "Missed grand slam > 30%",
  wrong_game: "WRONG game: success odds ratio < 0.8",
};
const SUITS = [["S", "♠"], ["H", "♥"], ["D", "♦"], ["C", "♣"]];
const FULL_SCAN_SHAPES = 23;

const pct = (value) => value == null ? "—" : `${(value * 100).toFixed(0)}%`;

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

function nsCellKey(caseData) {
  return [
    caseData.north_hcp, caseData.south_hcp,
    ...(caseData.north_shape || []), ...(caseData.south_shape || []),
  ].join(":");
}

function auctionRows(calls = []) {
  const rows = [];
  for (let index = 0; index < calls.length; index += 4) rows.push(calls.slice(index, index + 4));
  return rows;
}

function groupCasesByNsCell(cases, ewSampleCount = 0) {
  const groups = new Map();
  cases.forEach((caseData) => {
    const key = nsCellKey(caseData);
    const group = groups.get(key) || {
      key, cases: [], categories: new Set(), ewSamples: 0,
    };
    group.cases.push(caseData);
    caseData.categories.forEach((category) => group.categories.add(category));
    group.ewSamples = Math.max(group.ewSamples, ewSampleCount || Number(caseData.dds_boards) || 0);
    groups.set(key, group);
  });
  return [...groups.values()].map((group) => ({
    ...group,
    categories: [...group.categories].sort(),
  }));
}

function matrixCell(caseData, ewIndex) {
  if (caseData.blocked || !caseData.contract) return "BLOCK 卡";
  const result = caseData.ew_results?.[ewIndex];
  if (result === "made") return "MAKE";
  if (result === "down") return "LOSE";
  if (ewIndex >= (Number(caseData.dds_boards) || 0)) return "—";
  return caseData.contract || "BLOCK 卡";
}

function warningValue(flag, value) {
  return flag === "wrong_game" && value != null ? `OR ${Number(value).toFixed(2)}` : pct(value);
}

function caseDetail(caseData, group) {
  if (!caseData) return e("div", { className: "iv-empty-detail" }, "Select a numbered deal to inspect its hands and auction.");
  const rates = caseData.rates || {};
  const alternatives = Object.entries(caseData.alternative_game_rates || {})
    .filter(([, rate]) => rate > 0);
  return e("div", { className: "iv-detail-body" },
    e("div", { className: "iv-detail-heading" },
      e("span", { className: "iv-eyebrow" }, `DEAL #${caseData.id}`),
      e("h3", null, caseData.contract
        ? `${caseData.contract} · ${caseData.declarer?.toUpperCase()} declares`
        : "Auction blocked"),
      e("p", null, caseData.auction || "No calls recorded"),
    ),
    e("div", { className: "iv-hands" }, handCard("n", caseData), handCard("s", caseData)),
    e("div", { className: "iv-detail-section" },
      e("h4", null, "Auction"),
      e("div", { className: "iv-auction-rows" },
        auctionRows(caseData.calls).map((row, rowIndex) => e("div", {
          className: "iv-auction-row", key: rowIndex,
        }, row.map((call, index) => e("span", { key: index }, call))))),
    ),
    group && e("div", { className: "iv-detail-section" },
      e("h4", null, "NS / EW result matrix"),
      e("div", { className: "iv-ns-matrix" },
        e("div", { className: "iv-matrix-scroll" },
          e("table", null,
            e("thead", null, e("tr", null,
              e("th", { scope: "col" }, "NS pair"),
              Array.from({ length: group.ewSamples }, (_, index) => e("th", {
                scope: "col", key: index,
              }, `EW ${index + 1}`)),
            )),
            e("tbody", null, group.cases.map((pair) => e("tr", { key: pair.id },
              e("th", { scope: "row" }, `#${pair.id}`),
              Array.from({ length: group.ewSamples }, (_, index) => e("td", {
                key: index, className: index < (Number(pair.dds_boards) || 0) ? "" : "empty",
              }, matrixCell(pair, index))),
            ))),
          ),
        ),
      ),
    ),
    caseData.blocked && e("div", { className: "iv-detail-section iv-block-diagnostic" },
      e("h4", null, `Blocked at ${caseData.blocked.seat?.toUpperCase() || "?"}`),
      (caseData.blocked.diagnostics || []).map((line, index) => e("p", { key: index }, line)),
    ),
    caseData.flags?.length > 0 && e("div", { className: "iv-detail-section" },
      e("h4", null, "Warnings"),
      e("div", { className: "iv-warning-list" },
        caseData.flags.map((flag) => e("div", { key: flag },
          e("strong", null, FLAG[flag] || flag),
        e("span", null, warningValue(flag, rates[flag])),
        )),
      ),
      alternatives.length > 0 && e("p", { className: "iv-alternatives" },
        "Alternative games made when chosen game failed: ",
        alternatives.map(([name, rate]) => `${name} ${pct(rate)}`).join(" · "),
      ),
      e("p", { className: "iv-evidence" },
        `${caseData.class_pairs ?? "—"} similar N/S pairs · ${caseData.dds_boards ?? "—"} DDS boards. Rates use all boards in that class.`),
    ),
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
  const [selectedId, setSelectedId] = React.useState(null);
  const [search, setSearch] = React.useState("");
  const [hcpMin, setHcpMin] = React.useState(0);
  const [hcpMax, setHcpMax] = React.useState(22);
  const [pairs, setPairs] = React.useState(2);
  const [ewSamples, setEwSamples] = React.useState(10);
  const [seed, setSeed] = React.useState(23);
  const loadedRun = React.useRef(null);

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
        setSelectedId(data.cases?.[0]?.id ?? null);
        setBusy(false);
      })
      .catch((failure) => { if (active) { setError(failure.message); setBusy(false); } });
    return () => { active = false; };
  }, [reportId]);

  React.useEffect(() => {
    let active = true;
    async function poll() {
      try {
        const result = await scannerRunStatus();
        if (!active) return;
        const next = result.run;
        setRun(next);
        if (next?.status === "completed" && next.profile === profileId
            && next.report_id && loadedRun.current !== next.id) {
          loadedRun.current = next.id;
          await refreshReports(next.report_id);
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

  const matches = (report?.cases || []).filter((item) => {
    if (category !== "all" && !item.categories.includes(category)) return false;
    const query = search.trim().toLowerCase();
    return !query || String(item.id).includes(query)
      || item.auction?.toLowerCase().includes(query)
      || item.hands.n?.toLowerCase().includes(query)
      || item.hands.s?.toLowerCase().includes(query);
  });
  const groups = groupCasesByNsCell(matches, report?.budget?.ew_samples);
  const selectedGroup = groups.find((group) => group.cases.some((item) => item.id === selectedId))
    || groups[0];
  const selected = selectedGroup?.cases.find((item) => item.id === selectedId)
    || selectedGroup?.cases[0];
  const running = run?.status === "running" || run?.status === "queued";
  const planned = (Number(hcpMax) - Number(hcpMin) + 1) * FULL_SCAN_SHAPES * Number(pairs);

  return e("section", { className: "iv-scanner" },
    e("header", { className: "iv-header" },
      e("div", null,
        e("span", { className: "iv-eyebrow" }, "GIBLE / DIAGNOSTICS"),
        e("h2", null, "IV Scanner"),
        e("p", null, "Find blocked auctions, missed contracts, failing contracts, and WRONG games."),
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
            onChange: (event) => { setReportId(event.target.value); setCategory("all"); setSearch(""); } },
            reports.length === 0 && e("option", { value: "" }, "No saved scans"),
            reports.map((item) => e("option", { key: item.id, value: item.id },
              `${item.id} · ${item.summary?.pairs ?? 0} pairs`)),
          )),
        ),
        report && e("div", { className: "iv-summary-line" },
          `${report.summary?.pairs ?? 0} N/S pairs · ${report.summary?.dds_boards ?? 0} DDS boards · `,
          `${report.summary?.unassessed ?? 0} completed cases without enough comparable boards`),
        e("div", { className: "iv-categories" },
          Object.entries(CATEGORY).map(([key, item], index) => e("button", {
            key, className: `iv-category iv-category-${key} ${category === key ? "selected" : ""}`,
            onClick: () => { setCategory(category === key ? "all" : key); setSelectedId(null); },
            "aria-pressed": category === key,
          }, e("span", null, `0${index + 1} / ${item.title}`),
          e("strong", null, report?.counts?.[key] ?? "—"),
          e("small", null, item.detail))),
        ),
        e("div", { className: "iv-inspection" },
          e("div", { className: "iv-list" },
            e("div", { className: "iv-list-tools" },
              e("span", null, busy ? "Loading…" : `${matches.length} findings · ${groups.length} NS cells`),
              e("input", { type: "search", placeholder: "Find deal #, auction, hand", value: search,
                "aria-label": "Search scanner findings", onChange: (event) => setSearch(event.target.value) }),
              category !== "all" && e("button", { onClick: () => setCategory("all") }, "Show all"),
            ),
            e("div", { className: "iv-list-scroll" },
              matches.length === 0 && e("p", { className: "iv-empty-list" },
                report ? "No matching findings in this report." : "Choose or run a scan to see findings."),
              groups.map((group) => e("button", { key: group.key,
                className: `iv-case ${selectedGroup?.key === group.key ? "selected" : ""}`,
                onClick: () => setSelectedId(group.cases[0].id),
              },
                e("span", { className: "iv-case-top" },
                  e("strong", null, `${group.cases.length} NS pair${group.cases.length === 1 ? "" : "s"}`),
                  e("span", null, `${group.ewSamples} EW samples`)),
                e("span", { className: "iv-case-tags" },
                  group.categories.map((key) => e("b", { key, className: `iv-tag iv-tag-${key}` }, CATEGORY[key]?.title || key))),
                e("span", { className: "iv-case-auction" },
                  `NS ${group.cases[0].north_hcp}/${group.cases[0].south_hcp} HCP · ${group.cases[0].auction || "—"}`),
              )),
            ),
          ),
          e("div", { className: "iv-detail" }, caseDetail(selected, selectedGroup)),
        ),
        e("p", { className: "iv-method" },
          "DDS compares complete four-hand deals. These rates are diagnostic samples, not estimates of actual declarer play. Similar hands share named-suit shapes and a maximum HCP/K–R span of 2 per seat."),
      ),
    ),
  );
}
