import { useEffect, useRef, useCallback } from "react";
import { useWebSocket } from "../services/WebSocketContext";


/**
 * useChartSubscription
 * 
 * Subscribes to a symbol interval pair, calls provided handlers
 * whenever the backend sends a message
 * 
 * Automatically unsubscribes when symbol/interval changes,
 * then subscribes to the new pair
 * 
 * @param {string} symbol 
 * @param {number} interval 
 * @param {object} handlers 
 */
export function useChartSubscription(symbol, interval, handlers) {
  const {subscribe} = useWebSocket();

  const handlersRef = useRef(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const handleMessage = useCallback((data) => {
    const { onSnapshot, onUpdate } = handlersRef.current;

    if (data.type === "snapshot") {
      onSnapshot?.(data.candles);
    } else if (data.type === "candle_update" || data.type === "candle_closed") {
      onUpdate?.(data.candle);
    }
  }, []);

  useEffect(() => {
    if (!symbol || interval == null) return;
    // subscribe and unsubscribe, in one go
    const unsubscribe = subscribe(symbol, interval, handleMessage);
    return unsubscribe;
  }, [symbol, interval, subscribe, handleMessage]);
}