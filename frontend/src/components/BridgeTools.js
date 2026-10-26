import { React, e } from "../ui/react.js";
import {
  axiomSummary,
  callClass,
  callLabel,
  handSummary,
  logicHint,
  rankLabel,
  suitClass,
  suitSymbol,
} from "../lib/bridge.js";

import { SEATS, SUITS, compactHand, normalizeHolding } from "../lib/deal.js";
import { analyzeContracts, analyzeRoutes } from "../api/gibleApi.js";
import { actorForAuction, buildContractAnalysisRequest, buildRouteAnalysisRequest } from "../lib/contractAnalysis.js";

const SUIT_NAMES = { S: "spades", H: "hearts", D: "diamonds", C: "clubs" };

export function BridgePanel({
  profileId,
  deal, setHolding, validation, showOpponents, setShowOpponents, onRandomDeal,
  trainingMode, setTrainingMode, targetOpening, setTargetOpening,
  targetResponse, setTargetResponse, targetOpener, setTargetOpener,
  trainingSeed, setTrainingSeed, trainingResult, trainingLoading,
  onGenerateTraining, onCancelTraining,
  onCompleteOpponents, onClearOpponents, canCompleteOpponents,
  dealer, setDealer, vulnerability, setVulnerability,
  simulation, simulationLoading, visibleCallCount,
  onShowFirst, onStepForward, onStepBackward, onShowAll,
}) {
  const [showAnalysisTools, setShowAnalysisTools] = React.useState(false);
  const records = simulation?.records ?? [];
  const visibleRecords = simulationLoading || !validation.valid ? [] : records.slice(0, visibleCallCount);
  const totalCalls = records.length;
  const replayAtEnd = Boolean(simulation) && !simulationLoading && visibleCallCount >= totalCalls;
  const blocked = simulation?.status === "blocked" ? simulation.blocked ?? {} : null;
  const station = (seat, position, label, compact = false) => e(HandStation, {
    seat, position, label, hand: deal[seat], setHolding, compact,
    validation: validation.hands[seat], vulnerable: isSeatVulnerable(seat, vulnerability),
  });

  return e("section", { className: "bridge-panel" },
    e("div", { className: "deal-toolbar" },
      e("div", { className: "deal-actions" },
        e("button", { className: "primary", onClick: onRandomDeal }, "Random deal"),
        e("button", {
          className: "ghost", onClick: onCompleteOpponents, disabled: !canCompleteOpponents,
          title: canCompleteOpponents
            ? "Keep N/S hands and randomly deal the remaining 26 cards to E/W"
            : "Enter 13 valid cards in each N/S hand, with no duplicates, to fill E/W",
        }, "Fill E/W hands"),
        e("button", { className: "ghost", onClick: onClearOpponents }, "Clear E/W hands"),
        e("button", {
          className: "ghost", "aria-pressed": showOpponents,
          onClick: () => setShowOpponents(!showOpponents),
        }, showOpponents ? "Hide E/W hands" : "Show E/W hands"),
      ),
      e("div", { className: validation.valid ? "deal-health valid" : "deal-health invalid", role: "status" },
        validation.valid ? "52 cards · Valid deal" : "Check hands before bidding",
      ),
    ),
    e("div", { className: "training-toolbar" },
      e("label", null, "Training", e("select", { "aria-label": "Training mode", value: trainingMode,
        onChange: (event) => setTrainingMode(event.target.value) },
        e("option", { value: "off" }, "Off"),
        e("option", { value: "opening" }, "Specified opening"),
        e("option", { value: "response" }, "Opening + response"))),
      trainingMode !== "off" && e(React.Fragment, null,
        e("label", null, "Opening", e("input", { "aria-label": "Target opening", value: targetOpening,
          onChange: (event) => setTargetOpening(event.target.value), placeholder: "1NT", list: "training-openings" })),
        e("datalist", { id: "training-openings" }, ["1NT", "1C", "1D", "1H", "1S", "2C", "2D", "2H", "2S"].map(
          (call) => e("option", { key: call, value: call }))),
        trainingMode === "response" && e("label", null, "Response", e("input", {
          "aria-label": "Target response", value: targetResponse,
          onChange: (event) => setTargetResponse(event.target.value), placeholder: "4C", list: "training-responses" })),
        e("datalist", { id: "training-responses" }, ["4C", "4D", "2C", "2D", "2H", "2S", "3NT"].map(
          (call) => e("option", { key: call, value: call }))),
        e("label", null, "Opener", e("select", { "aria-label": "Training opener", value: targetOpener,
          onChange: (event) => setTargetOpener(event.target.value) },
          [["ns", "North or South"], ["ew", "East or West"], ["random", "Random"],
            ["n", "North"], ["e", "East"], ["s", "South"], ["w", "West"]].map(
            ([value, label]) => e("option", { key: value, value }, label)))),
        e("label", null, "Seed", e("input", { "aria-label": "Training seed", value: trainingSeed,
          onChange: (event) => setTrainingSeed(event.target.value), placeholder: "Random", inputMode: "numeric" })),
        trainingLoading
          ? e("button", { className: "ghost", onClick: onCancelTraining }, "Cancel search")
          : e("button", { className: "primary", onClick: onGenerateTraining }, "Generate matching deal"),
        trainingResult?.status === "matched" && e("span", { className: "training-match", role: "status" },
          `Matched after ${trainingResult.attempts} deals · ${trainingResult.opener.toUpperCase()} opens`),
      ),
    ),
    e("div", { className: "bridge-layout" },
      e("div", { className: `bridge-table${showOpponents ? " opponents-visible" : ""}` },
        station("n", "north", "North"),
        showOpponents ? station("w", "west", "West", true)
          : e(SeatPanel, { seat: "west", label: "West", validation: validation.hands.w, vulnerable: isSeatVulnerable("west", vulnerability) }),
        e("div", { className: "auction-center" },
          e(AuctionPanel, { records: visibleRecords, dealer, vulnerability, loading: simulationLoading,
            invalid: !validation.valid, blocked, limited: simulation?.status === "limit" }),
          e(AuctionControls, {
            hasSimulation: Boolean(simulation),
            canBack: !simulationLoading && visibleCallCount > 0,
            canForward: !simulationLoading && (!simulation || visibleCallCount < totalCalls),
            replayAtEnd, hasCalls: totalCalls > 0, visibleCallCount, loading: simulationLoading || !validation.valid,
            onShowFirst, onStepForward, onStepBackward, onShowAll,
            dealer, setDealer, vulnerability, setVulnerability,
          }),
        ),
        showOpponents ? station("e", "east", "East", true)
          : e(SeatPanel, { seat: "east", label: "East", validation: validation.hands.e, vulnerable: isSeatVulnerable("east", vulnerability) }),
        station("s", "south", "South"),
      ),
    ),
    e("div", { className: "deal-help" }, "A K Q J T / 10–2 · Blank or - = void · ← → at field edges changes suit · Fill/Clear E/W hands keeps N/S · Training evaluates the selected profile; unsupported calls are reported"),
    e("section", { className: "analysis-tools" },
      e("div", { className: "analysis-tools-header" },
        e("span", null, "Analysis tools"),
        e("button", {
          type: "button", className: "ghost", "aria-controls": "analysis-tools-content",
          "aria-expanded": showAnalysisTools,
          onClick: () => setShowAnalysisTools((visible) => !visible),
        }, showAnalysisTools ? "Hide analysis tools" : "Show analysis tools"),
      ),
      e("div", { id: "analysis-tools-content", className: "analysis-tools-content", hidden: !showAnalysisTools },
        e(ContractAnalysis, { profileId, deal, dealer, vulnerability,
          calls: visibleRecords.map((record) => record.call), valid: validation.valid,
          replayKey: `${profileId}:${dealer}:${vulnerability}:${visibleCallCount}:${simulation?.auction ?? ""}` }),
        e(RouteExperiment, { profileId, deal, dealer, vulnerability,
          calls: visibleRecords.map((record) => record.call), valid: validation.valid,
          replayKey: `${profileId}:${dealer}:${vulnerability}:${visibleCallCount}:${simulation?.auction ?? ""}` }),
      ),
    ),
  );
}

