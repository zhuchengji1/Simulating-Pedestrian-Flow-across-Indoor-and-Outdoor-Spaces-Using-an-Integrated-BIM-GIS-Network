import csv
import math
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_SDNA_SHP = ROOT / "data0727" / "03_SZU_sDNAPrepare_0728_T_E_link_area_new.shp"
INPUT_AREA_SHP = ROOT / "data0727" / "03_SZU_sDNAPrepare_0727.shp"
OUTPUT_DIR = ROOT / "netlogo_data0728"
OUTPUT_CSV_FULL = OUTPUT_DIR / "SZU_network_0728_T_E_link_full.csv"
OUTPUT_CSV_SLIM = OUTPUT_DIR / "SZU_network_0728_T_E_link_slim.csv"
OUTPUT_MAPPING = OUTPUT_DIR / "area_name_area_type_mapping.csv"

SCALE = 1.0 / 10

BASIC_NETLOGO_ATTRS = [
    "area_name",
    "area_type",
    "In_outdoor",
    "LConn",
    "LLen",
]

SLIM_SDNA_ATTRS = [
    ("MCDn", ["MCDn"]),
    ("NQPDCn", ["NQPDCn"]),
    ("BtCn", ["BtCn"]),
    ("TPBtCn", ["TPBtCn"]),
    ("TPDn", ["TPDn"]),
    ("MGLCn", ["MGLCn"]),
    ("MCFn", ["MCFn"]),
    ("DivCn", ["DivCn"]),
    ("PR", ["PR"]),
    ("WPR", ["WPR"]),
    ("NQPDC500", ["NQPDC500"]),
    ("BtC500", ["BtC500"]),
]

DIRECTION_ATTRS = ["VecX", "VecY", "VecZ", "Azimuth"]

OUTDOOR_AREA_NAMES = {
    "road",
    "sports_field",
    "wenshan_lake_park",
    "dujuan_hill_park",
    "lawn_1",
    "lawn_2",
    "south_gate",
    "little_west_gate",
    "west_gate",
    "north_gate",
    "east_gate",
    "golf_course",
    "Alumni_Square",
    "football_field",
    "small_square",
    "flower_garden",
}

TEACHING_BUILDING_NAMES = {"teaching_building", "teaching_buliding"}


def calculate_3d_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)


