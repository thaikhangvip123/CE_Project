"use client";
import { useRef, useState, useEffect, forwardRef, useImperativeHandle, use } from "react";

const RADIUS = 6;

const LiveView = forwardRef(({ onWarped }, ref) => {
  const canvasRef = useRef(null);
  const imgRef = useRef(null);
  const draggingIndexRef = useRef(null);
  const [hoverBox, setHoverBox] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    
  const [points, setPoints] = useState([]);
  const [file, setFile] = useState(null);
  const [boxes, setBoxes] = useState([]);


  /* ------------------ Expose API ------------------ */
  useImperativeHandle(ref, () => ({
    detectBullets,
    warp,
    reset
  }));

  /* ------------------ Load Image ------------------ */
  const loadImage = e => {
    const f = e.target.files[0];
    setFile(f);
    setPoints([]);

    const img = new Image();
    img.src = URL.createObjectURL(f);
    img.onload = () => {
      imgRef.current = img;
      const canvas = canvasRef.current;
      canvas.width = img.width;
      canvas.height = img.height;
      redraw([], []);
    };
  };

  /* ------------------ Redraw ------------------ */
  const redraw = (pts, boxes) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if(!imgRef.current) return;
    if(!imgRef.current.complete) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(imgRef.current, 0, 0);

    // Vẽ bounding box
    (boxes ?? []).forEach(b => {
      ctx.strokeStyle = hoverBox === b ? "lime" : "red";
      ctx.lineWidth = 2;
      ctx.strokeRect(
        b.x1,
        b.y1,
        b.x2 - b.x1,
        b.y2 - b.y1
      );
    });

    pts.forEach(([x, y], i) => {
      ctx.fillStyle = "red";
      ctx.beginPath();
      ctx.arc(x, y, RADIUS, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "yellow";
      ctx.fillText(i + 1, x + 8, y - 8);
    });
  };

  /* ------------------ Mouse Events ------------------ */
  const getMousePos = e => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) * (canvas.width / rect.width),
      y: (e.clientY - rect.top) * (canvas.height / rect.height)
    };
  };

  const onMouseDown = e => {
    const { x, y } = getMousePos(e);

    for (let i = 0; i < points.length; i++) {
      const [px, py] = points[i];
      if (Math.hypot(px - x, py - y) < RADIUS + 2) {
        draggingIndexRef.current = i;
        return;
      }
    }

    if (points.length < 8) {
      const newPts = [...points, [x, y]];
      setPoints(newPts);
      redraw(newPts);
    }
  };

  const onMouseMove = e => {
    const { x, y } = getMousePos(e);

    setMousePos({ x, y });

    // Hover bounding box
    const box = findHoverBox(x, y);
    setHoverBox(box || null);

    // Drag point
    if (draggingIndexRef.current !== null) {
      const newPts = [...points];
      newPts[draggingIndexRef.current] = [x, y];
      setPoints(newPts);
      redraw(newPts, boxes);
    }
  };

  const onMouseUp = () => {
    draggingIndexRef.current = null;
  };

  /* ------------------ Actions ------------------ */
  async function detectBullets() {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    const res = await fetch("http://localhost:8000/api/predict-image", {
      method: "POST",
      body: form
    });

    const data = await res.json();
    setBoxes(data.boxes || []);
    redraw(points, data.boxes || []);
  }

  async function warp() {
    if (!file || points.length !== 8) {
      alert("Cần ảnh và đủ 8 điểm");
      return;
    }

    const form = new FormData();
    form.append("image", file);
    form.append("points", JSON.stringify(points));

    const res = await fetch("http://localhost:8000/homography", {
      method: "POST",
      body: form
    });

    const data = await res.json();
    const base64Src = `data:image/png;base64,${data.image}`;
    onWarped({
      image: base64Src,
      boxes: boxes,
      H: data.H
    });
    // const blob = await res.blob();
    // onWarped(URL.createObjectURL(blob));
  }

  useEffect(() => {``
    redraw(points, boxes);
  }, [boxes, points]);
  useEffect(() => {
    redraw(points, boxes);
  }, [hoverBox]);

  function reset() {
    setPoints([]);
    setBoxes([]);
    // imgRef.current = null;

    // const canvas = canvasRef.current;
    // const ctx = canvas.getContext("2d");
    // ctx.clearRect(0, 0, canvas.width, canvas.height);
    redraw([], []);
  }

  const findHoverBox = (x, y) => {
    return boxes.find(
      b => x >= b.x1 && x <= b.x2 && y >= b.y1 && y <= b.y2
    );
  };


  /* ------------------ Render ------------------ */
  return (
    <div className="rounded-xl border border-dashed p-2">
      <label className="cursor-pointer rounded-lg bg-blue-300 px-3 py-1.5 text-sm text-white hover:bg-blue-700 transition">
        Choose file to upload
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={loadImage}
        />
      </label>

      <canvas
        ref={canvasRef}
        className="mt-2 cursor-crosshair"
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
      />
      {hoverBox && (
      <div
        className="absolute bg-black text-white text-xs px-2 py-1 rounded pointer-events-none"
        style={{
          left: mousePos.x + 12,
          top: mousePos.y + 12
        }}
      >
        <div>x1: {Math.round(hoverBox.x1)}</div>
        <div>y1: {Math.round(hoverBox.y1)}</div>
        <div>x2: {Math.round(hoverBox.x2)}</div>
        <div>y2: {Math.round(hoverBox.y2)}</div>
        <div>conf: {hoverBox.confidence?.toFixed(2)}</div>
      </div>
    )}
    </div>
  );
});

LiveView.displayName = "LiveView";
export default LiveView;
