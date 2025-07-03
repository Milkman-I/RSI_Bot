import ccxt
import pandas as pd
import ta
import logging

def fetch_coins():
    """Fetches USDT pairs from Binance"""
    excluded_currencies = [
        'EUR','EURI', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD', 'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'RUB', 'INR', 'BRL', 'ZAR', 'NGN',
        'USDC', 'BUSD', 'TUSD', 'DAI', 'UST', 'USDP', 'GUSD', 'LUSD', 'FRAX', 'SUSD', 'USDD', 'USDN', 'USDJ', 'USDK', 'EURT', 'EURS', 'XAUT', 'PAXG', 'FDUSD', 'HUSD', 'CUSD', 'CDAI', 'CUSDC', 'PAX', 'TUSD', 'BUSD', 'USDS', 'USDSB', 'USDSC', 'USDSD', 'USDSF', 'USDSG', 'USDSH', 'USDSI', 'USDSJ', 'USDSL','WBTC', 'renBTC', 'sBTC', 'pBTC', 'tBTC', 'hBTC', 'wBTC', 'aBTC', 'bBTC', 'cBTC', 'dBTC', 'eBTC', 'fBTC', 'gBTC', 'hBTC', 'iBTC', 'jBTC', 'kBTC', 'lBTC', 'mBTC','XUSD','USD1','AEUR','win','fun'
    ]
    try:
        binance = ccxt.binance()
        markets = binance.load_markets()
        usdt_pairs = [
            market['symbol'].replace('/USDT', '')
            for market in markets.values()
            if market['quote'] == 'USDT' and market['active'] and market['type'] == 'spot' and market['base'] not in excluded_currencies
        ]
        open("list.txt", "w").write("\n".join(usdt_pairs))
        return usdt_pairs[:]
    except Exception as e:
        print(f"Error fetching coins: {e}")
        return []
def coin_pirce(symbol):
    try:
        exchange = ccxt.binance()
        exchange.load_markets()
        ticker = exchange.fetch_ticker(symbol)
        return f"${ticker['last']:,.6f}"
    except:
        return None
def Check_Coin(coin):
    exchange = ccxt.binance()
    try:
        timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '1d', '1w', '1M']
        rsi_values = {}
        for tf in timeframes:
            bars = exchange.fetch_ohlcv(coin, timeframe=tf, limit=100)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            rsi_series = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
            rsi_values[tf] = round(rsi_series.iloc[-1], 2)
        print(f"RSI values for {coin}:")
        for tf, rsi in rsi_values.items():
            print(f"{tf}: {rsi}")
        if all(rsi > 50 for rsi in rsi_values.values()):
            logging.info(f"Coin {coin} has RSI values greater than 50 across all timeframes.")
            return True
        else:
            logging.info(f"Coin {coin} does not have RSI values greater than 50 across all timeframes.")
            return False    
    except Exception as e:
        logging.error(f"Error fetching data for {coin}: {e}")
        return False
    return False



