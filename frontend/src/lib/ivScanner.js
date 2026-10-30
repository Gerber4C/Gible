export const DEFAULT_THRESHOLDS = Object.freeze({
  set: 0.6,
  missed: 0.3,
  wrong: 0.8,
  wrongFloor: 0.4,
});

const GAME_TARGETS = new Set(["3NT", "4S", "4H", "5D", "5C"]);
const MISSED_FLAGS = ["missed_game", "missed_small_slam", "missed_grand_slam"];

const probability = (value) => (
  typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1
    ? value
    : null
);

function reachedGame(contract) {
  const level = Number(contract?.[0]);
  const strain = contract?.slice(1);
  return level >= 6
    || (strain === "NT" && level >= 3)
    || ((strain === "H" || strain === "S") && level >= 4)
    || ((strain === "C" || strain === "D") && level >= 5);
}

export function wrongGameScores(pair = {}) {
  if (pair.status !== "complete" || !pair.contract || !GAME_TARGETS.has(pair.contract)) {
    return { chosen: null, bestOther: null, ratio: null };
  }
  const failure = probability(pair.rates?.contract_failure);
  if (failure == null) return { chosen: null, bestOther: null, ratio: null };
  const alternatives = Object.entries(pair.alternative_game_rates || {})
    .filter(([name]) => name !== pair.contract)
    .map(([, rate]) => probability(rate))
    .filter((rate) => rate != null);
  const bestOther = alternatives.length ? Math.max(...alternatives) : null;
  const chosen = 1 - failure;
  return { chosen, bestOther, ratio: bestOther ? chosen / bestOther : null };
}

export function pairFlags(pair = {}, thresholds = DEFAULT_THRESHOLDS) {
  if (pair.status !== "complete" || !pair.contract) return [];
  const rates = pair.rates || {};
  const flags = [];
  const failure = probability(rates.contract_failure);
  if (failure != null && failure > thresholds.set) flags.push("contract_failure");

  const { bestOther, ratio } = wrongGameScores(pair);
  if (bestOther != null && bestOther > thresholds.wrongFloor
      && ratio != null && ratio < thresholds.wrong) {
    flags.push("wrong_game");
  }

  const level = Number(pair.contract[0]);
  const missedGame = probability(rates.missed_game);
  if (!reachedGame(pair.contract) && missedGame != null
      && missedGame > thresholds.missed) {
    flags.push("missed_game");
  }
  const missedSmall = probability(rates.missed_small_slam);
  if (level < 6 && missedSmall != null && missedSmall > thresholds.missed) {
    flags.push("missed_small_slam");
  }
  const missedGrand = probability(rates.missed_grand_slam);
  if (level < 7 && missedGrand != null && missedGrand > thresholds.missed) {
    flags.push("missed_grand_slam");
  }
  return flags;
}

export function pairCategories(pair = {}, thresholds = DEFAULT_THRESHOLDS) {
  if (pair.status === "blocked") return ["block"];
  if (pair.status !== "complete") return [];
  const flags = new Set(pairFlags(pair, thresholds));
  return ["down", "missed", "wrong"].filter((category) => (
    category === "down" ? flags.has("contract_failure")
      : category === "wrong" ? flags.has("wrong_game")
        : MISSED_FLAGS.some((flag) => flags.has(flag))
  ));
}

export function groupCategories(group = {}, thresholds = DEFAULT_THRESHOLDS) {
  const present = new Set();
  (group.pairs || []).forEach((pair) => {
    pairCategories(pair, thresholds).forEach((category) => present.add(category));
  });
  return ["block", "missed", "down", "wrong"].filter((category) => present.has(category));
}

export function pairBadges(pair = {}, thresholds = DEFAULT_THRESHOLDS) {
  if (pair.status === "limit") return ["UNAVAILABLE"];
  if (pair.status === "blocked") return ["TD"];
  const flags = new Set(pairFlags(pair, thresholds));
  const badges = [];
  if (flags.has("contract_failure")) badges.push("SET");
  if (MISSED_FLAGS.some((flag) => flags.has(flag))) badges.push("LOSE");
  if (flags.has("wrong_game")) badges.push("WRONG");
  return badges.length ? badges : ["CLEAN"];
}

export function pairMatches(pair = {}, category = "all", search = "",
                            thresholds = DEFAULT_THRESHOLDS) {
  if (category !== "all" && !pairCategories(pair, thresholds).includes(category)) {
    return false;
  }
  const query = String(search).trim().toLowerCase();
  if (!query) return true;
  const evidence = [
    pair.id,
    pair.pair_slot,
    pair.auction,
    pair.hands?.n,
    pair.hands?.s,
  ];
  return evidence.some((value) => String(value ?? "").toLowerCase().includes(query));
}

