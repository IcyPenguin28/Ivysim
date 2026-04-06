from loading.data_loader import POKEMON_DATA, MOVE_DATA
from models.pokemon import Pokemon
from models.move import Move


PARTY_COUNT_OFFSET = 0x2F2C


PARTY_SPECIES_OFFSET = 0x2F2D


PARTY_DATA_OFFSET = 0x2F34
PARTY_DATA_SIZE = 0x2C


PARTY_NAMES_OFFSET = 0x307E
PARTY_NAMES_SIZE  = 0xB

TRAINER_NAME_OFFSET = 0x2598
TRAINER_NAME_SIZE = 0xB

RIVAL_NAME_OFFSET = 0x25F6
RIVAL_NAME_SIZE = 0xB

SPECIES_INTERNAL_IDS = {
    1: "rhydon",
    2: "kangaskhan",
    3: "nidoran-m",
    4: "clefairy",
    5: "spearow",
    6: "voltorb",
    7: "nidoking",
    8: "slowbro",
    9: "ivysaur",
    10: "exeggutor",
    11: "lickitung",
    12: "exeggcute",
    13: "grimer",
    14: "gengar",
    15: "nidoran-f",
    16: "nidoqueen",
    17: "cubone",
    18: "rhyhorn",
    19: "lapras",
    20: "arcanine",
    21: "mew",
    22: "gyarados",
    23: "shellder",
    24: "tentacool",
    25: "gastly",
    26: "scyther",
    27: "staryu",
    28: "blastoise",
    29: "pinsir",
    30: "tangela",
    31: "missingno.",
    32: "missingno.",
    33: "growlithe",
    34: "onix",
    35: "fearow",
    36: "pidgey",
    37: "slowpoke",
    38: "kadabra",
    39: "graveler",
    40: "chansey",
    41: "machoke",
    42: "mr. mime",
    43: "hitmonlee",
    44: "hitmonchan",
    45: "arbok",
    46: "parasect",
    47: "psyduck",
    48: "drowzee",
    49: "golem",
    50: "missingno.",
    51: "magmar",
    52: "missingno.",
    53: "electabuzz",
    54: "magneton",
    55: "koffing",
    56: "missingno.",
    57: "mankey",
    58: "seel",
    59: "diglett",
    60: "tauros",
    61: "missingno.",
    62: "missingno.",
    63: "missingno.",
    64: "farfetch'd",
    65: "venonat",
    66: "dragonite",
    67: "missingno.",
    68: "missingno.",
    69: "missingno.",
    70: "doduo",
    71: "poliwag",
    72: "jynx",
    73: "moltres",
    74: "articuno",
    75: "zapdos",
    76: "ditto",
    77: "meowth",
    78: "krabby",
    79: "missingno.",
    80: "missingno.",
    81: "missingno.",
    82: "vulpix",
    83: "ninetales",
    84: "pikachu",
    85: "raichu",
    86: "missingno.",
    87: "missingno.",
    88: "dratini",
    89: "dragonair",
    90: "kabuto",
    91: "kabutops",
    92: "horsea",
    93: "seadra",
    94: "missingno.",
    95: "missingno.",
    96: "sandshrew",
    97: "sandslash",
    98: "omanyte",
    99: "omastar",
    100: "jigglypuff",
    101: "wigglytuff",
    102: "eevee",
    103: "flareon",
    104: "jolteon",
    105: "vaporeon",
    106: "machop",
    107: "zubat",
    108: "ekans",
    109: "paras",
    110: "poliwhirl",
    111: "poliwrath",
    112: "weedle",
    113: "kakuna",
    114: "beedrill",
    115: "missingno.",
    116: "dodrio",
    117: "primeape",
    118: "dugtrio",
    119: "venomoth",
    120: "dewgong",
    121: "missingno.",
    122: "missingno.",
    123: "caterpie",
    124: "metapod",
    125: "butterfree",
    126: "machamp",
    127: "missingno.",
    128: "golduck",
    129: "hypno",
    130: "golbat",
    131: "mewtwo",
    132: "snorlax",
    133: "magikarp",
    134: "missingno.",
    135: "missingno.",
    136: "muk",
    137: "missingno.",
    138: "kingler",
    139: "cloyster",
    140: "missingno.",
    141: "electrode",
    142: "clefable",
    143: "weezing",
    144: "persian",
    145: "marowak",
    146: "missingno.",
    147: "haunter",
    148: "abra",
    149: "alakazam",
    150: "pidgeotto",
    151: "pidgeot",
    152: "starmie",
    153: "bulbasaur",
    154: "venusaur",
    155: "tentacruel",
    156: "missingno.",
    157: "goldeen",
    158: "seaking",
    159: "missingno.",
    160: "missingno.",
    161: "missingno.",
    162: "missingno.",
    163: "ponyta",
    164: "rapidash",
    165: "rattata",
    166: "raticate",
    167: "nidorino",
    168: "nidorina",
    169: "geodude",
    170: "porygon",
    171: "aerodactyl",
    172: "missingno.",
    173: "magnemite",
    174: "missingno.",
    175: "missingno.",
    176: "charmander",
    177: "squirtle",
    178: "charmeleon",
    179: "wartortle",
    180: "charizard",
    181: "missingno.",
    182: "missingno.",
    183: "missingno.",
    184: "missingno.",
    185: "oddish",
    186: "gloom",
    187: "vileplume",
    188: "bellsprout",
    189: "weepinbell",
    190: "victreebel"
}


