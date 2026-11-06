"""Run the public Random passage-flow model for 20,000 ticks.

Set NETLOGO_HOME to the NetLogo 7 installation directory before running. The
script stages the restricted network input supplied on request next to the
models because the models read those filenames relative to their own folder.
"""
from __future__ import annotations

import csv
import os
import shutil
import subprocess
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2]
MODEL_DIR = PACKAGE / "code" / "02_simulation" / "models"
INPUT_DIR = PACKAGE / "data" / "input"
OUTPUT = PACKAGE / "data" / "reproduced_outputs"
NETLOGO_HOME = Path(os.environ["NETLOGO_HOME"])
JAVA = NETLOGO_HOME / "runtime" / "bin" / "java.exe"
JAR = NETLOGO_HOME / "app" / "netlogo-7.0.4.jar"
RUNS = (
    ("Random", "Random_OD", "random_movement_passage_flow_20000_ticks.nlogox3d"),
)

def stage_inputs() -> None:
    # The public Random model requires the restricted network input supplied on request.
    shutil.copy2(INPUT_DIR / "network" / "SZU_network_0728_T_E_link_slim.csv", MODEL_DIR / "SZU_network_0728_T_E_link_slim.csv")

def command(model: Path, table: Path) -> list[str]:
    return [str(JAVA), "-Xms32m", "-Xmx512m", "-XX:+UseSerialGC", "-Dfile.encoding=UTF-8",
        f"-Dnetlogo.docs.dir={NETLOGO_HOME}", f"-Dnetlogo.models.dir={NETLOGO_HOME / 'models'}",
        f"-Dnetlogo.extensions.dir={NETLOGO_HOME / 'extensions'}", "--add-exports=java.base/java.lang=ALL-UNNAMED",
        "--add-exports=java.desktop/sun.awt=ALL-UNNAMED", "--add-exports=java.desktop/sun.java2d=ALL-UNNAMED",
        "-Dorg.nlogo.is3d=true", "-classpath", str(JAR), "org.nlogo.headless.Main", "--3D",
        "--model", str(model), "--experiment", "hybrid_run", "--table", str(table), "--threads", "1"]

def validate(agent_file: Path, segment_file: Path) -> None:
    agents = list(csv.DictReader(agent_file.open(encoding="utf-8-sig", newline="")))
    segments = list(csv.DictReader(segment_file.open(encoding="utf-8-sig", newline="")))
    if len(agents) != 1000 or len({row["agent_id"] for row in agents}) != 1000:
        raise RuntimeError(f"Expected 1,000 unique agents in {agent_file.name}")
    if any(int(row["global_passage_flow"]) != int(row["indoor_passage_flow"]) + int(row["outdoor_passage_flow"]) for row in agents):
        raise RuntimeError(f"Indoor/outdoor totals are inconsistent in {agent_file.name}")
    if sum(int(row["global_passage_flow"]) for row in agents) != sum(int(row["passage_flow"]) for row in segments):
        raise RuntimeError(f"Agent and segment totals disagree for {agent_file.name}")

def main() -> None:
    if not JAVA.exists() or not JAR.exists():
        raise FileNotFoundError("NETLOGO_HOME does not point to a NetLogo 7 installation.")
    stage_inputs(); OUTPUT.mkdir(parents=True, exist_ok=True)
    for label, prefix, model_name in RUNS:
        before_agents = set(OUTPUT.glob(f"agent_cumulative_passage_flow_{prefix}_Hybrid*.csv"))
        before_segments = set(OUTPUT.glob(f"formal_segment_cumulative_passage_flow_{prefix}_Hybrid*.csv"))
        table = OUTPUT / f"behaviorspace_passage_flow_{label}.csv"
        subprocess.run(command(MODEL_DIR / model_name, table), cwd=OUTPUT, check=True)
        agents = set(OUTPUT.glob(f"agent_cumulative_passage_flow_{prefix}_Hybrid*.csv")) - before_agents
        segments = set(OUTPUT.glob(f"formal_segment_cumulative_passage_flow_{prefix}_Hybrid*.csv")) - before_segments
        if len(agents) != 1 or len(segments) != 1:
            raise RuntimeError(f"Unexpected export count for {label}")
        validate(agents.pop(), segments.pop())

if __name__ == "__main__":
    main()

