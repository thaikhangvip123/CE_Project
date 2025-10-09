import React from "react";

export default function Controls({ connectWebSocket, wsConnected }) {
  return (
    <div className="controls">
      <button onClick={connectWebSocket}>
        {wsConnected ? "🔌 Disconnect" : "⚡ Connect to WebSocket"}
      </button>
      <p>Status: {wsConnected ? "🟢 Connected" : "🔴 Disconnected"}</p>
    </div>
  );
}
