import { useEffect, useRef } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";
import Controls from "./Controls";

export default function PriceChart() {
  const chartContainerRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const wsRef = useRef(null);
  const priceRef = useRef(100);

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

  function updateInterval(interval) {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current?.send(
        JSON.stringify({
          type: "update_interval",
          interval,
        })
      );
    }
  }

  return (
    <div>
      <div
        ref={chartContainerRef}
        style={{ width: "100%", height: "400px", marginTop: "20px" }}
      ></div>
      <Controls control={updateInterval} />
    </div>
  );
}
