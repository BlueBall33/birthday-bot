import json
import os
import discord

from discord.ext import commands
from datetime import datetime
from pymongo import MongoClient
from typing import Optional,Any
from addons import Settings, TOKENS

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


if not os.path.exists(os.path.join(ROOT_DIR, "settings.json")):
    raise Exception("Settings file not set!")

#----------API CLIENT----------
tokens: TOKENS = TOKENS()

if not (tokens.mongodb_name and tokens.mongodb_url):
    raise Exception("MONGODB_NAME and MONGODB_URL can't not be empty in .env")

try:
    mongodb = MongoClient(host=tokens.mongodb_url, serverSelectionTimeoutMS=5000)
    mongodb.server_info()
    if tokens.mongodb_name not in mongodb.list_database_names():
        raise Exception(f"{tokens.mongodb_name} does not exist in your mongoDB!")
    print("Successfully connected to MongoDB!")

except Exception as e:
    raise Exception("Not able to connect MongoDB! Reason:", e)

USER_DB = mongodb[tokens.mongodb_name]['User']
SETTINGS_DB = mongodb[tokens.mongodb_name]['Settings']

settings: Settings
ERROR_LOGS: dict[int, dict[int, str]] = {} #Stores error that not a Voicelink Exception
LANGS: dict[str, dict[str, str]] = {} #Stores all the languages in ./langs
GUILD_SETTINGS: dict[int, dict[str, Any]] = {} #Cache guild language
USER: dict[int, dict[str, Any]] = {}
LOCAL_LANGS: dict[str, dict[str, str]] = {} #Stores all the localization languages in ./local_langs

def get_user(user_id: int) -> dict:
    user = USER.get(user_id, None)
    print(user)
    if not user:
        user = USER_DB.find_one({"_id": user_id})
        if not user:
            USER_DB.insert_one({"_id": user_id})
        USER[user_id] = user or {}
    return user

def get_birthday(month: int,day:int) -> object:
    user = USER_DB.find({"dateBirthday.month":month,"dateBirthday.day":day} )

    return user

def update_user(user_id: int, data: dict, mode="set") -> bool:
    user = get_user(user_id)
    for key, value in data.items():
        if user.get(key) != value:
            match mode:
                case "set":
                    USER[user_id][key] = value
                case "unset":
                    USER[user_id].pop(key)
                case _:
                    return False

    result = USER_DB.update_one({"_id": user_id}, {f"${mode}": data})
    return result.modified_count > 0



def get_settings(guild_id: int) -> dict:
    settings = GUILD_SETTINGS.get(guild_id, None)
    if not settings:
        settings = SETTINGS_DB.find_one({"_id": guild_id})
        if not settings:
            SETTINGS_DB.insert_one({"_id": guild_id})

        GUILD_SETTINGS[guild_id] = settings or {}
    return settings

def update_settings(guild_id: int, data: dict, mode="set") -> bool:
    settings = get_settings(guild_id)
    for key, value in data.items():
        if settings.get(key) != value:
            match mode:
                case "set":
                    GUILD_SETTINGS[guild_id][key] = value
                case "unset":
                    GUILD_SETTINGS[guild_id].pop(key)
                case _:
                    return False

    result = SETTINGS_DB.update_one({"_id": guild_id}, {f"${mode}": data})
    return result.modified_count > 0



def open_json(path: str) -> dict:
    try:
        with open(os.path.join(ROOT_DIR, path), encoding="utf8") as json_file:
            return json.load(json_file)
    except:
        return {}


def update_json(path: str, new_data: dict) -> None:
    data = open_json(path)
    if not data:
        return

    data.update(new_data)

    with open(os.path.join(ROOT_DIR, path), "w") as json_file:
        json.dump(data, json_file, indent=4)

def get_lang(guild_id:int, key:str) -> str:
    lang = get_settings(guild_id).get("langs", "PL")
    if lang in LANGS and not LANGS[lang]:
        LANGS[lang] = open_json(os.path.join("langs", f"{lang}.json"))

    return LANGS.get(lang, {}).get(key, "Language pack not found!")

def init() -> None:
    global settings

    json = open_json("settings.json")
    if json is not None:
        settings = Settings(json)

def langs_setup() -> None:
    for language in os.listdir(os.path.join(ROOT_DIR, "langs")):
        if language.endswith('.json'):
            LANGS[language[:-5]] = {}

    for language in os.listdir(os.path.join(ROOT_DIR, "local_langs")):
        if language.endswith('.json'):
            LOCAL_LANGS[language[:-5]] = open_json(os.path.join("local_langs", language))

    return


def cooldown_check(ctx: commands.Context) -> Optional[commands.Cooldown]:
    if ctx.author.id in settings.bot_access_user:
        return None
    cooldown = settings.cooldowns_settings.get(f"{ctx.command.parent.qualified_name} {ctx.command.name}" if ctx.command.parent else ctx.command.name)
    if not cooldown:
        return None
    return commands.Cooldown(cooldown[0], cooldown[1])

def get_aliases(name: str) -> list:
    return settings.aliases_settings.get(name, [])

