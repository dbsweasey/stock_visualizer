import { useEffect, useRef, useCallback } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";
import { useChartSubscription } from "../hooks/useChartSubscription";

/**
 * 
 * PriceChart
 * 
 * Responsible for rendering chart. Separate from communication channels.
 * Data is ingested from useChartSubscription
 * 
 * @param {string} symbol
 * @param {number} interval (seconds)
 */
export default function PriceChart({ symbol, interval }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);

  // ── Chart init and cleanup ───────────────────────────────────────────────
  useEffect(() => {
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 400,
      layout: { background: { color: "#0f1117" }, textColor: "#c9d1d9" },
      grid: {
        vertLines: { color: "#1e2330" },
        horzLines: { color: "#1e2330" },
      },
      timeScale: { timeVisible: true, secondsVisible: true },
    });

    const series = chart.addSeries(CandlestickSeries);
    chartRef.current = chart;
    seriesRef.current = series;

    // Resize handler
    const ro = new ResizeObserver(() => {
      chart.applyOptions({ width: containerRef.current.clientWidth });
    });
    ro.observe(containerRef.current);

    // Cleanup
    return () => {
      ro.disconnect();
      chart.remove();
    };
  }, []);

  // ── Subscription handlers ────────────────────────────────────────────────
  const onSnapshot = useCallback((candles) => {
    seriesRef.current?.setData(candles);
  }, []);

  const onUpdate = useCallback((candle) => {
    seriesRef.current?.update(candle);
  }, []);

  useChartSubscription(symbol, interval, { onSnapshot, onUpdate });

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "400px" }}
    />
  );
}