function RouteExperiment({ profileId, deal, dealer, vulnerability, calls, valid, replayKey }) {
  const [routes, setRoutes] = React.useState("");
  const [seed, setSeed] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const requestRef = React.useRef(null);
  const actor = actorForAuction(dealer, calls);
  const canRun = valid && calls.join("") === "1NP" && (actor === "n" || actor === "s");

  React.useEffect(() => {
    requestRef.current?.abort();
    setLoading(false);
    setResult(null);
    setError("");
  }, [deal, replayKey]);

  async function runExperiment() {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const payload = buildRouteAnalysisRequest({ profileId, deal, dealer,
        vulnerability, calls, routeText: routes, seedText: seed });
      const response = await analyzeRoutes(payload, controller.signal);
      if (requestRef.current === controller) setResult(response);
    } catch (caught) {
      if (requestRef.current === controller && caught?.name !== "AbortError") setError(caught.message);
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null;
        setLoading(false);
      }
    }
  }

  return e("section", { className: "contract-analysis", "aria-label": "Route experiment" },
    e("div", { className: "contract-analysis-heading" },
      e("h3", null, "Compare bidding routes"),
      e("p", null, "At the first response to 1NT, try calls on the same possible deals. Missing continuations count as blocked, not failed contracts. This report does not rank calls.")),
    e("div", { className: "contract-analysis-controls" },
      e("label", null, "First calls", e("input", { "aria-label": "First calls to compare",
        value: routes, onChange: (event) => { setRoutes(event.target.value); setResult(null); setError(""); },
        placeholder: "4C, 2D" })),
      e("label", null, "Seed (optional)", e("input", { "aria-label": "Route experiment seed",
        value: seed, onChange: (event) => { setSeed(event.target.value); setResult(null); setError(""); },
        placeholder: "Random" })),
      e("button", { className: "ghost", disabled: !canRun || loading || !routes.trim(),
        onClick: runExperiment }, loading ? "Comparing..." : "Compare routes"),
    ),
    !canRun && e("p", { className: "contract-analysis-hint" },
      !valid ? "Complete a valid deal first." : "Step to a North or South first response to 1NT."),
    error && e("p", { className: "contract-analysis-error", role: "alert" }, error),
    result && e("div", { className: "contract-analysis-results", role: "status" },
      e("p", null, `${result.sample_count} shared sampled deals · ${result.attempts} attempts · seed ${result.seed} · opponents pass · solver ${result.solver?.package ?? "unknown"}${result.solver?.version ? ` ${result.solver.version}` : ""}`),
      e("ul", null, result.routes.map((route) => e("li", { key: route.first_call },
        e("strong", null, route.first_call),
        e("span", null, route.status === "unavailable"
          ? `Route unavailable: ${route.reason}`
          : `${route.completed}/${result.sample_count} completed · ${route.made} made, ${route.failed} failed · ${route.blocked} blocked`),
        route.completion_interval_95 && e("span", null,
          `Making rate ${Math.round(route.completion_rate * 100)}% · 95% interval ${Math.round(route.completion_interval_95[0] * 100)}–${Math.round(route.completion_interval_95[1] * 100)}%`),
        route.contracts.map((contract) => e("span", { key: `${contract.contract}-${contract.declarer}` },
          `${contract.contract} ${contract.declarer.toUpperCase()}: ${contract.made}/${contract.count} made`)),
        route.block_reasons.map((blocked) => e("span", { key: blocked.reason },
          `${blocked.count} blocked: ${blocked.reason}`)),
      ))),
    ),
  );
}

