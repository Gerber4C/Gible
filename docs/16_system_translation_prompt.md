# Translating bridge agreements with a language model

The model should translate a system file into **candidate Gible rules**, not
decide what an unstated agreement ought to mean. A bridge expert can infer
context from shorthand such as `oM`, `+1`, "cue", or `1NT–2C–2D–4C`; a model
needs that context supplied explicitly and must be allowed to return unknowns.

## Knowledge pack supplied with every translation job

1. Auction grammar: seats, turn order, legal bid ranking, Pass/double/redouble,
   natural versus artificial calls, and how declarership is determined.
2. Terminology: a versioned dictionary for abbreviations and profile-specific
   words, including `M/m`, `oM/om`, "hard/soft values", "control", "forcing",
   "game forcing", "signoff", and "agreed trump". Start from
   [the current glossary](14_bidding_terminology.md).
3. State semantics: shared [axioms](11_axioms.md), public versus private facts,
   partnership side, and unset/provisional/agreed trump. An agreed suit is a
   reference for interpreting later calls, not necessarily the final contract.
4. Relevant profile passages and their exceptions, with stable source IDs and
   line spans. Send only the section needed for the current auction family,
   plus cross-referenced definitions. Do not assume a full file fits usefully in
   one model context.
5. Owner-labeled positive and negative auction/hand examples. A hand example
   checks *when to choose* a call; an auction example checks *what it means*.

## Extraction prompt template

```text
You translate a human bridge bidding agreement into candidate Gible rules.
Use only the supplied knowledge pack and passage. Do not add standard bridge
conventions merely because a name resembles one. Distinguish:
  (a) public meaning and state change of a call already made;
  (b) private hand condition for choosing it;
  (c) policy priority among multiple valid calls.

For every rule, return: source_span, auction_pattern, actor/partnership,
call, public_meaning, private_applicability, public_hand_promises,
state_transition, forcing_obligation, priority_or_exception,
positive_examples, negative_examples, unresolved_questions.

Preserve explicit exceptions before general rules. If two meanings for the
same call overlap, output a conflict with both source spans. If a needed
threshold, role, answer mapping, or continuation is absent, put it in
unresolved_questions and do not invent a value. If a Pass or bid would be
illegal in its auction, flag it instead of emitting a rule.

Return structured JSON only. Every nonempty field must cite a supplied
source span or an explicit glossary/axiom item.
```

## Validation prompt and deterministic checks

Feed the extracted rules and held-out examples to a second pass: ask it to
identify which exact condition matches each example and where multiple rules
claim the same call. Then run code checks for auction legality, unreachable
branches, incompatible public meanings, forcing/Pass contradictions, and
sampled-hand consistency. The model's explanation is diagnostic; the rule is
accepted only after deterministic checks and owner review.

This separation supports local models: private system documents can stay on
the user's machine, while the same structured validation runs regardless of
whether translation used a local or cloud model. The open decision is which
model to bundle or permit, not the meaning of the source agreements.
