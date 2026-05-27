import urllib.request
import json
import os
import time
import requests

SAVE_PATH = "events.json"
IGNORE_KEYS_PATH = "ignore_keys.json"
EVENTS_URL = "https://github.com/Piet2001/Inzetten/raw/refs/heads/main/events.json"
WEBHOOK_URLS = [os.getenv("DISCORD"), os.getenv("DISCORD2")]


def send_discord(title: str, description: str):
    """Post an embed message to all configured Discord webhooks."""
    if not WEBHOOK_URLS:
        return
    embed = {
        "title": title,
        "description": description,
    }
    webhookdata = {
        "username": "Event Change Tracking",
        "embeds": [embed],
    }
    headers = {"Content-Type": "application/json"}
    for webhook_url in WEBHOOK_URLS:
        if webhook_url:
            result = requests.post(webhook_url, json=webhookdata, headers=headers)
            if 200 <= result.status_code < 300:
                print(f"Webhook sent {result.status_code} to {webhook_url}")
            else:
                print(f"Not sent with {result.status_code} to {webhook_url}, response:\n{result.text}")

# Load ignore keys
ignore_keys = set()
if os.path.exists(IGNORE_KEYS_PATH):
    with open(IGNORE_KEYS_PATH, "r", encoding="utf-8") as f:
        ignore_list = json.load(f)
        if isinstance(ignore_list, list):
            ignore_keys = set(ignore_list)

# Load existing data for comparison (if available)
old_by_id = {}
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    old_by_id = {item["id"]: item for item in old_data}

# Download new data
with urllib.request.urlopen(EVENTS_URL) as response:
    data = json.loads(response.read().decode())

# Save new data
with open(SAVE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Downloaded events.json")

# Compare
if not old_by_id:
    print("No previous version found — skipping comparison.")
else:
    new_by_id = {item["id"]: item for item in data}

    added_ids = set(new_by_id) - set(old_by_id)
    removed_ids = set(old_by_id) - set(new_by_id)
    common_ids = set(old_by_id) & set(new_by_id)

    def sort_key(x):
        x_str = str(x)
        return (0, int(x_str)) if x_str.isdigit() else (1, x_str)

    changes_found = False

    # Compose summary message for added/removed mission_type_ids per event
    mission_type_changes = []
    for event_id in sorted(common_ids, key=sort_key):
        old = old_by_id[event_id]
        new = new_by_id[event_id]
        old_missions = set(old.get("mission_type_ids", []))
        new_missions = set(new.get("mission_type_ids", []))
        added_missions = sorted(new_missions - old_missions)
        removed_missions = sorted(old_missions - new_missions)
        caption = new.get("caption", "")
        if added_missions or removed_missions:
            line = f""
            if added_missions:
                line += f"\n Added missions: {', '.join(map(str, added_missions))}."
            if removed_missions:
                line += f"\n Removed missions: {', '.join(map(str, removed_missions))}."
            mission_type_changes.append(line)
    if mission_type_changes:
        send_discord(
            title=f"[CHANGED] id={event_id} {caption}",
            description="\n".join(mission_type_changes),
        )
        time.sleep(2)

    for event_id in sorted(added_ids, key=sort_key):
        msg = f"**[ADDED]** id={event_id} — {new_by_id[event_id].get('caption', '')}"
        print(msg)
        send_discord(
            title=f"[ADDED] id={event_id}",
            description=new_by_id[event_id].get("caption", ""),
        )
        time.sleep(5)
        changes_found = True

    for event_id in sorted(removed_ids, key=sort_key):
        msg = f"**[REMOVED]** id={event_id} — {old_by_id[event_id].get('caption', '')}"
        print(msg)
        send_discord(
            title=f"[REMOVED] id={event_id}",
            description=old_by_id[event_id].get("caption", ""),
        )
        time.sleep(5)
        changes_found = True


    # No per-field change reporting needed; only mission_type_ids and event add/remove notifications remain.

