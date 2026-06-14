import { useState } from "react";
import ChartCard from "./ChartCard";
import "./Dashboard.css";

// Chart ID
let nextId = 1;

function makeChart(symbol = "AAPL", interval = 5) {
  return { id: nextId++, symbol, interval };
}

/**
 * Dashboard
 * 
 * Manages an ordered list of active charts.
 * Each is identified by an id so adding an removing does
 * not create rendering confusion
 * 
 * @param {string[]} symbols 
 * @param {object[]} invertals [{label, value}]
 */
export default function Dashboard({ symbols, intervals }) {
  const [charts, setCharts] = useState([makeChart()]);

  // Adds chart to existing list
  function addChart() {
    setCharts((prev) => [...prev, makeChart()]);
  }

  // Removes chart, by ID
  function removeChart(id) {
    setCharts((prev) => prev.filter((c) => c.id !== id));
  }

  return (
    <div className="dashboard">
      <div className="dashboard__toolbar">
        <h1 className="dashboard__heading">Gooper Stocks Dashboard</h1>
        <button className="dashboard__add-btn" onClick={addChart}>
          + Add Chart
        </button>
      </div>

      {/* Grid of charts */}
      <div className="dashboard__grid">
        {charts.map((chart) => (
          <ChartCard
            key={chart.id}
            initialSymbol={chart.symbol}
            initialInterval={chart.interval}
            symbols={symbols}
            intervals={intervals}
            onRemove={() => removeChart(chart.id)}
          />
        ))}
      </div>
      
      {/* If the user has no charts. */}
      {charts.length === 0 && (
        <div className="dashboard__empty">
          <p>No charts yet.</p>
          <button onClick={addChart}>Add a Chart</button>
        </div>
      )}
    </div>
  );
}