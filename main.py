import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import time
import os
import json
import asyncio
from copy import deepcopy
from datetime import datetime
import io
import aiohttp
from PIL import Image

# ------------------------
# CONFIG
# ------------------------
INTENTS = discord.Intents.default()
INTENTS.message_content = True

PREFIX = "-"
DATA_FILE = "data.json"
IMAGE_STORAGE_CHANNEL = 1468260725284802755  # Channel for storing composite battle images

# ------------------------
# CHARACTERS (base)
# Each character has the same base stats across rarities; rarities only affect max_level
CHARACTERS = [
    {
        "id": "kai",
        "name": "Kai",
        "base": {"hp": 81, "atk": 79, "def": 85, "spd": 75},
        "ability": "First turn: +100% DEF",
        "ability_type": "first_turn_def",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467230569225257021/IMG_6242.webp?ex=697fa073&is=697e4ef3&hm=fcf57c98aa851d3720a077233c986ff8ca097d9f627f8f3d0015418dec20b63f&=&format=webp&width=691&height=967"
    },
    {
        "id": "valkyrie",
        "name": "Valkyrie",
        "base": {"hp": 70, "atk": 70, "def": 70, "spd": 75},
        "ability": "First turn: +100% SPD",
        "ability_type": "first_turn_spd",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467231114069541167/IMG_6243.jpg?ex=697fa0f5&is=697e4f75&hm=9ea3fc0b57e952f3ef19b47890d430953154d550c8080ed4a126d9a6cdb1315c&=&format=webp&width=692&height=968"
    },
    {
        "id": "shishilan_pasalan",
        "name": "Shishilan Pasalan",
        "base": {"hp": 75, "atk": 88, "def": 75, "spd": 50},
        "ability": "First turn: +50% ATK",
        "ability_type": "first_turn_atk",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467230025437679638/IMG_6240.webp?ex=697f9ff1&is=697e4e71&hm=12d51b8f9340d44c7fb9350c23ac32b0acd9d1dbf0724625bd6cb5c3027307b0&=&format=webp&width=691&height=967"
    },
    {
        "id": "kasli",
        "name": "Kasli",
        "base": {"hp": 92, "atk": 80, "def": 91, "spd": 80},
        "ability": "Every turn: if DEF > enemy DEF, +20% DEF and heals 20% max HP",
        "ability_type": "def_boost_and_heal",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467226612956135477/IMG_6235.webp?ex=697f9cc4&is=697e4b44&hm=009816068e835a51f08118c55ba0f89b8056998576aaed3728fe0503cbd85328&=&format=webp&width=691&height=968"
    },
    {
        "id": "emma",
        "name": "Emma",
        "base": {"hp": 90, "atk": 72, "def": 94, "spd": 70},
        "ability": "When HP < 50%: +50% DEF",
        "ability_type": "low_hp_def_boost",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467227714330038302/IMG_6237.webp?ex=697f9dca&is=697e4c4a&hm=228c56a9a127727b6ef49d93f076f017e74d81a74fde02c5a36a298602161f2c&=&format=webp&width=691&height=968"
    },
    {
        "id": "thundia",
        "name": "Thundia",
        "base": {"hp": 82, "atk": 85, "def": 89, "spd": 79},
        "ability": "First attack: Paralyze enemy for 2 turns",
        "ability_type": "paralyze",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467228234142716057/IMG_6238.webp?ex=697f9e46&is=697e4cc6&hm=c818fc48e0c497096815093781fb55da02dc6b43037dc1999374f22b1ed18bed&=&format=webp&width=691&height=967"
    },
    {
        "id": "jeanne",
        "name": "Jeanne",
        "base": {"hp": 88, "atk": 69, "def": 85, "spd": 69},
        "ability": "First attack: Heal 30% max HP, +30% DEF",
        "ability_type": "heal_and_def",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467229071741026486/IMG_6239.webp?ex=697f9f0e&is=697e4d8e&hm=3ced57c2b8f5be94667b84252de7ccd99720d94b36eb37e410434a64111750b0&=&format=webp&width=691&height=967"
    },
    {
        "id": "balrog",
        "name": "Balrog",
        "base": {"hp": 88, "atk": 75, "def": 80, "spd": 80},
        "ability": "Every turn: +20% ATK (stacks)",
        "ability_type": "rampage",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467437264329248902/IMG_6249.webp?ex=698060f3&is=697f0f73&hm=afc7db51b57d8bff8d4668b82bffa0c089b0e812761c53632e7c023e8f74ac05&=&format=webp&width=691&height=968"
    },
    {
        "id": "verbena",
        "name": "Verbena",
        "base": {"hp": 88, "atk": 75, "def": 80, "spd": 80},
        "ability": "Survives with 1 HP once when taking fatal damage",
        "ability_type": "survive",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467287024011837731/IMG_6245.webp?ex=697fd507&is=697e8387&hm=9ac193ff03c2f6090ad9970be4809415d93e34c0f7080763d678371e187e36c3&=&format=webp&width=692&height=968"
    },
    {
        "id": "yukimura",
        "name": "Yukimura",
        "base": {"hp": 79, "atk": 92, "def": 72, "spd": 65},
        "ability": "When HP < 50%: Lifesteal (heal 50% of damage dealt)",
        "ability_type": "lifesteal",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467439641987907688/IMG_6241.webp?ex=6980632a&is=697f11aa&hm=3644ff1507591152d68d5f02da1ea81d6787cbd7dbd363a37c9b90b1793a0c1d&=&format=webp"
    },
    {
        "id": "ruri",
        "name": "Ruri",
        "base": {"hp": 93, "atk": 71, "def": 93, "spd": 69},
        "ability": "For 3 turns: +50% DEF",
        "ability_type": "def_boost_3turns",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467441355885252791/IMG_6251.webp?ex=698064c2&is=697f1342&hm=1c1f5a11027d3c447d1f0933fea38cbeff8ceb374ac4da5f683e5c6da2dd16ff&=&format=webp&width=691&height=968"
    },
    {
        "id": "lunacia",
        "name": "Lunacia",
        "base": {"hp": 85, "atk": 80, "def": 70, "spd": 90},
        "ability": "If SPD > enemy SPD: Deal +50% bonus damage",
        "ability_type": "speed_bonus",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467304124465807543/IMG_6246.webp?ex=697fe4f4&is=697e9374&hm=589f49e7ea6fb044cf8aba2211088db958a1d872be585be1ad801671eb1f5409&=&format=webp&width=692&height=968"
    },
    {
        "id": "bahamut",
        "name": "Bahamut",
        "base": {"hp": 66, "atk": 91, "def": 76, "spd": 91},
        "ability": "When HP < 50%: +50% ATK",
        "ability_type": "low_hp_atk_boost",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467305407293948141/IMG_6247.webp?ex=697fe626&is=697e94a6&hm=b21bd82a8e152875c3964ff175a11fb0152693ab005bcca061bf7eff28c7ec86&=&format=webp"
    },
    {
        "id": "windy",
        "name": "Windy",
        "base": {"hp": 88, "atk": 70, "def": 66, "spd": 66},
        "ability": "If HP < 50%, heals 50% of max HP (once)",
        "ability_type": "low_hp_big_heal",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467581480770207786/IMG_6281.webp?ex=6980e743&is=697f95c3&hm=cb6acdb1e97b1d8acc57a002b28650048badd08e84abd1d9c021f0445a7e1d03&=&format=webp&width=691&height=967"
    },
    {
        "id": "nobunaga",
        "name": "Nobunaga",
        "base": {"hp": 70, "atk": 80, "def": 75, "spd": 70},
        "ability": "If HP < 50%, increases SPD by 50%",
        "ability_type": "low_hp_spd_boost",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467583149960859750/IMG_6284.webp?ex=6980e8d1&is=697f9751&hm=4b89114a61ce971c96ec616278c3691b9d0429d3dce6d5f721d1b5cefb854976&=&format=webp"
    },
    {
        "id": "izanagi",
        "name": "Izanagi",
        "base": {"hp": 91, "atk": 90, "def": 70, "spd": 70},
        "ability": "Every turn: if ATK > enemy ATK, +20% ATK and heals 20% max HP",
        "ability_type": "atk_boost_and_heal",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467584718621905068/IMG_6285.webp?ex=6980ea47&is=697f98c7&hm=fe8288fb73ba343ecea2e03d6876dedc44c84ba3b06f4dadfc4237b1a719eeb4&=&format=webp&width=692&height=968"
    },
    {
        "id": "luminalia",
        "name": "Luminalia",
        "base": {"hp": 89, "atk": 60, "def": 79, "spd": 80},
        "ability": "For 3 turns, increases SPD by 50%",
        "ability_type": "spd_boost_3turns",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467585963424219228/IMG_6282.png?ex=6980eb70&is=697f99f0&hm=4e2038a7aa30f07ba00efba04f9bf4b9ffeabf464adc6f1b52c500a639bb94d0&=&format=webp&quality=lossless&width=691&height=968"
    },
    {
        "id": "mitama",
        "name": "Mitama",
        "base": {"hp": 94, "atk": 65, "def": 78, "spd": 62},
        "ability": "First attack: Heals 50% max HP",
        "ability_type": "first_attack_heal",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467941345611091969/IMG_6305.webp?ex=69823669&is=6980e4e9&hm=5b8367041b4201d36c4bae2b2efa511ba27c9fa2e910387e1b0a8bba2e4290e8&=&format=webp&width=691&height=967"
    },
    {
        "id": "deale",
        "name": "Deale",
        "base": {"hp": 77, "atk": 76, "def": 78, "spd": 88},
        "ability": "First attack: +50% SPD",
        "ability_type": "first_attack_spd",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467942208543129772/IMG_6304.webp?ex=69823737&is=6980e5b7&hm=251d7918dad0471308b5baaf271a47c14d296c21f7f821e829461185d5b666c8&=&format=webp&width=691&height=968"
    },
    {
        "id": "kuu",
        "name": "Kuu",
        "base": {"hp": 83, "atk": 83, "def": 75, "spd": 75},
        "ability": "After 3 turns: +50% ATK",
        "ability_type": "turn3_atk_boost",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467943692521443462/IMG_6306.webp?ex=69823899&is=6980e719&hm=09e31480ec693e1419e1385cb8f2f595ecac176acdbd3a676f44ffd818217d5d&=&format=webp&width=691&height=968"
    },
    {
        "id": "himeyuri",
        "name": "Himeyuri",
        "base": {"hp": 70, "atk": 75, "def": 79, "spd": 78},
        "ability": "After 3 turns: Heals 50% max HP",
        "ability_type": "turn3_heal",
        "image": "https://media.discordapp.net/attachments/1467048963415871621/1467944233175617639/IMG_6307.webp?ex=6982391a&is=6980e79a&hm=6ea5933cbac24768162937bf8093519651aec5ecaac7134f5464fe3c284f110f&=&format=webp&width=250&height=350"
    },
    {
        "id": "kalisa",
        "name": "Kalisa",
        "base": {"hp": 75, "atk": 75, "def": 75, "spd": 79},
        "ability": "After 3 turns: +20% ATK and +20% DEF",
        "ability_type": "turn3_atk_def_boost",
        "image": "https://cdn.discordapp.com/attachments/1467048963415871621/1468707381247475723/IMG_6316.webp?ex=6984ffd6&is=6983ae56&hm=811db3ebbd9eab0312b4a5f156a7530e1f0100022a92c7760550986ff5df18e0&"
    },
    {
        "id": "trixi",
        "name": "Trixi",
        "base": {"hp": 70, "atk": 75, "def": 70, "spd": 92},
        "ability": "Every turn: +20% SPD (stacks)",
        "ability_type": "spd_rampage",
        "image": "https://cdn.discordapp.com/attachments/1467048963415871621/1468708225028325530/IMG_6315.webp?ex=698500a0&is=6983af20&hm=9a116c7c9bc971ad9d5a09914423c16e2a241a51d45eec0653de908f7ce8d13b&"
    },
    {
        "id": "sidmi",
        "name": "Sidmi",
        "base": {"hp": 85, "atk": 80, "def": 75, "spd": 65},
        "ability": "After 3 turns: +50% bonus damage",
        "ability_type": "turn3_bonus_damage",
        "image": "https://cdn.discordapp.com/attachments/1467048963415871621/1468709244382744675/IMG_6314.webp?ex=69850193&is=6983b013&hm=53dc82cd67097cff821246e70e179f79e583554e2455556f8c7cb09feda29ef7&"
    },
]

# Catbox URLs for composite battle images (permanent hosting, used only for create_battle_image)
CATBOX_IMAGES = {
    "Kai": "https://files.catbox.moe/xz2vu1.webp",
    "Valkyrie": "https://files.catbox.moe/t3u7dm.webp",
    "Shishilan Pasalan": "https://files.catbox.moe/cydbca.webp",
    "Kasli": "https://files.catbox.moe/54abmy.webp",
    "Emma": "https://files.catbox.moe/5k1lst.webp",
    "Thundia": "https://files.catbox.moe/t6vhbz.webp",
    "Jeanne": "https://files.catbox.moe/kue3er.webp",
    "Balrog": "https://files.catbox.moe/1v24g0.webp",
    "Verbena": "https://files.catbox.moe/ytf7gh.webp",
    "Yukimura": "https://files.catbox.moe/5m8qzb.webp",
    "Ruri": "https://files.catbox.moe/nhi0u0.webp",
    "Lunacia": "https://files.catbox.moe/fpchfy.webp",
    "Bahamut": "https://files.catbox.moe/z870na.webp",
    "Windy": "https://files.catbox.moe/m0osh8.webp",
    "Nobunaga": "https://files.catbox.moe/blue8c.webp",
    "Izanagi": "https://files.catbox.moe/a2c4ci.webp",
    "Luminalia": "https://files.catbox.moe/3n2n9e.webp",
    "Mitama": "https://files.catbox.moe/qj212b.webp",
    "Deale": "https://files.catbox.moe/vzpzkz.webp",
    "Kuu": "https://files.catbox.moe/cmuqok.webp",
    "Himeyuri": "https://files.catbox.moe/3l2cyv.webp",
    "Kalisa": "https://files.catbox.moe/7p18b6.jpeg",
    "Trixi": "https://files.catbox.moe/w845px.jpeg",
    "Sidmi": "https://files.catbox.moe/j1m90q.jpeg",
}

# Boss images on Catbox (permanent hosting for composite battle images)
BOSS_CATBOX_IMAGES = {
    "crazed_cat_phase1": "https://files.catbox.moe/xr9aku.webp",
    "crazed_cat_phase2": "https://files.catbox.moe/cvk5bn.webp",
    "crazed_tank_phase1": "https://files.catbox.moe/htt56w.webp",
    "crazed_tank_phase2": "https://files.catbox.moe/civgc5.png",
}

RARITY_MAX_LEVEL = {
    "Common": 30,
    "Rare": 40,
    "Epic": 50,
    "Legendary": 60,
}
RARITIES = ["Common", "Rare", "Epic", "Legendary"]
RARITY_WEIGHTS = [60, 25, 10, 5]  # weights for random drops

# rating rank for sorting inventory
RARITY_RANK = {"Common": 1, "Rare": 2, "Epic": 3, "Legendary": 4}

# Fuse system constants
FUSE_COSTS = {
    "Common": 5000,      # Common -> Rare
    "Rare": 50000,       # Rare -> Epic
    "Epic": 500000,      # Epic -> Legendary
}

RARITY_UPGRADE = {
    "Common": "Rare",
    "Rare": "Epic",
    "Epic": "Legendary",
}

# Character lookup dictionary for O(1) access
CHARACTERS_BY_ID = {c["id"]: c for c in CHARACTERS}

# ------------------------
# BOSSES (3v1 Boss Battle Mode)
# Each boss can have 1 phase or 2 phases (if it has 2 phases, when defeated, resurrects with full HP and increased stats)
# ------------------------
BOSSES = [
    {
        "id": "crazed_cat",
        "name": "Crazed Cat",
        "phases": [
            {
                "hp": 5000,
                "atk": 160,
                "def": 80,
                "spd": 60,
                "image": "https://cdn.discordapp.com/attachments/815650716730654743/1467647916746211509/IMG_6296.webp?ex=6981cde2&is=69807c62&hm=79e7bcb2a615071592b3c0cc79ecde8594231ae8b205a6ed63ce86a623fbe2c4&"
            },
            {
                "hp": 5000,
                "atk": 200,
                "def": 120,
                "spd": 80,
                "image": "https://cdn.discordapp.com/attachments/815650716730654743/1467647917400784926/IMG_6298.webp?ex=6981cde3&is=69807c63&hm=a4d3098a6f923479d627295d5f929d99301b4b974d1da10b7d62e1eea37205d2&"
            }
        ],
        "rewards": {"gold": 1000, "exp": 500, "guaranteed_rarity": "Epic"}
    },
    {
        "id": "crazed_tank",
        "name": "Crazed Tank",
        "phases": [
            {
                "hp": 9999,
                "atk": 140,
                "def": 100,
                "spd": 60,
                "image": "https://cdn.discordapp.com/attachments/815650716730654743/1467919226970050560/IMG_6301.webp?ex=698221d0&is=6980d050&hm=3b813a9b8b9cf8351ba50e89c5b82db90c71e72f01f95945f1fa1022d5711c9c&"
            },
            {
                "hp": 9999,
                "atk": 180,
                "def": 140,
                "spd": 80,
                "image": "https://cdn.discordapp.com/attachments/815650716730654743/1467919227527888999/IMG_6303.webp?ex=698221d0&is=6980d050&hm=571ad25ae8bbccf3a501a1958a392751baf32d66fa35cfd3160c4b89869cc34f&"
            }
        ],
        "rewards": {"gold": 2500, "exp": 1000, "guaranteed_rarity": "Legendary"}
    }
]

# Boss lookup dictionary
BOSSES_BY_ID = {b["id"]: b for b in BOSSES}

# ------------------------
# DATA (persisted in data.json)
# ------------------------
data_lock = asyncio.Lock()
data = {"users": {}}

def _load_data_from_disk():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return {"users": {}}
    return {"users": {}}

async def load_data():
    global data
    loaded = await asyncio.to_thread(_load_data_from_disk)
    data = loaded if loaded is not None else {"users": {}}

