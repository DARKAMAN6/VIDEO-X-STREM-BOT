import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
admins = {}
SESSION_NAME = getenv("SESSION_NAME", "session")
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_NAME = getenv("BOT_NAME", "Video Stream")
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
OWNER_NAME = getenv("OWNER_NAME", "R0Y41_KING")
ALIVE_NAME = getenv("ALIVE_NAME", "R0Y41_KING")
BOT_USERNAME = getenv("BOT_USERNAME", "NOTHING")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "ALEXAMUSIC")
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "DARKAMANSUPPORT")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "DARKAMANCHANNEL")
SUDO_USERS = list(map(int, getenv("SUDO_USERS").split()))
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! .").split())
ALIVE_IMG = getenv("ALIVE_IMG", "https://telegra.ph/file/cd216fb722b2b5f8e9752.jpg")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "60"))
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/DARKAMAN6/VIDEO-X-STREM-BOT")
ROYAL_IMG = getenv("ROYAL_IMG", "https://telegra.ph/file/cd216fb722b2b5f8e9752.jpg")
