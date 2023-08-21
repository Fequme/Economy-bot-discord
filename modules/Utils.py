import json

class Utils:

    def __init__(self):
        self.active_games = []
        self.messageCount = {}

    # Server games
    def start_game(self, member_id):
        self.active_games.append(member_id)

    def stop_game(self, member_id):
        self.active_games.remove(member_id)

    def is_active_game(self, member_id):
        if member_id in self.active_games:
            return True
        else:
            return False

    # Get guild id
    def get_guild_id():
        with open("./assets/settings.json", "r", encoding="utf8") as settings:
            data = json.load(settings)

        return data.get("guild_id")

    def get_patch_db(db):
        with open("./assets/settings.json", "r", encoding="utf8") as settings:
            data = json.load(settings)

        if db == "main":
            return data.get("path_main_db")
        elif db == "log":
            return data.get("path_log_db")

    # Counter messages
    def write_message(self, author):
        if author in self.messageCount:
            self.messageCount[author] += 1
        else:
            self.messageCount[author] = 1

    def get_messages(self):
        messages = self.messageCount
        self.messageCount = {}
        
        return messages