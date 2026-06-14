import { createContext, useCallback, useContext, useEffect, useRef } from "react"
import { DEV_IP, PORT } from "../config"

/**
 * Subscription keys look like "<SYMBOL>:<INTERVAL>"
 * e.g. "AAPL:5"
 * 
 * Registry: Map<subscriptionKey, Set<(message)=>void>>
 */


// Context to be used throughout application, avoids passing around as a prop
const WebSocketContext = createContext(null);

/**
 * WebSocketProvider
 * 
 * Establishes a WebSocket context for communicating with backend
 * 
 * @param {object[]} children 
 */
export function WebSocketProvider({children}) {
  const wsRef = useRef(null);
  const registryRef = useRef(new Map());
  const reconnectTimerRef = useRef(null);

  // ── Helpers ──────────────────────────────────────────────────────────────
  function makeKey(symbol, interval) {
    return `${symbol}:${interval}`;
  }

  // Send message to appropriate callbacks
  function dispatch(symbol, interval, msg) {
    const key = makeKey(symbol, interval);
    const callbacks = registryRef.current.get(key)

    if (callbacks) {
      callbacks.forEach((cb) => cb(msg));
    }
  }

  // ── WS Lifecycle ─────────────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN 
      || wsRef.current.readyState === WebSocket.CONNECTING)) {
        return;
      }

    const ws = new WebSocket(`ws://${DEV_IP}:${PORT}/ws`);

    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to backend");

      // Resubscribe if needed
      registryRef.current.forEach((callbacks, key) => {
        if (callbacks.size > 0) {
          const [symbol, interval] = key.split(":");
          ws.send(JSON.stringify({
            type: "subscribe",
            symbol,
            interval: Number(interval)
          }));
        }
      });
    };

    // Received backend message
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { symbol, interval } = data;
        if (symbol && interval != null) {
          // Send candle_update or candle_closed event to correct Chart(s)
          dispatch(symbol, interval, data)
        }
      } catch (err) {
        console.log("Error: ", err)
      }
    };

    ws.onerror = (err) => console.error("[WS] Error:", err);

    ws.onclose = () => {
      console.warn("WS disconnected. Reconnecting in 2 seconds...");
      // Automatically reconnect
      reconnectTimerRef.current = setTimeout(connect, 2000);
    };
  }, []);

  useEffect(() => {
    connect();
    // Cleanup
    return () => {
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close()
    };
  }, [connect]);

  // ── API ──────────────────────────────────────────────────────────────────

  /**
   * Subscribe a callback to a specific symbol interval pair.
   * Sends message to backend the first time this pair is registered
   * 
   * @param {string} symbol 
   * @param {number} interval 
   * @param {()=>void} callback 
   * @returns {(string, int, ()=>void)=>void} unsubscribe function
   */
  function subscribe(symbol, interval, callback) {
    const key = makeKey(symbol, interval);

    if (!registryRef.current.has(key)) {
      registryRef.current.set(key, new Set());
    }

    const callbacks = registryRef.current.get(key)
    const isFirstSubscriber = callbacks.size === 0;
    callbacks.add(callback)

    // Check if first sub so as to not flood backend
    if (isFirstSubscriber && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "subscribe",
        symbol,
        interval: Number(interval)
      }));
    }
    
    // Cleanup, unsubscribe
    return () => unsubscribe(symbol, interval, callback);
  }

  /**
   * Remove a callback from registry. Send an unsubscribe message to backend when
   * the last is removed for a given key.
   * 
   * @param {string} symbol 
   * @param {number} interval 
   * @param {()=>void} callback 
   */
  function unsubscribe(symbol, interval, callback) {
    const key = makeKey(symbol, interval);
    const callbacks = registryRef.current.get(key);

    if (!callbacks) return;

    callbacks.delete(callback);

    // Send unsubscribe to backend
    if (callbacks.size === 0) {
      registryRef.current.delete(key);
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: "unsubscribe",
          symbol,
          interval: Number(interval)
        }));
      }
    }
  }

  /** Future message sending (if needed) */
  function send(message) {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("Socket not open. Cannot send", message)
    }
  }

  return (
    <WebSocketContext.Provider value ={{subscribe, unsubscribe, send}}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const ctx = useContext(WebSocketContext);

  if (!ctx) throw new Error("useWebSocket must be inside <WebSocketProvider");
  return ctx;
}