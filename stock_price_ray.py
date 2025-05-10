import ray
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# Initialize Ray
ray.init()

@ray.remote
def fetch_stock_price(ticker):
    """
    Fetch stock price data for a given ticker using yfinance.
    This function will be executed in parallel using Ray.
    """
    try:
        # Get stock data for the last 5 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            return {
                'ticker': ticker,
                'price': latest_price,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                'ticker': ticker,
                'error': 'No data available',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except Exception as e:
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    # List of stock tickers to fetch
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
    
    print("Starting parallel stock price fetching...")
    start_time = time.time()
    
    # Launch parallel tasks
    futures = [fetch_stock_price.remote(ticker) for ticker in tickers]
    
    # Get results
    results = ray.get(futures)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Display results
    print("\nResults:")
    print("-" * 50)
    for result in results:
        if 'error' in result:
            print(f"{result['ticker']}: Error - {result['error']}")
        else:
            print(f"{result['ticker']}: ${result['price']:.2f}")
    
    print(f"\nExecution time: {execution_time:.2f} seconds")
    
    # Shutdown Ray
    ray.shutdown()

if __name__ == "__main__":
    main() 