def _save_data_to_disk(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

async def save_data():
    async with data_lock:
        await asyncio.to_thread(_save_data_to_disk, data)

# ------------------------
# HELPERS
# ------------------------
def create_hp_bar(current_hp: int, max_hp: int, length: int = 20) -> str:
    """Create a visual HP bar using block characters."""
    if max_hp <= 0:
        return "░" * length
    filled = int((current_hp / max_hp) * length)
    filled = max(0, min(filled, length))
    bar = "█" * filled + "░" * (length - filled)
    return bar

def ensure_user(user_id: int):
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "stamina": 100,
            "max_stamina": 100,
            "last_stamina_regen": time.time(),
            "gold": 0,
            "inventory": [],
            "last_hourly": 0.0,
            "level": 1,
            "exp": 0,
            "floor": 1,
            "floor_unlocked": 1,
            # user selected card instance id:
            "selected": None,
            # Boss battle team (3 cards):
            "team": [],
            "boss_unlocked": 1,
        }
    # Normalize existing inventory entries if missing fields (basic migration)
    user = data["users"][uid]
    
    # Migrazione: aggiungi max_stamina e last_stamina_regen se non esistono
    if "max_stamina" not in user:
        # max_stamina = 100 + (livello - 1) * 5
        user["max_stamina"] = 100 + (user.get("level", 1) - 1) * 5
    if "last_stamina_regen" not in user:
        user["last_stamina_regen"] = time.time()
    
    # Rigenera stamina automaticamente
    current_time = time.time()
    time_passed = current_time - user.get("last_stamina_regen", current_time)
    intervals_passed = int(time_passed / 300)  # 300 secondi = 5 minuti
    
    if intervals_passed > 0:
        stamina_to_add = intervals_passed * 5
        user["stamina"] = min(user.get("max_stamina", 100), user.get("stamina", 0) + stamina_to_add)
        user["last_stamina_regen"] = current_time - (time_passed % 300)  # reset con remainder
    inv = user.get("inventory", [])
    for c in inv:
        if "level" not in c:
            c.setdefault("level", 1)
        if "exp" not in c:
            c.setdefault("exp", 0)
        if "max_level" not in c:
            c["max_level"] = RARITY_MAX_LEVEL.get(c.get("rarity", "Common"), 30)
        if "base" not in c:
            # try to find base by id
            base = CHARACTERS_BY_ID.get(c.get("id"))
            if base:
                c["base"] = base["base"]
                c.setdefault("ability", base.get("ability", ""))
                c.setdefault("image", base.get("image", ""))
        # MIGRAZIONE: aggiungi ability_type alle carte vecchie
        if "ability_type" not in c:
            base = CHARACTERS_BY_ID.get(c.get("id"))
            if base and "ability_type" in base:
                c["ability_type"] = base["ability_type"]
    
    # MIGRAZIONE: aggiungi team e boss_unlocked per utenti esistenti
    if "team" not in user:
        user["team"] = []
    if "boss_unlocked" not in user:
        user["boss_unlocked"] = 1
    
    return user

def exp_to_next(level: int) -> int:
    return 100 * level

def maybe_level_up_user(user: dict) -> list:
    """Checks and performs user level ups. Returns list of level-up messages."""
    messages = []
    while user.get("exp", 0) >= exp_to_next(user.get("level", 1)):
        need = exp_to_next(user.get("level", 1))
        user["exp"] -= need
        user["level"] = user.get("level", 1) + 1
        # increase max stamina by 5 per level
        bonus = 5
        user["max_stamina"] = user.get("max_stamina", 100) + bonus
        # Also add current stamina (as a level up bonus)
        user["stamina"] = min(user.get("max_stamina"), user.get("stamina", 0) + bonus)
        messages.append(f"⬆️ Level up! Now level {user['level']} (Max stamina: {user['max_stamina']})")
    return messages

def create_card_instance(card_base: dict, rarity: str):
    inst_id = f"{card_base['id']}_{int(time.time()*1000)}_{random.randint(1000,9999)}"
    return {
        "instance_id": inst_id,
        "id": card_base["id"],
        "name": card_base["name"],
        "rarity": rarity,
        "level": 1,
        "exp": 0,
        "max_level": RARITY_MAX_LEVEL[rarity],
        "base": card_base["base"],
        "ability": card_base["ability"],
        "image": card_base.get("image", ""),
    }

def find_card_by_name(name: str):
    # Try direct ID lookup first (most efficient)
    card_id = name.lower().replace(" ", "_")
    if card_id in CHARACTERS_BY_ID:
        return CHARACTERS_BY_ID[card_id]
    # Fallback to name search
    for c in CHARACTERS:
        if c["name"].lower() == name.lower():
            return c
    return None

def card_power(card_inst: dict) -> float:
    # scale base stats by level (e.g., +3% per level)
    lvl = card_inst.get("level", 1)
    mult = 1 + 0.03 * (lvl - 1)
    b = card_inst["base"]
    return (b["hp"] * 0.2 + b["atk"] + b["def"] + b["spd"]) * mult

def sort_inventory(inv: list) -> list:
    """
    Return a new list sorted by rarity (desc), then level (desc),
    then instance timestamp (newer first).
    """
    def inst_time(c):
        parts = str(c.get("instance_id","")).split("_")
        try:
            return int(parts[1])
        except Exception:
            return 0
    return sorted(
        inv,
        key=lambda c: (
            -RARITY_RANK.get(c.get("rarity", "Common"), 1),
            -c.get("level", 1),
            -inst_time(c)
        )
    )

# ------------------------
# TRADING SYSTEM CLASSES AND HELPERS
# ------------------------
# Global dictionary to store active trades
active_trades = {}

class Trade:
    def __init__(self, user1_id, user2_id):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user1_offer = {"gold": 0, "cards": []}  # cards are instance_ids
        self.user2_offer = {"gold": 0, "cards": []}
        self.user1_confirmed = False
        self.user2_confirmed = False
        self.created_at = datetime.now()
        self.timeout_minutes = 10
    
    def is_expired(self):
        return (datetime.now() - self.created_at).total_seconds() > self.timeout_minutes * 60
    
    def get_offer(self, user_id):
        if user_id == self.user1_id:
            return self.user1_offer
        return self.user2_offer
    
    def set_confirmed(self, user_id, value=True):
        if user_id == self.user1_id:
            self.user1_confirmed = value
        else:
            self.user2_confirmed = value
    
    def is_confirmed(self, user_id):
        if user_id == self.user1_id:
            return self.user1_confirmed
        return self.user2_confirmed
    
    def both_confirmed(self):
        return self.user1_confirmed and self.user2_confirmed
    
    def get_other_user(self, user_id):
        if user_id == self.user1_id:
            return self.user2_id
        return self.user1_id
    
    def reset_confirmations(self):
        self.user1_confirmed = False
        self.user2_confirmed = False

class DuelView(View):
    def __init__(self, challenger, challenged, timeout=60):
        super().__init__(timeout=timeout)
        self.challenger = challenger
        self.challenged = challenged
        self.accepted = False
        self.declined = False
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("❌ This duel is not for you!", ephemeral=True)
            return
        self.accepted = True
        self.stop()
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("❌ This duel is not for you!", ephemeral=True)
            return
        self.declined = True
        self.stop()

class TradeView(View):
    def __init__(self, initiator, target, timeout=60):
        super().__init__(timeout=timeout)
        self.initiator = initiator
        self.target = target
        self.accepted = False
        self.declined = False
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ This trade request is not for you!", ephemeral=True)
            return
        self.accepted = True
        self.stop()
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ This trade request is not for you!", ephemeral=True)
            return
        self.declined = True
        self.stop()

def get_user_trade(user_id):
    """Get active trade for a user, or None if no active trade or expired."""
    for key, trade in list(active_trades.items()):
        if trade.is_expired():
            del active_trades[key]
            continue
        if user_id in [trade.user1_id, trade.user2_id]:
            return trade
    return None

# ------------------------
# BOT
# ------------------------
bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS, help_command=None)

@bot.event
async def on_ready():
    await load_data()
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")

# ------------------------
# COMMANDS
# ------------------------
class HelpView(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.current_page = "main"
    
    async def show_page(self, interaction, page):
        self.current_page = page
        embed = self.get_embed(page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    def get_embed(self, page):
        if page == "main":
            embed = discord.Embed(
                title="📚 Testazzo Bot - Help Menu",
                description="Select a category to view commands:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📊 Categories",
                value=(
                    "🎴 **Cards** - Card management & gacha\n"
                    "⚔️ **Battle** - Combat & progression\n"
                    "👥 **Social** - PvP, trading & multiplayer\n"
                    "ℹ️ **Info** - Stats & information\n"
                    "💰 **Economy** - Gold & resources"
                ),
                inline=False
            )
            embed.set_footer(text=f"Prefix: {PREFIX} | Click buttons to navigate")
        
        elif page == "cards":
            embed = discord.Embed(title="🎴 Card Commands", color=discord.Color.green())
            embed.add_field(
                name="Commands",
                value=(
                    f"`{PREFIX}drop` (`{PREFIX}d`) - Get a random card\n"
                    f"`{PREFIX}inventory` (`{PREFIX}inv`) - View your cards\n"
                    f"`{PREFIX}select <n>` - Select a card for battle\n"
                    f"`{PREFIX}enhance <source> <target>` - Power up cards\n"
                    f"`{PREFIX}fuse <card1> <card2> ...` - Fuse cards together\n"
                    f"`{PREFIX}dex` - View all available cards"
                ),
                inline=False
            )
            embed.add_field(
                name="Filters",
                value=f"`{PREFIX}inv -r <rarity>` - Filter by rarity\n`{PREFIX}inv -n <name>` - Filter by name",
                inline=False
            )
        
        elif page == "battle":
            embed = discord.Embed(title="⚔️ Battle Commands", color=discord.Color.red())
            embed.add_field(
                name="Floor Battles",
                value=(
                    f"`{PREFIX}battle` (`{PREFIX}bt`, `{PREFIX}b`) - Start a battle\n"
                    f"`{PREFIX}floor [next|n]` - Manage floors\n"
                    f"`{PREFIX}farm` - Auto-farm resources"
                ),
                inline=False
            )
            embed.add_field(
                name="👹 Boss Battles (3v1)",
                value=(
                    f"`{PREFIX}team` - View your team\n"
                    f"`{PREFIX}team set 1 2 3` - Set team (3 cards)\n"
                    f"`{PREFIX}team clear` - Clear team\n"
                    f"`{PREFIX}boss` - View available bosses\n"
                    f"`{PREFIX}boss <n>` - Fight boss #n"
                ),
                inline=False
            )
        
        elif page == "social":
            embed = discord.Embed(title="👥 Social Commands", color=discord.Color.purple())
            embed.add_field(
                name="Commands",
                value=(
                    f"`{PREFIX}duel <@user>` - Challenge another player\n"
                    f"`{PREFIX}trade <@user>` - Trade cards with players\n"
                    f"`{PREFIX}give <@user> <gold>` - Gift gold to players"
                ),
                inline=False
            )
        
        elif page == "info":
            embed = discord.Embed(title="ℹ️ Info Commands", color=discord.Color.orange())
            embed.add_field(
                name="Commands",
                value=(
                    f"`{PREFIX}profile` (`{PREFIX}p`) - View your profile\n"
                    f"`{PREFIX}info <n>` - Detailed card info\n"
                    f"`{PREFIX}cinfo <name>` - View card base stats\n"
                    f"`{PREFIX}dex` - Browse all cards\n"
                    f"`{PREFIX}level [@user]` - Check user level"
                ),
                inline=False
            )
        
        elif page == "economy":
            embed = discord.Embed(title="💰 Economy Commands", color=discord.Color.gold())
            embed.add_field(
                name="Commands",
                value=(
                    f"`{PREFIX}gold` (`{PREFIX}g`) - Check your gold\n"
                    f"`{PREFIX}stamina` (`{PREFIX}stam`) - Check stamina\n"
                    f"`{PREFIX}hourly` - Claim hourly reward"
                ),
                inline=False
            )
        
        return embed
    
    @discord.ui.button(label="🎴 Cards", style=discord.ButtonStyle.green, row=0)
    async def cards_button(self, interaction: discord.Interaction, button: Button):
        await self.show_page(interaction, "cards")
    
    @discord.ui.button(label="⚔️ Battle", style=discord.ButtonStyle.red, row=0)
    async def battle_button(self, interaction: discord.Interaction, button: Button):
        await self.show_page(interaction, "battle")
    
    @discord.ui.button(label="👥 Social", style=discord.ButtonStyle.blurple, row=0)
    async def social_button(self, interaction: discord.Interaction, button: Button):
        await self.show_page(interaction, "social")
    
    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.gray, row=1)
    async def info_button(self, interaction: discord.Interaction, button: Button):
        await self.show_page(interaction, "info")
    
    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.gray, row=1)
    async def economy_button(self, interaction: discord.Interaction, button: Button):
        await self.show_page(interaction, "economy")
    
    @discord.ui.button(label="🏠 Main Menu", style=discord.ButtonStyle.gray, row=1)
    async def main_button(self, interaction: discord.Interaction, button: Button):
        await self.show_page(interaction, "main")

@bot.command(name="help")
async def help_cmd(ctx):
    """Show help menu with interactive categories"""
    view = HelpView(ctx)
    embed = view.get_embed("main")
    await ctx.send(embed=embed, view=view)

@bot.command(name="profile", aliases=["p"])
async def profile(ctx):
    """Show user profile: stamina, gold, level and cards."""
    user = ensure_user(ctx.author.id)
    
    # Calcola tempo alla prossima rigenerazione
    current_time = time.time()
    time_since_regen = current_time - user.get("last_stamina_regen", current_time)
    time_to_next = 300 - (time_since_regen % 300)  # 300 secondi = 5 minuti
    minutes = int(time_to_next // 60)
    seconds = int(time_to_next % 60)
    
    stamina_info = f"⚡ Stamina: {user['stamina']}/{user.get('max_stamina', 100)}"
    if user['stamina'] < user.get('max_stamina', 100):
        stamina_info += f" (Next +5 in {minutes}m {seconds}s)"
    
    await ctx.send(
        f"👤 **Profile — {ctx.author.name}**\n"
        f"{stamina_info}\n"
        f"💰 Gold: {user['gold']}\n"
        f"🎴 Cards owned: {len(user['inventory'])}\n"
        f"⭐ Level: {user.get('level',1)} | EXP: {user.get('exp',0)}/{exp_to_next(user.get('level',1))}\n"
        f"🗼 Floor: {user.get('floor',1)} (unlocked: {user.get('floor_unlocked',1)})"
    )

@bot.command(name="stamina", aliases=["stam"])
async def stamina_cmd(ctx):
    """Show current stamina."""
    user = ensure_user(ctx.author.id)
    
    # Calcola tempo alla prossima rigenerazione
    current_time = time.time()
    time_since_regen = current_time - user.get("last_stamina_regen", current_time)
    time_to_next = 300 - (time_since_regen % 300)
    minutes = int(time_to_next // 60)
    seconds = int(time_to_next % 60)
    
    stamina_msg = f"⚡ Current stamina: **{user['stamina']}/{user.get('max_stamina', 100)}**"
    if user['stamina'] < user.get('max_stamina', 100):
        stamina_msg += f"\n🕐 Next +5 in **{minutes}m {seconds}s**"
    
    await ctx.send(stamina_msg)

@bot.command(name="gold", aliases=["g"])
async def gold_cmd(ctx):
    """Show current gold."""
    user = ensure_user(ctx.author.id)
    await ctx.send(f"💰 Gold: **{user['gold']}**")

class InventoryView(View):
    def __init__(self, ctx, cards, page=1, filter_rarity=None, filter_name=None, full_inventory=None):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.cards = cards  # Carte filtrate
        self.full_inventory = full_inventory  # Inventario completo ordinato
        self.page = page
        self.per_page = 10
        self.filter_rarity = filter_rarity
        self.filter_name = filter_name
        self.total_pages = max(1, (len(cards) + self.per_page - 1) // self.per_page)
        
        # Disable buttons if on first/last page
        if self.page <= 1:
            self.prev_button.disabled = True
        if self.page >= self.total_pages:
            self.next_button.disabled = True
    
    def get_page_embed(self):
        user = ensure_user(self.ctx.author.id)
        start_idx = (self.page - 1) * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.cards))
        
        embed = discord.Embed(
            title=f"🎴 {self.ctx.author.name}'s Inventory",
            color=discord.Color.blue()
        )
        
        # Add filter info if active
        filters = []
        if self.filter_rarity:
            filters.append(f"Rarity: {self.filter_rarity}")
        if self.filter_name:
            filters.append(f"Name: {self.filter_name}")
        if filters:
            embed.description = f"**Filters:** {', '.join(filters)}"
        
        # List cards
        card_list = []
        for c in self.cards[start_idx:end_idx]:
            # Trova il VERO indice nell'inventario completo
            real_index = None
            if self.full_inventory:
                for i, full_card in enumerate(self.full_inventory, start=1):
                    if full_card.get("instance_id") == c.get("instance_id"):
                        real_index = i
                        break
            
            # Usa l'indice reale se disponibile, altrimenti usa indice filtrato
            display_index = real_index if real_index else "?"
            
            name = c.get("name", "Unknown")
            rarity = c.get("rarity", "")
            lvl = c.get("level", 1)
            sel_mark = "🔹" if user.get("selected") == c.get("instance_id") else ""
            card_list.append(f"`{display_index}.` **{name}** `{rarity}` Lv.{lvl} {sel_mark}")
        
        embed.add_field(
            name=f"Cards ({start_idx + 1}-{end_idx} of {len(self.cards)})",
            value="\n".join(card_list) if card_list else "No cards found",
            inline=False
        )
        
        if filters:
            embed.set_footer(text=f"Page {self.page}/{self.total_pages} | Numbers show position in full inventory | Use -select <n>")
        else:
            embed.set_footer(text=f"Page {self.page}/{self.total_pages} | Use -select <n> to select a card")
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.page = max(1, self.page - 1)
        
        # Update button states
        self.prev_button.disabled = (self.page <= 1)
        self.next_button.disabled = (self.page >= self.total_pages)
        
        embed = self.get_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.page = min(self.total_pages, self.page + 1)
        
        # Update button states
        self.prev_button.disabled = (self.page <= 1)
        self.next_button.disabled = (self.page >= self.total_pages)
        
        embed = self.get_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)

@bot.command(name="inventory", aliases=["inv"])
async def inventory_cmd(ctx, *args):
    """List your cards. Usage: -inv [-r rarity] [-n name] [page]"""
    user = ensure_user(ctx.author.id)
    inv = user["inventory"]
    
    if not inv:
        await ctx.send("🎴 Your inventory is empty.")
        return
    
    # Parse arguments for filters
    filter_rarity = None
    filter_name = None
    page = 1
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-r" and i + 1 < len(args):
            # Capture all args until next flag or end
            values = []
            j = i + 1
            while j < len(args) and not args[j].startswith('-'):
                values.append(args[j])
                j += 1
            filter_rarity = ' '.join(values)
            i = j
        elif arg == "-n" and i + 1 < len(args):
            # Capture all args until next flag or end
            values = []
            j = i + 1
            while j < len(args) and not args[j].startswith('-'):
                values.append(args[j])
                j += 1
            filter_name = ' '.join(values)
            i = j
        elif arg.isdigit():
            page = int(arg)
            i += 1
        else:
            i += 1
    
    # Ordina PRIMA l'inventario completo
    full_sorted_inv = sort_inventory(inv)
    
    # Poi applica i filtri
    filtered_inv = full_sorted_inv
    if filter_rarity:
        # Split by comma and strip whitespace
        rarities = [r.strip().capitalize() for r in filter_rarity.split(',')]
        filtered_inv = [c for c in filtered_inv if c.get("rarity", "").lower() in [r.lower() for r in rarities]]
    if filter_name:
        # Split by comma and strip whitespace
        names = [n.strip().lower() for n in filter_name.split(',')]
        filtered_inv = [c for c in filtered_inv if any(name in c.get("name", "").lower() for name in names)]
    
    if not filtered_inv:
        await ctx.send("🎴 No cards match your filters.")
        return
    
    # Passa ANCHE l'inventario completo alla view
    view = InventoryView(ctx, filtered_inv, page, filter_rarity, filter_name, full_inventory=full_sorted_inv)
    embed = view.get_page_embed()
    await ctx.send(embed=embed, view=view)