MOVE_INTERNAL_IDS = {
    1: "pound",
    2: "karate chop",
    3: "double slap",
    4: "comet punch",
    5: "mega punch",
    6: "pay day",
    7: "fire punch",
    8: "ice punch",
    9: "thunder punch",
    10: "scratch",
    11: "vice grip",
    12: "gilloutine",
    13: "razor wind",
    14: "swords dance",
    15: "cut",
    16: "gust",
    17: "wing attack",
    18: "whirlwind",
    19: "fly",
    20: "bind",
    21: "slam",
    22: "vine whip",
    23: "stomp",
    24: "double kick",
    25: "mega kick",
    26: "jump kick",
    27: "rolling kick",
    28: "sand attack",
    29: "headbutt",
    30: "horn attack",
    31: "fury attack",
    32: "horn drill",
    33: "tackle",
    34: "body slam",
    35: "wrap",
    36: "take down",
    37: "thrash",
    38: "double edge",
    39: "tail whip",
    40: "poison sting",
    41: "twineedle",
    42: "pin missile",
    43: "leer",
    44: "bite",
    45: "growl",
    46: "roar",
    47: "sing",
    48: "supersonic",
    49: "sonic boom",
    50: "disable",
    51: "acid",
    52: "ember",
    53: "flamethrower",
    54: "mist",
    55: "water gun",
    56: "hydro pump",
    57: "surf",
    58: "ice beam",
    59: "blizzard",
    60: "psybeam",
    61: "bubblebeam",
    62: "aurora beam",
    63: "hyper beam",
    64: "peck",
    65: "drill peck",
    66: "submission",
    67: "low kick",
    68: "counter",
    69: "seismic toss",
    70: "strength",
    71: "absorb",
    72: "mega drain",
    73: "leech seed",
    74: "growth",
    75: "razor leaf",
    76: "solar beam",
    77: "poison powder",
    78: "stun spore",
    79: "sleep powder",
    80: "petal dance",
    81: "string shot",
    82: "dragon rage",
    83: "fire spin",
    84: "thunder shock",
    85: "thunderbolt",
    86: "thunder wave",
    87: "thunder",
    88: "rock throw",
    89: "earthquake",
    90: "fissure",
    91: "dig",
    92: "toxic",
    93: "confusion",
    94: "psychic",
    95: "hypnosis",
    96: "meditate",
    97: "agility",
    98: "quick attack",
    99: "rage",
    100: "teleport",
    101: "night shade",
    102: "mimic",
    103: "screech",
    104: "double team",
    105: "recover",
    106: "harden",
    107: "minimize",
    108: "smokescreen",
    109: "confuse ray",
    110: "withdraw",
    111: "defense curl",
    112: "barrier",
    113: "light screen",
    114: "haze",
    115: "reflect",
    116: "focus energy",
    117: "bide",
    118: "metronome",
    119: "mirror move",
    120: "self-destruct",
    121: "egg bomb",
    122: "lick",
    123: "smog",
    124: "sludge",
    125: "bone club",
    126: "fire blast",
    127: "waterfall",
    128: "clamp",
    129: "swift",
    130: "skull bash",
    131: "spike cannon",
    132: "constrict",
    133: "amnesia",
    134: "kinesis",
    135: "soft-boiled",
    136: "high jump kick",
    137: "glare",
    138: "dream eater",
    139: "poison gas",
    140: "barrage",
    141: "leech life",
    142: "lovely kiss",
    143: "sky attack",
    144: "transform",
    145: "bubble",
    146: "dizzy punch",
    147: "spore",
    148: "flash",
    149: "psywave",
    150: "splash",
    151: "acid armor",
    152: "crabhammer",
    153: "explosion",
    154: "fury swipes",
    155: "bonemerang",
    156: "rest",
    157: "rock slide",
    158: "hyper fang",
    159: "sharpen",
    160: "conversion",
    161: "tri attack",
    162: "super fang",
    163: "slash",
    164: "substitute",
    165: "struggle"
}

