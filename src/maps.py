# src/maps.py
from config import * # Importer toutes les constantes de config.py

# --- Fonctions pour créer des objets communs ---
def create_tree(x, y, trunk_w=20, trunk_h=40, crown_r=30):
    return {"type": "tree", "x": x, "y": y, "trunk_width": trunk_w, "trunk_height": trunk_h, "crown_radius": crown_r, "solid": True}

def create_rock(x, y, radius):
    return {"type": "rock", "x": x, "y": y, "radius": radius, "solid": True}

def create_wall(x, y, width, height, color=BROWN):
    return {"type": "wall", "x": x, "y": y, "width": width, "height": height, "color": color, "solid": True}

# --- Définitions des cartes ---
GAME_MAPS = {
    "player_house_inside": {
        "name": "Maison du Joueur", "background_color": (210,180,140),
        "world_width": SCREEN_WIDTH, "world_height": SCREEN_HEIGHT, # Taille de cette carte en pixels
        "global_offset_x": 200, # Position (coin sup gauche) de cette carte sur la carte globale 0-1000
        "global_offset_y": 200,
        "objects": [
            create_wall(0,0,800,40), create_wall(0,560,800,40), create_wall(0,40,40,520), create_wall(760,40,40,520),
            {"type":"bed","x":60,"y":60,"width":120,"height":80,"color":(205,133,63),"solid":True},
            {"type":"table","x":650,"y":70,"width":100,"height":60,"color":(160,82,45),"solid":True},
            {"type":"rug","x":325,"y":250,"width":150,"height":100,"color":(176,23,31),"solid":False},
            {"type":"player_chest","id":"home_player_chest","x":60,"y":450,"width":70,"height":50,"color":BROWN,"solid":True},
            {"type":"window","x":250,"y":40,"width":100,"height":20,"color":(173,216,230),"solid":False},
            {"type":"window","x":450,"y":40,"width":100,"height":20,"color":(173,216,230),"solid":False},
        ],
        "transition_zones": [{"rect":(370,540,60,20),"target_map_id":"nelyria_forest_home_area","target_player_x":400,"target_player_y":70}]
    },
    "nelyria_forest_home_area": {
        "name": "Forêt (Près Maison)", "background_color": LIGHT_GREEN,
        "world_width": SCREEN_WIDTH, "world_height": SCREEN_HEIGHT,
        "global_offset_x": 200, # Doit correspondre au village "Départ"
        "global_offset_y": 200,
        "objects": [create_tree(100,100), create_tree(150,200), create_tree(600,150), create_tree(700,400), create_rock(300,300,25), {"type":"house_door_marker","x":370,"y":40,"width":60,"height":20,"color":(101,67,33),"solid":False}],
        "monsters_spawn_config": [{"type":"goblin","level_range":(1,2),"count_range":(1,3)}, {"type":"wolf","level_range":(1,3),"count_range":(0,2)}],
        "transition_zones": [
            {"rect":(370,20,60,20),"target_map_id":"player_house_inside","target_player_x":400,"target_player_y":500},
            {"rect":(790,0,10,600),"target_map_id":"nelyria_forest_deeper","target_player_x":50,"target_player_y":300},
            {"rect":(0,590,800,10),"target_map_id":"zayen_village_entrance","target_player_x":400,"target_player_y":50}
        ]
    },
    "nelyria_forest_deeper": {
        "name": "Forêt Profonde", "background_color": DARK_GREEN,
        "world_width": SCREEN_WIDTH, "world_height": SCREEN_HEIGHT,
        "global_offset_x": 200 + MAP_FOOTPRINT_ON_WORLD_UNITS, # Exemple: à droite de la zone maison
        "global_offset_y": 200,
        "objects": [create_tree(50,50,25,50,35),create_tree(100,150,30,60,40),create_tree(400,300),create_rock(250,400,30)],
        "monsters_spawn_config": [{"type":"goblin_shaman","level_range":(2,4),"count_range":(1,2)}, {"type":"giant_spider","level_range":(3,5),"count_range":(1,1)}],
        "transition_zones": [{"rect":(0,0,10,600),"target_map_id":"nelyria_forest_home_area","target_player_x":750,"target_player_y":300}]
    },
    "zayen_village_entrance": {
        "name":"Entrée de Zayen", "background_color":SAND_YELLOW,
        "world_width": SCREEN_WIDTH, "world_height": SCREEN_HEIGHT,
        "global_offset_x": 440, # Près de Zayen (450, 350) mais c'est l'entrée, donc un peu avant
        "global_offset_y": 340,
        "objects": [ {"type":"house_structure","x":100,"y":100,"width":80,"height":100,"color":BROWN,"solid":True}, {"type":"house_structure","x":600,"y":150,"width":100,"height":120,"color":(180,180,180),"solid":True}, {"type":"path","x":350,"y":0,"width":100,"height":600,"color":(205,170,125),"solid":False}],
        "npcs": [{"id":"zayen_guard_1","type":"guard","x":380,"y":150,"dialogue_id":"guard_greeting_zayen"}],
        "transition_zones": [{"rect":(0,0,800,10),"target_map_id":"nelyria_forest_home_area","target_player_x":400,"target_player_y":550}, {"rect":(0,590,800,10),"target_map_id":"zayen_village_center","target_player_x":400,"target_player_y":50}]
    },
     "zayen_village_center": {
        "name": "Zayen - Centre", "background_color": SAND_YELLOW,
        "world_width": SCREEN_WIDTH, "world_height": SCREEN_HEIGHT,
        "global_offset_x": 450, # Correspond à la position de Zayen
        "global_offset_y": 350,
        "objects": [ {"type":"market_square_floor","x":200,"y":150,"width":400,"height":300,"color":(210,185,150),"solid":False}, {"type":"house_structure","id":"zayen_house_1","x":50,"y":50,"width":120,"height":100,"color":BROWN,"solid":True}, {"type":"house_structure","id":"zayen_shop","x":50,"y":200,"width":120,"height":150,"color":(100,100,200),"solid":True,"door_message":"Boutique"}, {"type":"house_structure","id":"zayen_mayor_house","x":630,"y":200,"width":150,"height":150,"color":(200,180,100),"solid":True,"door_message":"Mairie"}],
        "npcs": [{"id":"zayen_shopkeeper","type":"shopkeeper","x":100,"y":270,"dialogue_id":"shopkeeper_greeting"}, {"id":"zayen_child_1","type":"child","x":300,"y":300,"dialogue_id":"child_play"}],
        "transition_zones": [{"rect":(0,0,800,10),"target_map_id":"zayen_village_entrance","target_player_x":400,"target_player_y":550}]
    },
    # Ajoutez les autres cartes (Elvenwood, Morvath, Donjons) ici avec leurs global_offset_x/y
    # Exemple pour Elvenwood:
    "elvenwood_main": {
        "name": "Elvenwood", "background_color": DARK_GREEN, # Vert plus magique
        "world_width": SCREEN_WIDTH, "world_height": SCREEN_HEIGHT,
        "global_offset_x": 650, # Correspond à Elvenwood dans config
        "global_offset_y": 150,
        "objects": [ create_tree(100,100,15,70,30), {"type":"glowing_flower", "x":200, "y":200, "radius":10, "color":CYAN, "solid":False}], # Exemple d'objet elfique
        "npcs": [{"id":"elf_elder", "type":"elf", "x":400, "y":300, "dialogue_id":"elf_wisdom"}],
        "transition_zones": [] # À définir
    }
}

def get_map_data(map_id):
    if map_id not in GAME_MAPS:
        print(f"ERREUR : Map ID '{map_id}' non trouvé ! Utilisation de la maison.")
        return GAME_MAPS.get("player_house_inside", {}) 
    return GAME_MAPS[map_id]