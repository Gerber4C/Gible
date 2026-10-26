import { compactHand } from "./deal.js";

const SEATS = ["n", "e", "s", "w"];

export function parseContractTargets(text) {
  const pieces = String(text).toUpperCase().split(",").map((item) => item.trim());
  if (!pieces.length || pieces.some((item) => !item)) {
    throw new Error("Enter contracts such as 4HN, 6HN with the declarer seat.");
  }
  return pieces.map((piece) => {
    const match = /^([1-7])(NT|[CDHS])\s*([NESW])$/.exec(piece);
    if (!match) throw new Error(`Contract ${piece} needs a level, suit and declarer (for example 4HN).`);
    return { level: Number(match[1]), strain: match[2], declarer: match[3].toLowerCase() };
  });
}

export function actorForAuction(dealer, calls) {
  const index = SEATS.indexOf(dealer);
  if (index < 0) throw new Error("Choose a valid dealer.");
  return SEATS[(index + calls.length) % 4];
}

export function buildContractAnalysisRequest({
  profileId, deal, dealer, vulnerability, calls, targetText, seedText = "", sampleCount = 10,
}) {
  const seat = actorForAuction(dealer, calls);
  if (!deal?.[seat]) throw new Error("The acting hand is missing.");
  const seed = seedText.trim();
  if (seed && (!/^-?\d+$/.test(seed) || !Number.isSafeInteger(Number(seed)))) {
    throw new Error("Seed must be a safe integer.");
  }
  const request = {
    profile: { id: profileId }, auction: calls.join(""), dealer, vulnerability,
    seat, hand: compactHand(deal[seat]), targets: parseContractTargets(targetText),
    sample_count: sampleCount,
  };
  if (seed) request.seed = Number(seed);
  return request;
}

export function buildRouteAnalysisRequest({
  profileId, deal, dealer, vulnerability, calls, routeText, seedText = "", sampleCount = 8,
}) {
  const seat = actorForAuction(dealer, calls);
  if (!deal?.[seat]) throw new Error("The acting hand is missing.");
  if (calls.join("") !== "1NP") throw new Error("Route experiments start at the first response to 1NT.");
  const firstCalls = String(routeText).toUpperCase().split(",").map((item) => item.trim());
  if (!firstCalls.length || firstCalls.length > 3 ||
      firstCalls.some((item) => !/^[1-7](?:NT|[CDHS])$/.test(item))) {
    throw new Error("Enter one to three first calls, such as 4C, 2D.");
  }
  const normalized = firstCalls.map((call) => call.replace("NT", "N"));
  if (new Set(normalized).size !== normalized.length) throw new Error("First calls must be distinct.");
  const seed = seedText.trim();
  if (seed && (!/^-?\d+$/.test(seed) || !Number.isSafeInteger(Number(seed)))) {
    throw new Error("Seed must be a safe integer.");
  }
  const request = {
    profile: { id: profileId }, auction: calls.join(""), dealer, vulnerability,
    seat, hand: compactHand(deal[seat]), first_calls: normalized, sample_count: sampleCount,
  };
  if (seed) request.seed = Number(seed);
  return request;
}
