"""
Reads missions.json from the project root and writes one JSON file per mission
into the missionfiles/ folder, grouped by base ID range and base ID.

Structure:
  missionfiles/
    0-99/
      0/
        0.json
      25/
        25.json
        25_a.json
    100-199/
      150/
        150.json
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MISSIONS_PATH = os.path.join(ROOT, "missions.json")
OUTPUT_DIR = os.path.join(ROOT, "missionfiles")
RANGE_SIZE = 100


def range_folder(base_id: int) -> str:
    start = (base_id // RANGE_SIZE) * RANGE_SIZE
    end = start + RANGE_SIZE - 1
    return f"{start}-{end}"


def main() -> None:
    with open(MISSIONS_PATH, "r", encoding="utf-8") as f:
        missions = json.load(f)

    for mission in missions:
        mission_id = str(mission["id"])
        base_str = mission_id.split("/")[0]
        safe_id = mission_id.replace("/", "_").replace("\\", "_")

        if base_str.isdigit():
            base_id = int(base_str)
        elif "base_mission_id" in mission and str(mission["base_mission_id"]).isdigit():
            base_id = int(mission["base_mission_id"])
            base_str = str(base_id)
        else:
            base_id = None

        if base_id is not None:
            folder = os.path.join(OUTPUT_DIR, range_folder(base_id), base_str)
        else:
            folder = os.path.join(OUTPUT_DIR, "other", safe_id)

        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, f"{safe_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mission, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"Written {len(missions)} mission file(s) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
