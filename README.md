# Stock Visualizer

![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)![FastAPI](https://img.shields.io/badge/fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)![NPM](https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white)


WebSocket based live stocks dashboard. Supports several symbols and 7 candle intervals, including 1 second candles. Built with FastAPI, Python, and React. Leverages Alpaca for live stock data and TradingView for sleek candle charts. Manages trade bucketing based on intervals, handles empty candles, overcomes network jitters and lag, and allows concurrent charts.

## Overview

The Stock Visualizer allows users to view multiple live stock charts at once. The ability to switch symbol and candle interval is seamless.

Live data is streamed from Alapca (https://alpaca.markets/). It is then bucketed into intervals, transformed into candle data, and cached. Candles are broadcast to the frontend based on subscriptions. Each subscription is a combination of symbol and interval and corresponds 1-to-1 to a chart. 

Each chart is built using TradingView (https://www.tradingview.com/). They provide sleek, customizable charts with timestamps, current price indicators, color-coded candles, and intuitive panning and zooming. 

### Symbols
Supports 7 symbols:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOG (Google)
- AMZN (Amazon)
- NVDA (NVIDIA)
- META (Meta)
- TSLA (Tesla)

### Intervals
The architecture supports any number of intervals spanning any amount of time; these are the 7 I've chosen for short-term trading. 
- 1 second
- 5 second
- 15 second
- 1 minute
- 5 minute
- 15 minute
- 1 hour

## Demo
Waiting until market opens to capture video.

## Features
- Live market data
- Per symbol per interval WebSocket subscriptions
- Any number of charts
- Candles cached since server startup
- Handles network jitters
- Gracefully displays empty candles
- Backend WebSocket subscription map with clean disconnects/unsubscribes
- Backend logging

## Architecture
Work in progress

## Tech Stack
### Backend
- Python 3.10.0
- FastAPI
- asyncio
- pip
- alpaca-py
- logging

### Frontend
- JavaScript
- React
- Vite
- WebSockets
- TradingView
- NPM

## Motivation
Stocks, trading, and economics in general have always been interesting to me. Smart investing is a great way to build wealth and become financially secure, and the market has an unimaginable amount of data. That combination makes it a topic worth exploring.

This project provided me with an opportunity to work through the fun challenge of combining live candle updates and candle closures across multiple different intervals while also managing incoming market data.

I want to add AI elements to analyze each chart with technical indicators, market context and sentiment, and provide entry and exit points. 

## Project Structure
```
stock_visualizer/
├── server/
│   ├── engine/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── websocket/
│   ├── alpaca_test.py (exploring functionality and data structure)
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
│
├── client/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── cards/
│   │   │   ├── clients/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Dropdown.tsx
│   │   │   ├── Header.css
│   │   │   ├── Header.tsx
│   │   │   └── PlayButton.tsx
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── config.js
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── eslint.config.js
│   └── vite.config.js
│
└── README.md
```

## Future Improvemenmts
- Implement Redis cache for persistence
- Use Alpaca historical data for long-term trading
- tracemalloc for memory optimization
- Add technical indicators
- Agentic capabilities for technical indicators, market sentiment, etc.

