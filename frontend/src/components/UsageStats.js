import React, { useEffect, useState } from "react";

export default function UsageStats() {
  const [cpu, setCpu] = useState(15);
  const [ram, setRam] = useState(45);
  const [gpu, setGpu] = useState(20);

  // Fake random update for demo
  useEffect(() => {
    const interval = setInterval(() => {
      setCpu(Math.floor(Math.random() * 100));
      setRam(Math.floor(Math.random() * 100));
      setGpu(Math.floor(Math.random() * 100));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="stats">
      <h3>💻 System Usage</h3>
      <p>CPU: {cpu}%</p>
      <p>RAM: {ram}%</p>
      <p>GPU: {gpu}%</p>
    </div>
  );
}