@bot.command(name="select")
async def select_cmd(ctx, index: int):
    """Select a card to use in floors by inventory index (sorted by rarity+level). Usage: -select <index>"""
    user = ensure_user(ctx.author.id)
    inv = user["inventory"]
    if not inv:
        await ctx.send("Your inventory is empty.")
        return
    sorted_inv = sort_inventory(inv)
    if index < 1 or index > len(sorted_inv):
        await ctx.send(f"Invalid index (1-{len(sorted_inv)}).")
        return
    card = sorted_inv[index - 1]
    user["selected"] = card["instance_id"]
    await save_data()
    await ctx.send(f"Selected card `{card['name']}` (ID: `{card['instance_id']}`).")

@bot.command(name="hourly")
async def hourly_cmd(ctx):
    """Claim a random stamina reward every hour (5,10,15)."""
    user = ensure_user(ctx.author.id)
    now = time.time()
    elapsed = now - user.get("last_hourly", 0.0)
    cooldown = 3600
    if elapsed < cooldown:
        remaining = int((cooldown - elapsed) / 60)
        remaining_secs = int(cooldown - elapsed)
        minutes = remaining
        seconds = remaining_secs - minutes * 60
        await ctx.send(f"⏳ Hourly not ready. Try again in {minutes} minutes and {seconds} seconds.")
        return
    amount = random.choice([5, 10, 15])
    user["last_hourly"] = now
    user["stamina"] = user.get("stamina", 0) + amount
    await save_data()
    await ctx.send(f"🎁 Hourly claimed! +{amount} stamina.")

@bot.command(name="farm")
@commands.cooldown(1, 900, commands.BucketType.user)
async def farm_cmd(ctx):
    """Farm to get gold (15-minute cooldown)."""
    user = ensure_user(ctx.author.id)
    amount = random.randint(100, 1000)
    user["gold"] = user.get("gold", 0) + amount
    await save_data()
    await ctx.send(f"⛏️ You gained **{amount}** gold!")

@bot.command(name="drop", aliases=["d"])
@commands.cooldown(1, 5, commands.BucketType.user)
async def drop_cmd(ctx):
    """Get a random card (15-minute cooldown), does not consume stamina."""
    user = ensure_user(ctx.author.id)
    base = deepcopy(random.choice(CHARACTERS))
    rarity = random.choices(RARITIES, weights=RARITY_WEIGHTS, k=1)[0]
    card_instance = create_card_instance(base, rarity)
    user["inventory"].append(card_instance)
    await save_data()
    await ctx.send(
        f"🎉 **New card obtained!**\n"
        f"🧙 {card_instance['name']} ({card_instance['rarity']}) Lv{card_instance['level']}\n"
        f"ID: `{card_instance['instance_id']}`\n"
        f"✨ Ability: {card_instance['ability']}"
    )

@bot.command(name="cinfo")
async def cinfo_cmd(ctx, *, name: str):
    """Show the base information of a card (base stats). Usage: -cinfo <card name>"""
    base = find_card_by_name(name)
    if not base:
        await ctx.send("Card not found.")
        return
    stats = base["base"]

    embed = discord.Embed(
        title=f"{base['name']} — Base stats (Common Lv1)",
        description=f"Ability: {base['ability']}",
        color=discord.Color.blue()
    )
    embed.add_field(name="HP", value=str(stats['hp']), inline=True)
    embed.add_field(name="ATK", value=str(stats['atk']), inline=True)
    embed.add_field(name="DEF", value=str(stats['def']), inline=True)
    embed.add_field(name="SPD", value=str(stats['spd']), inline=True)

    image_url = base.get("image", "")
    if image_url:
        # put image at the bottom of the embed
        embed.set_image(url=image_url)

    await ctx.send(embed=embed)

class DexView(View):
    def __init__(self, ctx, cards, page=1, filter_rarity=None, filter_name=None):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.cards = cards
        self.page = page
        self.per_page = 8
        self.filter_rarity = filter_rarity
        self.filter_name = filter_name
        self.total_pages = max(1, (len(cards) + self.per_page - 1) // self.per_page)
        
        if self.page <= 1:
            self.prev_button.disabled = True
        if self.page >= self.total_pages:
            self.next_button.disabled = True
    
    def get_page_embed(self):
        start_idx = (self.page - 1) * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.cards))
        
        embed = discord.Embed(
            title="📖 Card Dex - All Available Cards",
            color=discord.Color.purple()
        )
        
        # Add filter info
        filters = []
        if self.filter_rarity:
            filters.append(f"Rarity: {self.filter_rarity}")
        if self.filter_name:
            filters.append(f"Name: {self.filter_name}")
        if filters:
            embed.description = f"**Filters:** {', '.join(filters)}"
        
        # List cards
        for i, char in enumerate(self.cards[start_idx:end_idx], start=start_idx + 1):
            stats = char["base"]
            stat_line = f"HP:{stats['hp']} ATK:{stats['atk']} DEF:{stats['def']} SPD:{stats['spd']}"
            embed.add_field(
                name=f"{i}. {char['name']}",
                value=f"`{stat_line}`",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.page}/{self.total_pages} | Total: {len(self.cards)} cards\nUse -cinfo <name> for details")
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.page = max(1, self.page - 1)
        self.prev_button.disabled = (self.page <= 1)
        self.next_button.disabled = (self.page >= self.total_pages)
        embed = self.get_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.page = min(self.total_pages, self.page + 1)
        self.prev_button.disabled = (self.page <= 1)
        self.next_button.disabled = (self.page >= self.total_pages)
        embed = self.get_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)

@bot.command(name="dex")
async def dex_cmd(ctx, *args):
    """Browse all available cards. Usage: -dex [-r rarity] [-n name]"""
    # Parse arguments
    filter_rarity = None
    filter_name = None
    page = 1
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-r" and i + 1 < len(args):
            # Capture all args until next flag or end
            values = []
            j = i + 1
            while j < len(args) and not args[j].startswith('-'):
                values.append(args[j])
                j += 1
            filter_rarity = ' '.join(values)
            i = j
        elif arg == "-n" and i + 1 < len(args):
            # Capture all args until next flag or end
            values = []
            j = i + 1
            while j < len(args) and not args[j].startswith('-'):
                values.append(args[j])
                j += 1
            filter_name = ' '.join(values)
            i = j
        elif arg.isdigit():
            page = int(arg)
            i += 1
        else:
            i += 1
    
    # Apply filters
    filtered_chars = CHARACTERS.copy()
    if filter_name:
        # Split by comma and strip whitespace
        names = [n.strip().lower() for n in filter_name.split(',')]
        filtered_chars = [c for c in filtered_chars if any(name in c["name"].lower() for name in names)]
    
    if not filtered_chars:
        await ctx.send("📖 No cards match your filters.")
        return
    
    view = DexView(ctx, filtered_chars, page, filter_rarity, filter_name)
    embed = view.get_page_embed()
    await ctx.send(embed=embed, view=view)

@bot.command(name="info")
async def info_cmd(ctx, index: int):
    """Show detailed stats of your card by inventory index. Usage: -info <index>"""
    user = ensure_user(ctx.author.id)
    inv = user["inventory"]
    if not inv:
        await ctx.send("Your inventory is empty.")
        return
    sorted_inv = sort_inventory(inv)
    if index < 1 or index > len(sorted_inv):
        await ctx.send(f"Invalid index (1-{len(sorted_inv)}).")
        return
    
    card = sorted_inv[index - 1]
    lvl = card.get("level", 1)
    base = card["base"]
    
    # Calculate actual stats with level scaling
    mult = 1 + 0.03 * (lvl - 1)
    hp = int(base["hp"] * mult)
    atk = int(base["atk"] * mult)
    defense = int(base["def"] * mult)
    spd = int(base["spd"] * mult)
    
    embed = discord.Embed(
        title=f"{card['name']} — {card['rarity']} Lv{lvl}",
        description=f"**Ability:** {card.get('ability', 'None')}",
        color=discord.Color.gold()
    )
    embed.add_field(name="HP", value=str(hp), inline=True)
    embed.add_field(name="ATK", value=str(atk), inline=True)
    embed.add_field(name="DEF", value=str(defense), inline=True)
    embed.add_field(name="SPD", value=str(spd), inline=True)
    embed.add_field(name="EXP", value=f"{card.get('exp', 0)}/{100 * lvl}", inline=True)
    embed.add_field(name="Max Level", value=str(card.get('max_level', 30)), inline=True)
    embed.set_footer(text=f"ID: {card.get('instance_id', 'N/A')}")
    
    if card.get("image"):
        embed.set_image(url=card["image"])
    
    await ctx.send(embed=embed)

@bot.command(name="enhance")
async def enhance_cmd(ctx, target: str, *args):
    """Enhance a card's level using gold. Usage: -enhance <index> [-l <target_level>]
    Cost: 100 gold per level. If -l is omitted, enhances to max level."""
    user = ensure_user(ctx.author.id)
    inv = user["inventory"]
    
    # Find target card
    target_card = None
    if target.isdigit():
        idx = int(target) - 1
        sorted_inv = sort_inventory(inv)
        if 0 <= idx < len(sorted_inv):
            target_card = sorted_inv[idx]
    else:
        for c in inv:
            if c["instance_id"] == target:
                target_card = c
                break
    
    if not target_card:
        await ctx.send("Target card not found in inventory.")
        return
    
    current_level = target_card.get("level", 1)
    max_level = target_card.get("max_level", 30)
    
    if current_level >= max_level:
        await ctx.send(f"This card is already at max level ({max_level}).")
        return
    
    # Parse -l flag for target level
    target_level = max_level  # default to max
    it = iter(args)
    for a in it:
        if a == "-l":
            try:
                target_level = int(next(it))
            except (StopIteration, ValueError):
                await ctx.send("Invalid level specified.")
                return
    
    # Validate target level
    if target_level <= current_level:
        await ctx.send(f"Target level must be higher than current level ({current_level}).")
        return
    if target_level > max_level:
        target_level = max_level
    
    # Calculate cost: 100 gold per level
    levels_to_gain = target_level - current_level
    cost = levels_to_gain * 100
    
    # Check gold
    if user.get("gold", 0) < cost:
        await ctx.send(f"❌ Not enough gold! You need **{cost}** gold but you have **{user.get('gold', 0)}** gold.")
        return
    
    # Apply enhancement
    user["gold"] -= cost
    target_card["level"] = target_level
    target_card["exp"] = 0  # reset exp when leveling up via gold
    
    await save_data()
    await ctx.send(f"✨ **Enhancement complete!**\n{target_card['name']} is now **Lv{target_level}**!\n💰 Cost: {cost} gold")

@bot.command(name="fuse")
async def fuse_cmd(ctx, card1_idx: int, card2_idx: int):
    """Fuse two identical max-level cards to increase rarity. Usage: -fuse <index1> <index2>
    Both cards must have the same name, same rarity, and be at max level.
    Cost: Common->Rare: 1000g | Rare->Epic: 10000g | Epic->Legendary: 100000g"""
    user = ensure_user(ctx.author.id)
    inv = user["inventory"]
    
    if not inv:
        await ctx.send("Your inventory is empty.")
        return
    
    sorted_inv = sort_inventory(inv)
    
    # Validate indices
    if card1_idx < 1 or card1_idx > len(sorted_inv):
        await ctx.send(f"Invalid first card index (1-{len(sorted_inv)}).")
        return
    if card2_idx < 1 or card2_idx > len(sorted_inv):
        await ctx.send(f"Invalid second card index (1-{len(sorted_inv)}).")
        return
    if card1_idx == card2_idx:
        await ctx.send("You must select two different cards.")
        return
    
    card1 = sorted_inv[card1_idx - 1]
    card2 = sorted_inv[card2_idx - 1]
    
    # Check same name
    if card1.get("name") != card2.get("name"):
        await ctx.send(f"❌ Cards must have the same name!\n`{card1.get('name')}` ≠ `{card2.get('name')}`")
        return
    
    # Check same rarity
    if card1.get("rarity") != card2.get("rarity"):
        await ctx.send(f"❌ Cards must have the same rarity!\n`{card1.get('rarity')}` ≠ `{card2.get('rarity')}`")
        return
    
    rarity = card1.get("rarity")
    
    # Check if can be upgraded
    if rarity not in RARITY_UPGRADE:
        await ctx.send("❌ Legendary cards cannot be fused further!")
        return
    
    # Check both at max level
    max_lvl1 = card1.get("max_level", 30)
    max_lvl2 = card2.get("max_level", 30)
    if card1.get("level", 1) < max_lvl1:
        await ctx.send(f"❌ First card must be at max level ({max_lvl1})! Currently Lv{card1.get('level', 1)}.")
        return
    if card2.get("level", 1) < max_lvl2:
        await ctx.send(f"❌ Second card must be at max level ({max_lvl2})! Currently Lv{card2.get('level', 1)}.")
        return
    
    # Check gold
    cost = FUSE_COSTS[rarity]
    if user.get("gold", 0) < cost:
        await ctx.send(f"❌ Not enough gold! You need **{cost}** gold but you have **{user.get('gold', 0)}** gold.")
        return
    
    # Perform fusion
    new_rarity = RARITY_UPGRADE[rarity]
    new_max_level = RARITY_MAX_LEVEL[new_rarity]
    
    # Create new card (level 1, new rarity)
    # Find base character data
    base_char = CHARACTERS_BY_ID.get(card1.get("id"))
    
    if not base_char:
        await ctx.send("❌ Error: Could not find base character data.")
        return
    
    new_card = create_card_instance(base_char, new_rarity)
    
    # Remove gold and old cards
    user["gold"] -= cost
    inv.remove(card1)
    inv.remove(card2)
    
    # Add new card
    inv.append(new_card)
    
    # If selected card was fused, clear selection
    if user.get("selected") in [card1.get("instance_id"), card2.get("instance_id")]:
        user["selected"] = None
    
    await save_data()
    await ctx.send(
        f"🔮 **Fusion successful!**\n"
        f"2x {card1.get('name')} ({rarity}) → **{new_card['name']} ({new_rarity}) Lv1**\n"
        f"💰 Cost: {cost} gold\n"
        f"New card ID: `{new_card['instance_id']}`"
    )

@bot.command(name="level")
async def level_cmd(ctx, member: discord.Member = None):
    """Show the user's level."""
    target = member or ctx.author
    user = ensure_user(target.id)
    await ctx.send(f"{target.name} — Level {user.get('level',1)} | EXP: {user.get('exp',0)}/{exp_to_next(user.get('level',1))}")

# ------------------------
# BATTLE (animated embed)
# ------------------------
ENEMY_IMAGE = "https://cdn.discordapp.com/attachments/815650716730654743/1466823551628869786/IMG_6214.jpg?ex=697e2562&is=697cd3e2&hm=a30d2cdc6f5f819ca69f575fc2ae0e24719c085230e4521f5f07c6d64982d899"

