import test from "node:test";
import assert from "node:assert/strict";
import {
  pairBadges, pairMatches, filterScannerGroups, selectPairForGroup,
} from "../src/lib/ivScanner.js";

const pair = (overrides = {}) => ({
  id: 11,
  pair_slot: 0,
  status: "complete",
  categories: [],
  flags: [],
  auction: "1N P 2C P 2H P",
  hands: { n: "SAKQJH432D432C32", s: "S432HAKQJDAKQJC32" },
  ...overrides,
});

test("limit pairs are unavailable without fabricated TD or result badges", () => {
  assert.deepEqual(pairBadges(pair({
    status: "limit",
    blocked: { seat: "s" },
    flags: ["contract_failure", "missed_game", "wrong_game"],
    ew_results: [{ outcome: "MAKE", lose: true }],
  })), ["UNAVAILABLE"]);
});

test("blocked pairs receive only the TD badge", () => {
  assert.deepEqual(pairBadges(pair({
    status: "blocked",
    categories: ["block"],
    blocked: { seat: "s" },
  })), ["TD"]);
});

test("complete warning badges merge all missed targets into one LOSE badge", () => {
  assert.deepEqual(pairBadges(pair({
    categories: ["down", "missed", "wrong"],
    flags: [
      "contract_failure", "missed_game", "missed_small_slam",
      "missed_grand_slam", "wrong_game",
    ],
  })), ["SET", "LOSE", "WRONG"]);
});

test("clean complete pairs receive a CLEAN badge", () => {
  assert.deepEqual(pairBadges(pair()), ["CLEAN"]);
});

test("pair matching combines category and normalized search across pair evidence", () => {
  const warned = pair({
    id: 42,
    pair_slot: 6,
    categories: ["wrong"],
    auction: "1N P 3N P",
    hands: { n: "SAKQJ", s: "H9876" },
  });
  assert.equal(pairMatches(warned, "wrong", " 3n "), true);
  assert.equal(pairMatches(warned, "wrong", "akqj"), true);
  assert.equal(pairMatches(warned, "wrong", "42"), true);
  assert.equal(pairMatches(warned, "down", "42"), false);
  assert.equal(pairMatches(warned, "wrong", "missing"), false);
});

test("group filtering retains every sibling when any child matches", () => {
  const clean = pair({ id: 1 });
  const warned = pair({ id: 2, categories: ["down"], flags: ["contract_failure"] });
  const other = { id: "other", pairs: [pair({ id: 3 })] };
  const group = { id: "10:0", pairs: [clean, warned] };

  const matches = filterScannerGroups([group, other], "down", "2");

  assert.equal(matches.length, 1);
  assert.equal(matches[0], group);
  assert.deepEqual(matches[0].pairs, [clean, warned]);
});

test("pair selection picks the first matching child without pruning siblings", () => {
  const group = {
    id: "10:0",
    pairs: [
      pair({ id: 1 }),
      pair({ id: 2, categories: ["down"], flags: ["contract_failure"] }),
      pair({ id: 3, categories: ["down"], flags: ["contract_failure"], auction: "unique relay" }),
    ],
  };
  assert.equal(selectPairForGroup(group, "down", "")?.id, 2);
  assert.equal(selectPairForGroup(group, "down", "unique relay")?.id, 3);
  assert.equal(selectPairForGroup(group, "all", "")?.id, 1);
});
