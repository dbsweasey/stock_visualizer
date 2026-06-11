export default function Symbols({symbols, changeSymbol }) {
  return (
    <div>
      {symbols.map(symbol => (
        <button key={symbol} onClick={() => changeSymbol(symbol)}>{symbol}</button> 
      ))}
    </div>
  )
}
