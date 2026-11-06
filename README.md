# Simulating Pedestrian Flow across Indoor and Outdoor Spaces Using an Integrated BIM-GIS Network

This repository provides public synthetic code, anonymized Random passage-flow values, and published summary results for the study **Simulating Pedestrian Flow across Indoor and Outdoor Spaces Using an Integrated BIM-GIS Network**. The study connects three-dimensional indoor circulation with two-dimensional outdoor paths, represents movement at segment and stroke scales, and records passage flow under alternative movement-demand mechanisms.

The public release is intentionally minimal. It documents the core workflow without distributing restricted BIM/IFC building information, the derived integrated network, activity sequences, or raw passage-flow records.

## What this repository contains

| File | Purpose |
| --- | --- |
| `code/01_network_construction/merge_segments_into_strokes_self_best_fit_45_degrees.py` | Merges adjacent segments into strokes using a 45-degree self-best-fit rule. |
| `code/01_network_construction/prepare_integrated_pedestrian_network_for_netlogo.py` | Converts a prepared pedestrian network into the input form required by NetLogo. |
| `examples/` | A standalone synthetic NetLogo example and fictional input data demonstrating passage-flow counting. |
| `data/anonymized_random_segment_passage_flow.csv` | Anonymized segment-level passage-flow values for the Random mechanism. |
| `data/README.md` | Scope, fields, and restrictions for the anonymized Random flow file. |
| `results/published_tables/` | Machine-readable versions of Tables 4-8 in the manuscript. |
| `docs/DATA_AVAILABILITY.md` | Data availability statement. |
| `docs/TABLE_ALIGNMENT.md` | Correspondence between repository CSV files and manuscript tables. |

## Passage flow

At each simulation tick, an agent moves along its selected path. When the segment occupied by agent \(a\) changes from segment \(A\) at tick \(t-1\) to segment \(B\) at tick \(t\), the passage flow of segment \(B\) increases by one:

\[
PF_B = \sum_{a} \sum_{t=1}^{T} \mathbb{I}\left[s_a(t-1)=A,\;s_a(t)=B,\;A\ne B\right].
\]

Accordingly, passage flow is the cumulative number of agent entries into each segment. Stroke-level flow is obtained by summing the passage flow of the segments belonging to each stroke, with each segment counted once.

## Repository scope

The executable NetLogo material is a synthetic example that documents the passage-flow counting procedure without reproducing the empirical network or the full study model. The anonymized Random flow file retains only non-spatial row identifiers and flow values. The published CSV tables are summary outputs. No public file contains coordinates, original network identifiers, POI records, agent trajectories, raw structure metrics, or BIM/IFC-derived attributes.

## Requirements

- Python 3.10 or later
- Packages listed in `requirements.txt`
- NetLogo 7.0.4
- Java runtime distributed with NetLogo
- Environment variable `NETLOGO_HOME` pointing to the NetLogo installation directory

## Running the synthetic example

Open `examples/netlogo/passage_flow_sample.nlogox3d` in NetLogo 7, click `setup`, click `go`, and then click `export-results`. The model and its 3 by 3 by 3 lattice inputs are fully synthetic. See `examples/README.md` for details.

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

