import os
import psycopg2
from dotenv import load_dotenv
import sys

"""Setup script to (re)create the PostgreSQL schema for this project.

This script deletes existing tables and recreates the necessary tables.
By default it targets the 'dev' environment (use 'prod' argument to target production).
"""

def setup_database(env='dev'):
    day_limit = 31 if env == 'dev' else 24
    env_file = f'.env.{env}'
    
    if not os.path.exists(env_file):
        print(f"❌ File {env_file} not found!")
        return
    
    load_dotenv(env_file, override=True)
    
    db_url = os.getenv('DATABASE_URL')
    environment_name = 'Production' if env == 'prod' else 'Development'
    print(f"🔧 Setup {environment_name} Database with {day_limit} days...")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        # 1. Delete old tables
        print("🗑️  Deleting old tables...")
        cur.execute('DROP TABLE IF EXISTS solutions CASCADE;')
        cur.execute('DROP TABLE IF EXISTS answers CASCADE;')
        cur.execute('DROP TABLE IF EXISTS riddles CASCADE;')
        conn.commit()
        print("✅ Old tables deleted\n")
        
        # 2. Create new tables
        print("📦 Create new tables...")
        
        cur.execute(f'''
            CREATE TABLE riddles (
                id SERIAL PRIMARY KEY,
                day_number INTEGER NOT NULL UNIQUE CHECK (day_number BETWEEN 1 AND {day_limit}),
                riddle_text TEXT NOT NULL
            );
        ''')
        print("✅ `riddles` created")
        
        cur.execute('''
            CREATE TABLE answers (
                id SERIAL PRIMARY KEY,
                riddle_id INTEGER NOT NULL UNIQUE REFERENCES riddles(id) ON DELETE CASCADE,
                answer_text JSONB NOT NULL
            );
        ''')
        print("✅ `answers` created")
        
        cur.execute('''
            CREATE TABLE solutions (
                id SERIAL PRIMARY KEY,
                riddle_id INTEGER NOT NULL UNIQUE REFERENCES riddles(id) ON DELETE CASCADE,
                solution_content TEXT NOT NULL
            );
        ''')
        print("✅ `solutions` created")
        
        # 3. Create indexes
        print("\n📑 Create indexes...")
        cur.execute('CREATE INDEX idx_answers_riddle_id ON answers(riddle_id);')
        cur.execute('CREATE INDEX idx_solutions_riddle_id ON solutions(riddle_id);')
        print("✅ indexes created")
        
        conn.commit()
        print(f"\n🎉 {environment_name} database successfully created!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Issue: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    confirm = input("⚠️ Database will be reset! Continue? (yes/no): ")
    env = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    if confirm.strip().lower() in ('yes', 'y'):
        setup_database(env)
    else:
        print("❌ Cancelled!")