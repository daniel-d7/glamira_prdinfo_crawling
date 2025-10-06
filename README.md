# Glamira Product Info Crawling

This project is designed to crawl and collect product information from Glamira and related domains. It provides scripts and utilities for scraping, monitoring, and managing data collection processes.

## Features
- Full scraping pipeline for product information
- Proxy verification and management
- Monitoring and checkpoint management
- Utilities for debugging and quick testing

## Project Structure
```
main.py                  # Main entry point
requirements.txt         # Python dependencies

/data/
    input_data/
        domains_cleaned.csv   # List of cleaned domains to crawl

/scripts/
    checkpoint_manager.py     # Manages scraping checkpoints
    monitor.py                # Monitors scraping progress
    run_full_scraping.py      # Runs the full scraping process
    start_scraping.py         # Starts scraping for a domain

/utils/
    debug_json_output.py      # Debugs JSON output
    launcher.py               # Launches utility scripts
    quick_test.py             # Quick test utilities
    test_json_output.py       # Tests JSON output
    verify_proxy_implementation.py # Verifies proxy setup
```

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```powershell
   git clone https://github.com/daniel-d7/glamira_prdinfo_crawling.git
   cd glamira_prdinfo_crawling
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Usage
- Run the main script:
  ```powershell
  python main.py
  ```
- To start full scraping:
  ```powershell
  python scripts/run_full_scraping.py
  ```
- For monitoring or checkpoint management, use the respective scripts in the `scripts/` folder.

### Data
- Place your input domains in `data/input_data/domains_cleaned.csv`.

## Utilities
- Use scripts in the `utils/` folder for debugging, testing, and proxy verification.