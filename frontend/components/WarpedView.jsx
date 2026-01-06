"use client";
import { useEffect, useRef, useState } from "react";
import { warpBoundingBox } from "../utils/homography";

export default function WarpedView({ src, boxes = [], H = null }) {
  const canvasRef = useRef(null);
  const imgRef = useRef(null);

  const [hoverBox, setHoverBox] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  // // Warp boxes nếu có H
  // const warpedBoxes = H && boxes.length ? boxes.map(b => warpBoundingBox(b, H)) : boxes;

  /* ---------------- Draw image + boxes ---------------- */
  useEffect(() => {
    if (!src || !imgRef.current) return;

    // const img = imgRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // const draw = () => {
    canvas.width = 600;
    canvas.height = 600;

    // const scaleX = canvas.width / img.naturalWidth;
    // const scaleY = canvas.height / img.naturalHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(imgRef.current, 0, 0, canvas.width, canvas.height);

    boxes.forEach(b => {
      ctx.strokeStyle = hoverBox === b ? "lime" : "red";
      ctx.lineWidth = 2;
      ctx.strokeRect(
        b.x1, 
        b.y1, 
        b.x2 - b.x1, 
        b.y2 - b.y1
      );
    });
    // };

    // img.onload = draw;
    // draw();
  }, [src, boxes, hoverBox]);

  /* ---------------- Mouse hover ---------------- */
  const onMouseMove = e => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);
    const y = (e.clientY - rect.top) * (canvas.height / rect.height);

    const box = boxes.find(b => x >= b.x1 && x <= b.x2 && y >= b.y1 && y <= b.y2);
    setHoverBox(box || null);
    setMousePos({ x, y });
  };

  /* ---------------- Render ---------------- */
  return (
    <div className="relative w-[600px] h-[600px] mx-auto border border-dashed">
      {src ? (
        <>
          <img
            ref={imgRef}
            src={src}
            width={600}
            height={600}
            className="absolute top-0 left-0 select-none pointer-events-none"
          />
          <canvas
            ref={canvasRef}
            width={600}
            height={600}
            className="absolute top-0 left-0"
            onMouseMove={onMouseMove}
          />

          {/* Tooltip hover */}
          {hoverBox && (
            <div
              className="absolute bg-black text-white text-xs px-2 py-1 rounded pointer-events-none"
              style={{
                left: mousePos.x + 12,
                top: mousePos.y + 12
              }}
            >
              <div>#{Math.round(hoverBox.rank)}</div>
              <div>x1: {Math.round(hoverBox.x1)}</div>
              <div>y1: {Math.round(hoverBox.y1)}</div>
              <div>x2: {Math.round(hoverBox.x2)}</div>
              <div>y2: {Math.round(hoverBox.y2)}</div>
            </div>
          )}
        </>
      ) : (
        <div className="flex h-full items-center justify-center">
          Ảnh sau khi nắn
        </div>
      )}
    </div>
  );
}
