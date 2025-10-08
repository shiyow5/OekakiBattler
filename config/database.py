import sqlite3
from pathlib import Path
from config.settings import Settings

def initialize_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(Settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Characters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            magic INTEGER NOT NULL,
            luck INTEGER DEFAULT 50,
            description TEXT,
            image_path TEXT NOT NULL,
            sprite_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            battle_count INTEGER DEFAULT 0,
            win_count INTEGER DEFAULT 0
        )
    """)

    # Add luck column to existing tables if it doesn't exist
    try:
        cursor.execute("ALTER TABLE characters ADD COLUMN luck INTEGER DEFAULT 50")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Battles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS battles (
            id TEXT PRIMARY KEY,
            character1_id TEXT NOT NULL,
            character2_id TEXT NOT NULL,
            winner_id TEXT,
            battle_log TEXT,
            duration REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character1_id) REFERENCES characters (id),
            FOREIGN KEY (character2_id) REFERENCES characters (id),
            FOREIGN KEY (winner_id) REFERENCES characters (id)
        )
    """)
    
    # Battle turns table (for detailed battle analysis)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS battle_turns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            battle_id TEXT NOT NULL,
            turn_number INTEGER NOT NULL,
            attacker_id TEXT NOT NULL,
            defender_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            damage INTEGER DEFAULT 0,
            is_critical BOOLEAN DEFAULT 0,
            is_miss BOOLEAN DEFAULT 0,
            attacker_hp_after INTEGER NOT NULL,
            defender_hp_after INTEGER NOT NULL,
            FOREIGN KEY (battle_id) REFERENCES battles (id),
            FOREIGN KEY (attacker_id) REFERENCES characters (id),
            FOREIGN KEY (defender_id) REFERENCES characters (id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect(Settings.DATABASE_PATH)

def execute_query(query, params=None):
    """Execute a database query"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
            
        return result
    finally:
        conn.close()