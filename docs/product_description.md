# Product Description

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

## One-Sentence Summary

Partner is a bridge bidding platform where players define their partnership agreements, turn those agreements into an explainable bot partner, and test them through practice, system notes, and future human-plus-custom-bot competition.

## What The Product Is

Partner is built around one idea: bridge players should be able to bring their own agreements.

Instead of playing with a fixed robot that guesses what you mean, a user defines a Convention Set. The platform executes that Convention Set through a bot partner that can explain both the public meaning of its calls and the internal origin of its choices.

Partner has two layers.

The first layer is **Convention Set authoring and execution**. It supports editing Conventions, sharing files, importing and exporting agreement definitions, generating formal human-readable system notes, testing hands and deals, and asking the engine what to bid.

The second layer is **tournament and inter-user play**. It will use the first layer to support human-plus-custom-bot competition, challenges, system sharing, comparison, and analytics.

The first layer must be useful by itself. It is a system-design, training, and partnership-agreement tool even before tournament features exist.

## Product Modules

### Convention Authoring And Execution

This module should support:

- Editing complete Convention Sets.
- Editing portable Conventions.
- Sharing Convention Set and Convention files.
- Generating formal system notes from structured files.
- Running bidding practice on a hand, auction, and environment.
- Simulating a full partnership auction from supplied hands for training and benchmark tests.
- Using shared test-case pools to compare auction results across different Convention Sets.
- Entering deals manually, dealing random hands, and importing deal formats such as PBN.
- Explaining selected calls with public meaning and internal origin.
- Drafting structured files from natural bridge descriptions with LLM assistance, followed by validation and user approval.

### Tournament And Inter-User Platform

This module should support:

- Human-plus-custom-bot versus human-plus-custom-bot play.
- User accounts and saved Convention Sets.
- Sharing, copying, and forking agreements.
- Inter-user challenges.
- Tournament-style comparison on shared boards.
- Analytics about agreement performance and undefined auctions.

The tournament layer should depend on the Convention engine. It should not own bidding logic.

## The Problem

Bridge players often care deeply about partnership agreements. A common frustration with robot bridge is not simply that the robot is imperfect, but that it does not play **your** agreements.

Examples:

- You play four-way transfers, but the robot treats a bid as natural.
- You play a double as penalty, but the robot pulls it.
- You play an artificial raise, but the robot explains it vaguely.
- You want to compare Bergen raises against another raise structure.
- You and a partner have detailed agreements, but live practice is hard to schedule.

Partner makes agreements explicit, testable, shareable, and explainable.

## Core Value Proposition

### Customizable Partnership Agreements

Users can define what their bot partner plays.

Casual users should eventually choose from presets and guided controls. Advanced users should be able to inspect or edit the formal objects directly.

Conventions should be modular. A player should be able to choose transfers without Puppet Stayman, Puppet Stayman without one specific transfer structure, Bergen without Drury, or slam tools such as RKCB, Gerber, Kickback, Minorwood, Exclusion keycard, and control bidding across many auctions instead of only inside one notrump sequence.

Example casual choices:

- 2/1 game forcing.
- Four-way transfers.
- Bergen raises.
- Inverted minors.
- Puppet Stayman.
- Splinters.
- Competitive doubles.

Example advanced questions:

- What does `X` mean after `1H 1S 4H`?
- When is `4N` quantitative, keycard, natural, or competitive?
- What continuations apply after an artificial relay?
- What counts as a superaccept?
- What happens after a transfer is doubled?

### Strict Agreement Following

The bot should follow the selected Convention Set. It should not silently replace a user’s agreement with generic bridge culture.

If the agreement says partner must pass a penalty double unless an explicit escape applies, the bot should respect that.

### Explainable Bidding

Every selected bid should be traceable.

The platform should be able to answer:

- Which Convention produced this bid?
- Which Call Specification applied?
- What is the public meaning?
- Which candidate calls or plans were compared?
- Which Call Selection Policy made the judgment?
- Which Protocol Frames or Bidding Plans were active?
- Was the call alertable?

Public meaning and internal origin are separate. Public meaning is disclosure-oriented. Internal origin is for training, debugging, and system design.

### Generated System Notes

Partner should generate human-readable system notes from structured Convention files.

The generated notes should be formal enough that a bridge player, software engineer, or LLM can reliably interpret them. The source of truth remains the structured objects, while `description` and `system_notes` fields improve readability.

Target flow:

```text
Convention Set and Convention files -> formal system notes
```

Future reverse flow:

```text
human notes -> LLM-assisted draft -> BSL or IR -> validation -> user approval
```

LLM output should never become active silently.

### Shareable Agreements

Users should eventually export, import, fork, and share Convention Sets and Conventions.

Possible workflows:

- A teacher publishes a beginner 2/1 Convention Set.
- A pair forks that set and adds their competitive agreements.
- A club shares recommended agreements.
- A professional player licenses a premium Convention Set.
- A user exports a four-way transfer Convention and imports it into another Convention Set.

### Competitive Testing

Users should be able to test agreements on the same boards.

This supports questions like:

- Does my notrump structure perform better with four-way transfers?
- Is this competitive double structure robust?
- Does this Convention create too many undefined continuations?
- Do my agreements produce better auctions than a standard preset?

The platform should eventually include curated and user-created test-case pools. A user could run the same hands through several Convention Sets, compare the resulting auctions, inspect explanation traces, and compare contract choices against references such as expert annotations or double-dummy results where those baselines are meaningful.

## Target Users

### Casual And Intermediate Bridge Players

These users should not need to write code.

They should be able to use:

- Presets.
- Checkboxes.
- Dropdowns.
- Convention-card-like controls.
- Guided questions.

### Advanced Players

Advanced players want control over exact auctions, custom meanings, forcing obligations, superaccept logic, and specialized judgment.

### Teachers And Coaches

Teachers can use Partner to demonstrate agreements, compare candidate calls, assign practice auctions, and detect missing continuations.

### System Designers

System designers can build Conventions, test them, generate notes, and publish Convention Sets.

### Potential Investors And Partners

Partner can become a training platform, a competitive bridge product, a system-sharing marketplace, and a premium advanced-agreement builder.

## What Is A Convention?

A Convention is a portable bridge agreement module that can be included in a Convention Set.

Examples:

- Four-way transfers.
- Bergen raises.
- Inverted minors.
- Puppet Stayman.
- Splinters.
- Competitive doubles.
- A foundational 2/1 opening structure.

A Convention can include:

- Call Specifications.
- Public meanings.
- Continuations.
- Call Selection Policies.
- Bidding Plans.
- Protocol Frames.
- Semantic effects.
- Alertability data.
- Notes text for generated system notes.

## Product Principles

### Agreement-Driven, Not Opaque

Evaluation is allowed, but it should be defined by the selected Convention Set or an approved evaluator. If a Convention uses a concept such as "good suit," it should eventually be backed by a formal metric or predicate.

### Semantic State Is Derived

The client submits visible context:

- Convention Set.
- Seat.
- Auction.
- Hand.
- Dealer.
- Vulnerability.
- Scoring.

The engine reconstructs semantic state by replaying the auction through active Conventions.

### Modular UI, Parallel Logic

The user interface may show Conventions as modules. The engine searches active Conventions together.

Correct mental model:

```text
Auction + Hand + Environment + Active Conventions
  -> applicable Call Specifications
  -> active Protocol Frames
  -> candidate calls and Bidding Plans
  -> Call Selection Policy
  -> selected call
```

### Expert-System Coverage

Partner should eventually handle mainstream and highly artificial structures:

- Washington Standard and expert 2/1.
- Strong diamond and strong club families.
- Precision and Polish Club.
- KK/Symmetric Relay.
- Common competitive and slam agreements.

The goal is not to hard-code these systems. The goal is to provide formal building blocks that can represent them.

## Example Scenario

Alice wants to test her notrump structure.

She chooses:

- 2/1 foundation.
- 1N range 15-17.
- Four-way transfers.
- Superaccepts enabled.

Auction:

```text
1N P 2D P
```

Alice’s bot holds:

```text
S AQ74 / H KJ83 / D A62 / C Q5
```

The platform recommends:

```text
3H
```

Alice can inspect:

- Public meaning: superaccepting the heart transfer.
- Origin: Four-Way Jacoby Transfer Convention, relevant Call Specification.
- Compared candidates: `3H` and `2H`.
- Structured reasons: pending transfer, 16 HCP, four-card heart support.

## Product Ideas

Possible tiers:

### Free

- Preset Convention Sets.
- Simple Convention toggles.
- Casual practice.
- Limited sharing.

### Paid

- Advanced builder.
- Custom Conventions.
- Analytics.
- More sharing features.
- Tournament access.

### Pro

- Full advanced authoring.
- Custom evaluator hooks.
- Versioned repositories.
- Advanced competitive agreements.
- High-level tournament modes.

These are ideas, not final pricing decisions.

## Current Prototype Snapshot

The current checkpoint is a Python backend prototype with canonical bidding notation, compact hand strings, directory-based Conventions, a Meow 2/1 benchmark Convention Set, modular notrump methods, minor-opening continuations, major-raise methods, reusable slam Conventions, seat/vulnerability-sensitive preempts, Gambling 3N, auction replay, semantic trace and typed auction-state output, candidate comparison, separate public/internal explanation layers, fixture-driven tests, full-auction simulations, and generated Markdown system notes.

Open implementation work and future product ideas are tracked in `docs/todo.md`.