function ContractAnalysis({ profileId, deal, dealer, vulnerability, calls, valid, replayKey }) {
  const [targets, setTargets] = React.useState("");
  const [seed, setSeed] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const requestRef = React.useRef(null);
  const actor = actorForAuction(dealer, calls);
  const canAnalyze = valid && calls.length > 0 && (actor === "n" || actor === "s");

  React.useEffect(() => {
    requestRef.current?.abort();
    setLoading(false);
    setResult(null);
    setError("");
  }, [deal, replayKey]);

  async function runAnalysis() {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const payload = buildContractAnalysisRequest({ profileId, deal, dealer,
        vulnerability, calls, targetText: targets, seedText: seed });
      const response = await analyzeContracts(payload, controller.signal);
      if (requestRef.current === controller) setResult(response);
    } catch (caught) {
      if (requestRef.current === controller && caught?.name !== "AbortError") setError(caught.message);
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null;
        setLoading(false);
      }
    }
  }

  return e("section", { className: "contract-analysis", "aria-label": "Contract analysis" },
    e("div", { className: "contract-analysis-heading" },
      e("h3", null, "Contract analysis"),
      e("p", null, "Enter specific contracts to estimate how often each is made. This does not choose a bid.")),
    e("div", { className: "contract-analysis-controls" },
      e("label", null, "Contracts", e("input", { "aria-label": "Contracts to analyze",
        value: targets, onChange: (event) => { setTargets(event.target.value); setResult(null); setError(""); },
        placeholder: "4HN, 6HN" })),
      e("label", null, "Seed (optional)", e("input", { "aria-label": "Analysis seed",
        value: seed, onChange: (event) => { setSeed(event.target.value); setResult(null); setError(""); },
        placeholder: "Random" })),
      e("button", { className: "ghost", disabled: !canAnalyze || loading || !targets.trim(),
        onClick: runAnalysis }, loading ? "Analyzing..." : "Analyze"),
    ),
    !canAnalyze && e("p", { className: "contract-analysis-hint" },
      !valid ? "Complete a valid deal first." : !calls.length ? "Show an auction call first."
        : "Step to a North or South turn to analyze that player's hand."),
    error && e("p", { className: "contract-analysis-error", role: "alert" }, error),
    result && e("div", { className: "contract-analysis-results", role: "status" },
      e("p", null, `${result.sample_count} sampled deals · ${result.attempts} attempts · seed ${result.seed}`),
      e("ul", null, result.estimates.map((estimate) => e("li", {
        key: `${estimate.contract}-${estimate.declarer}` },
        e("strong", null, `${estimate.contract} ${estimate.declarer.toUpperCase()}`),
        e("span", null, `${estimate.made}/${estimate.sample_count} made (${Math.round(estimate.completion_rate * 100)}%)`),
      ))),
    ),
  );
}

