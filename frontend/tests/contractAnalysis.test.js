import test from "node:test";
import assert from "node:assert/strict";
import { initialDeal } from "../src/lib/deal.js";
import { buildContractAnalysisRequest, buildRouteAnalysisRequest, parseContractTargets } from "../src/lib/contractAnalysis.js";

test("explicit target syntax retains each level, strain and declarer", () => {
  assert.deepEqual(parseContractTargets("4HN, 6H N, 3NT S"), [
    { level: 4, strain: "H", declarer: "n" },
    { level: 6, strain: "H", declarer: "n" },
    { level: 3, strain: "NT", declarer: "s" },
  ]);
  assert.throws(() => parseContractTargets("4H"), /declarer/);
});

test("analysis request contains only the acting hand and public auction", () => {
  const deal = initialDeal();
  const opts = { profileId: "daqiush_2over1", deal, dealer: "n", vulnerability: "none",
    calls: ["1N", "P"], targetText: "4HS", seedText: "17" };
  const before = buildContractAnalysisRequest(opts);
  const modified = structuredClone(deal);
  modified.e = { S: "secret", H: "", D: "", C: "" };
  modified.w = { S: "other", H: "", D: "", C: "" };
  modified.n = { S: "changed", H: "", D: "", C: "" };
  const after = buildContractAnalysisRequest({ ...opts, deal: modified });
  assert.deepEqual(after, before);
  assert.equal(before.seat, "s");
  assert.equal(before.auction, "1NP");
  assert.equal(before.hand.includes("secret"), false);
  assert.equal(JSON.stringify(before).includes("hands"), false);
});

test("route experiment uses one visible hand and declared first calls", () => {
  const deal = initialDeal();
  const opts = { profileId: "daqiush_2over1", deal, dealer: "n", vulnerability: "none",
    calls: ["1N", "P"], routeText: "4C, 2D", seedText: "17" };
  const before = buildRouteAnalysisRequest(opts);
  assert.deepEqual(before.first_calls, ["4C", "2D"]);
  const modified = structuredClone(deal);
  modified.n = { S: "hidden", H: "", D: "", C: "" };
  modified.e = { S: "other", H: "", D: "", C: "" };
  modified.w = { S: "other", H: "", D: "", C: "" };
  assert.deepEqual(buildRouteAnalysisRequest({ ...opts, deal: modified }), before);
  assert.throws(() => buildRouteAnalysisRequest({ ...opts, routeText: "4C, 4C" }), /distinct/);
});
