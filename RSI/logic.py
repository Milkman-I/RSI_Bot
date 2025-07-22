import ccxt
import pandas as pd
import ta
import logging

import ta.momentum
import ta.trend

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
            market['symbol']
            for market in markets.values()
            if market['quote'] in ['USDT','BTC'] and market['active'] and market['type'] == 'spot' and market['base'] not in excluded_currencies
        ]
        open("list.txt", "w").write("\n".join(usdt_pairs))
        return usdt_pairs[:]
    except Exception as e:
        print(f"Error fetching coins: {e}")
        return []
def coin_pirce(symbol):
    """
    Fetch the current price for a given symbol
    Returns float price or None if failed
    """
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
        # Load markets first to ensure the symbol exists
        exchange.load_markets()
        
        # Check if the symbol exists in the exchange's markets
        if symbol not in exchange.markets:
            print(f"Symbol {symbol} not found in Binance markets")
            return None
            
        # Fetch the ticker
        ticker = exchange.fetch_ticker(symbol)
        if not ticker or 'last' not in ticker or ticker['last'] is None:
            print(f"No price data available for {symbol}")
            return None
            
        return float(ticker['last'])
        
    except ccxt.NetworkError as e:
        print(f"Network error while fetching price for {symbol}: {str(e)}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error while fetching price for {symbol}: {str(e)}")
    except Exception as e:
        print(f"Error fetching price for {symbol}: {str(e)}")
    
    return None
def Check_Coin(coin):
    exchange = ccxt.binance()
    try:
        timeframes = ['15m', '30m', '1h', '2h', '4h', '6h', '1d','1w']
        sma_windows = {
            '15m': 180, '30m': 120,
            '1h': 90, '2h': 100, '4h': 120, '6h': 90, '1d': 100,'1w':20
        }
        if coin.endswith('BTC'):
            timeframes = ['15m', '30m', '1h', '2h', '4h', '6h', '12h','1d']
            sma_windows = {
                '15m': 180, '30m': 120,
                '1h': 90, '2h': 100, '4h': 120, '6h': 90,'12h':50,'1d':100
            }
        rsi_values = {}
        sma_values={}
        BB=False
        for tf in timeframes:
            bars = exchange.fetch_ohlcv(coin, timeframe=tf, limit=600)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            if len(df) < sma_windows[tf]:
                print(f"Warning: Not enough data for {coin} {tf}. Need at least {sma_windows[tf]} candles, got {len(df)}")
                rsi_values[tf] = 0  # Will fail the RSI > 50 check
                sma_values[tf] = False
                continue
            rsi_series = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
            sma_calc = ta.trend.SMAIndicator(close=df["close"], window=sma_windows[tf]).sma_indicator()
            
            last_close = float(df["close"].iloc[-2])
            last_sma = float(sma_calc.iloc[-2])
            last_rsi = float(rsi_series.iloc[-2])
            
            if (tf == '1d' and coin.endswith('BTC')) or (tf == '1w' and coin.endswith('USDT')):
                bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
                bb_middle = bb.bollinger_mavg()
                last_bb_middle = float(bb_middle.iloc[-2])
                BB = last_close > last_bb_middle
                
            rsi_values[tf] = last_rsi
            sma_values[tf] = last_close > last_sma
            

            print(f"{coin} {tf}: Close={last_close:.8f}, SMA({sma_windows[tf]})={last_sma:.8f}, RSI={last_rsi:.2f}, Above_SMA={'YES' if sma_values[tf] else 'NO'}, RSI>50={'YES' if last_rsi > 50 else 'NO'}")

        rsi_condition = all(rsi > 50 for rsi in rsi_values.values())
        sma_condition = all(sma for sma in sma_values.values())
        
        print(f"\n{coin} Summary:")
        print(f"All RSI > 50: {'YES' if rsi_condition else 'NO'}")
        print(f"All Above SMA: {'YES' if sma_condition else 'NO'}")
        print(f"Above BB: {'YES' if BB else 'NO'}")
        print("-" * 50)

        if rsi_condition and sma_condition and BB:
            logging.info(f"Coin {coin} has RSI values greater than 50  and SMA across all timeframes.")
            return True
        else:
            logging.info(f"Coin {coin} does not have RSI values greater than 50 and SMA across all timeframes.")
            return False    
    except Exception as e:
        logging.error(f"Error fetching data for {coin}: {e}")
        return False
    return False
