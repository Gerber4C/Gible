import { parseHand, seatName, suitSymbol } from "./bridge.js";

export const SUITS = ["S", "H", "D", "C"];
export const SEATS = ["n", "e", "s", "w"];
const RANKS = "AKQJT98765432";

export function normalizeHolding(value) {
  const text = String(value ?? "").toUpperCase().replace(/\s+/g, "").replaceAll("10", "T");
  return text === "-" ? "" : text;
}

export function compactHand(hand) {
  return SUITS.map((suit) => suit + (normalizeHolding(hand[suit]) || "-")).join("");
}

export function validateDeal(deal, seats = SEATS) {
  const hands = {};
  const owners = new Map();
  for (const seat of seats) {
    const result = { count: 0, errors: [], suitErrors: {}, normalized: {} };
    hands[seat] = result;
    for (const suit of SUITS) {
      const holding = normalizeHolding(deal[seat]?.[suit]);
      result.normalized[suit] = holding;
      const errors = result.suitErrors[suit] = [];
      const invalid = [...new Set([...holding].filter((rank) => !RANKS.includes(rank)))];
      if (invalid.length) errors.push(`${suitSymbol(suit)} Invalid rank: ${invalid.join(" ")}. Use A K Q J T or 10–2; leave voids blank.`);
      const seen = new Set();
      for (const rank of holding) {
        if (!RANKS.includes(rank)) continue;
        result.count++;
        if (seen.has(rank)) {
          const message = `${suitSymbol(suit)}${rank} appears more than once.`;
          if (!errors.includes(message)) errors.push(message);
          continue;
        }
        seen.add(rank);
        const card = suit + rank;
        if (!owners.has(card)) owners.set(card, []);
        owners.get(card).push(seat);
      }
    }
    if (result.count !== 13) result.errors.push(`Expected 13 cards; currently ${result.count}.`);
  }
  for (const [card, seats] of owners) {
    if (seats.length < 2) continue;
    for (const seat of seats) {
      const others = seats.filter((other) => other !== seat).map(seatName).join(", ");
      hands[seat].suitErrors[card[0]].push(`${suitSymbol(card[0])}${card[1]} is also in ${others}.`);
    }
  }
  for (const hand of Object.values(hands)) hand.errors.push(...Object.values(hand.suitErrors).flat());
  const errors = seats.flatMap((seat) => hands[seat].errors.map((message) => `${seatName(seat)}: ${message}`));
  return { valid: errors.length === 0, hands, errors };
}

function deck() {
  return SUITS.flatMap((suit) => [...RANKS].map((rank) => ({ suit, rank })));
}

function emptyHand() {
  return Object.fromEntries(SUITS.map((suit) => [suit, ""]));
}

function shuffle(cards) {
  for (let index = cards.length - 1; index > 0; index--) {
    const other = Math.floor(Math.random() * (index + 1));
    [cards[index], cards[other]] = [cards[other], cards[index]];
  }
  return cards;
}

export function completeOpponents(deal) {
  // Old E/W holdings are replaced; only N/S constrain this new deal.
  const validation = validateDeal(deal, ["n", "s"]);
  if (!validation.valid) throw new Error(validation.errors.join(" "));
  const { n, s } = validation.hands;
  const cards = shuffle(deck().filter(({ suit, rank }) =>
    !n.normalized[suit].includes(rank) && !s.normalized[suit].includes(rank)));
  const completed = { ...deal, e: emptyHand(), w: emptyHand() };
  cards.forEach(({ suit, rank }, index) => { completed[index % 2 ? "w" : "e"][suit] += rank; });
  for (const seat of ["e", "w"]) for (const suit of SUITS) {
    completed[seat][suit] = [...completed[seat][suit]].sort((a, b) => RANKS.indexOf(a) - RANKS.indexOf(b)).join("");
  }
  return completed;
}

export function clearOpponents(deal) {
  return { ...deal, e: emptyHand(), w: emptyHand() };
}

export function randomDeal() {
  const cards = shuffle(deck());
  const deal = Object.fromEntries(SEATS.map((seat) => [seat, emptyHand()]));
  cards.forEach(({ suit, rank }, index) => { deal[SEATS[index % 4]][suit] += rank; });
  for (const hand of Object.values(deal)) for (const suit of SUITS) {
    hand[suit] = [...hand[suit]].sort((a, b) => RANKS.indexOf(a) - RANKS.indexOf(b)).join("");
  }
  return deal;
}

export function initialDeal() {
  // Keep a simple 1NT/Texas example, with four disjoint hands.
  const deal = { n: parseHand("SAQ7HKJ8DA762CQ54"), s: parseHand("ST2HAQT976D53CKJ2"), e: emptyHand(), w: emptyHand() };
  const remainder = deck().filter(({ suit, rank }) => !deal.n[suit].includes(rank) && !deal.s[suit].includes(rank));
  remainder.forEach(({ suit, rank }, index) => { deal[index % 2 ? "w" : "e"][suit] += rank; });
  return deal;
}