# Why does gen 1 not use ASCII, just to make my life hell?
GEN1_CHARACTER_TABLE = {
    0x80: 'A',
    0x81: 'B',
    0x82: 'C',
    0x83: 'D',
    0x84: 'E',
    0x85: 'F',
    0x86: 'G',
    0x87: 'H',
    0x88: 'I',
    0x89: 'J',
    0x8A: 'K',
    0x8B: 'L',
    0x8C: 'M',
    0x8D: 'N',
    0x8E: 'O',
    0x8F: 'P',
    0x90: 'Q',
    0x91: 'R',
    0x92: 'S',
    0x93: 'T',
    0x94: 'U',
    0x95: 'V',
    0x96: 'W',
    0x97: 'X',
    0x98: 'Y',
    0x99: 'Z',
    0x9A: '(',
    0x9B: ')',
    0x9C: ':',
    0x9D: ';',
    0x9E: '[',
    0x9F: ']',
    0xA0: 'a',
    0xA1: 'b',
    0xA2: 'c',
    0xA3: 'd',
    0xA4: 'e',
    0xA5: 'f',
    0xA6: 'g',
    0xA7: 'h',
    0xA8: 'i',
    0xA9: 'j',
    0xAA: 'k',
    0xAB: 'l',
    0xAC: 'm',
    0xAD: 'n',
    0xAE: 'o',
    0xAF: 'p',
    0xB0: 'q',
    0xB1: 'r',
    0xB2: 's',
    0xB3: 't',
    0xB4: 'u',
    0xB5: 'v',
    0xB6: 'w',
    0xB7: 'x',
    0xB8: 'y',
    0xB9: 'z',
    0xBA: 'é',
    0xBB: '\'d',
    0xBC: '\'l',
    0xBD: '\'s',
    0xBE: '\'t',
    0xBF: '\'v',
    0xE0: '\'',
    0xE1: 'PK',
    0xE2: 'MN',
    0xE3: '-',
    0xE4: '\'r',
    0xE5: '\'m',
    0xE6: '?',
    0xE7: '!',
    0xE8: '.',
    0xE9: 'ァ',
    0xEA: 'ゥ',
    0xEB: 'ェ',
    0xEC: '▷',
    0xEE: '▼',
    0xEF: '♂',
    0xF1: '×',
    0xF2: '.',
    0xF3: '/',
    0xF4: ',',
    0xF5: '♀',
    0xF6: '0',
    0xF7: '1',
    0xF8: '2',
    0xF9: '3',
    0xFA: '4',
    0xFB: '5',
    0xFC: '6',
    0xFD: '7',
    0xFE: '8',
    0xFF: '9'
}


def decode_gen1_string(data : bytes):
    string = ""

    for byte in data:
        if byte == 0x50:
            # terminator character
            break
        string += GEN1_CHARACTER_TABLE.get(byte, '?')
    return string
    

