# Anonymized Random Passage Flow

`anonymized_random_segment_passage_flow.csv` contains the segment-level passage-flow values for the Random movement mechanism used in the study.

The file includes only two fields:

- `sequence_id`: a newly assigned, non-spatial row identifier.
- `random_passage_flow`: the cumulative passage-flow value for that anonymized record.

The file does not contain original segment identifiers, coordinates, indoor/outdoor labels, stroke membership, POI information, network-structure metrics, trajectories, BIM/IFC attributes, or any mapping back to the integrated pedestrian network. It supports transparent inspection of the univariate Random passage-flow values, but it cannot reproduce spatial analyses or reconstruct the study network.

Passage-flow data for the Purposive and Simulated mechanisms remain available from the corresponding author upon reasonable request.

