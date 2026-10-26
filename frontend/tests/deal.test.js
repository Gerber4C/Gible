import test from "node:test";
import assert from "node:assert/strict";
import { SUITS, SEATS, normalizeHolding, compactHand, validateDeal, randomDeal, initialDeal, completeOpponents, clearOpponents } from "../src/lib/deal.js";

test("clears only E/W cards without changing N/S or the input deal", () => {
  const deal = initialDeal();
  deal.n.S = " a q 7 ";
  const before = structuredClone(deal);
  const cleared = clearOpponents(deal);
  assert.deepEqual(cleared.n, before.n);
  assert.deepEqual(cleared.s, before.s);
  for (const seat of ["e", "w"]) {
    assert.deepEqual(cleared[seat], { S: "", H: "", D: "", C: "" });
    assert.equal(validateDeal(cleared).hands[seat].count, 0);
  }
  assert.deepEqual(deal, before);
});

test("completes only opponents from the remaining cards, preserving raw N/S input", () => {
  const deal = initialDeal();
  deal.n.S = " a q 7 ";
  deal.e = { S: "AZ", H: "", D: "", C: "" };
  deal.w = { ...deal.s };
  const before = structuredClone(deal);
  const outcomes = new Set();
  for (let attempt = 0; attempt < 20; attempt++) {
    const completed = completeOpponents(deal);
    assert.deepEqual(completed.n, before.n);
    assert.deepEqual(completed.s, before.s);
    assert.equal(validateDeal(completed).valid, true);
    assert.equal(validateDeal(completed).hands.e.count, 13);
    assert.equal(validateDeal(completed).hands.w.count, 13);
    outcomes.add(JSON.stringify(completed.e));
  }
  assert.deepEqual(deal, before);
  assert.ok(outcomes.size > 1);
  const { n, s } = deal;
  assert.equal(validateDeal(completeOpponents({ n, s })).valid, true);
});

test("refuses completion for incomplete, illegal, or duplicate N/S cards", () => {
  for (const holding of ["AQ", "AQ77", "AQ7Z", "AA7", "AT7"]) {
    const deal = initialDeal();
    deal.n.S = holding; // AT7 also conflicts with South's T.
    const before = structuredClone(deal);
    assert.throws(() => completeOpponents(deal), /North|South/);
    assert.deepEqual(deal, before);
  }
});

test("normalizes lowercase, ten, spaces and voids without hiding invalid ranks", () => {
  assert.equal(normalizeHolding(" a k 10 2 "), "AKT2");
  assert.equal(normalizeHolding("-"), "");
  assert.equal(normalizeHolding("Az"), "AZ");
  assert.equal(normalizeHolding("A-"), "A-");
});

test("serializes suit fields to the backend format", () => {
  assert.equal(compactHand({ S: "a10", H: "-", D: "kq", C: "2" }), "SATH-DKQC2");
});

test("the initial four hands form a complete legal deal", () => {
  const result = validateDeal(initialDeal());
  assert.equal(result.valid, true, result.errors.join("; "));
  for (const seat of SEATS) assert.equal(result.hands[seat].count, 13);
});

test("rejects illegal ranks even if thirteen other cards are present", () => {
  const deal = initialDeal();
  deal.n.S += "Z";
  const result = validateDeal(deal);
  assert.equal(result.valid, false);
  assert.match(result.hands.n.suitErrors.S.join(" "), /Invalid/);
});

test("rejects repeated cards within a suit", () => {
  const deal = initialDeal();
  deal.n.S = "AA7";
  assert.match(validateDeal(deal).hands.n.suitErrors.S.join(" "), /more than once/);
});

test("marks a card shared by two hands on both hands", () => {
  const deal = initialDeal();
  deal.s.S = "A2";
  const result = validateDeal(deal);
  assert.equal(result.valid, false);
  assert.match(result.hands.n.suitErrors.S.join(" "), /South/);
  assert.match(result.hands.s.suitErrors.S.join(" "), /North/);
});

test("checks all four hands including unseen opponents", () => {
  const deal = initialDeal();
  deal.e = { S: "", H: "", D: "", C: "" };
  const result = validateDeal(deal);
  assert.equal(result.valid, false);
  assert.match(result.hands.e.errors.join(" "), /13 cards/);
});

test("rejects fourteen cards and mixed void markers", () => {
  const deal = initialDeal();
  deal.n.S += "2";
  assert.match(validateDeal(deal).hands.n.errors.join(" "), /14/);
  deal.n.S = "A-";
  assert.equal(validateDeal(deal).valid, false);
});

test("random deals have 52 unique cards, 13 per seat, sorted holdings", () => {
  const rankOrder = "AKQJT98765432";
  const outcomes = new Set();
  for (let attempt = 0; attempt < 40; attempt++) {
    const deal = randomDeal();
    assert.equal(validateDeal(deal).valid, true);
    const cards = SEATS.flatMap((seat) => SUITS.flatMap((suit) => [...deal[seat][suit]].map((rank) => suit + rank)));
    assert.equal(cards.length, 52);
    assert.equal(new Set(cards).size, 52);
    for (const seat of SEATS) for (const suit of SUITS) {
      assert.equal(deal[seat][suit], [...deal[seat][suit]].sort((a, b) => rankOrder.indexOf(a) - rankOrder.indexOf(b)).join(""));
    }
    outcomes.add(JSON.stringify(deal));
  }
  assert.ok(outcomes.size > 1);
});
