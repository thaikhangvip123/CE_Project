import React, { useRef, useEffect, useState } from "react";

const WS_URL = "ws://localhost:8000/ws";

export default function VideoStream() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [ws, setWs] = useState(null);
  const [streaming, setStreaming] = useState(false);
  const [fps, setFps] = useState(null);
  let sendLoopId = null;

  // Start camera
  async function startCamera() {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 960 } },
      audio: false
    });
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      return new Promise((resolve) => {
        videoRef.current.onloadedmetadata = () => {
          canvasRef.current.width = videoRef.current.videoWidth;
          canvasRef.current.height = videoRef.current.videoHeight;
          resolve();
        };
      });
    }
  }

  // Draw detections
  function drawDetections(dets) {
    const ctx = canvasRef.current.getContext("2d");
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    ctx.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);

    ctx.lineWidth = 2;
    ctx.font = "14px Arial";

    dets.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox;
      const w = x2 - x1, h = y2 - y1;

      ctx.strokeStyle = "rgba(16,185,129,1)";
      ctx.strokeRect(x1, y1, w, h);

      const label = `${det.class_name} ${det.confidence.toFixed(2)}`;
      ctx.fillStyle = "rgba(0,0,0,0.6)";
      ctx.fillRect(x1, y1 - 16, ctx.measureText(label).width + 8, 16);
      ctx.fillStyle = "#fff";
      ctx.fillText(label, x1 + 4, y1 - 4);
    });
  }

  // Send frames loop
  async function sendFrameLoop(socket) {
    const off = document.createElement("canvas");
    off.width = canvasRef.current.width;
    off.height = canvasRef.current.height;
    const offCtx = off.getContext("2d");

    const loop = () => {
      if (!streaming || socket.readyState !== WebSocket.OPEN) return;

      offCtx.drawImage(videoRef.current, 0, 0, off.width, off.height);
      off.toBlob(blob => {
        if (blob) socket.send(blob);
      }, "image/jpeg", 0.8);

      sendLoopId = setTimeout(loop, 120);
    };
    loop();
  }

  function startStream() {
    startCamera().then(() => {
      const socket = new WebSocket(WS_URL);
      socket.onopen = () => {
        setStreaming(true);
        setWs(socket);
        sendFrameLoop(socket);
      };
      socket.onmessage = ev => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "detections") {
          drawDetections(msg.detections);
        }
      };
      socket.onclose = () => setStreaming(false);
    });
  }

  function stopStream() {
    setStreaming(false);
    if (sendLoopId) clearTimeout(sendLoopId);
    if (ws && ws.readyState === WebSocket.OPEN) ws.close();
  }

  return (
    <div>
      <div className="video-wrap">
        <video ref={videoRef} autoPlay playsInline></video>
        <canvas ref={canvasRef}></canvas>
      </div>
      <div className="controls">
        <button onClick={startStream} disabled={streaming}>Start</button>
        <button onClick={stopStream} disabled={!streaming}>Stop</button>
        <span>Status: {streaming ? "Connected" : "Idle"}</span>
        <span>{fps ? `FPS: ${fps}` : ""}</span>
      </div>
    </div>
  );
}
