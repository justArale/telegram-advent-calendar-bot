import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # create tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS riddles (
            id SERIAL PRIMARY KEY,
            day_number INTEGER NOT NULL UNIQUE CHECK (day_number BETWEEN 1 AND 24),
            riddle_text TEXT NOT NULL
        );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id SERIAL PRIMARY KEY,
            riddle_id INTEGER NOT NULL REFERENCES riddles(id) ON DELETE CASCADE,
            answer_text JSONB NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id SERIAL PRIMARY KEY,
            riddle_id INT NOT NULL REFERENCES riddles(id) ON DELETE CASCADE,
            solution_content TEXT NOT NULL
        );
    ''')
    
    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_answers_riddle_id ON answers(riddle_id);
    ''')

    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_solutions_riddle_id ON solutions(riddle_id);
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables successfully created!")

if __name__ == "__main__":
    create_tables()