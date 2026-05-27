import json
import os
import urllib.request

EVENTS_URL = "https://github.com/Piet2001/Inzetten/raw/refs/heads/main/events.json"
KEYS_PATH = "keys.json"
IGNORE_KEYS_PATH = "ignore_keys.json"
OUTPUT_PATH = "missing_event_keys.json"

def collect_all_keys(obj):
    """Recursively collect all keys from nested dicts and lists."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            keys.update(collect_all_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.update(collect_all_keys(item))
    return keys

# Download events.json from URL
with urllib.request.urlopen(EVENTS_URL) as response:
    events = json.load(response)

# Collect all unique keys from events (including nested)
all_keys = set()
for event in events:
    all_keys.update(collect_all_keys(event))

# Load keys.json
existing_keys = set()
if os.path.exists(KEYS_PATH):
    with open(KEYS_PATH, "r", encoding="utf-8") as f:
        keys_data = json.load(f)
        if isinstance(keys_data, dict):
            existing_keys = set(keys_data.keys())

# Load ignore_keys.json and add to existing_keys
if os.path.exists(IGNORE_KEYS_PATH):
    with open(IGNORE_KEYS_PATH, "r", encoding="utf-8") as f:
        ignore_list = json.load(f)
        if isinstance(ignore_list, list):
            existing_keys.update(ignore_list)

# Find missing
missing_keys = sorted(all_keys - existing_keys)

# Write to file
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(missing_keys, f, indent=2, ensure_ascii=False)

print(f"Missing event keys written to {OUTPUT_PATH}")
