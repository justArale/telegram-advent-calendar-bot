import os
import json
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import sys

"""Data import script for the Advent Riddle PostgreSQL database.

This script loads riddle data from a JSON file into the database tables.
It first clears existing data (riddles, answers, solutions) and then inserts fresh records.

By default, it targets the 'dev' environment (use 'prod' as an argument for production).
"""

def import_advent_data(env='dev'):
    env_file = f'.env.{env}'
    
    if not os.path.exists(env_file):
        print(f"❌ File {env_file} not found!")
        return
    
    # Load env-file
    load_dotenv(env_file, override=True)
    
    print(f"📦 Import data for: {env}")
    db_url = os.getenv('DATABASE_URL')
    
    # Load JSON-file
    json_file = f'riddle_data_{env}.json'
    
    if not os.path.exists(json_file):
        print(f"❌ File {json_file} not found!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        # Delete old data
        print(f"🗑️  Delete old {env}-data...")
        cur.execute('DELETE FROM solutions;')
        cur.execute('DELETE FROM answers;')
        cur.execute('DELETE FROM riddles;')
        conn.commit()
        print(f"✅ Old {env}-data deleted\n")
        
        for riddle in data['riddles']:
            print(f"📝 For day {riddle['day_number']}...")
            
            # 1. Set riddle
            cur.execute('''
                INSERT INTO riddles (day_number, riddle_text)
                VALUES (%s, %s)
                RETURNING id;
            ''', (riddle['day_number'], riddle['riddle_text']))
            
            riddle_id = cur.fetchone()[0]
            print(f"   ✅ Riddle ID: {riddle_id}")
            
            # 2. Set answers
            cur.execute('''
                INSERT INTO answers (riddle_id, answer_text)
                VALUES (%s, %s);
            ''', (riddle_id, Json(riddle['answers'])))
            print(f"   ✅ Set answers: {riddle['answers']}")
            
            # 3. Set solution
            cur.execute('''
                INSERT INTO solutions (riddle_id, solution_content)
                VALUES (%s, %s);
            ''', (riddle_id, riddle['solution_content']))
            print(f"   ✅ Set solution: {riddle['solution_content']}\n")
        
        conn.commit()
        print(f"🎉 All {env}-data successfully imported!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Issue with importing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    import_advent_data(env)