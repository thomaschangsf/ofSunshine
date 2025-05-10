import click
import ray
import time
import logging
from typing import List
from config import Config
from jobs.stock_price import run_stock_price_job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Ray distributed computing CLI."""
    pass

@cli.command()
@click.option('--tickers', '-t', required=True, help='Comma-separated list of stock tickers')
@click.option('--env', '-e', type=click.Choice(['local', 'kubernetes']), default='local', help='Execution environment')
def stock_price(tickers: str, env: str):
    """Run stock price fetching job."""
    # Parse tickers
    ticker_list = [t.strip().upper() for t in tickers.split(',') if t.strip()]
    
    if not ticker_list:
        logger.error("No valid tickers provided")
        return
    
    logger.info(f"Processing tickers: {ticker_list}")
    
    # Initialize Ray with appropriate configuration
    try:
        if env == 'local':
            logger.info("Initializing Ray locally...")
            ray.init(**Config.get_local_config())
        else:
            logger.info("Initializing Ray on Kubernetes...")
            ray.init(**Config.get_kubernetes_config())
        
        print(f"Starting stock price fetching job in {env} environment...")
        start_time = time.time()
        
        # Run the job
        results = run_stock_price_job(ticker_list)
        
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
    
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise
    
    finally:
        # Shutdown Ray
        logger.info("Shutting down Ray...")
        ray.shutdown()

if __name__ == '__main__':
    cli() 