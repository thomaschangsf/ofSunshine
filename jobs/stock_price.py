import ray
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time
import requests
from requests.exceptions import RequestException
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_yfinance_session():
    """Setup a custom session for yfinance with retry logic."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    return session

@ray.remote
def fetch_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock price data for a given ticker using yfinance.
    This function will be executed in parallel using Ray.
    """
    try:
        logger.info(f"Fetching data for ticker: {ticker}")
        
        # Add retry logic with exponential backoff
        max_retries = 3
        base_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Create a new session for each attempt
                session = setup_yfinance_session()
                
                # Use download function instead of Ticker object
                df = yf.download(
                    tickers=ticker,
                    period="1d",  # Just get today's data
                    interval="1d",
                    progress=False,
                    session=session
                )
                
                if not df.empty:
                    latest_price = df['Close'].iloc[-1]
                    logger.info(f"Latest price for {ticker}: ${latest_price:.2f}")
                    return {
                        'ticker': ticker,
                        'price': latest_price,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'date': df.index[-1].strftime('%Y-%m-%d')
                    }
                else:
                    logger.warning(f"No data available for {ticker} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Waiting {delay} seconds before retry...")
                        time.sleep(delay)
                        continue
                    return {
                        'ticker': ticker,
                        'error': 'No data available after multiple attempts',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            except RequestException as e:
                logger.error(f"Network error fetching {ticker} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue
                raise
            except Exception as e:
                logger.error(f"Error fetching {ticker} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue
                raise
                
    except Exception as e:
        logger.error(f"Error fetching {ticker}: {str(e)}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def run_stock_price_job(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Run the stock price fetching job for multiple tickers.
    """
    logger.info(f"Starting stock price job for tickers: {tickers}")
    
    # Process tickers in smaller batches to avoid rate limiting
    batch_size = 2
    results = []
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        logger.info(f"Processing batch: {batch}")
        
        # Launch batch of futures
        futures = [fetch_stock_price.remote(ticker) for ticker in batch]
        batch_results = ray.get(futures)
        results.extend(batch_results)
        
        # Add delay between batches
        if i + batch_size < len(tickers):
            delay = 5  # seconds
            logger.info(f"Waiting {delay} seconds before next batch...")
            time.sleep(delay)
    
    logger.info(f"Job completed. Results: {results}")
    return results 