import requests
import time
import os

# ========== CONFIG ==========
SERVER = "arenkarki.minehut.gg"
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
CHECK_INTERVAL = 45
# ============================

if not NTFY_TOPIC:
    print("Error: NTFY_TOPIC environment variable is not set!")
    exit(1)

last_players = set()  # Store the names of players from the last check

def get_server_data():
    try:
        r = requests.get(f"https://api.mcsrvstat.us/3/{SERVER}", timeout=10)
        data = r.json()

        # Check if server is offline
        motd = " ".join(data.get("motd", {}).get("clean", [])).lower()
        if "server is offline" in motd or not data.get("online", False):
            return 0, set()

        online = data.get("players", {}).get("online", 0)
        
        # Get player names if available
        players = set()
        player_list = data.get("players", {}).get("list", [])
        if player_list:
            for p in player_list:
                if isinstance(p, dict):
                    players.add(p.get("name", "Unknown"))
                else:
                    players.add(str(p))
        
        return online, players
    except Exception as e:
        print(f"Error checking server: {e}")
        return None, None

def send_notification(message):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": "Minecraft Server Alert",
                "Priority": "high",
                "Tags": "video_game"
            }
        )
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

print("Starting Minecraft monitor...")
print(f"Watching: {SERVER}")
print(f"ntfy topic: {NTFY_TOPIC}")

while True:
    online, current_players = get_server_data()

    if online is not None:
        if not last_players and online == 0:
            # First run or empty
            last_players = current_players
            print(f"Initial players: {online}")
        else:
            # Find who joined
            joined = current_players - last_players
            # Find who left
            left = last_players - current_players

            if joined:
                names = ", ".join(joined)
                send_notification(f"{names} joined the server! Now {online} online.")
            
            if left:
                names = ", ".join(left)
                send_notification(f"{names} left the server. Now {online} online.")

            # Fallback if we have no names but count changed
            if not joined and not left:
                if online > len(last_players):
                    send_notification(f"Someone joined the server! Now {online} online.")
                elif online < len(last_players):
                    send_notification(f"Someone left the server. Now {online} online.")

            last_players = current_players

    time.sleep(CHECK_INTERVAL)
