# src/config.py

import pygame
pygame.init()

# --- Dimensions de l'écran ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- Couleurs ---
WHITE = (255, 255, 255); BLACK = (0, 0, 0); RED = (255, 0, 0); GREEN = (0, 255, 0); BLUE = (0, 0, 255)
YELLOW = (255, 255, 0); CYAN = (0, 255, 255); MAGENTA = (255, 0, 255); GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50); LIGHT_GRAY = (200, 200, 200); BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144); DARK_GREEN = (0, 100, 0); SAND_YELLOW = (244, 164, 96)
WATER_BLUE = (0, 105, 148) # Bleu océan pour carte du monde
LIGHT_BLUE = (173,216,230) # Utilisé pour la barre d'XP
CHEST_COLOR = BROWN; CHEST_LOOTED_COLOR = (100,100,100)
GOBLIN_COLOR = (50,150,50); WOLF_COLOR = (100,100,100); SPIDER_COLOR = (30,30,30)
GENERIC_MONSTER_COLOR = (150,50,50); IMP_COLOR = (139,0,0)

# --- Touches ---
INTERACTION_KEY = pygame.K_e; INVENTORY_KEY = pygame.K_i; WEAPON_CYCLE_KEY = pygame.K_q
ATTACK_KEY = pygame.K_SPACE; SHOW_MONSTER_INFO_KEY = pygame.K_p; SHOW_WORLD_MAP_KEY = pygame.K_m

# --- Mini-carte ---
MINIMAP_WIDTH = 150; MINIMAP_HEIGHT = 150; MINIMAP_BORDER = 2; MINIMAP_ALPHA = 200
MINIMAP_PLAYER_DOT_COLOR = RED; MINIMAP_OBJECT_DOT_COLOR = GRAY
MINIMAP_MONSTER_DOT_COLOR = (255,165,0); MINIMAP_NPC_DOT_COLOR = BLUE

# --- Cooldowns ---
ATTACK_COOLDOWN_DURATION = 500 
PLAYER_HIT_COOLDOWN_DURATION = 1000
FPS = 60

# --- Carte du Monde (Touche M) ---
WORLD_MAP_BACKGROUND_COLOR = (34, 139, 34) # Vert pour la terre de l'île
WORLD_MAP_OCEAN_COLOR = (0, 105, 148)      # Bleu océan
WORLD_MAP_PLAYER_COLOR = YELLOW
WORLD_MAP_VILLAGE_COLOR = (255, 223, 186) # Beige clair pour les villages
WORLD_MAP_TEXT_COLOR = WHITE
WORLD_MAP_CURRENT_AREA_HIGHLIGHT_COLOR = (255, 0, 0, 100) # Rouge semi-transparent

# Coordonnées conceptuelles des villages sur une "carte du monde" de 0-1000 en x et 0-1000 en y.
VILLAGE_POSITIONS_ON_WORLD_MAP = {
    "Point de Départ (Maison)": {"x": 200, "y": 200, "name_on_map": "Départ"},
    "Zayen (Village Central)":  {"x": 450, "y": 350, "name_on_map": "Zayen"},
    "Elvenwood (Forêt Nord)":   {"x": 650, "y": 150, "name_on_map": "Elvenwood"},
    "Morvath (Village Portuaire Sud)": {"x": 550, "y": 800, "name_on_map": "Morvath"},
    "Donjon Nord":              {"x": 700, "y": 300, "name_on_map": "Donjon N."},
    "Donjon Sud":               {"x": 650, "y": 550, "name_on_map": "Donjon S."}
}

# Taille totale conceptuelle de l'île pour le mapping des positions.
TOTAL_WORLD_WIDTH_UNITS = 1000
TOTAL_WORLD_HEIGHT_UNITS = 1000

# Taille approximative (en unités de la carte du monde 0-1000) qu'une carte de jeu individuelle "occupe"
# Ajustez cette valeur si le déplacement du joueur sur la carte du monde semble trop petit ou trop grand.
# Si votre île est grande et que les cartes locales sont petites, cette valeur sera petite.
# Si l'île est petite et les cartes locales grandes, cette valeur sera plus grande.
# C'est une approximation pour la mise à l'échelle du mouvement local du joueur sur la carte globale.
MAP_FOOTPRINT_ON_WORLD_UNITS = 100 # Exemple: chaque carte locale "couvre" une zone de 100x100 sur la carte globale 0-1000.