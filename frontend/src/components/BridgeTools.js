import { React, e } from "../ui/react.js";
import {
  callClass,
  callLabel,
  handSummary,
  logicHint,
  parseHand,
  rankLabel,
  suitClass,
  suitSymbol,
} from "../lib/bridge.js";

const SEATS = ["n", "e", "s", "w"];

export function BridgePanel({
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
  onShowFirst,
  onStepForward,
  onStepBackward,
  onShowAll,
}) {
  const records = simulation?.records ?? [];
  const visibleRecords = simulationLoading ? [] : records.slice(0, visibleCallCount);
  const totalCalls = records.length;
  const isComplete = !simulationLoading && totalCalls > 0 && visibleCallCount >= totalCalls;

  return e("section", { className: "bridge-panel" },
    e("div", { className: "bridge-layout" },
      e("div", { className: "bridge-table" },
        e(HandStation, {
          seat: "north",
          label: "North",
          hand: northHand,
          setHand: setNorthHand,
          vulnerable: isSeatVulnerable("north", vulnerability),
        }),
        e(SeatPanel, { seat: "west", label: "West", vulnerable: isSeatVulnerable("west", vulnerability) }),
        e("div", { className: "auction-center" },
          e(AuctionPanel, { records: visibleRecords, dealer, vulnerability, loading: simulationLoading }),
          e(AuctionControls, {
            hasSimulation: Boolean(simulation),
            canBack: !simulationLoading && visibleCallCount > 0,
            canForward: !simulationLoading && (!simulation || visibleCallCount < totalCalls),
            isComplete,
            visibleCallCount,
            loading: simulationLoading,
            onShowFirst,
            onStepForward,
            onStepBackward,
            onShowAll,
            dealer,
            setDealer,
            vulnerability,
            setVulnerability,
          }),
        ),
        e(SeatPanel, { seat: "east", label: "East", vulnerable: isSeatVulnerable("east", vulnerability) }),
        e(HandStation, {
          seat: "south",
          label: "South",
          hand: southHand,
          setHand: setSouthHand,
          vulnerable: isSeatVulnerable("south", vulnerability),
        }),
      ),
    ),
  );
}

function HandStation({ seat, label, hand, setHand, vulnerable }) {
  return e("div", { className: `hand-station ${seat}${vulnerable ? " vulnerable" : ""}` },
    e(HandDiagram, { hand }),
    e("div", { className: "hand-meta" },
      e("div", { className: "hand-station-head" },
        e("span", { className: "seat-badge" }, label[0]),
        e("div", null,
          e("strong", null, label),
          e("small", null, handSummary(hand)),
        ),
      ),
      e("label", { className: "hand-entry" },
        e("span", null, "Hand"),
        e("input", {
          className: "hand-input",
          value: hand,
          onChange: (event) => setHand(event.target.value),
          "aria-label": `${label} hand`,
        }),
      ),
    ),
  );
}

function SeatPanel({ seat, label, vulnerable }) {
  return e("div", { className: `seat-panel ${seat}${vulnerable ? " vulnerable" : ""}` },
    e("span", { className: "seat-badge" }, label[0]),
    e("strong", null, label),
  );
}

function AuctionControls({
  hasSimulation,
  canBack,
  canForward,
  isComplete,
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
        disabled: loading || !hasSimulation,
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
        disabled: loading || isComplete,
        title: "Show full auction",
        "aria-label": "Show full auction",
        onClick: onShowAll,
      }, "\u23ed"),
    ),
    e("div", { className: "auction-player-spacer" }),
  );
}

function HandDiagram({ hand }) {
  const parsed = parseHand(hand);
  const cards = ["S", "H", "D", "C"].flatMap((suit) =>
    parsed[suit].split("").map((rank, index) => ({ suit, rank, key: `${suit}-${rank}-${index}` })),
  );
  return e("div", { className: "card-fan" },
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

function AuctionPanel({ records, dealer, vulnerability, loading }) {
  const [tooltip, setTooltip] = React.useState(null);
  const rows = auctionRows(records, dealer);
  function showTooltip(record, event) {
    setTooltip({
      text: logicHint(record),
      ...tooltipPosition(event),
    });
  }

  function moveTooltip(event) {
    setTooltip((prior) => prior ? { ...prior, ...tooltipPosition(event) } : prior);
  }

  return e("div", { className: "auction-panel" },
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
                onMouseLeave: record ? () => setTooltip(null) : undefined,
                onFocus: record ? (event) => showTooltip(record, event) : undefined,
                onBlur: record ? () => setTooltip(null) : undefined,
                tabIndex: record ? 0 : undefined,
              }, record
                ? e(React.Fragment, null,
                    e("span", { className: "call-text" }, callLabel(record.call)),
                    isAlertable(record) && e("span", { className: "alert-mark", title: "Alertable call" }, "!"),
                  )
                : "");
            }),
          ))
        : e("div", { className: "auction-empty" }, "Press \u25b6 to begin."),
    ),
    tooltip && e("div", {
      className: "auction-tooltip",
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
  return {
    x: Math.max(8, Math.min(event.clientX + offsetX, viewportWidth - maxWidth - 8)),
    y: Math.max(8, Math.min(event.clientY + offsetY, viewportHeight - maxHeight - 8)),
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
