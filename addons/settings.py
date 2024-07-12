import os
from dotenv import load_dotenv

class Settings:
    def __init__(self, settings: dict) -> None:
        self.invite_link = settings.get("invite_link","")
        self.invite_bot_link = settings.get("invite_bot_link","")
        self.nodes = settings.get("nodes", {})
        self.bot_prefix = settings.get("prefix", "")
        self.bot_name = settings.get("bot_name","")
        self.activity = settings.get("activity", [{"listen": "/help"}])
        self.embed_color = int(settings.get("embed_color", "0xb3b3b3"), 16)
        self.bot_access_user = settings.get("bot_access_user", [])
        self.emoji_source_raw = settings.get("emoji_source_raw", {})
        self.cooldowns_settings = settings.get("cooldowns", {})
        self.aliases_settings = settings.get("aliases", {})
        self.controller = settings.get("default_controller", {})
        self.lyrics_platform = settings.get("lyrics_platform", "A_ZLyrics").lower()
        self.version = settings.get("version", "")

class TOKENS:
    def __init__(self) -> None:
        load_dotenv()

        self.token = os.getenv("TOKEN")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret_id = os.getenv("CLIENT_SECRET_ID")
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.mongodb_name = os.getenv("MONGODB_NAME")