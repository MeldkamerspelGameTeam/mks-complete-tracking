"""
Reads missions.json from the project root and writes one JSON file per mission
into the missionfiles/ folder. Each file is named <mission_id>.json.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MISSIONS_PATH = os.path.join(ROOT, "missions.json")
OUTPUT_DIR = os.path.join(ROOT, "missionfiles")


def main() -> None:
    with open(MISSIONS_PATH, "r", encoding="utf-8") as f:
        missions = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for mission in missions:
        mission_id = mission["id"]
        safe_id = str(mission_id).replace("/", "_").replace("\\", "_")
        out_path = os.path.join(OUTPUT_DIR, f"{safe_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mission, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"Written {len(missions)} mission file(s) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
