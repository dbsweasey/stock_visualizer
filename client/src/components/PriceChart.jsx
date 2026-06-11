import { useEffect, useRef, useState } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";
import Controls from "./Controls";
import Symbols from "./Symbols";

export default function PriceChart({intervals, symbols}) {
  const chartContainerRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const wsRef = useRef(null);
//   const priceRef = useRef(100);
  const [chartInterval, setChartInterval] = useState(5);
  const [chartIntervalText, setChartIntervalText] = useState("5 seconds");
  const [chartSymbol, setChartSymbol] = useState("AAPL");

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: { background: { color: "#ffffff" }, textColor: "black" },
      grid: { vertLines: { color: "#eee" }, horzLines: { color: "#eee" } },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries);
    candleSeriesRef.current = candleSeries;

    wsRef.current = new WebSocket("ws://127.0.0.1:8000/ws");

    wsRef.current.onopen = () => {
      console.log("Connected to backend");
    };

    wsRef.current.onerror = (e) => {
      console.log(e);
    };

    wsRef.current.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      console.log(data);

      if (data.type === "chart" || data.type === "snapshot") {
        console.log("Updating chart...");
        candleSeries.setData(data.candles);
      } else if (
        data.type === "candle_update" ||
        data.type === "candle_closed"
      ) {
        candleSeries.update(data.candle);
      }
    };

    return () => {
      wsRef.current.close();
      chart.remove();
    };
  }, []);

  function getIntervalText(interval) {
    let intervalText = '';
    let reducedInterval = interval
    if (interval >= 3600) {
      reducedInterval = interval / 3600
      intervalText = 'hour'
    } else if (interval >= 60) {
      reducedInterval = interval / 60
      intervalText = 'minute'
    } else {
      intervalText += 'second'
    }
    if (reducedInterval > 1)
      intervalText += 's'
    return `${reducedInterval} ${intervalText}`
  }

  function updateInterval(interval) {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current?.send(
        JSON.stringify({
          type: "update_interval",
          symbol: chartSymbol,
          interval,
        })
      ); 
      setChartInterval(interval)
      setChartIntervalText(getIntervalText(interval))
    }
  }

  function changeSymbol(symbol) {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current?.send(
        JSON.stringify({
          type: "update_interval",
          interval: chartInterval,
          symbol,
        })
      );
      console.log(`Old Symbol: ${chartSymbol}, New Symbol: ${symbol}, Interval: ${chartInterval}`)
      setChartSymbol(symbol)
    }
  }

  return (
    <div>
      <h1>{chartSymbol} at interval {chartIntervalText}</h1>
      <div
        ref={chartContainerRef}
        style={{ width: "100%", height: "400px", marginTop: "20px" }}
      ></div>
      <Controls intervals={intervals} control={updateInterval} />
      <Symbols symbols={symbols} changeSymbol={changeSymbol} />
    </div>
  );
}
