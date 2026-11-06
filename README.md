# Simulating Pedestrian Flow across Indoor and Outdoor Spaces Using an Integrated BIM-GIS Network

This repository provides the public code and published summary results for the study **Simulating Pedestrian Flow across Indoor and Outdoor Spaces Using an Integrated BIM-GIS Network**. The study connects three-dimensional indoor circulation with two-dimensional outdoor paths, represents movement at segment and stroke scales, and records passage flow under alternative movement-demand mechanisms.

The public release is intentionally minimal. It documents the core workflow without distributing restricted BIM/IFC building information, the derived integrated network, activity sequences, or raw passage-flow records.

## What this repository contains

| File | Purpose |
| --- | --- |
| `code/01_network_construction/merge_segments_into_strokes_self_best_fit_45_degrees.py` | Merges adjacent segments into strokes using a 45-degree self-best-fit rule. |
| `code/01_network_construction/prepare_integrated_pedestrian_network_for_netlogo.py` | Converts a prepared pedestrian network into the input form required by NetLogo. |
| `code/02_simulation/run_random_passage_flow_simulation_20000_ticks.py` | Runs the public Random mechanism for 20,000 ticks and validates the exported passage-flow totals. |
| `code/02_simulation/models/random_movement_passage_flow_20000_ticks.nlogox3d` | NetLogo 3D model for the Random movement mechanism. |
| `examples/` | A standalone synthetic NetLogo example and fictional input data demonstrating passage-flow counting. |
| `results/published_tables/` | Machine-readable versions of Tables 4-8 in the manuscript. |
| `docs/DATA_AVAILABILITY.md` | Data availability statement. |
| `docs/INPUT_REQUIREMENTS.md` | Requirements for the restricted input network. |
| `docs/TABLE_ALIGNMENT.md` | Correspondence between repository CSV files and manuscript tables. |

## Passage flow

At each simulation tick, an agent moves along its selected path. When the segment occupied by agent \(a\) changes from segment \(A\) at tick \(t-1\) to segment \(B\) at tick \(t\), the passage flow of segment \(B\) increases by one:

\[
PF_B = \sum_{a} \sum_{t=1}^{T} \mathbb{I}\left[s_a(t-1)=A,\;s_a(t)=B,\;A\ne B\right].
\]

Accordingly, passage flow is the cumulative number of agent entries into each segment. Stroke-level flow is obtained by summing the passage flow of the segments belonging to each stroke, with each segment counted once.

## Repository scope

The public release contains only the **Random** model. The full study also implements Purposive and Simulated mechanisms, but their models and activity-sequence inputs are not included here. The public runner has therefore been configured to execute only the Random model.

The published CSV tables are summary outputs. They contain no coordinates, original network identifiers, POI records, agent trajectories, raw structure metrics, or raw flow data.

## Requirements

- Python 3.10 or later
- Packages listed in `requirements.txt`
- NetLogo 7.0.4
- Java runtime distributed with NetLogo
- Environment variable `NETLOGO_HOME` pointing to the NetLogo installation directory

## Running the public Random workflow

The Random model requires a restricted network input named `SZU_network_0728_T_E_link_slim.csv`. Once approved access to this input has been obtained, place it in the location described in `docs/INPUT_REQUIREMENTS.md`, set `NETLOGO_HOME`, and run:

```powershell
$env:NETLOGO_HOME = "C:\\Path\\To\\NetLogo 7.0.4"
python code/02_simulation/run_random_passage_flow_simulation_20000_ticks.py
```

The script runs the Random mechanism for 20,000 ticks and checks that the total agent passage flow equals the total segment passage flow.

## Published summary results

The `results/published_tables/` directory reproduces the values displayed in the manuscript:

| File | Manuscript table |
| --- | --- |
| `Table_04_Pure_Power_Law_Fits_for_Network_Structural_Metrics.csv` | Table 4. Pure-power-law exponent estimates and goodness of fit for structural metrics. |
| `Table_05_Passage_Flow_and_Network_Structure_Correlations.csv` | Table 5. Pearson correlations between passage flow and structural metrics. |
| `Table_06_Passage_Flow_Concentration_by_Spatial_Subset_and_Analytical_Scale.csv` | Table 6. Concentration of passage flow by spatial subset and analytical scale. |
| `Table_07_Likelihood_Ratio_Comparison_of_Power_Law_and_Power_Law_with_Exponential_Cutoff.csv` | Table 7. Likelihood-ratio comparisons of a pure power law and a power law with exponential cutoff. |
| `Table_08_Power_Law_with_Exponential_Cutoff_Parameter_Estimates_and_Goodness_of_Fit.csv` | Table 8. Power-law-with-cutoff parameter estimates and goodness-of-fit results. |

`Hybrid`, `Indoor`, and `Outdoor` identify the network subset. Segment and stroke identify the analytical scale. In Table 7, LR is defined as the log likelihood of PL with cutoff minus that of the pure power law.

## Data availability

Outdoor road and path data are available from OpenStreetMap. Point-of-interest data were obtained through the Amap API, subject to its access conditions. Population inputs for the simulations were estimated from annual admissions announcements and staff information publicly available on the Shenzhen University website.

The BIM/IFC building models and the integrated pedestrian network derived from them cannot be made publicly available because they contain institutionally restricted building information. Simulated passage-flow data supporting the analyses are available from the corresponding author upon reasonable request.

## Citation

Please cite the associated Simcampus3D manuscript or its final published version. A complete citation and DOI will be added after publication.

## License and attribution

See `LICENSE_NOTICE.md` for code-use notes and OpenStreetMap attribution requirements.