export function groupMatches(group = {}, category = "all", search = "",
                             thresholds = DEFAULT_THRESHOLDS) {
  if (category !== "all" && !groupCategories(group, thresholds).includes(category)) {
    return false;
  }
  const query = String(search).trim().toLowerCase();
  if (!query) return true;
  return (group.pairs || []).some(
    (pair) => pairMatches(pair, "all", query, thresholds));
}

export function filterScannerGroups(groups = [], category = "all", search = "",
                                    thresholds = DEFAULT_THRESHOLDS) {
  return groups.filter((group) => groupMatches(group, category, search, thresholds));
}

export function selectPairForGroup(group, category = "all", search = "",
                                   thresholds = DEFAULT_THRESHOLDS) {
  return group?.pairs?.find(
    (pair) => pairMatches(pair, category, search, thresholds)) || null;
}

export function paginateGroups(groups = [], page = 1, pageSize = 100) {
  const total = groups.length;
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const current = Math.min(Math.max(Number(page) || 1, 1), pages);
  const startIndex = (current - 1) * pageSize;
  return {
    items: groups.slice(startIndex, startIndex + pageSize),
    page: current,
    pages,
    total,
    start: total ? startIndex + 1 : 0,
    end: Math.min(startIndex + pageSize, total),
  };
}

function reachedContractGame(contract) {
  return reachedGame(contract);
}

function processContractFlags(item = {}, thresholds = DEFAULT_THRESHOLDS) {
  const contract = item.contract || "";
  const level = Number(contract[0]);
  const rates = item.rates || {};
  const flags = [];
  const failure = probability(rates.contract_failure);
  if (failure != null && failure > thresholds.set) flags.push("contract_failure");
  const wrong = probability(rates.wrong_game);
  if (wrong != null && wrong < thresholds.wrong) flags.push("wrong_game");
  if (!reachedContractGame(contract)) {
    const missedGame = probability(rates.missed_game);
    if (missedGame != null && missedGame > thresholds.missed) {
      flags.push("missed_game");
    }
  }
  if (level < 6) {
    const missedSmall = probability(rates.missed_small_slam);
    if (missedSmall != null && missedSmall > thresholds.missed) {
      flags.push("missed_small_slam");
    }
  }
  if (level < 7) {
    const missedGrand = probability(rates.missed_grand_slam);
    if (missedGrand != null && missedGrand > thresholds.missed) {
      flags.push("missed_grand_slam");
    }
  }
  return flags;
}

export function processFlags(process = {}, thresholds = DEFAULT_THRESHOLDS) {
  const flags = new Set();
  (process.contracts || []).forEach((item) => {
    processContractFlags(item, thresholds).forEach((flag) => flags.add(flag));
  });
  return [...flags];
}

export function processCategories(process = {}, thresholds = DEFAULT_THRESHOLDS) {
  const flags = new Set(processFlags(process, thresholds));
  (process.north_groups || []).forEach((group) => {
    Object.entries(group.categories || {}).forEach(([key, count]) => {
      if (count > 0) flags.add(key === "block" ? "block" : key);
    });
  });
  (process.south_groups || []).forEach((group) => {
    Object.entries(group.categories || {}).forEach(([key, count]) => {
      if (count > 0) flags.add(key === "block" ? "block" : key);
    });
  });
  return ["block", "missed", "down", "wrong"].filter((category) => (
    category === "down" ? flags.has("contract_failure")
      : category === "wrong" ? flags.has("wrong_game")
        : category === "missed"
          ? MISSED_FLAGS.some((flag) => flags.has(flag))
          : flags.has(category)
  ));
}

export function processMatches(process = {}, category = "all", search = "",
                               thresholds = DEFAULT_THRESHOLDS) {
  if (category !== "all" && !processCategories(process, thresholds).includes(category)) {
    return false;
  }
  const query = String(search).trim().toLowerCase();
  if (!query) return true;
  const evidence = [
    process.auction,
    (process.process || []).join(" "),
    ...(process.contracts || []).map((item) => item.contract),
    ...(process.north_groups || []).map((group) => (group.north_shape || []).join("-")),
    ...(process.south_groups || []).map((group) => (group.south_shape || []).join("-")),
  ];
  return evidence.some((value) => String(value ?? "").toLowerCase().includes(query));
}

export function filterProcessGroups(processes = [], category = "all", search = "",
                                    thresholds = DEFAULT_THRESHOLDS) {
  return processes.filter((process) => processMatches(process, category, search, thresholds));
}

export function processBoardCount(process = {}) {
  return (process.contracts || []).reduce((sum, item) => sum + (item.boards || 0), 0);
}

export function processWorstFailure(process = {}) {
  return (process.contracts || []).reduce((worst, item) => {
    const value = probability(item.rates?.contract_failure);
    return value == null ? worst : Math.max(worst, value);
  }, 0);
}
