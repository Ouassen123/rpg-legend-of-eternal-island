# src/database.py
import sqlite3
import os # Pour s'assurer que le dossier db existe

DB_PATH = 'db'
DB_NAME = os.path.join(DB_PATH, 'game.db')

def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH) # Crée le dossier db s'il n'existe pas
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            gender TEXT,
            x INTEGER,
            y INTEGER,
            inventory TEXT,
            xp INTEGER,
            level INTEGER,
            max_xp INTEGER,
            hp INTEGER,
            max_hp INTEGER,
            current_weapon_index INTEGER,
            current_map_id TEXT,
            chest_inventory TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS looted_chests (
            chest_id TEXT PRIMARY KEY, 
            is_looted INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_player(player):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    player_data_tuple = player.save_data()
    cursor.execute('''
        INSERT OR REPLACE INTO player 
        (name, gender, x, y, inventory, xp, level, max_xp, hp, max_hp, current_weapon_index, current_map_id, chest_inventory)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', player_data_tuple)
    conn.commit()
    conn.close()

def load_player(player_name="Hero"): # Nom par défaut si aucun n'est spécifié
    if not os.path.exists(DB_NAME): # Si la DB n'existe pas, pas de sauvegarde
        return None
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, gender, x, y, inventory, xp, level, max_xp, hp, max_hp, current_weapon_index, current_map_id, chest_inventory 
        FROM player WHERE name = ?
    ''', (player_name,))
    data = cursor.fetchone()
    conn.close()
    return data

def mark_chest_as_looted(map_id, chest_identifier_in_map_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    chest_db_id = f"{map_id};{chest_identifier_in_map_data}"
    cursor.execute("INSERT OR REPLACE INTO looted_chests (chest_id, is_looted) VALUES (?, 1)", (chest_db_id,))
    conn.commit()
    conn.close()

def is_chest_looted(map_id, chest_identifier_in_map_data):
    if not os.path.exists(DB_NAME):
        return False
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    chest_db_id = f"{map_id};{chest_identifier_in_map_data}"
    cursor.execute("SELECT is_looted FROM looted_chests WHERE chest_id = ?", (chest_db_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 1