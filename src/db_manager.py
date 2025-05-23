import sqlite3
import os
from config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize the database and create tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    x_position REAL,
                    y_position REAL,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create game_states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    save_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    game_data TEXT,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            ''')
            
            conn.commit()

    def save_player(self, name, score=0, x_pos=0, y_pos=0):
        """Save or update player information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO players (name, score, x_position, y_position)
                VALUES (?, ?, ?, ?)
            ''', (name, score, x_pos, y_pos))
            return cursor.lastrowid

    def get_player(self, player_id):
        """Retrieve player information by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
            return cursor.fetchone()

    def update_player_position(self, player_id, x_pos, y_pos):
        """Update player's position."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET x_position = ?, y_position = ?, last_played = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (x_pos, y_pos, player_id))

    def update_score(self, player_id, new_score):
        """Update player's score."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET score = ?, last_played = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_score, player_id))

    def save_game_state(self, player_id, game_data):
        """Save current game state."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_states (player_id, game_data)
                VALUES (?, ?)
            ''', (player_id, game_data))

    def load_game_state(self, player_id):
        """Load the most recent game state for a player."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_data FROM game_states 
                WHERE player_id = ? 
                ORDER BY save_date DESC 
                LIMIT 1
            ''', (player_id,))
            result = cursor.fetchone()
            return result[0] if result else None
