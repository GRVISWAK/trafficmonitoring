import { useEffect, useState, useCallback } from 'react';
import { Anomaly, WebSocketMessage } from '../types';
import { alarmManager } from '../utils/alarmManager';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const useWebSocket = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = useCallback(() => {
    const websocket = new WebSocket(WS_URL);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      
      const pingInterval = setInterval(() => {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.send('ping');
        }
      }, 30000);

      websocket.addEventListener('close', () => {
        clearInterval(pingInterval);
      });
    };

    websocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        if (message.type === 'anomaly_detected' && message.data) {
          // Play alarm for CRITICAL or HIGH priority anomalies
          if (message.data.alarm && (message.data.priority === 'CRITICAL' || message.data.priority === 'HIGH')) {
            alarmManager.playMultipleAlerts(message.data.priority, message.data.priority === 'CRITICAL' ? 3 : 2);
          }
          
          setAnomalies((prev: Anomaly[]) => [message.data!, ...prev].slice(0, 100));
        } else if (message.type === 'anomaly' && message.data) {
          setAnomalies((prev: Anomaly[]) => [message.data!, ...prev].slice(0, 100));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      
      setTimeout(() => {
        connect();
      }, 5000);
    };

    setWs(websocket);
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [connect]);

  return { anomalies, connected };
};
