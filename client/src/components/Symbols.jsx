import "./Symbols.css";

/**
 * Symbols
 * 
 * Handles the symbol drop down in each ChartCard. changeSymbol is callback to WebSocketContext
 * to handle unsubscribing from the old and subscribing to the new symbol.
 * 
 * @param {string[]} symbols
 * @param {()=>void} changeSymbol 
 */
export default function Symbols({symbols, changeSymbol}, initial) {
  return (
    <div>
        <select className="symbol__dropdown" onChange={(e) => changeSymbol(e.target.value)}>
          {symbols.map(symbol => (
            <option
              value={symbol} 
              key={symbol}
              className="symbol__dropdown">
            {symbol}
            </option> 
          ))}
      </select>
    </div>
  )
}
