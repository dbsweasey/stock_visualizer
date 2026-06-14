import "./Intervals.css"

/**
 * Intervals
 * 
 * Handles the interval control panel for a ChartCard. Control is a callback to WebSocketContext
 * to handle unsubscribing from the old and subscribing to the new interval.
 * 
 * 
 * @param {object[]} intervals [{value, label}]
 * @param {()=>void} control
 * @param {string} selected
 */
export default function Intervals({ intervals, control, selected }) {
  return (
    <div>
      {intervals.map(({ value, label }) => (
        <button 
          className={selected === value ? "interval__btn interval__btn--active": "interval__btn"}
          key={value} 
          onClick={() => control(value)}
          disabled={selected === value}>
        {label}
        </button>
      ))}
    </div>
  );
}