import requests
import time
import os

# ========== CONFIG ==========
SERVER = "arenkarki.minehut.gg"
NTFY_TOPIC = os.getenv("NTFY_TOPIC")  # Set this in Railway
CHECK_INTERVAL = 45  # seconds between checks
# ============================

if not NTFY_TOPIC:
    print("Error: NTFY_TOPIC environment variable is not set!")
    exit(1)

last_online = -1  # -1 means we don't know yet

def get_player_count():
    try:
        r = requests.get(f"https://api.mcsrvstat.us/3/{SERVER}", timeout=10)
        data = r.json()

        # Detect if the actual server is offline
        motd = " ".join(data.get("motd", {}).get("clean", [])).lower()
        if "server is offline" in motd or not data.get("online", False):
            return 0

        return data.get("players", {}).get("online", 0)
    except Exception as e:
        print(f"Error checking server: {e}")
        return None

def send_notification(message):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={"Title": "Minecraft Server Alert", "Priority": "high", "Tags": "video_game"}
        )
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

print("Starting Minecraft monitor...")
print(f"Watching: {SERVER}")
print(f"ntfy topic: {NTFY_TOPIC}")

while True:
    count = get_player_count()

    if count is not None:
        if last_online == -1:
            # First check - just record the number
            last_online = count
            print(f"Initial player count: {count}")
        else:
            if count > last_online:
                difference = count - last_online
                if difference == 1:
                    send_notification(f"Someone joined the server! Now {count} online.")
                else:
                    send_notification(f"{difference} players joined! Now {count} online.")
            elif count < last_online:
                print(f"Player left. Now {count} online.")
            
            last_online = count

    time.sleep(CHECK_INTERVAL)
