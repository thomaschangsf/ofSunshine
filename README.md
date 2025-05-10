# Ray Distributed Computing Framework

This project demonstrates the use of Ray for distributed computing with support for multiple compute tasks and execution environments (local and Kubernetes).

## Features

- Modular job structure for different compute tasks
- Command-line interface for job execution
- Support for both local and Kubernetes Ray clusters
- Easy to extend with new compute jobs
- Environment-based configuration

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For Kubernetes support, create a `.env` file with your cluster configuration:
```bash
RAY_KUBERNETES_ADDRESS=kubernetes://ray-cluster
RAY_KUBERNETES_NAMESPACE=ray
RAY_IMAGE=rayproject/ray:latest
```

## Usage

### Stock Price Job

Run the stock price fetching job locally:
```bash
python main.py stock-price --tickers AAPL,GOOGL,MSFT --env local
```

Run the stock price fetching job on Kubernetes:
```bash
python main.py stock-price --tickers AAPL,GOOGL,MSFT --env kubernetes
```

### Adding New Jobs

To add a new compute job:

1. Create a new module in the `jobs` directory
2. Implement your job logic using Ray's distributed computing features
3. Add a new command to `main.py` using the Click framework

## Project Structure

```
.
├── config.py           # Configuration for different environments
├── main.py            # CLI entry point
├── requirements.txt   # Project dependencies
├── jobs/             # Compute job modules
│   └── stock_price.py # Stock price fetching job
└── .env              # Environment configuration (optional)
```

## Contributing

To add a new compute job:

1. Create a new Python module in the `jobs` directory
2. Implement your job logic using Ray's distributed computing features
3. Add a new command to `main.py` using the Click framework
4. Update the README with usage instructions for your new job 

