import React, { useState, useRef, useEffect } from "react";
import CameraFeed from "./components/CameraFeed";

export default function App() {
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/ws");
    ws.current.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.current.onmessage = (event) => {
      // event.data = processed frame (image bytes)
      const img = document.getElementById("result");
      img.src = URL.createObjectURL(event.data);
    };

    ws.current.onclose = () => {
      console.log("❌ WebSocket closed");
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  const sendFrame = () => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;

    const video = document.getElementById("video");
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, 640, 480);

    canvas.toBlob((blob) => {
      blob.arrayBuffer().then((buf) => ws.current.send(buf));
    }, "image/jpeg");
  };
  const [cameraOn, setCameraOn] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);

  const toggleCamera = () => setCameraOn((v) => !v);

  const toggleWebSocket = () => {
    if (!wsRef.current) {
      const s = new WebSocket("ws://localhost:8000/ws"); // adjust as needed
      s.onopen = () => setWsConnected(true);
      s.onclose = () => { setWsConnected(false); wsRef.current = null; };
      s.onerror = () => setWsConnected(false);
      s.onmessage = (ev) => {
        // handle detections here
      };
      wsRef.current = s;
    } else {
      wsRef.current.close();
    }
  };
  
  return (
    <div className="app">
      <header style={{textAlign: "center", marginTop: 12}}>
        <h1>AI Realtime Detection</h1>
      </header>

      <div style={{display: "flex", justifyContent: "center", gap: 12}}>
        <button onClick={toggleCamera}>{cameraOn ? "Stop Camera" : "Start Camera"}</button>
        <button onClick={toggleWebSocket}>{wsConnected ? "Disconnect WS" : "Connect WS"}</button>
      </div>

      {/* pass autoStart prop to CameraFeed */}
      <CameraFeed autoStart={cameraOn} />

      <footer style={{textAlign: "center", marginTop: 12}}>
        WebSocket: {wsConnected ? "Connected ✅" : "Disconnected ❌"}
      </footer>
    </div>
  );
}