import { useEffect, useState } from "react";
import { DEV_IP, PORT } from "../config";

/**
 * Checks backend to grab config. Contains which intervals and
 * symbols are available by the backend. Allows backend to be source
 * of truth.
 * 
 * @returns {object} {config, loading}
 */
export default function useDashboardConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("Fetching config...")
    fetch(`http://localhost:8000/config`)
      .then((r) => r.json())
      .then(setConfig)
      .catch((err) => console.error("Fetch failed:", err))
      .finally(() => setLoading(false));

    console.log("Config fetched:", config)
  }, [])

  return {config, loading}
}