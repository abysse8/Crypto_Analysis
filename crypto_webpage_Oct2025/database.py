import sqlite3
from datetime import datetime

class CryptoDatabase:
    def __init__(self, db_name='crypto_prices.db'):
        self.db_name = db_name
        self.max_records_per_coin = 96  # 15-min intervals * 24 hours
        self.init_database()
    
    def init_database(self):
        """Initialize database with proper schema"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price_usd REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS current_prices (
                symbol TEXT PRIMARY KEY,
                price_usd REAL NOT NULL,
                price_change_24h REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
            ON price_history(symbol, last_updated)
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def cleanup_old_data(self, symbol):
        """Remove old data beyond our 24-hour window"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM price_history WHERE symbol = ?', (symbol,))
        count = cursor.fetchone()[0]
        
        if count > self.max_records_per_coin:
            delete_count = count - self.max_records_per_coin
            cursor.execute('''
                DELETE FROM price_history 
                WHERE id IN (
                    SELECT id FROM price_history 
                    WHERE symbol = ? 
                    ORDER BY last_updated ASC 
                    LIMIT ?
                )
            ''', (symbol, delete_count))
        
        conn.commit()
        conn.close()
    
    def store_price_data(self, symbol, price_data):
        """Store price data in database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Insert into price history
        cursor.execute('''
            INSERT INTO price_history (symbol, price_usd)
            VALUES (?, ?)
        ''', (symbol, price_data['price_usd']))
        
        # Update current prices
        cursor.execute('''
            INSERT OR REPLACE INTO current_prices 
            (symbol, price_usd, price_change_24h)
            VALUES (?, ?, ?)
        ''', (symbol, price_data['price_usd'], price_data.get('price_change_24h', 0)))
        
        conn.commit()
        conn.close()
        
        # Clean up old data
        self.cleanup_old_data(symbol)
    
    def get_current_prices(self):
        """Get all current prices"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, price_usd, price_change_24h, last_updated 
            FROM current_prices 
            ORDER BY symbol
        ''')
        
        prices = {}
        for row in cursor.fetchall():
            symbol, price_usd, change_24h, last_updated = row
            prices[symbol] = {
                'price_usd': price_usd,
                '24h_change': change_24h,
                'symbol': symbol,
                'last_updated': last_updated
            }
        
        conn.close()
        return prices
    
    def get_price_history(self, symbol, hours=24):
        """Get price history for chart"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_updated, price_usd 
            FROM price_history 
            WHERE symbol = ? AND last_updated >= datetime('now', ?)
            ORDER BY last_updated ASC
        ''', (symbol, f'-{hours} hours'))
        
        history = cursor.fetchall()
        conn.close()
        return history