# Enemy images for Location 1 floors (1-27)
FLOOR_IMAGES = [
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539861048135812/IMG_6252.webp?ex=6980c080&is=697f6f00&hm=5e5b7a0a4b78fbf0b4482814d6279459bf0fc02fe3a2a7c6f8985bbb0c908db1&",  # Floor 1
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539861450785003/IMG_6253.webp?ex=6980c080&is=697f6f00&hm=0d7c37ba0469c815fb21dd8d41d8d40028d7618c777f013a03ec922010fc794f&",  # Floor 2
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539862101168331/IMG_6256.webp?ex=6980c080&is=697f6f00&hm=3479dcef726fd43888819bb745510a60b1648d91ebadb92ddb76fa9d62972e5f&",  # Floor 3
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539862591770769/IMG_6254.webp?ex=6980c080&is=697f6f00&hm=4ed691a0aeeb56b3d434fa4227ed8b9a19e6acf8702c7ce294bba58dc8ca7ed3&",  # Floor 4
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539862897824016/IMG_6258.webp?ex=6980c080&is=697f6f00&hm=bb0f483f6eb7a29e33757ad84b4a0b8699eb46b77ebc875d5560984c38e35f6d&",  # Floor 5
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539863313317918/IMG_6259.webp?ex=6980c080&is=697f6f00&hm=5769da1af047671f8d492011a5dd2c3b4138d2dd2c79d112f33868c34624abf5&",  # Floor 6
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539863690547425/IMG_6260.webp?ex=6980c081&is=697f6f01&hm=e051857058a3555a9704d34258f808f3d90f49962c2d0ef5af80c93af5f4ddc8&",  # Floor 7
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539864076419307/IMG_6261.webp?ex=6980c081&is=697f6f01&hm=feb4fce1cf763b5a892fdaa6ea5257ac2ae2f4676d5de44433f0da8730a02768&",  # Floor 8
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539864349053060/IMG_6262.webp?ex=6980c081&is=697f6f01&hm=b234c5eb3e2d724b8512d413f78bb0f01dbb5d6cb63c1757b92fba45c8c0aa00&",  # Floor 9
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539974915096810/IMG_6263.webp?ex=6980c09b&is=697f6f1b&hm=1609c23948f2cabc36585ce86685c94f11055abcf6fa0fe0026e69a27d233ec6&",  # Floor 10
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539975422742829/IMG_6264.webp?ex=6980c09b&is=697f6f1b&hm=6e8bd62c6fd3d512840245921143e1da440c3b66c267772555d52b54cd6acc89&",  # Floor 11
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539975745573200/IMG_6265.webp?ex=6980c09b&is=697f6f1b&hm=510c7e68a8e71ce78c46b70bf47e81e2883025f27b0a604b844c0ebbbf4f5f27&",  # Floor 12
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539976148221993/IMG_6266.webp?ex=6980c09b&is=697f6f1b&hm=c794c186be8947dc58611cf930ec3a098a85ee435c28471b2574566803e61634&",  # Floor 13
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539976798474321/IMG_6267.webp?ex=6980c09c&is=697f6f1c&hm=4cf1e2c0a2e190741a45ec31661e5dbf1cfb2f14b81d8644480bf695ba6d47b0&",  # Floor 14
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539977553318010/IMG_6268.webp?ex=6980c09c&is=697f6f1c&hm=1b2577da59afc169fe7f5970dc2a5280bffc8123f0b6818c771f08fb3f82430b&",  # Floor 15
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539978819993701/IMG_6269.webp?ex=6980c09c&is=697f6f1c&hm=b9b74995479f50c5901047acb08b1db992ddb25f1b7020546ef8d329960a2747&",  # Floor 16
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539979201810613/IMG_6270.webp?ex=6980c09c&is=697f6f1c&hm=10e7c09d288baf06ea0bc89bd1cd2b6878f8aa4610a830b0c57662db5105d213&",  # Floor 17
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539979650727966/IMG_6271.webp?ex=6980c09c&is=697f6f1c&hm=98897064e919a7fe01cf3efac081f9baf7da2dd9101d9bdfc2c028b8adabb5c0&",  # Floor 18
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539999355568315/IMG_6272.webp?ex=6980c0a1&is=697f6f21&hm=b8230cc76677b96db3aba4e95fbc59b5f2c3ee43645dd513add71446446c02ee&",  # Floor 19
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539999636324465/IMG_6273.webp?ex=6980c0a1&is=697f6f21&hm=45dda5bdc90cb90bb21fc378269476dddc721db6f976ce5ae0249c5522ffedf1&",  # Floor 20
    "https://cdn.discordapp.com/attachments/815650716730654743/1467539999909216348/IMG_6274.webp?ex=6980c0a1&is=697f6f21&hm=96bbdc07b343cb678b5bba760813233dc5a62932e9c13e26a59aa3b7a122fa30&",  # Floor 21
    "https://cdn.discordapp.com/attachments/815650716730654743/1467540000202686728/IMG_6275.webp?ex=6980c0a1&is=697f6f21&hm=c9d62bf110619152b274dd89a3b181448104a6218434219dfd9b621646496110&",  # Floor 22
    "https://cdn.discordapp.com/attachments/815650716730654743/1467540000592629822/IMG_6276.webp?ex=6980c0a1&is=697f6f21&hm=1e8953a60e7fd9bbcb3b6092e7ac38a95709077eb33276d40bccbc7d986a0765&",  # Floor 23
    "https://cdn.discordapp.com/attachments/815650716730654743/1467540000823574568/IMG_6277.webp?ex=6980c0a1&is=697f6f21&hm=a701943324ff2e6b99d145026b667837e9798566947e5f43aacf35380cd6e6c4&",  # Floor 24
    "https://cdn.discordapp.com/attachments/815650716730654743/1467540001184153744/IMG_6278.webp?ex=6980c0a1&is=697f6f21&hm=183b1ce0a67bc4a527e2e9a4be5ea1e0210e4bfef301bc2c2f207c5e4a56de4b&",  # Floor 25
    "https://cdn.discordapp.com/attachments/815650716730654743/1467540001452462242/IMG_6279.webp?ex=6980c0a1&is=697f6f21&hm=6ea6e5c66432cddfc97a2b081347e834a053bdc953be410d84af50cbe0f45387&",  # Floor 26
    "https://cdn.discordapp.com/attachments/815650716730654743/1467540001666502737/IMG_6280.webp?ex=6980c0a1&is=697f6f21&hm=e8c664f9f2b9b50997bca2cb833a903fe5e4f76ee6bce3691169f098a7f03270&",  # Floor 27
]

# Location 1 (Loc 1): 27 floors balanced for Legendary Lv60 cards
# Future: Additional locations will be added with their own floor systems
def make_enemy_for_floor(floor: int) -> dict:
    """Return an enemy dict with stats scaled by floor (1-27 for Loc 1)."""
    base_hp = 120 + (floor - 1) * 72
    base_atk = 25 + int((floor - 1) * 8.7)
    base_def = 10 + int((floor - 1) * 5.4)
    base_spd = 20 + int((floor - 1) * 3.1)
    
    # Get floor-specific image (index 0 = floor 1)
    image_index = min(floor - 1, len(FLOOR_IMAGES) - 1)
    image = FLOOR_IMAGES[image_index] if FLOOR_IMAGES else ENEMY_IMAGE
    
    return {"name": f"Floor {floor} Enemy", "hp": base_hp, "atk": base_atk, "def": base_def, "spd": base_spd, "image": image}

def damage_formula(attacker_atk: int, defender_def: int) -> int:
    """Simple damage formula."""
    dmg = max(1, int(attacker_atk - defender_def * 0.5))
    return dmg

def apply_ability(ability_type, attacker, defender, flags, turn, mode="direct", is_team_battle=False):
    """
    Apply ability effects based on ability_type.
    
    Args:
        ability_type: The type of ability (e.g., "first_turn_def", "lifesteal", etc.)
        attacker: Dict with attacker stats (hp, atk, def, spd, hp_max, atk_base, def_base, spd_base, name, etc.)
        defender: Dict with defender stats
        flags: Dict with ability state flags (buff_applied, lifesteal_active, etc.)
        turn: Current turn number (round number)
        mode: "direct" for run_battle (modifies stats directly), "bonus" for run_boss_battle (returns bonuses)
        is_team_battle: True for boss battles (team mode), False for regular battles
    
    Returns:
        dict with:
            - "messages": List of messages to display
            - "bonuses": Dict with atk_bonus, def_bonus, spd_bonus (for mode="bonus")
    """
    messages = []
    bonuses = {"atk": 0.0, "def": 0.0, "spd": 0.0}
    
    # === FIRST-TURN ABILITIES ===
    if ability_type == "first_turn_def":  # Kai - First turn +100% DEF
        if turn == 1 and not flags.get("buff_applied"):
            if mode == "bonus":
                bonuses["def"] += 1.0
            else:
                attacker["def"] = int(attacker["def_base"] * 2)
                flags["buff_applied"] = True
    
    elif ability_type == "first_turn_spd":  # Valkyrie - First turn +100% SPD
        if turn == 1 and not flags.get("buff_applied"):
            if mode == "bonus":
                bonuses["spd"] += 1.0
            else:
                attacker["spd"] = int(attacker["spd_base"] * 2)
                flags["buff_applied"] = True
    
    elif ability_type == "first_turn_atk":  # Shishilan - First turn +50% ATK
        if turn == 1 and not flags.get("buff_applied"):
            if mode == "bonus":
                bonuses["atk"] += 0.5
            else:
                attacker["atk"] = int(attacker["atk_base"] * 1.5)
                flags["buff_applied"] = True
    
    # === 3-TURN BUFFS ===
    elif ability_type == "def_boost_3turns":  # Ruri - 3 turns +50% DEF
        if flags.get("ruri_turns", 0) > 0:
            if mode == "bonus":
                bonuses["def"] += 0.5
            # For direct mode, this is applied at initialization
    
    elif ability_type == "spd_boost_3turns":  # Luminalia - 3 turns +50% SPD
        if flags.get("luminalia_turns", 0) > 0:
            if mode == "bonus":
                bonuses["spd"] += 0.5
            # For direct mode, this is applied at initialization
    
    # === FIRST-ATTACK ABILITIES ===
    elif ability_type == "first_attack_heal":  # Mitama - First attack: Heals 50% max HP
        if turn == 1 and not flags.get("mitama_healed"):
            heal = int(attacker["hp_max"] * 0.5)
            attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal)
            flags["mitama_healed"] = True
            if is_team_battle:
                messages.append(f"💖 **Mitama's blessing!** Team heals {heal} HP")
            else:
                messages.append(f"✨ **{attacker['name']}'s divine blessing!** Heals {heal} HP")
    
    elif ability_type == "first_attack_spd":  # Deale - First attack: +50% SPD
        if turn == 1 and not flags.get("deale_boosted"):
            if mode == "bonus":
                bonuses["spd"] += 0.5
            else:
                attacker["spd"] = int(attacker["spd_base"] * 1.5)
            flags["deale_boosted"] = True
            if is_team_battle:
                messages.append(f"⚡ **Deale's swiftness!** Team SPD +50%")
            else:
                messages.append(f"💨 **{attacker['name']}'s swift strike!** SPD +50%")
    
    elif ability_type == "heal_and_def":  # Jeanne - First attack: Heal 30% HP + 30% DEF
        if turn == 1 and not flags.get("heal_and_def_used"):
            heal_amount = int(attacker["hp_max"] * 0.3)
            attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal_amount)
            flags["heal_and_def_used"] = True
            if is_team_battle:
                messages.append(f"✨ **Jeanne's protection!** Team heals {heal_amount} HP, DEF +30%")
            else:
                messages.append(f"✨ **{attacker['name']} heals {heal_amount} HP and gains +30% DEF!**")
        
        # Apply DEF bonus every turn after activation (permanent)
        if flags.get("heal_and_def_used"):
            if mode == "bonus":
                bonuses["def"] += 0.3
            else:
                if not flags.get("jeanne_def_boost"):
                    flags["jeanne_def_boost"] = 1.3
                attacker["def"] = int(attacker["def_base"] * flags.get("jeanne_def_boost", 1.3))
    
    # === TURN 3+ ACTIVATION ===
    elif ability_type == "turn3_atk_boost":  # Kuu - After turn 3: +50% ATK
        if turn >= 3:
            if not flags.get("kuu_boosted"):
                flags["kuu_boosted"] = True
                if is_team_battle:
                    messages.append(f"🔥 **Kuu's power awakens!** Team ATK +50%")
                else:
                    messages.append(f"🔥 **{attacker['name']}'s power awakens!** ATK +50%")
            if mode == "bonus":
                bonuses["atk"] += 0.5
            else:
                attacker["atk"] = int(attacker["atk_base"] * 1.5)
    
    elif ability_type == "turn3_heal":  # Himeyuri - Turn 3: Heal 50% HP
        if turn == 3 and not flags.get("himeyuri_healed"):
            heal = int(attacker["hp_max"] * 0.5)
            attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal)
            flags["himeyuri_healed"] = True
            if is_team_battle:
                messages.append(f"🌸 **Himeyuri's blessing!** Team heals {heal} HP")
            else:
                messages.append(f"🌸 **{attacker['name']}'s rejuvenation!** Heals {heal} HP")
    
    elif ability_type == "turn3_atk_def_boost":  # Kalisa - After turn 3: +20% ATK and DEF
        if turn >= 3:
            if not flags.get("kalisa_boosted"):
                flags["kalisa_boosted"] = True
                if is_team_battle:
                    messages.append(f"✨ **Kalisa's power awakens!** Team ATK +20%, DEF +20%")
                else:
                    messages.append(f"✨ **{attacker['name']}'s power awakens!** ATK +20%, DEF +20%")
            if mode == "bonus":
                bonuses["atk"] += 0.2
                bonuses["def"] += 0.2
            else:
                attacker["atk"] = int(attacker["atk_base"] * 1.2)
                attacker["def"] = int(attacker["def_base"] * 1.2)
    
    # === LOW HP TRIGGERS ===
    elif ability_type == "low_hp_def_boost":  # Emma - Low HP: +50% DEF
        if attacker["hp"] < (attacker["hp_max"] * 0.5) and not flags.get("low_hp_def_active"):
            if mode == "bonus":
                bonuses["def"] += 0.5
            else:
                attacker["def"] = int(attacker["def_base"] * 1.5)
            flags["low_hp_def_active"] = True
            if is_team_battle:
                messages.append(f"💚 **Emma's protection!** Team DEF +50%")
            else:
                messages.append(f"💚 **{attacker['name']}'s low HP ability activates!** DEF +50%")
    
    elif ability_type == "low_hp_atk_boost":  # Bahamut - Low HP: +50% ATK
        if attacker["hp"] < (attacker["hp_max"] * 0.5) and not flags.get("bahamut_active"):
            if mode == "bonus":
                bonuses["atk"] += 0.5
            else:
                attacker["atk"] = int(attacker["atk_base"] * 1.5)
            flags["bahamut_active"] = True
            if is_team_battle:
                messages.append(f"⚡ **Bahamut's fury!** Team ATK +50%")
            else:
                messages.append(f"⚡ **{attacker['name']}'s fury awakens!** ATK +50%")
    
    elif ability_type == "lifesteal":  # Yukimura - Low HP: Lifesteal activation
        if attacker["hp"] < (attacker["hp_max"] * 0.5) and not flags.get("lifesteal_active"):
            flags["lifesteal_active"] = True
            if is_team_battle:
                messages.append(f"🩸 **Yukimura's lifesteal activated!**")
            else:
                messages.append(f"🩸 **{attacker['name']}'s lifesteal awakens!** Heals 50% of damage dealt")
    
    elif ability_type == "low_hp_big_heal":  # Windy - Low HP: One-time 50% heal
        if attacker["hp"] < (attacker["hp_max"] * 0.5) and not flags.get("windy_healed"):
            heal = int(attacker["hp_max"] * 0.5)
            attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal)
            flags["windy_healed"] = True
            if is_team_battle:
                messages.append(f"🌬️ **Windy's emergency heal!** +{heal} HP")
            else:
                messages.append(f"🌬️ **{attacker['name']}'s emergency heal!** Heals {heal} HP")
    
    elif ability_type == "low_hp_spd_boost":  # Nobunaga - Low HP: +50% SPD
        if attacker["hp"] < (attacker["hp_max"] * 0.5) and not flags.get("nobunaga_active"):
            if mode == "bonus":
                bonuses["spd"] += 0.5
            else:
                attacker["spd"] = int(attacker["spd_base"] * 1.5)
            flags["nobunaga_active"] = True
            if is_team_battle:
                messages.append(f"⚡ **Nobunaga's speed!** Team SPD +50%")
            else:
                messages.append(f"⚡ **{attacker['name']}'s speed surge!** SPD +50%")
    
    # === SCALING ABILITIES ===
    elif ability_type == "def_boost_and_heal":  # Kasli - DEF comparison with stacking
        if attacker["def"] > defender["def"]:
            flags["kasli_stacks"] = flags.get("kasli_stacks", 0) + 1
            if mode == "bonus":
                bonuses["def"] += 0.2 * flags["kasli_stacks"]
            else:
                attacker["def"] = int(attacker["def_base"] * (1 + 0.2 * flags["kasli_stacks"]))
            heal = int(attacker["hp_max"] * 0.2)
            attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal)
            if is_team_battle:
                messages.append(f"🛡️ **Kasli's dominance!** DEF +{int(flags['kasli_stacks'] * 20)}%, heals {heal}")
            else:
                messages.append(f"🛡️ **{attacker['name']}'s DEF dominance!** DEF +{flags['kasli_stacks'] * 20}% and heals {heal} HP")
    
    elif ability_type == "atk_boost_and_heal":  # Izanagi - ATK comparison with stacking
        if attacker["atk"] > defender["atk"]:
            flags["izanagi_stacks"] = flags.get("izanagi_stacks", 0) + 1
            if mode == "bonus":
                bonuses["atk"] += 0.2 * flags["izanagi_stacks"]
            else:
                attacker["atk"] = int(attacker["atk_base"] * (1 + 0.2 * flags["izanagi_stacks"]))
            heal = int(attacker["hp_max"] * 0.2)
            attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal)
            if is_team_battle:
                messages.append(f"⚔️ **Izanagi's power!** ATK +{int(flags['izanagi_stacks'] * 20)}%, heals {heal}")
            else:
                messages.append(f"⚔️ **{attacker['name']}'s ATK dominance!** ATK +{flags['izanagi_stacks'] * 20}% and heals {heal} HP")
    
    # === RAMPAGE/STACKING ABILITIES ===
    elif ability_type == "rampage":  # Balrog - +20% ATK per turn
        flags["balrog_stacks"] = flags.get("balrog_stacks", 0) + 1
        if mode == "bonus":
            bonuses["atk"] += 0.2 * flags["balrog_stacks"]
        else:
            attacker["atk"] = int(attacker["atk_base"] * (1 + 0.2 * flags["balrog_stacks"]))
        if is_team_battle:
            messages.append(f"🔥 **Balrog's rage!** Team ATK +{int(flags['balrog_stacks'] * 20)}%")
        else:
            if flags["balrog_stacks"] == 1:
                messages.append(f"🔥 **{attacker['name']}'s rage grows!** ATK +20% (Total: +{flags['balrog_stacks'] * 20}%)")
            else:
                messages.append(f"🔥 **{attacker['name']}'s rage intensifies!** ATK +20% (Total: +{flags['balrog_stacks'] * 20}%)")
    
    elif ability_type == "spd_rampage":  # Trixi - +20% SPD per turn
        flags["trixi_stacks"] = flags.get("trixi_stacks", 0) + 1
        if mode == "bonus":
            bonuses["spd"] += 0.2 * flags["trixi_stacks"]
        else:
            attacker["spd"] = int(attacker["spd_base"] * (1 + 0.2 * flags["trixi_stacks"]))
        if is_team_battle:
            messages.append(f"💨 **Trixi's speed surge!** Team SPD +{int(flags['trixi_stacks'] * 20)}%")
        else:
            messages.append(f"💨 **{attacker['name']}'s speed increases!** SPD +{flags['trixi_stacks'] * 20}%")
    
    # === SPECIAL DAMAGE/PASSIVE ABILITIES ===
    # These are handled separately in damage calculation, but we track activation
    elif ability_type == "turn3_bonus_damage":  # Sidmi - After turn 3: +50% bonus damage
        if turn >= 3 and not flags.get("sidmi_active"):
            flags["sidmi_active"] = True
            messages.append(f"💥 **{attacker['name']}'s true power unleashed!** +50% bonus damage")
    
    # Note: speed_bonus, survive, and paralyze are handled in their respective sections
    # (damage calculation, defender death, first attack) and don't need stat modifications here
    
    return {"messages": messages, "bonuses": bonuses}

