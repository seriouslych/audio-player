from pypresence import Presence
import time

client_id = '1267916482835120169' 

class DiscordRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = Presence(client_id)
        self.connected = False

    def connect(self):
        if not self.connected:
            self.rpc.connect()
            self.connected = True

    def update(self, state, large_image, large_text, start):
        try:
            self.rpc.update(
                state=state,
                large_image=large_image,
                large_text=large_text,
                start=start
            )
            print("Discord RPC status updated successfully.")
        except Exception as e:
            print(f"Failed to update Discord RPC: {e}")

    def close(self):
        if self.connected:
            self.rpc.close()
            self.connected = False

discord_rpc = DiscordRPC(client_id)
discord_rpc.connect()

def update_discord_rpc(title, artist, image_name):
    discord_rpc.update(
        state=f"Playing: {artist} - {title}",
        large_image=image_name,
        large_text=f"{artist} - {title}",
        start=int(time.time())
    )