import requests
from datetime import datetime
from database import CryptoDatabase

class CryptoTracker:
    def __init__(self):
        self.db = CryptoDatabase()
        
        # 25 major cryptocurrencies
        self.tracked_coins = {
            "USDT": "tether",
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USDC": "usd-coin",
            "SOL": "solana",
            "XRP": "ripple",
            "BNB": "binancecoin",
            "DOGE": "dogecoin",
            "ADA": "cardano",
            "SUI": "sui",
            "LINK": "chainlink",
            "ICP": "internet-computer",
            "TRX": "tron",
            "LTC": "litecoin",
            "AVAX": "avalanche-2",
            "AAVE": "aave",
            "PEPE": "pepe",
            "APT": "aptos",
            "DOT": "polkadot",
            "NEAR": "near",
            "HBAR": "hedera-hashgraph",
            "BCH": "bitcoin-cash",
            "1INCH": "1inch",
            "ARB": "arbitrum",
            "SHIB": "shiba-inu",
            "FIL": "filecoin",
            "BONK": "bonk",
            "TON": "toncoin",
            "CRV": "curve-dao-token",
            "SEI": "sei",
            "OP": "optimism",
            "INJ": "injective-protocol",
            "FET": "fetch-ai",
            "ETC": "ethereum-classic",
            "ATOM": "cosmos",
            "ALGO": "algorand",
            "RENDER": "render-token",
            "LDO": "lido-dao",
            "FLOKI": "floki",
            "JASMY": "jasmy",
            "CHZ": "chiliz",
            "FIDA": "bonfida",
            "STX": "stacks",
            "MAGIC": "magic",
            "EOS": "eos"
}
        
        self.coingecko_url = "https://api.coingecko.com/api/v3"
    
    def fetch_all_prices(self):
        """Fetch prices for all tracked coins"""
        try:
            coin_ids = list(self.tracked_coins.values())
            url = f"{self.coingecko_url}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Store each coin's data
            for symbol, coin_id in self.tracked_coins.items():
                if coin_id in data:
                    coin_data = data[coin_id]
                    price_data = {
                        'price_usd': coin_data.get('usd', 0),
                        'price_change_24h': coin_data.get('usd_24h_change', 0)
                    }
                    self.db.store_price_data(symbol, price_data)
            
            print(f"✅ Prices updated at {datetime.now().strftime('%H:%M:%S')}")
            return True
            
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
            return False