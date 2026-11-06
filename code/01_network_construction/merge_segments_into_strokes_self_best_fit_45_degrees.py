import math
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "netlogo_data0728"
SLIM_CSV = DATA_DIR / "SZU_network_0728_T_E_link_slim.csv"
FULL_CSV = DATA_DIR / "SZU_network_0728_T_E_link_full.csv"
OUT_SLIM = DATA_DIR / "SZU_network_0728_T_E_link_slim_paper_self_best_fit45.csv"
OUT_FULL = DATA_DIR / "SZU_network_0728_T_E_link_full_paper_self_best_fit45.csv"
OUT_STATS = DATA_DIR / "stroke_summary_0728_paper_self_best_fit45.csv"

ANGLE_THRESHOLD_DEG = 45.0


def vector_from_node(row, node_id):
    if int(row.ID1) == node_id:
        return (
            float(row.X2) - float(row.X1),
            float(row.Y2) - float(row.Y1),
            float(row.Z2) - float(row.Z1),
        )
    return (
        float(row.X1) - float(row.X2),
        float(row.Y1) - float(row.Y2),
        float(row.Z1) - float(row.Z2),
    )


def angle_deg(v1, v2):
    n1 = math.sqrt(sum(x * x for x in v1))
    n2 = math.sqrt(sum(x * x for x in v2))
    if n1 == 0 or n2 == 0:
        return 180.0
    dot = sum(a * b for a, b in zip(v1, v2)) / (n1 * n2)
    dot = max(-1.0, min(1.0, dot))
    return math.degrees(math.acos(dot))


def turn_angle(edge_a, edge_b, node_id):
    v1 = vector_from_node(edge_a, node_id)
    v2 = vector_from_node(edge_b, node_id)
    return 180.0 - angle_deg(v1, v2)


def build_node_edges(df):
    node_edges = defaultdict(list)
    rows = {int(row.segment_ID): row for row in df.itertuples(index=False)}
    for row in rows.values():
        node_edges[int(row.ID1)].append(int(row.segment_ID))
        node_edges[int(row.ID2)].append(int(row.segment_ID))
    return rows, node_edges


def best_next_edge(rows, node_edges, current_edge_id, node_id, processed):
    current = rows[current_edge_id]
    candidates = []
    for other_id in node_edges[node_id]:
        if other_id == current_edge_id or other_id in processed:
            continue
        other = rows[other_id]
        angle = turn_angle(current, other, node_id)
        if angle <= ANGLE_THRESHOLD_DEG:
            candidates.append((angle, other_id))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1]))
    return candidates[0][1]


def extend_from_end(rows, node_edges, start_edge_id, start_node_id, processed):
    chain = []
    current_edge_id = start_edge_id
    node_id = start_node_id
    visited_local = set()

    while True:
        nxt = best_next_edge(rows, node_edges, current_edge_id, node_id, processed | visited_local)
        if nxt is None:
            break
        chain.append(nxt)
        visited_local.add(nxt)
        current_edge_id = nxt
        edge = rows[current_edge_id]
        node_id = int(edge.ID2) if int(edge.ID1) == node_id else int(edge.ID1)

    return chain


def assign_stroke_ids(df):
    rows, node_edges = build_node_edges(df)
    processed = set()
    stroke_ids = {}
    next_stroke = 0

    ordered_segments = sorted(rows.keys())
    for seg_id in ordered_segments:
        if seg_id in processed:
            continue

        stroke_members = [seg_id]
        processed.add(seg_id)

        start_edge = rows[seg_id]

        # extend from both ends using self-best-fit
        from_chain = extend_from_end(rows, node_edges, seg_id, int(start_edge.ID1), processed)
        for other_id in from_chain:
            if other_id not in processed:
                processed.add(other_id)
                stroke_members.append(other_id)

        to_chain = extend_from_end(rows, node_edges, seg_id, int(start_edge.ID2), processed)
        for other_id in to_chain:
            if other_id not in processed:
                processed.add(other_id)
                stroke_members.append(other_id)

        for member in stroke_members:
            stroke_ids[member] = next_stroke
        next_stroke += 1

    return [stroke_ids[int(seg_id)] for seg_id in df["segment_ID"]]


def stroke_summary(df):
    return (
        df.groupby("stroke_id")
        .agg(
            segment_count=("segment_ID", "count"),
            total_length=("Length", "sum"),
            mean_length=("Length", "mean"),
            road_ids=("Road_ID", lambda x: ";".join(map(str, x.astype(int).tolist()))),
            main_in_outdoor=("In_outdoor", lambda x: int(x.mode().iloc[0])),
            main_area_name=("area_name", lambda x: x.mode().iloc[0]),
            main_area_type=("area_type", lambda x: int(x.mode().iloc[0])),
        )
        .reset_index()
        .sort_values(["segment_count", "total_length"], ascending=[False, False])
    )


def main():
    slim = pd.read_csv(SLIM_CSV)
    full = pd.read_csv(FULL_CSV)

    stroke_ids = assign_stroke_ids(slim)
    slim.insert(1, "stroke_id", stroke_ids)

    stroke_map = slim[["segment_ID", "stroke_id"]]
    full = full.merge(stroke_map, on="segment_ID", how="left")
    full.insert(1, "stroke_id", full.pop("stroke_id"))

    slim.to_csv(OUT_SLIM, index=False, encoding="utf-8-sig")
    full.to_csv(OUT_FULL, index=False, encoding="utf-8-sig")
    summary = stroke_summary(slim)
    summary.to_csv(OUT_STATS, index=False, encoding="utf-8-sig")

    print(f"Input segments: {len(slim)}")
    print(f"Stroke count: {slim['stroke_id'].nunique()}")
    print(f"Max segments in a stroke: {summary['segment_count'].max()}")
    print(f"Mean segments per stroke: {len(slim) / slim['stroke_id'].nunique():.3f}")
    print(f"Slim written: {OUT_SLIM}")
    print(f"Full written: {OUT_FULL}")
    print(f"Summary written: {OUT_STATS}")


if __name__ == "__main__":
    main()
