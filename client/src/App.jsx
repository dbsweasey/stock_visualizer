import { WebSocketProvider } from "./services/WebSocketContext";
import Dashboard from "./components/Dashboard";
import useDashboardConfig from "./hooks/UseDashboardConfig";

function App() {

  // Get config
  const { config, loading } = useDashboardConfig()

  // Could make this nicer 
  if (loading) return <p>Loading...</p>
  return (
    <WebSocketProvider>
      <Dashboard symbols={config.symbols} intervals={config.intervals}/>
    </WebSocketProvider>
  );
}

export default App;
