# Frontend Architecture

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document is the engineering guide for the local browser workspace.

The frontend is a browser-based workspace for editing Partnership Profiles and trying bridge auctions against the local backend. It is currently a no-build React app served by a small Node server.

## Runtime Position

The local frontend serves files on:

```text
http://127.0.0.1:5173
```

The local backend serves API endpoints on:

```text
http://127.0.0.1:8765
```

The frontend never writes project files directly. It calls the backend file API, and the backend restricts reads and writes to the selected Partnership Profile directory.

## Startup

From the repository root, the normal startup command is:

```bat
run_local.cmd
```

That command starts both local servers in one CMD window. Keep the window open while using the browser workspace.

Manual startup is also available:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe backend\server.py
```

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe frontend\server.mjs
```

## Frontend File Layout

```text
frontend/
  index.html
  package.json
  server.mjs
  src/
    App.js
    main.js
    api/
      partnerApi.js
    components/
      BridgeTools.js
      CodeEditor.js
      FileTree.js
      StructuredEditor.js
    lib/
      bridge.js
      bsl.js
      files.js
    styles/
      app.css
    ui/
      react.js
```

## Module Responsibilities

`frontend/server.mjs`

- Serves the static frontend.
- Uses port `5173`.
- Does not contain product logic.

`frontend/src/main.js`

- Browser entrypoint.
- Mounts the React app into `index.html`.

`frontend/src/App.js`

- Owns top-level UI state:
  - selected Partnership Profile,
  - profile file list,
  - selected file path,
  - original file content,
  - current edited content,
  - dirty/save state,
  - editor/table workspace mode,
  - North/South hand inputs,
  - dealer and vulnerability controls,
  - auction result,
  - visible auction step count,
  - collapsed/expanded sidebar state.
- Coordinates API calls.
- Handles save, discard, reload, create, delete, auction stepping, and full-auction reveal.

`frontend/src/api/partnerApi.js`

- Defines the frontend API client.
- Uses `http://127.0.0.1:8765` as the backend base URL.
- Wraps fetch errors in user-readable messages.

`frontend/src/components/FileTree.js`

- Displays profile files as logical groups:
  - Profile,
  - Gadgets,
  - Policies,
  - Tests,
  - Documents.
- Supports creating and deleting files.
- Protects unsaved edits through confirmation handled by `App.js`.
- Keeps the "Workspace Files" title outside the scrolling file-list region so navigation labels do not overlap with file rows.

`frontend/src/components/StructuredEditor.js`

- Provides guide-mode editing for BSL and Policy Function source.
- Shows file metadata, Call Specifications, Frames, Private Routes, Named Evaluators, and Policy Functions.
- Exposes focused editors for source blocks when a GUI control cannot fully represent the source.
- Creates new Call Specifications in current Python-BSL style with `self.call(...)`, field assignments, and normal Python `applies` functions.

`frontend/src/components/CodeEditor.js`

- Provides code-mode editing.
- Shows line numbers.
- Highlights Python-like BSL, Policy Function files, and Markdown.
- Displays local syntax diagnostics from `lintText()`.
- Owns its own scrollable textarea region; disabling whole-page scrolling must never prevent code scrolling.

`frontend/src/components/BridgeTools.js`

- Provides the table workspace.
- Displays North and South hands as large overlapping card faces with the hand metadata and hand-string editor to the side of the cards.
- Displays the auction in a bridge-table layout with North/East/South/West columns.
- Builds a full partnership auction through the backend and reveals calls through a player workflow.
- Shows a hover/focus tooltip for every displayed call, using backend provenance from the auction record.
- Marks alertable calls with a visible alert symbol beside the call.
- Keeps `Dealer: ...` and `Vul: ...` controls in the compact auction player strip.
- Shows vulnerability through the relevant N/E/S/W auction headers, vulnerable seat panels, and restrained column tinting, not through the whole table background.

`frontend/src/lib/bsl.js`

- Parses source text for frontend visualization.
- Extracts class-authored BSL objects:
  - `class ... (Profile)`
  - `class ... (Gadget)`
  - `self.call(...)`
  - `self.frame(...)`
  - `self.route(...)`
  - `self.evaluator(...)`
  - `self.relay(...)`
- Extracts Policy Function definitions and the `policy_functions` registration list.
- Provides source-block replacement helpers used by structured editing.
- Provides lightweight bracket/string diagnostics for the code editor.

`frontend/src/lib/bridge.js`

- Formats bridge hands, suits, auction calls, and public meaning snippets for display.

`frontend/src/lib/files.js`

- Builds the logical file tree.
- Generates default source for new Gadget, Policy, Test, and Document files.
- Classifies file paths for editor behavior.

`frontend/src/styles/app.css`

- Defines the visual system for sidebar navigation, editor panels, code editor, structured cards, file tree, and table workspace.

## Workspace Modes

The UI has two main workspace modes.

### System Editor

The System Editor is for Partnership Profile source.

It has:

- a profile selector,
- grouped file tree,
- guide/code mode switch,
- save, discard, and reload controls,
- dirty-state indicator,
- structured editing for BSL and Policy Function files,
- source editing for full control.

Guide mode should expose the structure of the source without hiding important information. If a field is too flexible for safe GUI editing, guide mode should show a focused code block for that part.

Code mode is the escape hatch and source of full fidelity.

### Table

The Table workspace is for bridge interaction.

It has:

- North hand editor,
- South hand editor,
- compact dealer and vulnerability controls in the player strip,
- recorder-style auction controls for first, back, next/play, and full auction,
- bridge-style auction table,
- hover/focus call explanations showing meaning, origin, selected policy, compared candidates, and diagnostics when available.

