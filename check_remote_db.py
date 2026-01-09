import os
import dj_database_url
import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_aPjBTZvw8cD2@ep-autumn-math-ahlr3cf2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    print(f"Connecting to {DATABASE_URL[:20]}...")
    config = dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    
    conn = psycopg2.connect(
        dbname=config['NAME'],
        user=config['USER'],
        password=config['PASSWORD'],
        host=config['HOST'],
        port=config['PORT']
    )
    print("Connected successfully!")
    
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    tables = cur.fetchall()
    print("\nTables found:")
    for table in tables:
        print(f"- {table[0]}")
        
    # Check Member Schema
    if ('users_member',) in tables:
        print("\nChecking users_member columns...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users_member'
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
            
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
