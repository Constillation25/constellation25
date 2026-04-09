import sqlite3
import os
import sys

def init_database():
    db_path = 'db/c25_core.db'
    
    # Ensure directory exists
    os.makedirs('db', exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Initializing C25 Core Database ===")
        
        # Create Agents Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            designation VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Tasks Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            FOREIGN KEY(agent_id) REFERENCES agents(id)
        )
        ''')
        
        # Seed Initial Data
        cursor.execute("SELECT count(*) FROM agents")
        if cursor.fetchone()[0] == 0:
            print("Seeding initial agent data...")
            agents = [
                ('Earth Ops', 'active'),
                ('Data Archivist', 'pending'),
                ('Security', 'pending'),
                ('DevOps Core', 'active'),
                ('QA Validation', 'pending')
            ]
            cursor.executemany("INSERT INTO agents (designation, status) VALUES (?, ?)", agents)
        
        conn.commit()
        print(f"Database successfully initialized at {os.path.abspath(db_path)}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database()
