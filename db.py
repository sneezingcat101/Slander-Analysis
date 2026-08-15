import sqlite3, json

con = sqlite3.connect("sa.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

# create the data tables on first run
def init_db():
    cur.execute("""CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY,
            discord_id TEXT UNIQUE,
            usernames TEXT
        )
        """)
    
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER,
            content TEXT,
            timestamp TEXT,
            chunk_id INTEGER,
            target_id INTEGER,
            is_negative INTEGER,
            classified INTEGER DEFAULT 0,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        )
        """)
    
    con.commit()

# insert message authors data
def insert_authors(authors: dict):
    rows = []
    
    for d_id, data in authors.items():
        rows.append((data['id'], d_id, json.dumps(data['usernames'])))
    
    cur.executemany('INSERT OR IGNORE INTO authors (id, discord_id, usernames) VALUES (?, ?, ?)', rows)
    
    con.commit()

# insert parsed messages
def insert_messages(messages: list):
    rows = [(m['author_id'], m['content'], m['timestamp']) for m in messages]
    
    cur.executemany('INSERT INTO messages (author_id, content, timestamp) VALUES (?, ?, ?)', rows)
    
    con.commit()

# returns every single message
def get_all_messages() -> list:
    cur.execute('SELECT id, author_id, content, timestamp FROM messages ORDER BY timestamp')
    
    rows = cur.fetchall()
    
    return [dict(row) for row in rows]
        
# set chunk ids for every message
def set_chunk_ids(assignments: list):
    rows = [(a['chunk'], a['id']) for a in assignments]
    
    cur.executemany('UPDATE messages SET chunk_id = ? WHERE id = ?', rows)
    
    con.commit

# get a full conversation by chunk id
def get_chunk(chunk_id) -> int:
    cur.execute('SELECT id, author_id, content, timestamp FROM messages WHERE chunk_id = ?', (chunk_id,))
    
    rows = cur.fetchall()
    
    return [dict(row) for row in rows]

# returns every single message author
def get_authors():
    cur.execute('SELECT id, discord_id, usernames FROM authors ORDER BY id')
    
    rows = cur.fetchall()
    
    return [dict(row) for row in rows]