def calculate_orientation(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    dist = math.sqrt(dx**2 + dy**2 + dz**2)

    if dist > 0:
        vx, vy, vz = dx / dist, dy / dist, dz / dist
    else:
        vx, vy, vz = 0, 0, 0

    azimuth = math.degrees(math.atan2(dy, dx))
    if azimuth < 0:
        azimuth += 360
    return vx, vy, vz, azimuth


def clean_value(value):
    if pd.isna(value):
        return 0
    if isinstance(value, float):
        return round(value, 8)
    return value


def classify_in_outdoor(area_name, area_type):
    if str(area_name).strip() in OUTDOOR_AREA_NAMES:
        return 1
    try:
        return 1 if int(float(area_type)) == 0 else 0
    except (TypeError, ValueError):
        return 0


def attach_area_attributes(sdna_gdf, area_gdf):
    area = area_gdf[["Road_ID", "area_name", "area_type"]].copy()
    area["Road_ID"] = area["Road_ID"].astype(int)

    gdf = sdna_gdf.copy()
    gdf["Road_ID"] = gdf["ID"].astype(int)
    gdf = gdf.merge(area, on="Road_ID", how="left")

    missing_area = int(gdf["area_name"].isna().sum())
    if missing_area:
        print(f"Warning: rows without area attributes: {missing_area}")

    gdf["area_name"] = gdf["area_name"].fillna("none").astype(str).str.strip()
    gdf.loc[gdf["area_name"].eq(""), "area_name"] = "none"
    gdf["area_type"] = pd.to_numeric(gdf["area_type"], errors="coerce").fillna(0).astype(int)

    gdf.loc[gdf["area_name"].isin(TEACHING_BUILDING_NAMES), "area_type"] = 8
    gdf.loc[gdf["area_type"].eq(8), "area_name"] = "teaching_building"
    gdf["In_outdoor"] = gdf.apply(
        lambda row: classify_in_outdoor(row.get("area_name", ""), row.get("area_type", 0)),
        axis=1,
    )
    return gdf


def create_3d_multigraph(gdf):
    attributes = [
        col
        for col in gdf.columns
        if col != "geometry" and col.upper() not in ["FID", "ID"] and col != "Road_ID"
    ]
    graph = nx.MultiGraph()

    def add_line(line, base_attrs):
        coords = list(line.coords)
        if len(coords) < 2:
            return

        for i in range(len(coords) - 1):
            p1_raw = coords[i]
            p2_raw = coords[i + 1]
            p1 = (p1_raw[0], p1_raw[1], p1_raw[2]) if len(p1_raw) >= 3 else (p1_raw[0], p1_raw[1], 0.0)
            p2 = (p2_raw[0], p2_raw[1], p2_raw[2]) if len(p2_raw) >= 3 else (p2_raw[0], p2_raw[1], 0.0)

            vx, vy, vz, azimuth = calculate_orientation(p1, p2)
            attrs = base_attrs.copy()
            attrs["VecX"] = vx
            attrs["VecY"] = vy
            attrs["VecZ"] = vz
            attrs["Azimuth"] = azimuth

            graph.add_node(p1, x=p1[0], y=p1[1], z=p1[2])
            graph.add_node(p2, x=p2[0], y=p2[1], z=p2[2])
            graph.add_edge(p1, p2, **attrs)

    for _, row in gdf.iterrows():
        geom = row.geometry
        road_id = row.get("Road_ID", row.get("FID", row.get("ID", 0)))
        base_attrs = {"Road_ID": int(road_id) if not pd.isna(road_id) else 0}
        for attr in attributes:
            base_attrs[attr] = clean_value(row.get(attr))

        if geom.geom_type == "LineString":
            add_line(geom, base_attrs)
        elif geom.geom_type == "MultiLineString":
            for line in geom.geoms:
                add_line(line, base_attrs)

    print(f"Graph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    return graph, attributes


def calculate_pr_wpr(graph):
    line_graph = nx.line_graph(graph).to_directed()
    pr = nx.pagerank(line_graph, alpha=0.85, weight=None, max_iter=500)

    for _, v_node, edge_attrs in line_graph.edges(data=True):
        p1, p2, key = v_node
        edge_data = graph.get_edge_data(p1, p2, key)
        lconn = float(edge_data.get("LConn", 1))
        edge_attrs["w_lconn"] = lconn if lconn > 0 else 1.0

    wpr = nx.pagerank(line_graph, alpha=0.85, weight="w_lconn", max_iter=500)

    for p1, p2, key, data in graph.edges(keys=True, data=True):
        edge_key = (p1, p2, key)
        reverse_key = (p2, p1, key)
        data["PR"] = pr.get(edge_key, pr.get(reverse_key, 0))
        data["WPR"] = wpr.get(edge_key, wpr.get(reverse_key, 0))


def resolve_slim_sources(full_attrs):
    slim_attr_sources = []
    for attr in BASIC_NETLOGO_ATTRS + SLIM_SDNA_ATTRS + DIRECTION_ATTRS:
        output_names = [item[0] for item in slim_attr_sources]
        if isinstance(attr, tuple):
            output_name, candidates = attr
            source_name = next((candidate for candidate in candidates if candidate in full_attrs), None)
            if source_name and output_name not in output_names:
                slim_attr_sources.append((output_name, source_name))
        elif attr in full_attrs and attr not in output_names:
            slim_attr_sources.append((attr, attr))

    missing = []
    for attr in BASIC_NETLOGO_ATTRS + SLIM_SDNA_ATTRS:
        if isinstance(attr, tuple):
            output_name, candidates = attr
            if not any(candidate in full_attrs for candidate in candidates):
                missing.append(output_name)
        elif attr not in full_attrs:
            missing.append(attr)
    if missing:
        print(f"Warning: missing slim attributes: {missing}")

    return slim_attr_sources


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)


def export_csvs(graph, attributes):
    nodes = list(graph.nodes())
    node_to_id = {node: i for i, node in enumerate(nodes)}
    node_degrees = dict(graph.degree())

    full_attrs = attributes + DIRECTION_ATTRS + ["PR", "WPR"]
    slim_attr_sources = resolve_slim_sources(full_attrs)

    header_base = ["ID1", "ID2", "X1", "Y1", "Z1", "X2", "Y2", "Z2", "Length"]
    header_tail = ["Deg1", "Deg2"]

    full_header_base = ["Length"]
    full_rows = [["segment_ID", "Road_ID"] + full_header_base + full_attrs + header_tail]
    slim_rows = [["segment_ID", "Road_ID"] + header_base + [item[0] for item in slim_attr_sources] + header_tail]

    for segment_id, (p1, p2, _, data) in enumerate(graph.edges(keys=True, data=True)):
        id1 = node_to_id[p1]
        id2 = node_to_id[p2]
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        length = data.get("LLen", 0) or calculate_3d_distance(p1, p2)
        row_base = [
            id1,
            id2,
            x1 * SCALE,
            y1 * SCALE,
            z1 * SCALE,
            x2 * SCALE,
            y2 * SCALE,
            z2 * SCALE,
            length,
        ]
        road_id = data.get("Road_ID", 0)
        deg1 = node_degrees.get(p1, 0)
        deg2 = node_degrees.get(p2, 0)

        full_rows.append(
            [segment_id, road_id, length]
            + [clean_value(data.get(attr, 0)) for attr in full_attrs]
            + [deg1, deg2]
        )
        slim_rows.append(
            [segment_id, road_id]
            + row_base
            + [clean_value(data.get(source_attr, 0)) for _, source_attr in slim_attr_sources]
            + [deg1, deg2]
        )

    write_csv(OUTPUT_CSV_FULL, full_rows)
    write_csv(OUTPUT_CSV_SLIM, slim_rows)

    print(f"Full CSV written: {OUTPUT_CSV_FULL}")
    print(f"Slim CSV written: {OUTPUT_CSV_SLIM}")
    print(f"Slim attributes: {slim_attr_sources}")


def export_mapping(csv_path):
    df = pd.read_csv(csv_path, usecols=["area_name", "area_type", "In_outdoor"])
    mapping = (
        df.groupby(["area_name", "area_type", "In_outdoor"])
        .size()
        .reset_index(name="edge_count")
        .sort_values(["area_type", "area_name"])
    )
    mapping["area_type"] = mapping["area_type"].astype(int)
    mapping["In_outdoor"] = mapping["In_outdoor"].astype(int)
    mapping.to_csv(OUTPUT_MAPPING, index=False, encoding="utf-8-sig")
    print(f"Mapping written: {OUTPUT_MAPPING}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    sdna_gdf = gpd.read_file(INPUT_SDNA_SHP)
    area_gdf = gpd.read_file(INPUT_AREA_SHP)
    print(f"Read sDNA shp: {INPUT_SDNA_SHP}")
    print(f"sDNA rows: {len(sdna_gdf)}")
    print(f"Read area shp: {INPUT_AREA_SHP}")
    print(f"area rows: {len(area_gdf)}")

    gdf = attach_area_attributes(sdna_gdf, area_gdf)
    graph, attributes = create_3d_multigraph(gdf)
    calculate_pr_wpr(graph)
    export_csvs(graph, attributes)
    export_mapping(OUTPUT_CSV_SLIM)


if __name__ == "__main__":
    main()