function HandStation({ seat, position, label, hand, setHolding, vulnerable, validation, compact }) {
  const inputs = React.useRef([]);
  const displayHand = Object.fromEntries(SUITS.map((suit) => [suit, normalizeHolding(hand[suit]).replace(/[^AKQJT98765432]/g, "")]));
  function moveBetweenSuits(event, index) {
    if (event.shiftKey || event.ctrlKey || event.metaKey || event.altKey || event.nativeEvent.isComposing) return;
    const input = event.currentTarget;
    if (input.selectionStart !== input.selectionEnd) return;
    let next = null;
    if (event.key === "ArrowLeft" && input.selectionStart === 0 && index > 0) next = index - 1;
    if (event.key === "ArrowRight" && input.selectionEnd === input.value.length && index < SUITS.length - 1) next = index + 1;
    if (next === null) return;
    event.preventDefault();
    const target = inputs.current[next];
    target.focus();
    const cursor = next < index ? target.value.length : 0;
    target.setSelectionRange(cursor, cursor);
  }
  return e("div", { className: `hand-station ${position}${compact ? " compact-hand" : ""}${vulnerable ? " vulnerable" : ""}` },
    !compact && e(HandDiagram, { hand: displayHand }),
    e("div", { className: "hand-meta" },
      e("div", { className: "hand-station-head" },
        e("span", { className: "seat-badge" }, label[0]),
        e("div", null,
          e("strong", null, label),
          e("small", null, handSummary(compactHand(displayHand))),
        ),
      ),
      e("div", { className: "suit-inputs", role: "group", "aria-label": `${label} hand` },
        SUITS.map((suit, index) => {
          const errorId = `${seat}-${suit}-error`;
          return e("div", { className: "suit-field", key: suit },
            e("label", { className: `suit-entry ${suitClass(suit)}` },
              e("span", { "aria-hidden": true }, suitSymbol(suit)),
              e("input", {
                ref: (element) => { inputs.current[index] = element; },
                className: "suit-input", value: hand[suit],
                "aria-label": `${label} ${SUIT_NAMES[suit]}`,
                "aria-invalid": validation.suitErrors[suit].length > 0,
                "aria-describedby": validation.suitErrors[suit].length ? errorId : `${seat}-hand-status`,
                autoComplete: "off", spellCheck: false, autoCapitalize: "characters",
                placeholder: "—",
                onChange: (event) => setHolding(seat, suit, event.target.value),
                onBlur: (event) => setHolding(seat, suit, normalizeHolding(event.target.value)),
                onKeyDown: (event) => moveBetweenSuits(event, index),
              }),
            ),
            validation.suitErrors[suit].length > 0 && e("span", { id: errorId, className: "sr-only" }, validation.suitErrors[suit].join(" ")),
          );
        }),
      ),
      e("div", { className: validation.errors.length ? "hand-validation invalid" : "hand-validation", id: `${seat}-hand-status`, "aria-live": "polite" },
        e("span", { className: "hand-count" }, `${validation.count} / 13 cards`),
        validation.errors.length > 0 && e("ul", null, validation.errors.map((message) => e("li", { key: message }, message))),
      ),
    ),
  );
}

