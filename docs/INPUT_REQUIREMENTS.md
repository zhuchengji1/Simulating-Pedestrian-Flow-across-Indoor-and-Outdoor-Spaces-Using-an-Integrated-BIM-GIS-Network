# Input requirements

The public NetLogo model reads a file named `SZU_network_0728_T_E_link_slim.csv` from the model directory. The study input is restricted because it is derived in part from BIM/IFC building information. A requester who has obtained approved access should place that file in the model directory before running `run_random_passage_flow_simulation_20000_ticks.py`.

The required network file must contain at least the fields and column order expected by the supplied NetLogo model. The file must preserve the segment identifiers, endpoint identifiers, endpoint coordinates, area classification, network-structure metrics, and POI-access fields used by the original workflow. The repository deliberately does not include example rows because even a subset of the study network could reveal restricted building layout information.

The public runner is Random-only. It does not require the private activity-sequence file used by the Simulated mechanism.
