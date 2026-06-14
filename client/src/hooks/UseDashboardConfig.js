import { useEffect } from "react";

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
    fetch(`http://${DEV_IP}:${PORT}/config`)
      .then(r => r.json())
      .then(setConfig)
      .finally(() => setLoading(false));
  }, [])

  return {config, loading}
}