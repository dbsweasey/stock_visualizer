import { useState, useEffect } from "react";

import PriceChart from "./components/PriceChart";

function App() {

  const [config, setConfig] = useState(null);

  useEffect(() => {
    console.log("Fetching config...")
    fetch("http://127.0.0.1:8000/config")
      .then(r => r.json())
      .then(setConfig);
  }, [])

  if (!config) return <p>Loading...</p>
  return (
    <div>
      <PriceChart intervals = {config.intervals} symbols = {config.symbols}/>
    </div>
  );
}

export default App;