function SeatPanel({ seat, label, vulnerable, validation }) {
  return e("div", { className: `seat-panel ${seat}${vulnerable ? " vulnerable" : ""}` },
    e("span", { className: "seat-badge" }, label[0]),
    e("strong", null, label),
    e("small", null, "Hidden"),
    e("small", { className: validation.errors.length ? "hidden-hand-error" : "" },
      validation.errors.length ? "Check hand" : `${validation.count} cards`),
  );
}

function AuctionControls({
  hasSimulation,
  canBack,
  canForward,
  replayAtEnd,
  hasCalls,
  visibleCallCount,
  loading,
  onShowFirst,
  onStepForward,
  onStepBackward,
  onShowAll,
  dealer,
  setDealer,
  vulnerability,
  setVulnerability,
}) {
  const nextTitle = !hasSimulation || visibleCallCount === 0 ? "Start auction" : "Show next call";
  return e("div", { className: "auction-player" },
    e("div", { className: "auction-settings" },
      e("select", {
        value: dealer,
        title: "Dealer",
        "aria-label": "Dealer",
        onChange: (event) => setDealer(event.target.value),
      },
        SEATS.map((seat) => e("option", { key: seat, value: seat }, `Dealer: ${seatNameShort(seat)}`)),
      ),
      e("select", {
        value: vulnerability,
        title: "Vulnerability",
        "aria-label": "Vulnerability",
        onChange: (event) => setVulnerability(event.target.value),
      },
        e("option", { value: "none" }, "Vul: None"),
        e("option", { value: "ns" }, "Vul: N-S"),
        e("option", { value: "ew" }, "Vul: E-W"),
        e("option", { value: "both" }, "Vul: Both"),
      ),
    ),
    e("div", { className: "transport-controls" },
      e("button", {
        className: "transport-button ghost",
        disabled: loading || !hasSimulation || !hasCalls,
        title: "Show first call",
        "aria-label": "Show first call",
        onClick: onShowFirst,
      }, "\u23ee"),
      e("button", {
        className: "transport-button ghost",
        disabled: loading || !canBack,
        title: "Step backward",
        "aria-label": "Step backward",
        onClick: onStepBackward,
      }, "\u25c0"),
      e("button", {
        className: "transport-button primary",
        disabled: loading || (!canForward && hasSimulation),
        title: nextTitle,
        "aria-label": nextTitle,
        onClick: onStepForward,
      }, "\u25b6"),
      e("button", {
        className: "transport-button ghost",
        disabled: loading || replayAtEnd,
        title: "Show full auction",
        "aria-label": "Show full auction",
        onClick: onShowAll,
      }, "\u23ed"),
    ),
    e("div", { className: "auction-player-spacer" }),
  );
}

