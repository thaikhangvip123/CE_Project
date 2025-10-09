import React, { useEffect, useRef, useState } from "react";

export default function CameraFeed({ autoStart = false, width = 1280, height = 720 }) {
  const videoRef = useRef(null);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    let stream = null;
    let mounted = true;

    async function startCamera() {
      try {
        setError(null);
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: width }, height: { ideal: height } },
          audio: false,
        });

        if (!mounted) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play().catch(() => {});
        }
        setRunning(true);
      } catch (e) {
        console.error("Camera error:", e);
        setError(e.name ? `${e.name}: ${e.message || ""}` : String(e));
        setRunning(false);
      }
    }

    if (autoStart) startCamera();

    return () => {
      mounted = false;
      if (stream) stream.getTracks().forEach((t) => t.stop());
      if (videoRef.current) videoRef.current.srcObject = null;
    };
  }, [autoStart, width, height]);

  return (
    <div className="camera-container">
      {error ? (
        <div className="camera-error">
          <p><strong>Camera error:</strong> {error}</p>
          <p>Check browser permissions, console, and that you run over localhost/HTTPS.</p>
        </div>
      ) : (
        <video
          ref={videoRef}
          className="camera-video"
          autoPlay
          playsInline
          muted
          // no width/height attributes — let CSS fit it responsively
        />
      )}

      {/* small status badge */}
      <div className={`camera-badge ${running ? "running" : "stopped"}`}>
        {running ? "Camera: On" : "Camera: Off"}
      </div>
    </div>
  );
}