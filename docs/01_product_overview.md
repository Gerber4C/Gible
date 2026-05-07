# Partner Product Overview

Platform Version: 0.0.7
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

Partner is a bridge bidding platform for people who want a bot partner to bid their agreements, explain its choices, and produce structured system notes from executable agreement files.

The long-term product has three layers.

## Layer 1: Partnership Profile Authoring And Execution

This is the current focus.

A user defines a Partnership Profile: a complete set of bridge bidding agreements for a partnership. A profile is assembled from portable Gadgets. A Gadget can describe something small, such as RKCB 1430, or something broad, such as the opening structure of a 2/1 profile. Programmatically there is no special backend object called a "basic system"; broad and narrow bridge methods are all Gadgets.

The platform can:

- Parse compact bridge hands and auctions.
- Load a Partnership Profile from source files.
- Replay the auction to recover public auction state.
- Generate candidate calls from all active Gadgets.
- Use profile-level Python Policy Functions to choose among eligible candidates.
- Return both public meaning and internal training origin.
- Generate Markdown system notes from the structured source.
- Run fixture tests and full-auction simulations.

## Layer 2: Deal And Auction Workspace

This is the next product layer.

Users should be able to:

- Deal random hands.
- Enter hands manually.
- Import deals from PBN or other formats.
- Step through auctions.
- Ask the selected Partnership Profile for bidding hints.
- Compare how different Partnership Profiles bid the same deal.
- Use the platform for partnership training.

## Layer 3: Tournament And Inter-User Platform

This is a later product layer built on the authoring and execution engine.

Possible features:

- User accounts and saved profiles.
- Sharing, importing, forking, and versioning Partnership Profiles.
- Pair practice and challenges.
- Teaching rooms.
- Tournament-style robot partnership events.
- Analytics over bidding choices, final contracts, and test pools.

## Why Partner Exists

Human system notes are often not executable. They can omit judgment, defaults, route choices, and inferred consequences. Partner tries to make a bridge bidding agreement precise enough that a bot, a human editor, and an AI agent can all inspect the same object.

The platform separates:

- Public meaning: what the opponents and partner can know from the call agreement.
- Internal origin: why the bot selected the call, including compared candidates, selected Policy Function, Private Route memory, and state records.

That separation matters. A call such as `2D` over `1N` may publicly mean "transfer to hearts", but privately the bidder may have chosen a weak signoff route, a game route, or a slam exploration route. Partner can remember that private route for the same seat later in the deal without exposing it as public meaning.

## AI-Assisted Authoring

The platform should later allow a user to describe a Gadget in natural bridge language. An AI agent or LLM can draft structured BSL source, compile it, generate system notes, and create tests. AI output must remain a draft until validated and approved.

This feature depends on strong documentation. A fresh AI agent should be able to read the docs and code, then recover the current architecture without relying on chat history.
