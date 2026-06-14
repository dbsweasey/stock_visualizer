import { useState } from "react";
import PriceChart from "./PriceChart";
import Intervals from "./Intervals";
import Symbols from "./Symbols";


/**
 * ChartCard
 * 
 * Handles one chart slot with its own changeable symbol and interval.
 * When changed, PriceChart's useChartSubscription automatically unsubscribes to the 
 * old, the subscribes to the new pairing.
 * 
 * @param {string} initialSymbol
 * @param {number} initialInterval
 * @param {string[]} symbols
 * @param {object[]} intervals [{label, value}]
 * @param {()=>void} onRemove
 */
export default function ChartCard({
  initialSymbol = "AAPL",
  initialInterval = 5,
  symbols,
  intervals,
  onRemove,
}) {
  const [symbol, setSymbol] = useState(initialSymbol);
  const [interval, setInterval] = useState(initialInterval);

  // Converts interval (seconds) to a long string for display (5 -> 5 seconds)
  function getIntervalLabel(seconds) {
    if (seconds >= 3600) {
      const h = seconds / 3600;
      return `${h} hour${h > 1 ? "s" : ""}`;
    }
    if (seconds >= 60) {
      const m = seconds / 60;
      return `${m} minute${m > 1 ? "s" : ""}`;
    }
    return `${seconds} second${seconds > 1 ? "s" : ""}`;
  }

  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <span className="chart-card__title">
          {symbol}{" "}
          <span className="chart-card__interval">
            · {getIntervalLabel(interval)}
          </span>
        </span>
        <button className="chart-card__remove" onClick={onRemove} title="Remove chart">
          ✕
        </button>
      </div>

      <PriceChart symbol={symbol} interval={interval} />

      <div className="chart-card__controls">
        <Intervals intervals={intervals} control={setInterval} selected={interval} />
        <Symbols symbols={symbols} changeSymbol={setSymbol} initial={initialSymbol} />
      </div>
    </div>
  );
}