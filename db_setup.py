import sqlite3
from colorama import Fore, Style, init

# Initialize colorama for clean output
init(autoreset=True)

DB_FILE = 'financial_data.db'
COMPANY_DATA = [
    ('Apple', 'Big Fruit Corp', 'AAPL'),
    ('Microsoft', 'Redmond Tech', 'MSFT'),
    ('Google', 'Search Giant', 'GOOGL'),
    ('Tesla', 'Electric Car Co.', 'TSLA'),
    ('Amazon', 'Online Shopping Giant', 'AMZN')
]

def setup_database():
    """Creates the SQLite database and populates the company_metadata table."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 1. Create the table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_metadata (
                id INTEGER PRIMARY KEY,
                official_name TEXT,
                common_name TEXT,
                ticker TEXT UNIQUE
            )
        """)
        conn.commit()
        print(f"{Fore.CYAN}--- Database Setup ---{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Table 'company_metadata' ensured.{Style.RESET_ALL}")
        
        # 2. Insert mock data
        inserted_count = 0
        for official, common, ticker in COMPANY_DATA:
            try:
                cursor.execute("""
                    INSERT INTO company_metadata (official_name, common_name, ticker)
                    VALUES (?, ?, ?)
                """, (official, common, ticker))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # Skip if ticker already exists
                pass 
                
        conn.commit()
        print(f"{Fore.GREEN}✅ Inserted/Updated {inserted_count} mock companies.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}❌ Database Setup Error: {e}{Style.RESET_ALL}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    setup_database()