async def run_battle(ctx, player1_card, player2_card, player1_user, player2_user, is_pvp=False, floor=None, message=None):
    """
    Reusable battle function for both PvE (floor battles) and PvP (duels).
    
    Args:
        ctx: Discord context
        player1_card: Card dict for player 1 (challenger in PvP, player in PvE)
        player2_card: Card dict for player 2 (challenged in PvP, enemy in PvE)
        player1_user: Discord user for player 1
        player2_user: Discord user for player 2 (or None for PvE)
        is_pvp: True for duel (both have abilities), False for floor (only player1 has abilities)
        floor: Floor number (for PvE only)
        message: Optional existing message to edit instead of sending new
    
    Returns:
        dict with keys: 'winner' (1, 2, or 0 for draw), 'rounds', 'p1_hp', 'p2_hp'
    """
    
    # Calculate stats for player 1
    def calc_player_stats(card):
        lvl = card.get("level", 1)
        
        # Handle both formats: cards with "base" dict and enemies with direct stats
        if "base" in card:
            base = card["base"]
            mult = 1 + 0.03 * (lvl - 1)
            hp = int(base["hp"] * mult)
            atk = int(base["atk"] * mult)
            def_ = int(base["def"] * mult)
            spd = int(base["spd"] * mult)
        else:
            # Enemy format: stats are directly on the card, no level scaling
            hp = card["hp"]
            atk = card["atk"]
            def_ = card["def"]
            spd = card["spd"]
        
        return {
            "name": card["name"],
            "hp_max": hp,
            "hp": hp,
            "atk_base": atk,
            "atk": atk,
            "def_base": def_,
            "def": def_,
            "spd_base": spd,
            "spd": spd,
            "ability_type": card.get("ability_type", ""),
            "ability": card.get("ability", ""),
            "image": card.get("image", ""),
            "rarity": card.get("rarity", "Enemy"),
            "level": lvl
        }
    
    p1 = calc_player_stats(player1_card)
    p2 = calc_player_stats(player2_card)
    
    # FALLBACK: if ability_type doesn't exist (old cards), determine from id
    for p, card in [(p1, player1_card), (p2, player2_card)]:
        if not p["ability_type"]:
            char_id = card.get("id", "")
            if char_id == "kai":
                p["ability_type"] = "first_turn_def"
            elif char_id == "valkyrie":
                p["ability_type"] = "first_turn_spd"
            elif char_id == "shishilan_pasalan":
                p["ability_type"] = "first_turn_atk"
            elif char_id == "kasli":
                p["ability_type"] = "def_boost_and_heal"
            elif char_id == "emma":
                p["ability_type"] = "low_hp_def_boost"
            elif char_id == "thundia":
                p["ability_type"] = "paralyze"
            elif char_id == "jeanne":
                p["ability_type"] = "heal_and_def"
            elif char_id == "balrog":
                p["ability_type"] = "rampage"
            elif char_id == "verbena":
                p["ability_type"] = "survive"
            elif char_id == "lunacia":
                p["ability_type"] = "speed_bonus"
            elif char_id == "bahamut":
                p["ability_type"] = "low_hp_atk_boost"
            elif char_id == "yukimura":
                p["ability_type"] = "lifesteal"
            elif char_id == "ruri":
                p["ability_type"] = "def_boost_3turns"
            elif char_id == "windy":
                p["ability_type"] = "low_hp_big_heal"
            elif char_id == "nobunaga":
                p["ability_type"] = "low_hp_spd_boost"
            elif char_id == "izanagi":
                p["ability_type"] = "atk_boost_and_heal"
            elif char_id == "luminalia":
                p["ability_type"] = "spd_boost_3turns"
            elif char_id == "kalisa":
                p["ability_type"] = "turn3_atk_def_boost"
            elif char_id == "trixi":
                p["ability_type"] = "spd_rampage"
            elif char_id == "sidmi":
                p["ability_type"] = "turn3_bonus_damage"
    
    # Initialize ability flags for player 1
    p1_flags = {
        "buff_applied": False,
        "passive_damage_boost": False,
        "low_hp_def_active": False,
        "paralyze_turns": 0,
        "heal_and_def_used": False,
        "jeanne_def_boost": 1.0,
        "balrog_stacks": 0,
        "verbena_survived": False,
        "bahamut_active": False,
        "lifesteal_active": False,
        "ruri_turns": 0,
        "windy_healed": False,
        "nobunaga_active": False,
        "luminalia_turns": 0,
        "mitama_healed": False,
        "deale_boosted": False,
        "kuu_boosted": False,
        "himeyuri_healed": False,
        "kasli_stacks": 0,
        "izanagi_stacks": 0,
        "kalisa_boosted": False,
        "trixi_stacks": 0,
        "sidmi_active": False,
    }
    
    # Initialize ability flags for player 2
    p2_flags = {
        "buff_applied": False,
        "passive_damage_boost": False,
        "low_hp_def_active": False,
        "paralyze_turns": 0,
        "heal_and_def_used": False,
        "jeanne_def_boost": 1.0,
        "balrog_stacks": 0,
        "verbena_survived": False,
        "bahamut_active": False,
        "lifesteal_active": False,
        "ruri_turns": 0,
        "windy_healed": False,
        "nobunaga_active": False,
        "luminalia_turns": 0,
        "mitama_healed": False,
        "deale_boosted": False,
        "kuu_boosted": False,
        "himeyuri_healed": False,
        "kasli_stacks": 0,
        "izanagi_stacks": 0,
        "kalisa_boosted": False,
        "trixi_stacks": 0,
        "sidmi_active": False,
    }
    
    ability_text = ""
    
    # Apply passive and first-turn abilities for player 1 (initialization)
    if p1["ability_type"] == "def_boost_3turns":  # Ruri
        p1_flags["ruri_turns"] = 3
        p1["def"] = int(p1["def_base"] * 1.5)
        ability_text = f"✨ {p1['name']}'s ability activates!\n**{p1.get('ability', '')}**"
    elif p1["ability_type"] == "spd_boost_3turns":  # Luminalia
        p1_flags["luminalia_turns"] = 3
        p1["spd"] = int(p1["spd_base"] * 1.5)
        ability_text = f"✨ {p1['name']}'s ability activates!\n**{p1.get('ability', '')}**"
    elif p1["ability_type"] == "speed_bonus":  # Lunacia
        ability_text = f"✨ {p1['name']}'s ability is ready!\n**{p1.get('ability', '')}**"
    elif p1["ability_type"] == "rampage":  # Balrog
        ability_text = f"✨ {p1['name']}'s ability is ready!\n**{p1.get('ability', '')}**"
    elif p1["ability_type"] == "first_turn_def":  # Kai
        p1["def"] = int(p1["def_base"] * 2)
        p1_flags["buff_applied"] = True
        ability_text = f"✨ {p1['name']}'s ability activates!\n**{p1.get('ability', '')}**"
    elif p1["ability_type"] == "first_turn_spd":  # Valkyrie
        p1["spd"] = int(p1["spd_base"] * 2)
        p1_flags["buff_applied"] = True
        ability_text = f"✨ {p1['name']}'s ability activates!\n**{p1.get('ability', '')}**"
    elif p1["ability_type"] == "first_turn_atk":  # Shishilan
        p1["atk"] = int(p1["atk_base"] * 1.5)
        p1_flags["buff_applied"] = True
        ability_text = f"✨ {p1['name']}'s ability activates!\n**{p1.get('ability', '')}**"
    
    # Apply passive and first-turn abilities for player 2 (only in PvP)
    if is_pvp:
        if p2["ability_type"] == "def_boost_3turns":  # Ruri
            p2_flags["ruri_turns"] = 3
            p2["def"] = int(p2["def_base"] * 1.5)
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
        elif p2["ability_type"] == "spd_boost_3turns":  # Luminalia
            p2_flags["luminalia_turns"] = 3
            p2["spd"] = int(p2["spd_base"] * 1.5)
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
        elif p2["ability_type"] == "speed_bonus":  # Lunacia
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability is ready!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability is ready!\n**{p2.get('ability', '')}**"
        elif p2["ability_type"] == "rampage":  # Balrog
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability is ready!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability is ready!\n**{p2.get('ability', '')}**"
        elif p2["ability_type"] == "first_turn_def":  # Kai
            p2["def"] = int(p2["def_base"] * 2)
            p2_flags["buff_applied"] = True
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
        elif p2["ability_type"] == "first_turn_spd":  # Valkyrie
            p2["spd"] = int(p2["spd_base"] * 2)
            p2_flags["buff_applied"] = True
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
        elif p2["ability_type"] == "first_turn_atk":  # Shishilan
            p2["atk"] = int(p2["atk_base"] * 1.5)
            p2_flags["buff_applied"] = True
            if ability_text:
                ability_text += f"\n✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
            else:
                ability_text = f"✨ {p2['name']}'s ability activates!\n**{p2.get('ability', '')}**"
    
    # Determine turn order based on speed (after first-turn speed buffs)
    first_striker = None
    if p1["spd"] > p2["spd"]:
        turn_order = ["p1", "p2"]
        first_striker = "p1"
    elif p1["spd"] < p2["spd"]:
        turn_order = ["p2", "p1"]
        first_striker = "p2"
    else:
        if random.choice([True, False]):
            turn_order = ["p1", "p2"]
            first_striker = "p1"
        else:
            turn_order = ["p2", "p1"]
            first_striker = "p2"
    
    # Create initial embed
    if is_pvp:
        embed = discord.Embed(
            title=f"⚔️ DUEL ⚔️",
            description=f"Get ready to fight!",
            color=discord.Color.blue()
        )
        p1_stats = (
            f"**{player1_user.display_name}'s {p1['name']}** `{p1['rarity']}` Level `{p1['level']}`\n"
            f"HP: `{p1['hp_max']}` | ATK: `{p1['atk']}` | DEF: `{p1['def']}` | SPD: `{p1['spd']}`\n"
            f"{create_hp_bar(p1['hp'], p1['hp_max'])} `{p1['hp']}/{p1['hp_max']}`"
        )
        embed.add_field(name="🛡️ Fighter 1", value=p1_stats, inline=False)
        
        p2_stats = (
            f"**{player2_user.display_name}'s {p2['name']}** `{p2['rarity']}` Level `{p2['level']}`\n"
            f"HP: `{p2['hp_max']}` | ATK: `{p2['atk']}` | DEF: `{p2['def']}` | SPD: `{p2['spd']}`\n"
            f"{create_hp_bar(p2['hp'], p2['hp_max'])} `{p2['hp']}/{p2['hp_max']}`"
        )
        embed.add_field(name="⚡ Fighter 2", value=p2_stats, inline=False)
    else:
        embed = discord.Embed(
            title=f"⚔️ Battle — Floor {floor} ⚔️",
            description=f"Get ready to fight!",
            color=discord.Color.blue()
        )
        p1_stats = (
            f"**{player1_user.display_name}'s {p1['name']}** `{p1['rarity']}` Level `{p1['level']}`\n"
            f"HP: `{p1['hp_max']}` | ATK: `{p1['atk']}` | DEF: `{p1['def']}` | SPD: `{p1['spd']}`\n"
            f"{create_hp_bar(p1['hp'], p1['hp_max'])} `{p1['hp']}/{p1['hp_max']}`"
        )
        embed.add_field(name="🛡️ Your Fighter", value=p1_stats, inline=False)
        
        p2_stats = (
            f"**Enemy's {p2['name']}** `{p2['rarity']}` Level `{p2['level']}`\n"
            f"HP: `{p2['hp_max']}` | ATK: `{p2['atk']}` | DEF: `{p2['def']}` | SPD: `{p2['spd']}`\n"
            f"{create_hp_bar(p2['hp'], p2['hp_max'])} `{p2['hp']}/{p2['hp_max']}`"
        )
        embed.add_field(name="⚡ Enemy", value=p2_stats, inline=False)
    
    if p1.get("image"):
        embed.set_thumbnail(url=p1.get("image"))
    if p2.get("image"):
        embed.set_image(url=p2.get("image"))
    
    if message:
        await message.edit(embed=embed)
    else:
        message = await ctx.send(embed=embed)
    await asyncio.sleep(2.0)
    
    # Show ability activation if any
    if ability_text:
        embed.description = ability_text
        await message.edit(embed=embed)
        await asyncio.sleep(2.0)
    
    # Battle loop
    max_turns = 40
    current_round = 0
    
    while p1["hp"] > 0 and p2["hp"] > 0 and current_round < max_turns:
        current_round += 1
        round_log = []
        
        # Show who strikes first on first round
        if current_round == 1:
            if first_striker == "p1":
                if is_pvp:
                    round_log.append(f"**[ROUND {current_round}]** {player1_user.display_name}'s **{p1['name']}** has more SPD. It strikes first!")
                else:
                    round_log.append(f"**[ROUND {current_round}]** {player1_user.display_name}'s **{p1['name']}** has more SPD. It strikes first!")
            else:
                if is_pvp:
                    round_log.append(f"**[ROUND {current_round}]** {player2_user.display_name}'s **{p2['name']}** has more SPD. It strikes first!")
                else:
                    round_log.append(f"**[ROUND {current_round}]** Enemy's **{p2['name']}** has more SPD. It strikes first!")
        else:
            round_log.append(f"**[ROUND {current_round}]**")
        
        # Process each actor in turn order
        for actor in turn_order:
            if actor == "p1":
                attacker, defender = p1, p2
                attacker_flags, defender_flags = p1_flags, p2_flags
                attacker_user, defender_user = player1_user, player2_user
                is_enemy = False
            else:
                attacker, defender = p2, p1
                attacker_flags, defender_flags = p2_flags, p1_flags
                attacker_user, defender_user = player2_user, player1_user
                is_enemy = not is_pvp  # In PvE, p2 is the enemy
            
            if attacker["hp"] <= 0 or defender["hp"] <= 0:
                break
            
            # Check if attacker is paralyzed
            if attacker_flags["paralyze_turns"] > 0:
                attacker_flags["paralyze_turns"] -= 1
                round_log.append(f"⚡ **{attacker['name']} is paralyzed! Cannot attack.** ({attacker_flags['paralyze_turns']} turns left)")
                continue
            
            # Apply abilities - only for players with abilities (not enemies in PvE)
            if (not is_enemy or is_pvp):
                result = apply_ability(
                    attacker["ability_type"],
                    attacker,
                    defender,
                    attacker_flags,
                    current_round,
                    mode="direct"
                )
                round_log.extend(result["messages"])
            
            # Calculate damage
            base_dmg = damage_formula(attacker["atk"], defender["def"])
            
            # Apply attacker's damage modifiers (only if they have abilities)
            dmg = base_dmg
            if (not is_enemy or is_pvp):
                # Lunacia's speed bonus
                if attacker["ability_type"] == "speed_bonus" and attacker["spd"] > defender["spd"]:
                    bonus_dmg = int(attacker["atk"] * 0.5)
                    dmg += bonus_dmg
                    round_log.append(f"💨 **{attacker['name']}'s speed advantage!** +{bonus_dmg} bonus damage!")
                
                # Sidmi's bonus damage (after turn 3)
                if attacker_flags.get("sidmi_active", False):
                    bonus = int(attacker["atk"] * 0.5)
                    dmg += bonus
            
            # Deal damage
            defender["hp"] -= dmg
            defender["hp"] = max(0, defender["hp"])
            
            if is_enemy and not is_pvp:
                round_log.append(f"💥 Enemy's **{attacker['name']}** deals `{dmg}` damage.")
            else:
                if is_pvp:
                    round_log.append(f"⚔️ {attacker_user.display_name}'s **{attacker['name']}** deals `{dmg}` damage.")
                else:
                    round_log.append(f"⚔️ {player1_user.display_name}'s **{attacker['name']}** deals `{dmg}` damage.")
            
            # Lifesteal (only for attackers with abilities)
            if (not is_enemy or is_pvp) and attacker_flags["lifesteal_active"]:
                heal_amount = int(dmg * 0.5)
                attacker["hp"] = min(attacker["hp_max"], attacker["hp"] + heal_amount)
                round_log.append(f"🩸 **{attacker['name']} drains life!** +{heal_amount} HP restored")
            
            # Verbena survive (only for defenders with abilities)
            if defender["hp"] <= 0:
                if (actor == "p2" and not is_pvp):  # Enemy defending in PvE - no survive
                    pass
                elif (actor == "p1" and not is_pvp) or is_pvp:  # Player or PvP
                    if defender["ability_type"] == "survive" and not defender_flags["verbena_survived"]:
                        defender["hp"] = 1
                        defender_flags["verbena_survived"] = True
                        round_log.append(f"💫 **{defender['name']} refuses to fall!** Survived with 1 HP!")
            
            # Thundia paralyze (first attack only, only for attackers with abilities)
            if (not is_enemy or is_pvp) and attacker["ability_type"] == "paralyze" and current_round == 1:
                defender_flags["paralyze_turns"] = 2
                round_log.append(f"⚡ **{defender['name']} is paralyzed for 2 turns!**")
            
            # Update embed
            if is_pvp:
                embed = discord.Embed(
                    title=f"⚔️ DUEL ⚔️",
                    description="\n".join(round_log),
                    color=discord.Color.green() if actor == "p1" else discord.Color.red()
                )
                p1_stats = (
                    f"**{player1_user.display_name}'s {p1['name']}** `{p1['rarity']}` Level `{p1['level']}`\n"
                    f"HP: `{p1['hp_max']}` | ATK: `{p1['atk']}` | DEF: `{p1['def']}` | SPD: `{p1['spd']}`\n"
                    f"{create_hp_bar(p1['hp'], p1['hp_max'])} `{p1['hp']}/{p1['hp_max']}`"
                )
                embed.add_field(name="🛡️ Fighter 1", value=p1_stats, inline=False)
                
                p2_stats = (
                    f"**{player2_user.display_name}'s {p2['name']}** `{p2['rarity']}` Level `{p2['level']}`\n"
                    f"HP: `{p2['hp_max']}` | ATK: `{p2['atk']}` | DEF: `{p2['def']}` | SPD: `{p2['spd']}`\n"
                    f"{create_hp_bar(p2['hp'], p2['hp_max'])} `{p2['hp']}/{p2['hp_max']}`"
                )
                embed.add_field(name="⚡ Fighter 2", value=p2_stats, inline=False)
            else:
                embed = discord.Embed(
                    title=f"⚔️ Battle — Floor {floor} ⚔️",
                    description="\n".join(round_log),
                    color=discord.Color.green() if actor == "p1" else discord.Color.red()
                )
                p1_stats = (
                    f"**{player1_user.display_name}'s {p1['name']}** `{p1['rarity']}` Level `{p1['level']}`\n"
                    f"HP: `{p1['hp_max']}` | ATK: `{p1['atk']}` | DEF: `{p1['def']}` | SPD: `{p1['spd']}`\n"
                    f"{create_hp_bar(p1['hp'], p1['hp_max'])} `{p1['hp']}/{p1['hp_max']}`"
                )
                embed.add_field(name="🛡️ Your Fighter", value=p1_stats, inline=False)
                
                p2_stats = (
                    f"**Enemy's {p2['name']}** `{p2['rarity']}` Level `{p2['level']}`\n"
                    f"HP: `{p2['hp_max']}` | ATK: `{p2['atk']}` | DEF: `{p2['def']}` | SPD: `{p2['spd']}`\n"
                    f"{create_hp_bar(p2['hp'], p2['hp_max'])} `{p2['hp']}/{p2['hp_max']}`"
                )
                embed.add_field(name="⚡ Enemy", value=p2_stats, inline=False)
            
            if p1.get("image"):
                embed.set_thumbnail(url=p1.get("image"))
            if p2.get("image"):
                embed.set_image(url=p2.get("image"))
            
            await message.edit(embed=embed)
            await asyncio.sleep(1.5)
            
            # Reset first-turn buffs after first action
            if attacker_flags["buff_applied"]:
                attacker["atk"] = attacker["atk_base"]
                attacker["def"] = attacker["def_base"]
                attacker["spd"] = attacker["spd_base"]
                attacker_flags["buff_applied"] = False
            
            if defender["hp"] <= 0:
                break
            
            # Ruri's DEF boost countdown
            if (not is_enemy or is_pvp) and attacker["ability_type"] == "def_boost_3turns" and attacker_flags["ruri_turns"] > 0:
                attacker_flags["ruri_turns"] -= 1
                if attacker_flags["ruri_turns"] == 0:
                    attacker["def"] = attacker["def_base"]
                    # Note: DEF boost expiration message will show in next round
            
            # Luminalia's SPD boost countdown
            if (not is_enemy or is_pvp) and attacker["ability_type"] == "spd_boost_3turns" and attacker_flags["luminalia_turns"] > 0:
                attacker_flags["luminalia_turns"] -= 1
                if attacker_flags["luminalia_turns"] == 0:
                    attacker["spd"] = attacker["spd_base"]
                    round_log.append(f"💨 **{attacker['name']}'s SPD boost expired.**")
    
    # Return battle result
    winner = 0
    if p1["hp"] > 0 and p2["hp"] <= 0:
        winner = 1
    elif p2["hp"] > 0 and p1["hp"] <= 0:
        winner = 2
    
    return {
        "winner": winner,
        "rounds": current_round,
        "p1_hp": p1["hp"],
        "p2_hp": p2["hp"],
        "p1": p1,
        "p2": p2,
        "message": message
    }

