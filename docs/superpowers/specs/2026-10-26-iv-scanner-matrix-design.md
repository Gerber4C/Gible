# IV Scanner Matrix Display Design

## Goal

Merge IV Scanner findings that belong to the same North/South cell and show
their independent N/S pair and E/W sample results in a horizontally scrollable
matrix. Auction calls remain readable by inserting a line break after every
four calls.

## Scope and assumptions

- A finding's NS cell is identified by the existing scanner dimensions:
  `north_shape`, `south_shape`, `north_hcp`, and `south_hcp`.
- Existing category filtering and search behavior remains unchanged.
- The backend report schema remains unchanged; the browser derives display
  groups from the projected cases.
- Each projected case is one sampled N/S pair. Its `dds_boards` count is the
  number of E/W completions for that pair. The matrix therefore uses N/S pair
  cases as rows and E/W sample indexes as columns.
- The matrix displays the existing finding summary for each N/S pair and uses
  an empty placeholder when a pair has fewer E/W samples than the group
  maximum.

## Design

`IVScanner.js` will expose small pure helpers for grouping cases and chunking
auction calls. The filtered case list is transformed into groups keyed by the
four NS-cell dimensions. The list shows one button per group with the merged
category tags and pair count. Selecting a group renders the representative
hands/auction plus a matrix containing all group members.

The matrix is wrapped in a dedicated overflow container so wide E/W sample
sets do not widen the page. Rows are labeled with the sampled N/S pair id and
its contract/status; columns are labeled `EW 1`, `EW 2`, etc. Existing warning
rates and evidence remain below the matrix.

Auction calls are rendered as lines of at most four calls. The compact auction
string remains available in the heading for searchability, while the visual
call strip uses explicit rows.

## Validation

- Add browser-facing unit-level assertions for NS-cell grouping and four-call
  auction chunking where the existing frontend test setup permits.
- Extend the Playwright scanner smoke test to assert merged list entries,
  matrix overflow markup, and multiple auction rows.
- Run the existing frontend scanner browser test and backend IV scanner tests.
