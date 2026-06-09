# stock_visualizer
Real-time stock visualizer with AI integration for analytics and technical indicators. Monolithic, for now

### TO-DO
[] Use following structure for server
server/
|
|-- main.py (entrypoint / very thin)
|-- config.py (graceful way of handling settings/env variables)
|
|-- models/
|   |-- tick.py
|   |-- events.py
|   |-- candle.py
|
|-- engine/
|   |-- candle_engine.py
|   |-- timeframe_aggregator.py
|
|-- services/
|   |-- candle_consumer.py
|   |-- ingest.py (keep random for now, look to finnhub later)
|
|-- websocket/
|   |-- connection_manager.py
|   |-- handlers.py
|
|-- utils/
    |-- logging.py
    |-- time.py (centralize time.now and time bucketing, future for    locales)

[] clean up code, comment, and stash unused but maybe future code (mwe.py, fastapi-sol.py, mock_data.py, etc.)
[] add logging
[] abstract any time related actions to time.py
[] generalize where possible (e.g. subscriptions)
