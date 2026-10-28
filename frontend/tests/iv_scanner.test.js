import test from "node:test";
import assert from "node:assert/strict";
import {
  DEFAULT_THRESHOLDS, filterScannerGroups, groupCategories, paginateGroups,
  pairBadges, pairFlags, pairMatches, selectPairForGroup, wrongGameScores,
} from "../src/lib/ivScanner.js";

const LOW_RATES = {
  contract_failure: .10,
  missed_game: .10,
  missed_small_slam: .05,
  missed_grand_slam: .02,
  wrong_game: null,
};
const LOW_ALTERNATIVES = { "3NT": .3, "4H": .1, "5C": .05, "5D": .05 };

const pair = (overrides = {}) => ({
  id: 11,
  pair_slot: 0,
  status: "complete",
  categories: [],
  auction: "1NP2HP2SPPP",
  calls: ["1N", "P", "2H", "P", "2S", "P", "P", "P"],
  contract: "2S",
  declarer: "s",
  hands: { n: "SAKQJH432D432C432", s: "S432HAKQJDAKQJC32" },
  rates: { ...LOW_RATES },
  alternative_game_rates: { ...LOW_ALTERNATIVES },
  ...overrides,
});

test("default thresholds match the shared rule set", () => {
  assert.deepEqual(DEFAULT_THRESHOLDS, {
    set: 0.6, missed: 0.3, wrong: 0.8, wrongFloor: 0.4,
  });
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
    contract: "4S",
    rates: {
      contract_failure: .62, missed_game: .4, missed_small_slam: .4,
      missed_grand_slam: .4, wrong_game: .42,
    },
    alternative_game_rates: { "3NT": .9, "4H": .1, "5C": .05, "5D": .05 },
  })), ["SET", "LOSE", "WRONG"]);
});

test("clean complete pairs receive a CLEAN badge", () => {
  assert.deepEqual(pairBadges(pair()), ["CLEAN"]);
});

test("SET threshold is configurable and strict", () => {
  const candidate = pair({
    contract: "4S",
    rates: { ...LOW_RATES, contract_failure: .55 },
  });
  assert.deepEqual(pairFlags(candidate), []);
  assert.deepEqual(pairFlags(candidate, { ...DEFAULT_THRESHOLDS, set: .55 }), []);
  assert.deepEqual(pairFlags(candidate, { ...DEFAULT_THRESHOLDS, set: .5 }),
    ["contract_failure"]);
});

test("WRONG uses the chosen/best-other completion ratio at the set threshold", () => {
  const candidate = pair({
    contract: "3NT",
    rates: { ...LOW_RATES, contract_failure: .15 },
    alternative_game_rates: { "4S": 1.0, "4H": .1, "5C": .05, "5D": .05 },
  });
  assert.equal(wrongGameScores(candidate).ratio, .85);
  assert.deepEqual(pairFlags(candidate), []);
  assert.deepEqual(pairFlags(candidate, { ...DEFAULT_THRESHOLDS, wrong: .9 }),
    ["wrong_game"]);
});

test("LOSE threshold is configurable and merges missed targets", () => {
  const candidate = pair({
    contract: "2S",
    rates: { ...LOW_RATES, missed_game: .25 },
  });
  assert.deepEqual(pairFlags(candidate), []);
  assert.deepEqual(pairFlags(candidate, { ...DEFAULT_THRESHOLDS, missed: .2 }),
    ["missed_game"]);
});

test("WRONG is suppressed when the best other game fails the configured floor", () => {
  const candidate = pair({
    contract: "3NT",
    rates: { ...LOW_RATES, contract_failure: .75 },
    alternative_game_rates: { "4S": .35, "4H": .1, "5C": .05, "5D": .05 },
  });
  assert.ok(!pairFlags(candidate).includes("wrong_game"));
  assert.ok(pairFlags(candidate, { ...DEFAULT_THRESHOLDS, wrongFloor: .3 })
    .includes("wrong_game"));
});

test("pair matching combines category and normalized search across pair evidence", () => {
  const warned = pair({
    id: 42,
    pair_slot: 6,
    contract: "3NT",
    categories: ["wrong"],
    auction: "1NP3NPPP",
    hands: { n: "SAKQJ", s: "H9876" },
    rates: { ...LOW_RATES, contract_failure: .35 },
    alternative_game_rates: { "4S": .9, "4H": .1, "5C": .05, "5D": .05 },
  });
  assert.equal(pairMatches(warned, "wrong", " 3n "), true);
  assert.equal(pairMatches(warned, "wrong", "akqj"), true);
  assert.equal(pairMatches(warned, "wrong", "42"), true);
  assert.equal(pairMatches(warned, "down", "42"), false);
  assert.equal(pairMatches(warned, "wrong", "missing"), false);
});

test("group filtering retains every sibling when any child matches", () => {
  const clean = pair({ id: 1 });
  const warned = pair({
    id: 2,
    contract: "4S",
    rates: { ...LOW_RATES, contract_failure: .7 },
  });
  const other = { id: "other", pairs: [pair({ id: 3 })] };
  const group = { id: "10:0", pairs: [clean, warned] };

  const matches = filterScannerGroups([group, other], "down", "");

  assert.equal(matches.length, 1);
  assert.equal(matches[0], group);
  assert.deepEqual(matches[0].pairs, [clean, warned]);
  assert.deepEqual(groupCategories(group), ["down"]);
});

test("pair selection picks the first matching child without pruning siblings", () => {
  const group = {
    id: "10:0",
    pairs: [
      pair({ id: 1 }),
      pair({
        id: 2, contract: "4S",
        rates: { ...LOW_RATES, contract_failure: .7 },
      }),
      pair({
        id: 3, contract: "4S", auction: "unique relay",
        rates: { ...LOW_RATES, contract_failure: .7 },
      }),
    ],
  };
  assert.equal(selectPairForGroup(group, "down", "")?.id, 2);
  assert.equal(selectPairForGroup(group, "down", "unique relay")?.id, 3);
  assert.equal(selectPairForGroup(group, "all", "")?.id, 1);
});

test("overview pagination clamps to available pages and reports bounds", () => {
  const groups = Array.from({ length: 205 }, (_, index) => ({ id: `g${index}` }));

  const first = paginateGroups(groups, 1, 100);
  assert.equal(first.items.length, 100);
  assert.equal(first.pages, 3);
  assert.deepEqual([first.start, first.end, first.total], [1, 100, 205]);

  const last = paginateGroups(groups, 3, 100);
  assert.equal(last.items.length, 5);
  assert.deepEqual([last.start, last.end], [201, 205]);

  const clamped = paginateGroups(groups, 99, 100);
  assert.equal(clamped.page, 3);
  assert.equal(paginateGroups(groups, 0, 100).page, 1);
  assert.deepEqual(paginateGroups([], 5, 100), {
    items: [], page: 1, pages: 1, total: 0, start: 0, end: 0,
  });
});

test("raising the SET threshold hides a previously warned group", () => {
  const group = {
    id: "10:0",
    pairs: [pair({
      id: 1, contract: "4S",
      rates: { ...LOW_RATES, contract_failure: .62 },
    })],
  };
  assert.deepEqual(groupCategories(group), ["down"]);
  assert.deepEqual(groupCategories(group, { ...DEFAULT_THRESHOLDS, set: .7 }), []);
});
