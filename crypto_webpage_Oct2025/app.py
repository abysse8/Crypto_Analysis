import os
import schedule
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from tracker import CryptoTracker

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
tracker = CryptoTracker()

def schedule_price_updates():
    """Schedule price updates every 15 minutes"""
    def update_job():
        tracker.fetch_all_prices()
    
    # Schedule the job
    schedule.every(15).minutes.do(update_job)
    
    # Run immediately on startup
    print("🔄 Fetching initial prices...")
    update_job()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/prices')
def get_prices():
    """API endpoint to get current prices (normalized for frontend)"""
    prices = tracker.db.get_current_prices()
    
    result = []
    for symbol in tracker.tracked_coins.keys():
        if symbol in prices:
            p = prices[symbol].copy()
            # Normalize keys expected by the frontend
            result.append({
                'symbol': p.get('symbol', symbol),
                'price_usd': p.get('price_usd', None),
                # provide a consistent 24h change field for the UI
                '24h_change': p.get('price_change_24h', 0),
                'price_change_24h': p.get('price_change_24h', 0),
                'last_updated': p.get('last_updated')
            })
    
    return jsonify({
        'prices': result,
        'timestamp': datetime.now().isoformat(),
        'total_coins': len(result)
    })

@app.route('/api/history/<symbol>')
def get_history(symbol):
    """API endpoint to get price history for charts"""
    history = tracker.db.get_price_history(symbol)
    
    formatted_history = [
        {
            'timestamp': row[0],
            'price': row[1]
        }
        for row in history
    ]
    
    return jsonify({
        'symbol': symbol,
        'history': formatted_history,
        'data_points': len(history)
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    prices = tracker.db.get_current_prices()
    return jsonify({
        'status': 'healthy',
        'database_records': len(prices),
        'tracked_coins': len(tracker.tracked_coins),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Crypto Price Tracker")
    print("📊 Tracking 25 major cryptocurrencies")
    print("💾 Database: 24-hour circular buffer")
    print("⏰ Data collection: Every 15 minutes")
    print("📈 Features: Price charts with auto-scaling")
    print("🌐 Web interface: http://localhost:8888")
    print("")
    print("Make sure to run: ngrok http 8888")
    print("Then access from your phone using the ngrok URL")
    print("")
    
    # Start the scheduled price updates in a separate thread
    scheduler_thread = threading.Thread(target=schedule_price_updates, daemon=True)
    scheduler_thread.start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=8888, debug=False)