@bot.command(name="battle", aliases=["bt", "b"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def battle_cmd(ctx):
    """Start a battle on your current floor with your selected character."""
    user = ensure_user(ctx.author.id)
    if user.get("stamina", 0) < 5:
        await ctx.send("❌ Not enough stamina. You need 5 to battle.")
        return
    if not user.get("selected"):
        await ctx.send("❌ No character selected. Use `-select <n>` first.")
        return

    # find the selected card
    selected_id = user["selected"]
    chosen = None
    for c in user["inventory"]:
        if c.get("instance_id") == selected_id:
            chosen = c
            break
    if not chosen:
        await ctx.send("❌ Your selected character was not found. Use `-select <n>` again.")
        return

    # remove stamina and save immediately
    user["stamina"] -= 5
    await save_data()

    # battle logic
    floor = user.get("floor", 1)
    enemy = make_enemy_for_floor(floor)
    
    # Run the battle using the shared battle logic
    result = await run_battle(ctx, chosen, enemy, ctx.author, None, is_pvp=False, floor=floor)
    
    # Display final result
    p1 = result["p1"]
    p2 = result["p2"]
    message = result["message"]
    
    if result["winner"] == 1:
        # Player wins
        result_text = "🎉 VICTORY! 🎉"
        color = discord.Color.gold()
        result_desc = f"You defeated the enemy in {result['rounds']} rounds!"
    elif result["winner"] == 2:
        # Player loses
        result_text = "💀 DEFEAT 💀"
        color = discord.Color.dark_red()
        result_desc = f"You were defeated in {result['rounds']} rounds."
    else:
        # Draw
        result_text = "⚖️ DRAW ⚖️"
        color = discord.Color.orange()
        result_desc = f"Battle ended in a draw after {result['rounds']} rounds."
    
    embed = discord.Embed(
        title=f"⚔️ Battle — Floor {floor} ⚔️",
        description=f"**{result_text}**\n{result_desc}",
        color=color
    )
    
    # Final HP display
    player_stats = (
        f"**{ctx.author.display_name}'s {p1['name']}** `{p1['rarity']}` Level `{p1['level']}`\n"
        f"{create_hp_bar(p1['hp'], p1['hp_max'])} `{p1['hp']}/{p1['hp_max']}`"
    )
    embed.add_field(name="🛡️ Your Fighter", value=player_stats, inline=False)
    
    enemy_stats = (
        f"**Enemy's {p2['name']}** `{p2['rarity']}` Level `{p2['level']}`\n"
        f"{create_hp_bar(p2['hp'], p2['hp_max'])} `{p2['hp']}/{p2['hp_max']}`"
    )
    embed.add_field(name="⚡ Enemy", value=enemy_stats, inline=False)
    
    if chosen.get("image"):
        embed.set_thumbnail(url=chosen.get("image"))
    if enemy.get("image"):
        embed.set_image(url=enemy.get("image"))
    
    await message.edit(embed=embed)

    # apply rewards/penalties and progression
    if result["winner"] == 1:
        gold_gain = 50 + floor * 10
        exp_gain_user = 30 + floor * 5
        exp_gain_card = 40 + floor * 10
        user["gold"] = user.get("gold", 0) + gold_gain
        user["exp"] = user.get("exp", 0) + exp_gain_user
        # add exp to chosen instance
        chosen["exp"] = chosen.get("exp", 0) + exp_gain_card

        lvl_msgs = maybe_level_up_user(user)
        # level up card
        while chosen.get("level", 1) < chosen.get("max_level", 30):
            need = 100 * chosen.get("level", 1)
            if chosen.get("exp", 0) >= need:
                chosen["exp"] -= need
                chosen["level"] += 1
            else:
                break

        # unlock next floor
        if user.get("floor_unlocked", 1) < floor + 1:
            user["floor_unlocked"] = floor + 1

        await save_data()
        
        reward_msg = f"💰 **Rewards:**\n+{gold_gain} gold | +{exp_gain_user} EXP (user) | +{exp_gain_card} EXP ({chosen['name']})"
        if user.get("floor_unlocked", 1) > floor:
            reward_msg += f"\n🔓 Floor {user.get('floor_unlocked')} unlocked!"
        if lvl_msgs:
            reward_msg = "\n".join(lvl_msgs) + "\n" + reward_msg
        await ctx.send(reward_msg)
    else:
        # loss penalty
        user["stamina"] = max(0, user.get("stamina", 0) - 3)
        await save_data()
        await ctx.send("💀 You lost the battle. **-3 stamina**")

# Updated floor command: show info and restrict next to unlocked floors
@bot.command(name="floor", aliases=["fl"])
async def floor_cmd(ctx, action: str = None):
    """Manage floors. -floor next to go to the next floor (unlocks limited by progression). -floor <n> to set (only to unlocked)."""
    user = ensure_user(ctx.author.id)
    if not action:
        floor = user.get("floor", 1)
        unlocked = user.get("floor_unlocked", 1)
        # show enemy stats for current floor
        enemy = make_enemy_for_floor(floor)
        await ctx.send(
            f"You are at floor {floor} (unlocked up to {unlocked}).\n"
            f"Enemy stats — HP: {enemy['hp']} | ATK: {enemy['atk']} | DEF: {enemy['def']} | SPD: {enemy['spd']}"
        )
        return

    if action.lower() in ["next", "n"]:
        current = user.get("floor", 1)
        unlocked = user.get("floor_unlocked", 1)
        if current >= 27:
            await ctx.send("You are already at the maximum floor (27).")
            return
        if unlocked < current + 1:
            await ctx.send("Next floor is locked. Complete the current floor to unlock the next one.")
            return
        user["floor"] = current + 1
        await save_data()
        await ctx.send(f"You moved to floor {user['floor']}.")
        return

    # set to numeric floor only if unlocked
    if action.isdigit():
        n = int(action)
        unlocked = user.get("floor_unlocked", 1)
        if 1 <= n <= unlocked:
            user["floor"] = n
            await save_data()
            await ctx.send(f"Floor set to {n}.")
        else:
            await ctx.send(f"Cannot set floor to {n}. Unlocked up to {unlocked}.")
        return

    await ctx.send("Unrecognized floor action. Use `next` or a floor number you have unlocked.")

# ------------------------
# BOSS BATTLE (3v1 Mode)
# ------------------------
@bot.command(name="team")
async def team_cmd(ctx, action: str = None, *args):
    """Manage your boss battle team. Usage: -team, -team set 1 2 3, -team clear"""
    user = ensure_user(ctx.author.id)
    inv = user["inventory"]
    
    if not inv:
        await ctx.send("🎴 Your inventory is empty.")
        return
    
    sorted_inv = sort_inventory(inv)
    
    # Helper function to get ability type from card (with fallback to CHARACTERS)
    def get_ability_type(card):
        if card.get("ability_type"):
            return card["ability_type"]
        # Fallback: look up from CHARACTERS
        base = CHARACTERS_BY_ID.get(card.get("id"))
        if base and base.get("ability_type"):
            return base["ability_type"]
        return ""
    
    # Helper function to calculate combined stats
    def calc_team_stats(cards):
        total_hp = 0
        total_atk = 0
        total_def = 0
        total_spd = 0
        
        for card in cards:
            lvl = card.get("level", 1)
            base = card.get("base", {})
            if not base:
                base_char = CHARACTERS_BY_ID.get(card.get("id"))
                if base_char:
                    base = base_char["base"]
                else:
                    continue
            mult = 1 + 0.03 * (lvl - 1)
            total_hp += int(base.get("hp", 0) * mult)
            total_atk += int(base.get("atk", 0) * mult)
            total_def += int(base.get("def", 0) * mult)
            total_spd += int(base.get("spd", 0) * mult)
        
        return {"hp": total_hp, "atk": total_atk, "def": total_def, "spd": total_spd}
    
    # TEAM CLEAR
    if action and action.lower() == "clear":
        user["team"] = []
        await save_data()
        await ctx.send("✅ Team cleared!")
        return
    
    # TEAM SET
    if action and action.lower() == "set":
        if len(args) == 1:
            # Single card - ask for position
            try:
                card_idx = int(args[0])
            except ValueError:
                await ctx.send("❌ Invalid card index. Use a number.")
                return
            
            if card_idx < 1 or card_idx > len(sorted_inv):
                await ctx.send(f"❌ Invalid card index. Valid range: 1-{len(sorted_inv)}")
                return
            
            card = sorted_inv[card_idx - 1]
            
            # Ask for position
            await ctx.send(
                f"🎴 Selected **{card['name']}** ({card['rarity']}) Lv.{card.get('level', 1)}\n"
                f"Which position do you want to place it in? Reply with **1**, **2**, or **3**"
            )
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content in ["1", "2", "3"]
            
            try:
                msg = await bot.wait_for("message", check=check, timeout=30.0)
                position = int(msg.content) - 1  # 0-indexed
                
                # Initialize team if necessary
                if not user.get("team") or len(user["team"]) != 3:
                    user["team"] = [None, None, None]
                
                # Insert card in position
                user["team"][position] = card["instance_id"]
                
                await save_data()
                await ctx.send(f"✅ **{card['name']}** placed in position {position + 1} of your team!")
                
            except asyncio.TimeoutError:
                await ctx.send("⏰ Timeout expired. Try again with `-team set <card_number>`")
            return
        
        elif len(args) == 3:
            # Three cards - existing behavior
            try:
                indices = [int(x) for x in args]
            except ValueError:
                await ctx.send("❌ Invalid card indices. Use numbers.")
                return
            
            # Check for duplicates
            if len(set(indices)) != 3:
                await ctx.send("❌ You must select 3 different cards!")
                return
            
            # Validate indices
            for idx in indices:
                if idx < 1 or idx > len(sorted_inv):
                    await ctx.send(f"❌ Invalid card index {idx}. Valid range: 1-{len(sorted_inv)}")
                    return
            
            # Get the cards
            team_cards = [sorted_inv[idx - 1] for idx in indices]
            team_ids = [c["instance_id"] for c in team_cards]
            
            user["team"] = team_ids
            await save_data()
            
            # Calculate combined stats
            stats = calc_team_stats(team_cards)
            
            # Display the selected team with abilities
            embed = discord.Embed(
                title="✅ Team Set!",
                color=discord.Color.green()
            )
            
            team_display = []
            abilities_list = []
            for i, c in enumerate(team_cards, 1):
                ability_type = get_ability_type(c)
                ability_name = c.get("ability", "")
                if not ability_name:
                    base = CHARACTERS_BY_ID.get(c.get("id"))
                    if base:
                        ability_name = base.get("ability", "No ability")
                team_display.append(f"`{i}.` **{c['name']}** `{c['rarity']}` Lv.{c.get('level', 1)}")
                if ability_type:
                    abilities_list.append(f"• **{c['name']}**: {ability_name}")
            
            embed.add_field(name="👥 Team Members", value="\n".join(team_display), inline=False)
            embed.add_field(
                name="📊 Combined Stats",
                value=f"HP: `{stats['hp']}` | ATK: `{stats['atk']}` | DEF: `{stats['def']}` | SPD: `{stats['spd']}`",
                inline=False
            )
            if abilities_list:
                embed.add_field(name="✨ Active Abilities", value="\n".join(abilities_list), inline=False)
            
            # Show first card's image as thumbnail
            if team_cards[0].get("image"):
                embed.set_thumbnail(url=team_cards[0].get("image"))
            
            embed.set_footer(text="Use -boss to start a boss battle!")
            await ctx.send(embed=embed)
            return
        
        else:
            await ctx.send("❌ Use `-team set <card>` for one card or `-team set <c1> <c2> <c3>` for three cards.")
            return
    
    # TEAM VIEW (default, or if action is not recognized)
    if action is not None and action.lower() not in ["set", "clear"]:
        await ctx.send(f"❌ Unknown action `{action}`. Use: `-team`, `-team set 1 2 3`, or `-team clear`")
        return
    
    team_ids = user.get("team", [])
    if not team_ids or len(team_ids) != 3:
        await ctx.send("👥 You don't have a team set. Use `-team set <card1> <card2> <card3>` to set one.")
        return
    
    # Get team cards (handle None values)
    team_cards = []
    for instance_id in team_ids:
        if instance_id is None:
            team_cards.append(None)
        else:
            found = False
            for c in inv:
                if c.get("instance_id") == instance_id:
                    team_cards.append(c)
                    found = True
                    break
            if not found:
                team_cards.append(None)
    
    # Calculate combined stats (skip None cards)
    valid_cards = [c for c in team_cards if c is not None]
    stats = calc_team_stats(valid_cards) if valid_cards else {"hp": 0, "atk": 0, "def": 0, "spd": 0}
    
    # Create embed
    embed = discord.Embed(
        title=f"👥 {ctx.author.name}'s Boss Battle Team",
        color=discord.Color.blue()
    )
    
    team_display = []
    abilities_list = []
    for i, c in enumerate(team_cards, 1):
        if c is None:
            team_display.append(f"`{i}.` *Empty slot*")
        else:
            # Find position in sorted inventory
            inv_pos = "?"
            for j, sc in enumerate(sorted_inv, 1):
                if sc.get("instance_id") == c.get("instance_id"):
                    inv_pos = j
                    break
            
            ability_type = get_ability_type(c)
            ability_name = c.get("ability", "")
            if not ability_name:
                base = CHARACTERS_BY_ID.get(c.get("id"))
                if base:
                    ability_name = base.get("ability", "No ability")
            
            team_display.append(f"`{i}.` **{c['name']}** `{c['rarity']}` Lv.{c.get('level', 1)} (inv #{inv_pos})")
            if ability_type:
                abilities_list.append(f"• **{c['name']}**: {ability_name}")
    
    embed.add_field(name="🎴 Team Members", value="\n".join(team_display), inline=False)
    embed.add_field(
        name="📊 Combined Stats",
        value=f"HP: `{stats['hp']}` | ATK: `{stats['atk']}` | DEF: `{stats['def']}` | SPD: `{stats['spd']}`",
        inline=False
    )
    if abilities_list:
        embed.add_field(name="✨ Active Abilities", value="\n".join(abilities_list), inline=False)
    
    # Show first non-None card's image as thumbnail
    first_card = next((c for c in team_cards if c is not None), None)
    if first_card and first_card.get("image"):
        embed.set_thumbnail(url=first_card.get("image"))
    
    embed.set_footer(text="Use -team set 1 2 3 to change | -team clear to remove")
    await ctx.send(embed=embed)

async def create_battle_image(bot, team_cards, boss_id, phase_num):
    """
    Create a composite battle image with team cards on top and boss on bottom.
    Uses Discord channel for image hosting (much faster than Catbox).
    """
    # Get boss image URL from Catbox
    boss_key = f"{boss_id}_phase{phase_num}"
    boss_image_url = BOSS_CATBOX_IMAGES.get(boss_key, "")
    
    if not boss_image_url:
        return None
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            images = []
            
            # Download team card images
            for card in team_cards:
                card_name = card.get("name", "")
                img_url = CATBOX_IMAGES.get(card_name, "")
                
                if img_url:
                    try:
                        async with session.get(img_url) as resp:
                            if resp.status == 200:
                                img_data = await resp.read()
                                img = Image.open(io.BytesIO(img_data))
                                images.append(img)
                            else:
                                images.append(None)
                    except:
                        images.append(None)
                else:
                    images.append(None)
            
            # Download boss image
            boss_img = None
            try:
                async with session.get(boss_image_url) as resp:
                    if resp.status == 200:
                        img_data = await resp.read()
                        boss_img = Image.open(io.BytesIO(img_data))
            except:
                pass
            
            if not boss_img:
                return None
            
            # Card dimensions
            card_width = 140
            card_height = 200
            card_size = (card_width, card_height)
            
            # Resize cards
            resized_cards = []
            for img in images:
                if img:
                    img = img.convert("RGBA")
                    img.thumbnail(card_size, Image.Resampling.LANCZOS)
                    new_img = Image.new("RGBA", card_size, (40, 40, 40, 255))
                    x_offset = (card_width - img.width) // 2
                    y_offset = (card_height - img.height) // 2
                    new_img.paste(img, (x_offset, y_offset))
                    resized_cards.append(new_img)
                else:
                    placeholder = Image.new("RGBA", card_size, (60, 60, 60, 255))
                    resized_cards.append(placeholder)
            
            # Resize boss
            boss_img = boss_img.convert("RGBA")
            boss_max_width = card_width * 3 + 20
            boss_max_height = 250
            boss_ratio = min(boss_max_width / boss_img.width, boss_max_height / boss_img.height)
            new_boss_width = int(boss_img.width * boss_ratio)
            new_boss_height = int(boss_img.height * boss_ratio)
            boss_img = boss_img.resize((new_boss_width, new_boss_height), Image.Resampling.LANCZOS)
            
            # Create composite
            padding = 10
            total_width = card_width * 3 + padding * 4
            total_height = card_height + boss_max_height + padding * 3
            composite = Image.new("RGBA", (total_width, total_height), (25, 25, 30, 255))
            
            # Paste cards
            for i, card_img in enumerate(resized_cards[:3]):
                x = padding + i * (card_width + padding)
                composite.paste(card_img, (x, padding), card_img)
            
            # Paste boss
            boss_x = (total_width - new_boss_width) // 2
            boss_y = card_height + padding * 2
            composite.paste(boss_img, (boss_x, boss_y), boss_img)
            
            # Save to bytes
            composite_rgb = composite.convert("RGB")
            output = io.BytesIO()
            composite_rgb.save(output, format="PNG")
            output.seek(0)
            
            # Upload to Discord
            storage_channel = bot.get_channel(IMAGE_STORAGE_CHANNEL)
            if not storage_channel:
                return None
            
            file = discord.File(output, filename=f"battle_{boss_id}_p{phase_num}.png")
            msg = await storage_channel.send(file=file)
            
            if msg.attachments:
                return msg.attachments[0].url
            return None
    
    except:
        return None

async def run_boss_battle(ctx, team_cards, boss_data, user):
    """
    Run a 3v1 boss battle with combined team stats.
    
    Args:
        ctx: Discord context
        team_cards: List of 3 card dicts
        boss_data: Boss dict from BOSSES list
        user: User data dict
    
    Returns:
        dict with winner info and rewards
    """
    
    # Calculate combined team stats (sum all cards)
    def calc_combined_stats(cards):
        total_hp = 0
        total_atk = 0
        total_def = 0
        total_spd = 0
        
        for card in cards:
            lvl = card.get("level", 1)
            base = card["base"]
            mult = 1 + 0.03 * (lvl - 1)
            total_hp += int(base["hp"] * mult)
            total_atk += int(base["atk"] * mult)
            total_def += int(base["def"] * mult)
            total_spd += int(base["spd"] * mult)
        
        return {
            "hp_max": total_hp,
            "hp": total_hp,
            "atk_base": total_atk,
            "atk": total_atk,
            "def_base": total_def,
            "def": total_def,
            "spd_base": total_spd,
            "spd": total_spd
        }
    
    team = calc_combined_stats(team_cards)
    team["name"] = " + ".join([c["name"] for c in team_cards])
    team["cards"] = team_cards  # Keep reference to cards for abilities
    
    # Boss starts at phase 1
    current_phase = 0
    phases = boss_data["phases"]
    
    def get_boss_stats(phase_idx):
        phase = phases[phase_idx]
        total_phases = len(phases)
        return {
            "name": f"{boss_data['name']} (Phase {phase_idx + 1}/{total_phases})",
            "hp_max": phase["hp"],
            "hp": phase["hp"],
            "atk_base": phase["atk"],
            "atk": phase["atk"],
            "def_base": phase["def"],
            "def": phase["def"],
            "spd_base": phase["spd"],
            "spd": phase["spd"],
            "image": phase["image"]
        }
    
    boss = get_boss_stats(current_phase)
    
    # Initialize ability flags for combined team
    team_flags = {
        "buff_applied": False,
        "low_hp_def_active": False,
        "bahamut_active": False,
        "lifesteal_active": False,
        "balrog_stacks": 0,
        "kasli_stacks": 0,
        "izanagi_stacks": 0,
        "windy_healed": False,
        "nobunaga_active": False,
        "ruri_turns": 0,
        "luminalia_turns": 0,
        "verbena_survived": False,
        "paralyze_turns": 0,  # For boss
        # New ability flags
        "first_attack_heal_done": False,  # Mitama
        "first_attack_spd_done": False,   # Deale
        "turn3_atk_boost_done": False,    # Kuu
        "turn3_heal_done": False,         # Himeyuri
        "heal_and_def_done": False,       # Jeanne
        "kalisa_boosted": False,          # Kalisa
        "trixi_stacks": 0,                # Trixi
        "sidmi_active": False,            # Sidmi
    }
    
    # Get all ability types from team
    team_abilities = [c.get("ability_type", "") for c in team_cards]
    
    # Apply first-turn abilities
    ability_text = ""
    
    # ===== SISTEMA BUFF ADDITIVO - BUFF INIZIALI =====
    # Traccia i bonus separatamente
    initial_atk_bonus = 0.0
    initial_def_bonus = 0.0
    initial_spd_bonus = 0.0
    
    # Kai - First turn +100% DEF (based on total)
    if "first_turn_def" in team_abilities:
        initial_def_bonus += 1.0
        team_flags["buff_applied"] = True
        ability_text += "🛡️ **Kai's ability!** Team DEF +100%\n"
    
    # Valkyrie - First turn +100% SPD
    if "first_turn_spd" in team_abilities:
        initial_spd_bonus += 1.0
        team_flags["buff_applied"] = True
        ability_text += "💨 **Valkyrie's ability!** Team SPD +100%\n"
    
    # Shishilan - First turn +50% ATK
    if "first_turn_atk" in team_abilities:
        initial_atk_bonus += 0.5
        team_flags["buff_applied"] = True
        ability_text += "⚔️ **Shishilan's ability!** Team ATK +50%\n"
    
    # Ruri - 3 turns +50% DEF
    if "def_boost_3turns" in team_abilities:
        team_flags["ruri_turns"] = 3
        initial_def_bonus += 0.5
        ability_text += "🛡️ **Ruri's ability!** Team DEF +50% for 3 turns\n"
    
    # Luminalia - 3 turns +50% SPD
    if "spd_boost_3turns" in team_abilities:
        team_flags["luminalia_turns"] = 3
        initial_spd_bonus += 0.5
        ability_text += "💨 **Luminalia's ability!** Team SPD +50% for 3 turns\n"
    
    # Mitama - First attack: Heals 50% max HP
    if "first_attack_heal" in team_abilities:
        heal = int(team["hp_max"] * 0.5)
        team["hp"] = min(team["hp_max"], team["hp"] + heal)
        team_flags["first_attack_heal_done"] = True
        ability_text += f"💖 **Mitama's blessing!** Team heals {heal} HP\n"
    
    # Deale - First attack: +50% SPD
    if "first_attack_spd" in team_abilities:
        initial_spd_bonus += 0.5
        team_flags["first_attack_spd_done"] = True
        ability_text += "⚡ **Deale's swiftness!** Team SPD +50%\n"
    
    # Jeanne - First attack: Heal 30% HP, +30% DEF
    if "heal_and_def" in team_abilities:
        heal = int(team["hp_max"] * 0.3)
        team["hp"] = min(team["hp_max"], team["hp"] + heal)
        initial_def_bonus += 0.3
        team_flags["heal_and_def_done"] = True
        ability_text += f"✨ **Jeanne's protection!** Team heals {heal} HP, DEF +30%\n"
    
    # Applica i buff iniziali
    team["atk"] = int(team["atk_base"] * (1 + initial_atk_bonus))
    team["def"] = int(team["def_base"] * (1 + initial_def_bonus))
    team["spd"] = int(team["spd_base"] * (1 + initial_spd_bonus))
    
    # Create initial embed
    embed = discord.Embed(
        title=f"👹 BOSS BATTLE — {boss_data['name']} 👹",
        description=f"**Your Team vs {boss_data['name']}!**\n\n{ability_text}" if ability_text else f"**Your Team vs {boss_data['name']}!**",
        color=discord.Color.dark_red()
    )
    
    team_stats = (
        f"**{team['name']}**\n"
        f"HP: `{team['hp_max']}` | ATK: `{team['atk']}` | DEF: `{team['def']}` | SPD: `{team['spd']}`\n"
        f"{create_hp_bar(team['hp'], team['hp_max'])} `{team['hp']}/{team['hp_max']}`"
    )
    embed.add_field(name="👥 Your Team", value=team_stats, inline=False)
    
    boss_stats = (
        f"**{boss['name']}**\n"
        f"HP: `{boss['hp_max']}` | ATK: `{boss['atk']}` | DEF: `{boss['def']}` | SPD: `{boss['spd']}`\n"
        f"{create_hp_bar(boss['hp'], boss['hp_max'])} `{boss['hp']}/{boss['hp_max']}`"
    )
    embed.add_field(name="👹 Boss", value=boss_stats, inline=False)
    
    # Pre-generate composite images (one per phase) at battle start
    composite_urls = {}
    
    for phase_idx in range(len(phases)):
        phase_num = phase_idx + 1
        phase_url = await create_battle_image(ctx.bot, team_cards, boss_data["id"], phase_num)
        if phase_url:
            composite_urls[phase_num] = phase_url
        else:
            # Fallback to boss image for this phase
            composite_urls[phase_num] = boss_data["phases"][phase_idx].get("image", "")
    
    # Use the pre-generated URL for current phase
    composite_image_url = composite_urls.get(current_phase + 1, boss["image"])
    
    if composite_image_url:
        embed.set_image(url=composite_image_url)
    else:
        embed.set_image(url=boss["image"])
    
    message = await ctx.send(embed=embed)
    await asyncio.sleep(2.0)
    
    # Determine turn order
    if team["spd"] >= boss["spd"]:
        turn_order = ["team", "boss"]
    else:
        turn_order = ["boss", "team"]
    
    # Battle loop
    max_turns = 60
    current_round = 0
    
    while team["hp"] > 0 and (boss["hp"] > 0 or current_phase < len(phases) - 1):
        current_round += 1
        if current_round > max_turns:
            break
        
        round_log = [f"**[ROUND {current_round}]**"]
        
        for actor in turn_order:
            if team["hp"] <= 0:
                break
            
            if actor == "team":
                # Check if paralyzed
                if team_flags.get("team_paralyzed", 0) > 0:
                    team_flags["team_paralyzed"] -= 1
                    round_log.append(f"⚡ **Team is stunned!** Cannot attack.")
                    continue
                
                # ===== SISTEMA BUFF ADDITIVO =====
                # Traccia tutti i moltiplicatori separatamente, poi somma alla fine
                atk_bonus = 0.0  # bonus additivo (es: +0.2 = +20%)
                def_bonus = 0.0
                spd_bonus = 0.0
                
                # Apply individual abilities
                for ability in team_abilities:
                    if not ability:
                        continue
                    
                    # Create a temporary team dict with current bonuses applied for stat comparisons
                    team_with_bonuses = team.copy()
                    team_with_bonuses["atk"] = int(team["atk_base"] * (1 + atk_bonus))
                    team_with_bonuses["def"] = int(team["def_base"] * (1 + def_bonus))
                    team_with_bonuses["spd"] = int(team["spd_base"] * (1 + spd_bonus))
                    team_with_bonuses["name"] = "Team"
                    
                    result = apply_ability(
                        ability,
                        team_with_bonuses,
                        boss,
                        team_flags,
                        current_round,
                        mode="bonus",
                        is_team_battle=True
                    )
                    
                    # Accumulate bonuses
                    atk_bonus += result["bonuses"]["atk"]
                    def_bonus += result["bonuses"]["def"]
                    spd_bonus += result["bonuses"]["spd"]
                    
                    # Add messages to log
                    round_log.extend(result["messages"])
                    
                    # Update team HP if healed
                    team["hp"] = team_with_bonuses["hp"]
                
                # ===== APPLICA TUTTI I BUFF ALLE STATS =====
                team["atk"] = int(team["atk_base"] * (1 + atk_bonus))
                team["def"] = int(team["def_base"] * (1 + def_bonus))
                team["spd"] = int(team["spd_base"] * (1 + spd_bonus))
                
                # Calculate damage
                dmg = max(1, int(team["atk"] - boss["def"] * 0.5))
                
                # Lunacia speed bonus
                if "speed_bonus" in team_abilities and team["spd"] > boss["spd"]:
                    bonus = int(team["atk"] * 0.5)
                    dmg += bonus
                    round_log.append(f"💨 **Lunacia's speed bonus!** +{bonus} damage")
                
                # Sidmi bonus damage (after turn 3)
                if team_flags.get("sidmi_active", False):
                    bonus = int(team["atk"] * 0.5)
                    dmg += bonus
                
                boss["hp"] -= dmg
                round_log.append(f"⚔️ **Team attacks!** Deals `{dmg}` damage")
                
                # Lifesteal
                if team_flags["lifesteal_active"]:
                    heal = int(dmg * 0.5)
                    team["hp"] = min(team["hp_max"], team["hp"] + heal)
                    round_log.append(f"🩸 **Lifesteal!** +{heal} HP")
                
                # Thundia paralyze (first round only)
                if "paralyze" in team_abilities and current_round == 1:
                    team_flags["paralyze_turns"] = 2
                    round_log.append(f"⚡ **Thundia paralyzes the boss for 2 turns!**")
                
                # Check if boss phase changes
                if boss["hp"] <= 0 and current_phase < len(phases) - 1:
                    current_phase += 1
                    boss = get_boss_stats(current_phase)
                    # Update composite image URL for new phase
                    composite_image_url = composite_urls.get(current_phase + 1, boss["image"])
                    round_log.append(f"\n💀 **{boss_data['name']} transforms!** Phase {current_phase + 1}/{len(phases)}!")
                    round_log.append(f"Boss HP restored! New stats: ATK `{boss['atk']}` DEF `{boss['def']}` SPD `{boss['spd']}`")
            
            else:  # Boss turn
                if boss["hp"] <= 0:
                    continue
                
                # Check if boss is paralyzed
                if team_flags["paralyze_turns"] > 0:
                    team_flags["paralyze_turns"] -= 1
                    round_log.append(f"⚡ **{boss_data['name']} is paralyzed!** Cannot attack. ({team_flags['paralyze_turns']} turns left)")
                    continue
                
                # Boss attacks
                dmg = max(1, int(boss["atk"] - team["def"] * 0.5))
                team["hp"] -= dmg
                team["hp"] = max(0, team["hp"])
                round_log.append(f"👹 **{boss_data['name']} attacks!** Deals `{dmg}` damage")
                
                # Verbena survive
                if team["hp"] <= 0 and "survive" in team_abilities and not team_flags["verbena_survived"]:
                    team["hp"] = 1
                    team_flags["verbena_survived"] = True
                    round_log.append(f"💫 **Verbena refuses to fall!** Team survives with 1 HP!")
        
        # Decrement timed buffs (le stats vengono ricalcolate ogni turno con il sistema additivo)
        if team_flags["ruri_turns"] > 0:
            team_flags["ruri_turns"] -= 1
            if team_flags["ruri_turns"] == 0:
                round_log.append("🛡️ Ruri's DEF boost expired.")
        
        if team_flags["luminalia_turns"] > 0:
            team_flags["luminalia_turns"] -= 1
            if team_flags["luminalia_turns"] == 0:
                round_log.append("💨 Luminalia's SPD boost expired.")
        
        # Update embed
        embed = discord.Embed(
            title=f"👹 BOSS BATTLE — {boss_data['name']} 👹",
            description="\n".join(round_log),
            color=discord.Color.green() if actor == "team" else discord.Color.red()
        )
        
        team_stats = (
            f"**{team['name']}**\n"
            f"HP: `{team['hp_max']}` | ATK: `{team['atk']}` | DEF: `{team['def']}` | SPD: `{team['spd']}`\n"
            f"{create_hp_bar(team['hp'], team['hp_max'])} `{team['hp']}/{team['hp_max']}`"
        )
        embed.add_field(name="👥 Your Team", value=team_stats, inline=False)
        
        boss_stats = (
            f"**{boss['name']}**\n"
            f"HP: `{boss['hp_max']}` | ATK: `{boss['atk']}` | DEF: `{boss['def']}` | SPD: `{boss['spd']}`\n"
            f"{create_hp_bar(max(0, boss['hp']), boss['hp_max'])} `{max(0, boss['hp'])}/{boss['hp_max']}`"
        )
        embed.add_field(name="👹 Boss", value=boss_stats, inline=False)
        embed.set_image(url=composite_image_url)  # Use the same composite image URL
        
        await message.edit(embed=embed)
        await asyncio.sleep(1.5)
    
    # Determine winner
    if team["hp"] > 0 and boss["hp"] <= 0 and current_phase >= len(phases) - 1:
        winner = "team"
    elif team["hp"] <= 0:
        winner = "boss"
    else:
        winner = "draw"
    
    return {
        "winner": winner,
        "rounds": current_round,
        "team_hp": team["hp"],
        "boss_hp": boss["hp"],
        "message": message,
        "boss_data": boss_data
    }

@bot.command(name="boss")
@commands.cooldown(1, 5, commands.BucketType.user)
async def boss_cmd(ctx, boss_number: int = None):
    """Start a boss battle with your team. Usage: -boss [number]"""
    user = ensure_user(ctx.author.id)
    
    # Check stamina
    if user.get("stamina", 0) < 15:
        await ctx.send("❌ Not enough stamina. You need **15** stamina for boss battles.")
        return
    
    # Check if team is set
    team_ids = user.get("team", [])
    if len(team_ids) != 3:
        await ctx.send("❌ You need to set a team of 3 cards first! Use `-team set <card1> <card2> <card3>`")
        return
    
    # Check if all positions are filled (no None values)
    if any(id is None for id in team_ids):
        await ctx.send("❌ Your team has empty slots! Use `-team set` to fill all 3 positions before fighting bosses.")
        return
    
    # Get team cards
    team_cards = []
    for instance_id in team_ids:
        for c in user["inventory"]:
            if c.get("instance_id") == instance_id:
                team_cards.append(c)
                break
    
    if len(team_cards) != 3:
        await ctx.send("❌ Some cards in your team are missing. Please set a new team with `-team`.")
        return
    
    # If no boss specified, show available bosses
    if boss_number is None:
        unlocked = user.get("boss_unlocked", 1)
        boss_list = []
        for i, boss in enumerate(BOSSES, 1):
            status = "🔓" if i <= unlocked else "🔒"
            phase1 = boss["phases"][0]
            boss_list.append(f"{status} `{i}.` **{boss['name']}** — HP: {phase1['hp']} | ATK: {phase1['atk']} | Reward: {boss['rewards']['guaranteed_rarity']} card")
        
        await ctx.send(
            f"👹 **Available Bosses** (Unlocked: {unlocked}/{len(BOSSES)})\n\n" +
            "\n".join(boss_list) +
            f"\n\nUse `-boss <number>` to fight!"
        )
        return
    
    # Validate boss number
    if boss_number < 1 or boss_number > len(BOSSES):
        await ctx.send(f"❌ Invalid boss number. Valid range: 1-{len(BOSSES)}")
        return
    
    unlocked = user.get("boss_unlocked", 1)
    if boss_number > unlocked:
        await ctx.send(f"❌ Boss {boss_number} is locked! You need to defeat Boss {unlocked} first.")
        return
    
    boss_data = BOSSES[boss_number - 1]
    
    # Deduct stamina
    user["stamina"] -= 15
    await save_data()
    
    # Run the battle
    result = await run_boss_battle(ctx, team_cards, boss_data, user)
    
    # Handle result
    message = result["message"]
    
    if result["winner"] == "team":
        # Victory!
        rewards = boss_data["rewards"]
        gold_gain = rewards["gold"]
        exp_gain = rewards["exp"]
        guaranteed_rarity = rewards["guaranteed_rarity"]
        
        # Give rewards
        user["gold"] = user.get("gold", 0) + gold_gain
        user["exp"] = user.get("exp", 0) + exp_gain
        
        # Give guaranteed card
        random_char = random.choice(CHARACTERS)
        new_card = create_card_instance(random_char, guaranteed_rarity)
        user["inventory"].append(new_card)
        
        # Give EXP to team cards
        for card in team_cards:
            card["exp"] = card.get("exp", 0) + exp_gain
            # Level up card if possible
            while card.get("level", 1) < card.get("max_level", 30):
                need = 100 * card.get("level", 1)
                if card.get("exp", 0) >= need:
                    card["exp"] -= need
                    card["level"] += 1
                else:
                    break
        
        # Unlock next boss
        if boss_number == unlocked and unlocked < len(BOSSES):
            user["boss_unlocked"] = unlocked + 1
        
        lvl_msgs = maybe_level_up_user(user)
        await save_data()
        
        embed = discord.Embed(
            title=f"👹 BOSS BATTLE — {boss_data['name']} 👹",
            description=f"**🎉 VICTORY! 🎉**\nYou defeated {boss_data['name']} in {result['rounds']} rounds!",
            color=discord.Color.gold()
        )
        
        reward_text = f"💰 +{gold_gain} Gold\n⭐ +{exp_gain} EXP\n🎴 **{new_card['name']}** ({guaranteed_rarity})"
        if boss_number == unlocked and unlocked < len(BOSSES):
            reward_text += f"\n🔓 **Boss {unlocked + 1} unlocked!**"
        if lvl_msgs:
            reward_text = "\n".join(lvl_msgs) + "\n" + reward_text
        
        embed.add_field(name="🎁 Rewards", value=reward_text, inline=False)
        embed.set_image(url=boss_data["phases"][-1]["image"])
        
        await message.edit(embed=embed)
    
    elif result["winner"] == "boss":
        # Defeat
        embed = discord.Embed(
            title=f"👹 BOSS BATTLE — {boss_data['name']} 👹",
            description=f"**💀 DEFEAT 💀**\nYour team was defeated in {result['rounds']} rounds.",
            color=discord.Color.dark_red()
        )
        embed.set_image(url=boss_data["phases"][0]["image"])
        
        await message.edit(embed=embed)
        await ctx.send("💀 You lost the boss battle. Try leveling up your team!")
    
    else:
        # Draw
        embed = discord.Embed(
            title=f"👹 BOSS BATTLE — {boss_data['name']} 👹",
            description=f"**⚖️ DRAW ⚖️**\nBattle ended in a draw after {result['rounds']} rounds.",
            color=discord.Color.orange()
        )
        await message.edit(embed=embed)

@bot.command(name="give")
async def give_cmd(ctx, member: discord.Member, amount: int):
    """Give gold to another user. Usage: -give @user <amount>"""
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't give gold to yourself!")
        return
    
    if member.bot:
        await ctx.send("❌ You can't give gold to a bot!")
        return
    
    giver = ensure_user(ctx.author.id)
    receiver = ensure_user(member.id)
    
    if amount <= 0:
        await ctx.send("❌ Amount must be positive!")
        return
    
    if giver.get("gold", 0) < amount:
        await ctx.send(f"❌ You don't have enough gold! You have **{giver.get('gold', 0)}** gold.")
        return
    
    # Transfer gold
    giver["gold"] -= amount
    receiver["gold"] = receiver.get("gold", 0) + amount
    
    await save_data()
    await ctx.send(f"💰 **Gift sent!**\n{ctx.author.mention} gave **{amount}** gold to {member.mention}!")

@bot.command(name="duel")
async def duel_cmd(ctx, member: discord.Member):
    """Challenge another user to a PvP duel. Usage: -duel @user"""
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't duel yourself!")
        return
    
    if member.bot:
        await ctx.send("❌ You can't duel a bot!")
        return
    
    challenger_data = ensure_user(ctx.author.id)
    challenged_data = ensure_user(member.id)
    
    # Check both have selected cards
    if not challenger_data.get("selected"):
        await ctx.send("❌ You don't have a card selected! Use `-select <number>` first.")
        return
    
    if not challenged_data.get("selected"):
        await ctx.send(f"❌ {member.mention} doesn't have a card selected!")
        return
    
    # Get selected cards
    challenger_card = None
    for c in challenger_data["inventory"]:
        if c["instance_id"] == challenger_data["selected"]:
            challenger_card = c
            break
    
    challenged_card = None
    for c in challenged_data["inventory"]:
        if c["instance_id"] == challenged_data["selected"]:
            challenged_card = c
            break
    
    if not challenger_card or not challenged_card:
        await ctx.send("❌ Error finding selected cards.")
        return
    
    # Send duel request with buttons
    view = DuelView(ctx.author, member, timeout=60)
    msg = await ctx.send(
        f"⚔️ **DUEL REQUEST**\n"
        f"{ctx.author.mention} challenges {member.mention} to a duel!\n\n"
        f"**{ctx.author.name}**: {challenger_card['name']} ({challenger_card['rarity']}) Lv{challenger_card.get('level', 1)}\n"
        f"**{member.name}**: {challenged_card['name']} ({challenged_card['rarity']}) Lv{challenged_card.get('level', 1)}\n\n"
        f"{member.mention}, do you accept?",
        view=view
    )
    
    await view.wait()
    
    if view.declined:
        await msg.edit(content=f"❌ {member.mention} declined the duel.", view=None)
        return
    
    if not view.accepted:
        await msg.edit(content=f"⏰ Duel request timed out.", view=None)
        return
    
    # DUEL ACCEPTED - Run the battle!
    await msg.edit(content=f"⚔️ **DUEL STARTING!**\n{ctx.author.mention} vs {member.mention}", view=None)
    await asyncio.sleep(1.0)
    
    # Run the battle using the shared battle logic (PvP mode)
    result = await run_battle(ctx, challenger_card, challenged_card, ctx.author, member, is_pvp=True, message=msg)
    
    # Display final result
    p1 = result["p1"]
    p2 = result["p2"]
    
    if result["winner"] == 1:
        winner = ctx.author
        winner_card = p1["name"]
    elif result["winner"] == 2:
        winner = member
        winner_card = p2["name"]
    else:
        # Draw
        embed = discord.Embed(
            title=f"⚔️ DUEL ⚔️",
            description=f"**⚖️ DRAW ⚖️**\nBattle ended in a draw after {result['rounds']} rounds!",
            color=discord.Color.orange()
        )
        await msg.edit(embed=embed)
        return
    
    # Show victory message
    final_embed = discord.Embed(
        title=f"⚔️ DUEL ⚔️",
        description=f"**🏆 {winner.mention} WINS with {winner_card}!**\nBattle ended in {result['rounds']} rounds!",
        color=discord.Color.gold()
    )
    
    # Final HP display
    p1_stats = (
        f"**{ctx.author.display_name}'s {p1['name']}** `{p1['rarity']}` Level `{p1['level']}`\n"
        f"{create_hp_bar(p1['hp'], p1['hp_max'])} `{p1['hp']}/{p1['hp_max']}`"
    )
    final_embed.add_field(name="🛡️ Fighter 1", value=p1_stats, inline=False)
    
    p2_stats = (
        f"**{member.display_name}'s {p2['name']}** `{p2['rarity']}` Level `{p2['level']}`\n"
        f"{create_hp_bar(p2['hp'], p2['hp_max'])} `{p2['hp']}/{p2['hp_max']}`"
    )
    final_embed.add_field(name="⚡ Fighter 2", value=p2_stats, inline=False)
    
    if challenger_card.get("image"):
        final_embed.set_thumbnail(url=challenger_card.get("image"))
    if challenged_card.get("image"):
        final_embed.set_image(url=challenged_card.get("image"))
    
    await msg.edit(embed=final_embed)

@bot.command(name="trade")
async def trade_cmd(ctx, member: discord.Member = None):
    """Start a trade with another user. Usage: -trade @user"""
    if member is None:
        # Show current trade status
        trade = get_user_trade(ctx.author.id)
        if not trade:
            await ctx.send("❌ You don't have an active trade. Use `-trade @user` to start one.")
            return
        
        # Show trade status
        other_id = trade.get_other_user(ctx.author.id)
        other_user = await bot.fetch_user(other_id)
        
        user_offer = trade.get_offer(ctx.author.id)
        other_offer = trade.get_offer(other_id)
        
        user_data = ensure_user(ctx.author.id)
        
        # Get card names for display
        def format_cards(card_ids, user_id):
            if not card_ids:
                return "None"
            user = ensure_user(user_id)
            names = []
            for iid in card_ids:
                for c in user["inventory"]:
                    if c["instance_id"] == iid:
                        names.append(f"{c['name']} ({c['rarity']})")
                        break
            return ", ".join(names) if names else "None"
        
        your_confirm = "✅" if trade.is_confirmed(ctx.author.id) else "❌"
        their_confirm = "✅" if trade.is_confirmed(other_id) else "❌"
        
        await ctx.send(
            f"🔄 **Active Trade with {other_user.name}**\n\n"
            f"**Your Offer:** {your_confirm}\n"
            f"  💰 Gold: {user_offer['gold']}\n"
            f"  🎴 Cards: {format_cards(user_offer['cards'], ctx.author.id)}\n\n"
            f"**Their Offer:** {their_confirm}\n"
            f"  💰 Gold: {other_offer['gold']}\n"
            f"  🎴 Cards: {format_cards(other_offer['cards'], other_id)}\n\n"
            f"Use `-tr add/remove gold/cards`, `-tr confirm`, or `-tr cancel`"
        )
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't trade with yourself!")
        return
    
    if member.bot:
        await ctx.send("❌ You can't trade with a bot!")
        return
    
    # Check if either user already has an active trade
    if get_user_trade(ctx.author.id):
        await ctx.send("❌ You already have an active trade! Use `-tr cancel` to cancel it first.")
        return
    
    if get_user_trade(member.id):
        await ctx.send(f"❌ {member.mention} already has an active trade!")
        return
    
    # Send trade request with buttons
    view = TradeView(ctx.author, member, timeout=60)
    msg = await ctx.send(
        f"🔄 **TRADE REQUEST**\n"
        f"{ctx.author.mention} wants to trade with {member.mention}!\n\n"
        f"{member.mention}, do you accept?",
        view=view
    )
    
    await view.wait()
    
    if view.declined:
        await msg.edit(content=f"❌ {member.mention} declined the trade.", view=None)
        return
    
    if not view.accepted:
        await msg.edit(content=f"⏰ Trade request timed out.", view=None)
        return
    
    # Create trade session
    trade_key = f"{ctx.author.id}-{member.id}"
    active_trades[trade_key] = Trade(ctx.author.id, member.id)
    
    await msg.edit(
        content=f"✅ **Trade started between {ctx.author.mention} and {member.mention}!**\n\n"
        f"Use these commands:\n"
        f"`-tr add gold <amount>` - Add gold to your offer\n"
        f"`-tr add cards <numbers>` - Add cards (inventory numbers)\n"
        f"`-tr remove gold <amount>` - Remove gold\n"
        f"`-tr remove cards <numbers>` - Remove cards\n"
        f"`-tr confirm` - Confirm your offer\n"
        f"`-tr cancel` - Cancel the trade\n"
        f"`-trade` - View current trade status\n\n"
        f"⏰ Trade expires in 10 minutes.",
        view=None
    )

@bot.command(name="tr")
async def tr_cmd(ctx, action: str = None, item_type: str = None, *args):
    """Trade sub-commands. Usage: -tr <add/remove/confirm/cancel> [gold/cards] [amount/numbers]"""
    trade = get_user_trade(ctx.author.id)
    
    if not trade:
        await ctx.send("❌ You don't have an active trade. Use `-trade @user` to start one.")
        return
    
    if trade.is_expired():
        # Clean up expired trade
        for key in list(active_trades.keys()):
            if active_trades[key] == trade:
                del active_trades[key]
        await ctx.send("❌ Your trade has expired!")
        return
    
    user_data = ensure_user(ctx.author.id)
    offer = trade.get_offer(ctx.author.id)
    
    if action is None:
        await ctx.send("❌ Usage: `-tr <add/remove/confirm/cancel> [gold/cards] [amount/numbers]`")
        return
    
    action = action.lower()
    
    # CANCEL
    if action == "cancel":
        for key in list(active_trades.keys()):
            if active_trades[key] == trade:
                del active_trades[key]
        other_id = trade.get_other_user(ctx.author.id)
        other_user = await bot.fetch_user(other_id)
        await ctx.send(f"❌ Trade with {other_user.mention} has been cancelled by {ctx.author.mention}.")
        return
    
    # CONFIRM
    if action == "confirm":
        trade.set_confirmed(ctx.author.id, True)
        
        if trade.both_confirmed():
            # Execute the trade!
            user1_data = ensure_user(trade.user1_id)
            user2_data = ensure_user(trade.user2_id)
            
            user1_offer = trade.user1_offer
            user2_offer = trade.user2_offer
            
            # Validate gold
            if user1_data.get("gold", 0) < user1_offer["gold"]:
                await ctx.send("❌ Trade failed: User 1 doesn't have enough gold!")
                trade.reset_confirmations()
                return
            if user2_data.get("gold", 0) < user2_offer["gold"]:
                await ctx.send("❌ Trade failed: User 2 doesn't have enough gold!")
                trade.reset_confirmations()
                return
            
            # Validate cards exist
            def get_cards_by_ids(user_data, card_ids):
                cards = []
                for iid in card_ids:
                    for c in user_data["inventory"]:
                        if c["instance_id"] == iid:
                            cards.append(c)
                            break
                return cards
            
            user1_cards = get_cards_by_ids(user1_data, user1_offer["cards"])
            user2_cards = get_cards_by_ids(user2_data, user2_offer["cards"])
            
            if len(user1_cards) != len(user1_offer["cards"]):
                await ctx.send("❌ Trade failed: Some cards from User 1 are no longer available!")
                trade.reset_confirmations()
                return
            if len(user2_cards) != len(user2_offer["cards"]):
                await ctx.send("❌ Trade failed: Some cards from User 2 are no longer available!")
                trade.reset_confirmations()
                return
            
            # Execute gold transfer
            # User1: give away their offer, receive user2's offer
            user1_data["gold"] = user1_data.get("gold", 0) - user1_offer["gold"]
            user1_data["gold"] = user1_data.get("gold", 0) + user2_offer["gold"]
            # User2: give away their offer, receive user1's offer
            user2_data["gold"] = user2_data.get("gold", 0) - user2_offer["gold"]
            user2_data["gold"] = user2_data.get("gold", 0) + user1_offer["gold"]
            
            # Execute card transfer
            for card in user1_cards:
                user1_data["inventory"].remove(card)
                # Clear selection if traded card was selected
                if user1_data.get("selected") == card["instance_id"]:
                    user1_data["selected"] = None
                user2_data["inventory"].append(card)
            
            for card in user2_cards:
                user2_data["inventory"].remove(card)
                if user2_data.get("selected") == card["instance_id"]:
                    user2_data["selected"] = None
                user1_data["inventory"].append(card)
            
            await save_data()
            
            # Clean up trade
            for key in list(active_trades.keys()):
                if active_trades[key] == trade:
                    del active_trades[key]
            
            user1 = await bot.fetch_user(trade.user1_id)
            user2 = await bot.fetch_user(trade.user2_id)
            
            await ctx.send(
                f"✅ **Trade completed!**\n\n"
                f"**{user1.name}** gave: {user1_offer['gold']} gold, {len(user1_offer['cards'])} cards\n"
                f"**{user2.name}** gave: {user2_offer['gold']} gold, {len(user2_offer['cards'])} cards"
            )
        else:
            other_id = trade.get_other_user(ctx.author.id)
            other_user = await bot.fetch_user(other_id)
            await ctx.send(f"✅ {ctx.author.mention} confirmed! Waiting for {other_user.mention} to confirm...")
        return
    
    # ADD / REMOVE
    if action not in ["add", "remove"]:
        await ctx.send("❌ Invalid action. Use `add`, `remove`, `confirm`, or `cancel`.")
        return
    
    if item_type is None:
        await ctx.send("❌ Specify `gold` or `cards`. Example: `-tr add gold 500`")
        return
    
    item_type = item_type.lower()
    
    # Reset confirmations when offer changes
    trade.reset_confirmations()
    
    if item_type == "gold":
        if not args:
            await ctx.send("❌ Specify amount. Example: `-tr add gold 500`")
            return
        
        try:
            amount = int(args[0])
        except ValueError:
            await ctx.send("❌ Invalid amount.")
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        if action == "add":
            # Check if user has enough gold
            total_offered = offer["gold"] + amount
            if total_offered > user_data.get("gold", 0):
                await ctx.send(f"❌ You don't have enough gold! You have {user_data.get('gold', 0)} gold.")
                return
            offer["gold"] += amount
            await ctx.send(f"💰 Added **{amount}** gold to your offer. Total: **{offer['gold']}** gold.")
        else:  # remove
            if amount > offer["gold"]:
                amount = offer["gold"]
            offer["gold"] -= amount
            await ctx.send(f"💰 Removed **{amount}** gold from your offer. Total: **{offer['gold']}** gold.")
    
    elif item_type == "cards":
        if not args:
            await ctx.send("❌ Specify card numbers. Example: `-tr add cards 1 3 5`")
            return
        
        sorted_inv = sort_inventory(user_data["inventory"])
        
        if action == "add":
            for num_str in args:
                try:
                    idx = int(num_str) - 1
                except ValueError:
                    await ctx.send(f"❌ Invalid card number: {num_str}")
                    continue
                
                if idx < 0 or idx >= len(sorted_inv):
                    await ctx.send(f"❌ Invalid card number: {num_str}")
                    continue
                
                card = sorted_inv[idx]
                iid = card["instance_id"]
                
                if iid in offer["cards"]:
                    await ctx.send(f"⚠️ Card #{num_str} ({card['name']}) is already in your offer.")
                    continue
                
                offer["cards"].append(iid)
                await ctx.send(f"🎴 Added **{card['name']}** ({card['rarity']}) to your offer.")
        
        else:  # remove
            for num_str in args:
                try:
                    idx = int(num_str) - 1
                except ValueError:
                    await ctx.send(f"❌ Invalid card number: {num_str}")
                    continue
                
                if idx < 0 or idx >= len(sorted_inv):
                    await ctx.send(f"❌ Invalid card number: {num_str}")
                    continue
                
                card = sorted_inv[idx]
                iid = card["instance_id"]
                
                if iid not in offer["cards"]:
                    await ctx.send(f"⚠️ Card #{num_str} ({card['name']}) is not in your offer.")
                    continue
                
                offer["cards"].remove(iid)
                await ctx.send(f"🎴 Removed **{card['name']}** ({card['rarity']}) from your offer.")
    
    else:
        await ctx.send("❌ Invalid type. Use `gold` or `cards`.")

# error handler for cooldowns
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Command on cooldown. Try again in {int(error.retry_after)} seconds.")
    else:
        print(f"Unhandled command error: {error}")

# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("ERROR: set the DISCORD_TOKEN environment variable.")
    else:
        bot.run(token)
