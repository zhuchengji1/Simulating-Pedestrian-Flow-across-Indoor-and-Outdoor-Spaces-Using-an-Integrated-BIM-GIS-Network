# Synthetic NetLogo Example

This directory provides a minimal, fully fictional example of the passage-flow accounting used in the study. It is designed to show the data format and counting rule without disclosing the empirical pedestrian network, points of interest, trajectories, or flow records.

## Contents

- `netlogo/passage_flow_sample.nlogox3d`: standalone NetLogo 7 model with `setup`, `go`, and `export-results` controls.
- `netlogo/passage_flow_sample.nls`: model source code.
- `sample_data/synthetic_nodes.csv`: 27 fictional nodes arranged as a 3 by 3 by 3 cubic lattice.
- `sample_data/synthetic_segments.csv`: 54 fictional segments and their indoor/outdoor labels.
- `sample_data/synthetic_od_routes.csv`: five fictional OD routes represented by ordered node lists.

## Passage-flow rule

At each simulation tick, an agent advances by one link on its assigned route. Let its previous and current segment identifiers be \(A\) and \(B\). If \(A \ne B\), the passage flow of segment \(B\) increases by one:

\[
P_B \leftarrow P_B + 1.
\]

The model also retains agent-level global, indoor, and outdoor passage-flow totals. These are written to `synthetic_agent_passage_flow.csv`; segment-level counts are written to `synthetic_segment_passage_flow.csv` after clicking `export-results`.

## Run the example

1. Keep the `netlogo` and `sample_data` folders in their present relative locations.
2. Open `netlogo/passage_flow_sample.nlogox3d` in NetLogo 7.
3. Click `setup`, then click `go`.
4. After the model stops, click `export-results`.

All nodes, links, OD routes and generated outputs in this directory are synthetic. They do not reproduce, approximate, or disclose the study area, the empirical integrated pedestrian network, or the paper's reported flow results.

