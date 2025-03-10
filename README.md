
# General Algorithmic Trading Library

## Overview

Modular and state aware algorithmic trading library, handling data connections through multiple market data API providers and brokerages. Generates signals through momentum and sentiment based strategies.

![Python Version](https://img.shields.io/badge/Python-3.12%2B-green)
<!-- ![License](https://img.shields.io/badge/License-MIT-yellow) -->

## 📦 Prerequisites

- Python 3.12+
- pip (Python Package Manager)
- Virtual Environment (recommended)

## 🔧 Installation

1.Clone the repository in a desired folder (or alternatively download from the same URL):

```bash
git clone https://github.com/rvanhezel/algorithmic_trading_lib.git
cd algorithmic_trading_lib
```

2.Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3.Install dependencies:

```bash
poetry install
```

4.Set up environment variables for Alpaca and Twelve Data API's:

```bash
# Create a .env file in the project root directory with:
TWELVE_DATA_KEY = your_twelve_data_key

ALPACA_KEY = your_alpaca_key
ALPACA_SECRET = your_alpaca_secret_key
```

## 🎬 Running the Application

```bash
# Run the app
python main.py
```
