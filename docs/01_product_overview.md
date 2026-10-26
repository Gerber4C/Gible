# Gible Product Overview

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

Gible is a bridge platform for people who want a robot partner to use their own
bidding agreements, practice against partnerships using other agreements, and
compare alternative agreements through repeatable experiments. Card play after
the auction is an optional long-term capability.

The owner's goals are recorded in [Product Vision](12_product_vision.md), including
optional cloud storage and the still-undecided local-only confidentiality promise.
The development sequence is maintained in [Roadmap](08_roadmap_todo.md).

The product is organized into the following capability areas. Future capabilities
are distinguished from the current local prototype.

## Layer 1: Partnership Profile Authoring And Execution

This is the existing foundation.

A user defines a Partnership Profile: a complete set of bridge bidding agreements for a partnership. A profile is assembled from portable Gadgets. A Gadget can describe something small, such as RKCB 1430, or something broad, such as the opening structure of a 2/1 profile. Programmatically there is no special backend object called a "basic system"; broad and narrow bridge methods are all Gadgets.

The platform can:

- Parse compact bridge hands and auctions.
- Load a Partnership Profile from source files.
- Replay the auction to recover public auction state.
- Generate candidate calls from all active Gadgets.
- Apply mandatory Axioms, then use profile-level Python Policy Functions to choose among eligible candidates.
- Return both public meaning and internal training origin.
- Generate Markdown system notes from the structured source.
- Run fixture tests and full-auction simulations.
- Serve a local browser workspace for profile editing, hand display, auction display, and bidding experiments.

## Layer 2: Deal Workspace, Simulation, And Agreement Comparison

The local workspace is partly implemented. The next engine milestone adds
information-safe sampling and double-dummy evaluation at defined late-auction
decision points. The current full-auction runner is not that statistical simulator.

Users should be able to:

- Deal random hands.
- Enter hands manually.
- Import deals from PBN or other formats.
- Step through auctions.
- Ask the selected Partnership Profile for bidding hints.
- Compare how different Partnership Profiles bid the same deal.
- Use the platform for partnership training.
- Compare alternative call meanings together with their continuations on the same deals.
- Inspect expected-score estimates, uncertainty, and missing-continuation diagnostics.

Later research will calibrate double-dummy predictions against imperfect-information
card play. That research is planned, not a current product capability.

The current browser prototype starts this layer locally. It is not a distributed product: it reads and writes files in the local repository through a local backend server.

## Layer 3: Mixed-Profile Practice And Optional Card Play

This is a later product layer built on the authoring and execution engine.

The core goal is practice with humans and robots at the same table. For example,
North and East can be human, South and West robots, with a separate Partnership
Profile for each pair. Bidding-only practice must remain possible. Profile source
and private decision traces are distinct from the explanations shared at the table.

Planned capabilities:

- User accounts and saved profiles.
- Sharing, importing, forking, and versioning Partnership Profiles.
- Pair practice and challenges.
- Teaching rooms.
- Tournament-style robot partnership events.
- Analytics over bidding choices, final contracts, and test pools.

## Why Gible Exists

Human system notes are often not executable. They can omit judgment, defaults, route choices, and inferred consequences. Gible tries to make a bridge bidding agreement precise enough that a bot, a human editor, and an AI agent can all inspect the same object.

The platform separates:

- Public meaning: what the opponents and partner can know from the call agreement.
- Internal origin: why the bot selected the call, including compared candidates, selected Policy Function, Private Route memory, and state records.

That separation matters. A call such as `2D` over `1N` may publicly mean "transfer to hearts", but privately the bidder may have chosen a weak signoff route, a game route, or a slam exploration route. Gible can remember that private route for the same seat later in the deal without exposing it as public meaning.

## AI-Assisted Authoring

An explicit long-term goal is to translate natural-language bidding-system notes
into Gible's executable BSL agreements using an LLM. Support locally deployed
models as well as optional remote services. Local translation should keep the
notes and related processing on the user's device, with no silent remote fallback.

The workflow should expose ambiguous or missing agreements, generate reviewable
BSL changes and system notes, and validate representative test auctions before
the user applies a draft. Generated text must not invent agreements merely to
complete a branch. This is a planned capability, not part of the current prototype
or a prerequisite for the first usable website release.

This feature depends on strong documentation. A fresh AI agent should be able to read the docs and code, then recover the current architecture without relying on chat history.