def load_save(path : str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def get_party_count(save : bytes) -> int:
    return save[PARTY_COUNT_OFFSET]


def get_party_species(save : bytes, party_size : int):
    party_species = []
    for i in range(party_size):
        species_id = save[PARTY_SPECIES_OFFSET + i]
        party_species.append(species_id)
    return party_species


def parse_moves(block : bytes) -> list[str]:
    move_ids = block[8:12]
    moves = []

    for id in move_ids:
        if id == 0:
            # Empty move slot
            continue
        moves.append(MOVE_INTERNAL_IDS[id])
    return moves


def parse_nicknames(save: bytes, party_size : int):
    nicknames = []

    for i in range(party_size):
        start = PARTY_NAMES_OFFSET + i * PARTY_NAMES_SIZE
        raw = save[start:start+PARTY_NAMES_SIZE]
        nicknames.append(decode_gen1_string(raw))
    return nicknames


def parse_trainer_name(save : bytes):
    trainer_name = ""
    start = TRAINER_NAME_OFFSET
    raw = save[start:start+TRAINER_NAME_SIZE]
    trainer_name = decode_gen1_string(raw)
    return trainer_name


def parse_rival_name(save : bytes):
    rival_name = ""
    start = RIVAL_NAME_OFFSET
    raw = save[start:start+RIVAL_NAME_SIZE]
    rival_name = decode_gen1_string(raw)
    return rival_name


def parse_evs(block: bytes):
    return {
        "hp": int.from_bytes(block[17:19], "big"),
        "attack": int.from_bytes(block[19:21], "big"),
        "defense": int.from_bytes(block[21:23], "big"),
        "speed": int.from_bytes(block[23:25], "big"),
        "special": int.from_bytes(block[25:27], "big"),
    }


def parse_dvs(block: bytes):
    atk_def = block[27]
    spd_spc = block[28]

    attack = (atk_def >> 4) & 0xF
    defense = atk_def & 0xF
    speed = (spd_spc >> 4) & 0xF
    special = spd_spc & 0xF

    hp = (
        ((attack & 1) << 3) |
        ((defense & 1) << 2) |
        ((speed & 1) << 1) |
        (special & 1)
    )

    return {
        "hp": hp,
        "attack": attack,
        "defense": defense,
        "speed": speed,
        "special": special
    }


def parse_party_pokemon(save: bytes, party_size: int):
    pokemon = []
    nicknames = parse_nicknames(save, party_size)

    for i in range(party_size):
        start = PARTY_DATA_OFFSET + i * PARTY_DATA_SIZE
        block = save[start:start + PARTY_DATA_SIZE]

        level = block[33]
        # current_hp = (block[1] << 8) | block[2]
        
        moves = parse_moves(block)
        evs = parse_evs(block)
        dvs = parse_dvs(block)

        pokemon.append({
            "level": level,
            # "current_hp": current_hp,
            "moves": moves,
            "nickname": nicknames[i],
            "evs": evs,
            "dvs": dvs
        })

    return pokemon


def build_party(species_list, parsed_data):
    team = []

    for species_id, data in zip(species_list, parsed_data):

        species_name = SPECIES_INTERNAL_IDS[species_id]

        mon = Pokemon(
            species_name,
            data["level"],
            data["moves"],
            data["nickname"],
            data["evs"],
            data["dvs"]
        )

        # mon.current_hp = data["current_hp"]

        team.append(mon)

    return team


def parse_full_save(save_file: bytes):
    party_count = get_party_count(save_file)
    species = get_party_species(save_file, party_count)
    data = parse_party_pokemon(save_file, party_count)
    team : list[Pokemon] = build_party(species, data)
    trainer_name : str = parse_trainer_name(save_file)
    rival_name : str = parse_rival_name(save_file)

    formatted_team = []
    for mon in team:
        formatted_team.append({
            "species": mon.species,
            "level": mon.level,
            "moves": [m.name for m in mon.moves],
            "nickname": mon.nickname,
            "evs": list(mon.evs.values()) if isinstance(mon.evs, dict) else mon.evs,
            "dvs": list(mon.dvs.values()) if isinstance(mon.dvs, dict) else mon.dvs
        })
    
    return {
        "trainer_name": trainer_name,
        "rival_name": rival_name,
        "team": formatted_team
    }