function HandDiagram({ hand }) {
  const cards = ["S", "H", "D", "C"].flatMap((suit) =>
    hand[suit].split("").map((rank, index) => ({ suit, rank, key: `${suit}-${rank}-${index}` })),
  );
  return e("div", { className: "card-fan", style: { gridTemplateColumns: `repeat(${Math.max(1, cards.length)}, minmax(0, 1fr))` } },
    cards.length
      ? cards.map((card) => e("span", {
          className: `playing-card ${suitClass(card.suit)}`,
          key: card.key,
        },
          e("span", { className: "card-corner top" },
            e("b", null, rankLabel(card.rank)),
            e("span", null, suitSymbol(card.suit)),
          ),
          e("span", { className: "card-pip" }, suitSymbol(card.suit)),
          e("span", { className: "card-corner bottom" },
            e("b", null, rankLabel(card.rank)),
            e("span", null, suitSymbol(card.suit)),
          ),
        ))
      : e("span", { className: "card-void" }, "No cards parsed"),
  );
}

function AuctionPanel({ records, dealer, vulnerability, loading, invalid, blocked, limited }) {
  const [tooltip, setTooltip] = React.useState(null);
  const panelRef = React.useRef(null);
  const recordSignature = records.map((record) => `${record.seat}:${record.call}:${logicHint(record)}`).join("\u0001");
  const rows = auctionRows(records, dealer);
  function showTooltip(record, event) {
    const position = tooltipPosition(event);
    setTooltip((prior) => prior?.pinned ? prior : {
      text: logicHint(record),
      ...position,
    });
  }

  function moveTooltip(event) {
    const position = tooltipPosition(event);
    setTooltip((prior) => prior && !prior.pinned ? { ...prior, ...position } : prior);
  }

  function pinTooltip(record, key, event) {
    setTooltip({ text: logicHint(record), key, pinned: true, ...tooltipPosition(event) });
  }

  React.useEffect(() => { setTooltip(null); }, [recordSignature, dealer, loading, invalid]);

  React.useEffect(() => {
    if (!tooltip?.pinned) return undefined;
    function closeOnOutsideClick(event) {
      const target = event.target;
      if (panelRef.current?.contains(target)
          && target instanceof Element
          && target.closest(".auction-call-card:not(.empty), .auction-tooltip")) return;
      setTooltip(null);
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") setTooltip(null);
    }
    document.addEventListener("pointerdown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [tooltip?.pinned]);

  return e("div", { className: "auction-panel", ref: panelRef },
    e("div", { className: "auction-head" },
      SEATS.map((seat) => e("span", {
        className: isSeatVulnerable(seat, vulnerability) ? "auction-column vulnerable" : "auction-column",
        key: seat,
      },
        e("b", null, seatNameShort(seat)),
        dealer === seat && e("em", null, "Dealer"),
      )),
    ),
    e("div", { className: loading ? "auction-body loading" : "auction-body" },
      loading
        ? e("div", { className: "auction-empty waiting" }, "Waiting for server...")
        : rows.length
        ? rows.map((row, rowIndex) => e("div", { className: "auction-row", key: rowIndex },
            SEATS.map((seat) => {
              const record = row[seat];
              return e("span", {
                className: [
                  record ? `auction-call-card ${callClass(record.call)}` : "auction-call-card empty",
                  isSeatVulnerable(seat, vulnerability) ? "vulnerable-column" : "",
                ].filter(Boolean).join(" "),
                key: `${rowIndex}-${seat}`,
                onMouseEnter: record ? (event) => showTooltip(record, event) : undefined,
                onMouseMove: record ? moveTooltip : undefined,
                onMouseLeave: record ? () => setTooltip((prior) => prior?.pinned ? prior : null) : undefined,
                onFocus: record ? (event) => showTooltip(record, event) : undefined,
                onBlur: record ? () => setTooltip((prior) => prior?.pinned ? prior : null) : undefined,
                onClick: record ? (event) => pinTooltip(record, `${rowIndex}-${seat}`, event) : undefined,
                onKeyDown: record ? (event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    pinTooltip(record, `${rowIndex}-${seat}`, event);
                  }
                } : undefined,
                role: record ? "button" : undefined,
                tabIndex: record ? 0 : undefined,
              }, record
                ? e(React.Fragment, null,
                    e("span", { className: "call-text" }, callLabel(record.call)),
                    isAlertable(record) && e("span", { className: "alert-mark", title: "Alertable call" }, "!"),
                  )
                : "");
            }),
          ))
        : !blocked && e("div", { className: "auction-empty" }, invalid ? "Fix the highlighted hands to begin. Show E/W hands to check hidden cards." : "Press \u25b6 to begin."),
      !loading && !invalid && blocked && e("div", { className: "auction-blocked", role: "status" },
        e("strong", null, `Auction blocked${blocked.seat ? ` · ${seatNameShort(blocked.seat)}` : ""}`),
        e("p", null, "No acceptable call. Review the profile rules or change the deal to continue."),
        e("ul", null, [...(blocked.diagnostics ?? []), ...axiomSummary(blocked.axioms)].map((line, index) =>
          e("li", { key: index }, line))),
      ),
      !loading && !invalid && limited && e("div", { className: "auction-blocked", role: "status" },
        e("strong", null, "Auction stopped at the call limit"),
        e("p", null, "Replay shows the available calls; the auction is unfinished."),
      ),
    ),
    tooltip && e("div", {
      className: tooltip.pinned ? "auction-tooltip pinned" : "auction-tooltip",
      role: "note",
      style: { left: `${tooltip.x}px`, top: `${tooltip.y}px` },
    }, tooltip.text),
  );
}

function tooltipPosition(event) {
  const offsetX = 16;
  const offsetY = 18;
  const maxWidth = 400;
  const maxHeight = 180;
  const viewportWidth = window.innerWidth || 1200;
  const viewportHeight = window.innerHeight || 800;
  const rect = event.currentTarget?.getBoundingClientRect?.();
  const clientX = Number.isFinite(event.clientX) ? event.clientX : (rect?.left ?? 0) + (rect?.width ?? 0) / 2;
  const clientY = Number.isFinite(event.clientY) ? event.clientY : (rect?.top ?? 0) + (rect?.height ?? 0) / 2;
  return {
    x: Math.max(8, Math.min(clientX + offsetX, viewportWidth - maxWidth - 8)),
    y: Math.max(8, Math.min(clientY + offsetY, viewportHeight - maxHeight - 8)),
  };
}

function isAlertable(record) {
  const meaning = record?.explanation?.public_meaning?.meaning ?? {};
  return Boolean(meaning.alertable);
}

function seatNameShort(seat) {
  return { n: "North", e: "East", s: "South", w: "West" }[String(seat || "").toLowerCase()] || seat;
}

function auctionRows(records, dealer) {
  const rows = [];
  let current = { n: null, e: null, s: null, w: null };
  let priorIndex = SEATS.indexOf(dealer || "n") - 1;

  for (const record of records) {
    const seat = String(record.seat || "").toLowerCase();
    const seatIndex = SEATS.indexOf(seat);
    if (seatIndex < 0) continue;
    if (seatIndex <= priorIndex || current[seat]) {
      rows.push(current);
      current = { n: null, e: null, s: null, w: null };
    }
    current[seat] = record;
    priorIndex = seatIndex;
  }

  if (Object.values(current).some(Boolean)) rows.push(current);
  return rows;
}

function isSeatVulnerable(seat, vulnerability) {
  const normalizedSeat = String(seat || "").toLowerCase();
  const seatLetter = normalizedSeat[0];
  const normalizedVul = String(vulnerability || "none").toLowerCase();
  if (normalizedVul === "both") return true;
  if (normalizedVul === "ns") return seatLetter === "n" || seatLetter === "s";
  if (normalizedVul === "ew") return seatLetter === "e" || seatLetter === "w";
  return false;
}