The table should feel like a bridge workspace, not a debug console. Single-call "use this seat" controls do not belong on this screen; the visible workflow is auction playback and its explanation trail. Avoid separate reset/refresh controls unless they represent genuinely different user intentions. Dealer, vulnerability, and hand changes immediately clear stale visible calls, show a centered server-waiting state, and refresh an already-loaded auction after a short debounce.

The center auction area should dominate the table view. The left sidebar is retractable so the bidding table can use more horizontal space during auction playback. Do not duplicate the auction as both a table and a linear string.

## Backend API Used By Frontend

The frontend currently uses:

```text
GET    /api/profiles
GET    /api/profiles/<profile_id>/files
GET    /api/profiles/<profile_id>/file?path=<path>
POST   /api/profiles/<profile_id>/file
DELETE /api/profiles/<profile_id>/file?path=<path>
POST   /api/bid
POST   /api/simulate
```

API request construction lives in `partnerApi.js`. UI components should call exported API helpers, not `fetch()` directly.

## Editing Model

The frontend edits source text.

Structured editing is source-aware rather than database-backed:

1. Parse the current text into recognizable object blocks.
2. Show the object summary and editable fields.
3. Replace only the relevant source block or argument.
4. Keep unsaved edits in React state.
5. Save the complete file content through the backend.

This model preserves custom Python functions and unusual source layout better than a rigid form-only editor.

## Diagnostics

Current frontend diagnostics are local and lightweight:

- bracket matching,
- string literal closure,
- Markdown/Python-like highlighting,
- first diagnostic summary in the status bar below the code editor.

Backend compile diagnostics should later be exposed through an API endpoint so the editor can report real BSL and Policy Function loader errors before save or test runs.

## UX Rules

Frontend work should follow these rules:

1. Always provide Save and Discard for editable files.
2. Warn before losing unsaved edits.
3. Keep source fidelity. The GUI may simplify editing, but it must not silently delete source fields it cannot understand.
4. Keep bridge table output centered in the table workspace.
5. Keep profile file navigation grouped by meaning, not raw path length.
6. Use code view for full-fidelity editing.
7. Use guide view for structured inspection and safer common edits.
8. Avoid dumping debug arrays into user-facing bridge views.
9. Keep player buttons icon-like and compact; use titles/ARIA labels for explanation instead of large visible text.
10. Keep frontend-only parsing conservative. If uncertain, preserve source and show it as a code block.
11. Do not allow the whole page to scroll. Use contained scroll regions for the file tree, structured editor body, code editor, and auction table only.
12. Use bridge display colors for non-input calls and suits: clubs green, diamonds orange, hearts red, spades dark purple, double red, and redouble purple.
13. In the table workspace, show vulnerability through full auction header backgrounds, matching hand metadata backgrounds, vulnerable seat titles, and the compact vulnerability selector. Do not tint bid cells themselves just because that seat is vulnerable. Non-vulnerable state must remain visibly green, not nearly white; vulnerable red should stay clearly red while remaining lighter and less warning-like.
14. Hand displays should look like bridge-platform card faces, not plain debug strings; card ranks and suit symbols should be large enough to read at normal desktop zoom, including the small corner suit symbols. Suit cards may use a very subtle suit-tinted background, but the card must remain mostly white and each card must have a visible border. Keep the hand-string input compact but readable, and visually secondary to the cards. Metadata belongs beside the cards, not in a tall header above them.
15. Empty auction cells before the dealer or after the last visible call should preserve column alignment but should not draw placeholder bid boxes.
16. Auction headers should use full seat names, not single-letter abbreviations, and should not look like bid cards.
17. Alertable calls must display a visible alert marker beside the call text.
18. The auction surface should be restrained and low saturation. Prefer a light blue or aquamarine surface with light-green non-vulnerable headers. Avoid a full dark-green center panel unless the design explicitly calls for a table-felt theme.
19. User-facing table text should use "auction" or "auction playback"; reserve "simulation" for future deal/hand simulation features.
20. Call explanation tooltips should open to the lower-right of the cursor when possible so they do not cover previous auction calls.
21. Hand-area vulnerability and non-vulnerability outlines should be visibly thick enough to read as state, while avoiding a full-panel red fill.

## Verification

Frontend syntax checks:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check frontend\src\App.js
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check frontend\src\components\BridgeTools.js
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check frontend\src\components\StructuredEditor.js
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check frontend\src\lib\bsl.js
```

Manual browser verification:

1. Start `run_local.cmd`.
2. Open `http://127.0.0.1:5173`.
3. Confirm the profile selector loads `meow_2over1`.
4. Open a Gadget file in guide mode.
5. Switch to code mode and confirm line numbers, highlighting, and diagnostics display.
6. Make a small unsaved edit and confirm Save, Discard, and Reload behavior.
7. Open the Table workspace.
8. Press First, Start, Next, Back, and All.
9. Confirm the auction displays in N/E/S/W columns, bid cards use suit symbols and colors, and hovering a call shows its logic tooltip.
10. Change vulnerability and confirm the vulnerable auction headers, columns, and seats change color without turning the whole table into a colored panel.
11. Collapse and expand the sidebar in table mode and confirm the center auction area grows.
12. Confirm the browser viewport does not get a whole-page scrollbar; only the file tree, editor body, code area, and auction body should scroll.

## Roadmap Boundary

Future frontend work belongs in `docs/08_roadmap_todo.md`. This document describes the current frontend architecture and engineering rules.
