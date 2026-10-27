const MISSED_FLAGS = new Set([
  "missed_game", "missed_small_slam", "missed_grand_slam",
]);

export function pairBadges(pair = {}) {
  if (pair.status === "limit") return ["UNAVAILABLE"];
  if (pair.status === "blocked" || pair.blocked) return ["TD"];
  const flags = new Set(pair.flags || []);
  const badges = [];
  if (flags.has("contract_failure")) badges.push("SET");
  if ([...MISSED_FLAGS].some((flag) => flags.has(flag))) badges.push("LOSE");
  if (flags.has("wrong_game")) badges.push("WRONG");
  return badges.length ? badges : ["CLEAN"];
}

export function pairMatches(pair = {}, category = "all", search = "") {
  if (category !== "all" && !(pair.categories || []).includes(category)) return false;
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

export function filterScannerGroups(groups = [], category = "all", search = "") {
  return groups.filter((group) => (group.pairs || []).some(
    (pair) => pairMatches(pair, category, search),
  ));
}

export function selectPairForGroup(group, category = "all", search = "") {
  return group?.pairs?.find((pair) => pairMatches(pair, category, search)) || null;
}
