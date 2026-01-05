// app/page.tsx
"use client";
import { useRef, useState } from 'react';
import LiveView from '../components/LiveView';
import WarpedView from '../components/WarpedView';
import ScoreView from '../components/ScoreBoard';
import { warpBoundingBox } from '@/utils/homography';

export default function Home() {
  const [warped, setWarped] = useState(null);
  const [warpedBoxes, setWarpedBoxes] = useState([]);
  const [H, setH] = useState(null);
  const liveViewRef = useRef(null);
  const scoreViewRef = useRef(null);
  
  return (
    <main className="min-h-screen bg-gray-100 p-4">
      {/* Title */}
      <header className="mb-4 rounded-2xl bg-white p-6 shadow-md border-b-4 border-blue-600">
        <h1 className="text-3xl font-bold text-slate-900 text-center tracking-tight">
          HỆ THỐNG CHẤM ĐIỂM BẮN SÚNG TỰ ĐỘNG
        </h1>
        <p className="text-center text-base font-medium text-slate-600 mt-1">
          Thiết kế hệ thống chấm điểm tự động cho bài bắn 3D dựa trên thị giác máy tính
        </p>
      </header>

      {/* Main Layout */}
      <section className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        {/* Zone 1: Live View (Left - Main) */}
        <div className="lg:col-span-2 rounded-2xl bg-white p-4 shadow flex flex-col">
          <h2 className="mb-4 font-bold text-slate-800">LIVE VIEW</h2>
          {/* <div className="flex-1 flex items-center justify-center rounded-xl border border-dashed text-gray-400">
            Video gốc + Bounding Box (vùng hiển thị chính)
          </div> */}
        <LiveView ref={liveViewRef} 
          onWarped={(data) => {
            setWarped(data.image);       // Base64
            const wb = data.boxes.map(b => warpBoundingBox(b, data.H));
            setWarpedBoxes(wb);  // boxes
            setH(data.H);                // H matrix
        }} />
        </div>

        {/* Right Side */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          {/* Zone 2: Warped View */}
          <div className="rounded-2xl bg-white p-4 shadow">
            <h2 className="mb-4 font-bold text-slate-800 flex items-center gap-2">WARPED VIEW</h2>
            {/* <div className="flex h-150 items-center justify-center rounded-xl border border-dashed text-gray-400">
              Ảnh bia đã nắn thẳng
            </div> */}
          <WarpedView src={warped} boxes={warpedBoxes} />
          </div>

          {/* Zone 3: Scoreboard (Bottom Right) */}
          <div className="rounded-2xl bg-white p-4 shadow">
            <h2 className="mb-4 font-bold text-slate-800 flex items-center gap-2">SCORE</h2>
            {/* <div className="mt-4 p-3 bg-blue-50 rounded-lg font-bold text-blue-800 text-xl text-right"></div> */}
          <ScoreView warpedImage={warped} boxes={warpedBoxes} />
          </div>
        </div>
      </section>

      {/* Controls */}
      <footer className="mt-4 flex justify-center gap-4">
        <button 
          onClick={() => liveViewRef.current?.detectBullets()} 
          className="rounded-xl bg-yellow-500 px-4 py-2 text-white shadow
                    transition-all duration-200
                    hover:bg-yellow-700
                    hover:-translate-y-0.5
                    hover:shadow-lg
                    active:translate-y-0">
          Detect
        </button>
        <button 
          onClick={() => liveViewRef.current?.warp()} 
          className="rounded-xl bg-blue-500 px-4 py-2 text-white shadow
                    transition-all duration-200
                    hover:bg-blue-700
                    hover:-translate-y-0.5
                    hover:shadow-lg
                    active:translate-y-0">
          Warp
        </button>
        {/* <button 
          onClick={() => scoreViewRef.current?.handleScore()}
          className="rounded-xl bg-green-600 px-4 py-2 text-white shadow
                    transition-all duration-200
                    hover:bg-green-800
                    hover:-translate-y-0.5
                    hover:shadow-lg
                    active:translate-y-0" >
          Score
        </button> */}
        <button 
          onClick={() => {
            liveViewRef.current?.reset();
            setWarped(null);
          }}
          className="rounded-xl bg-red-500 px-4 py-2 text-white shadow
                    transition-all duration-200
                    hover:bg-red-700
                    hover:-translate-y-0.5
                    hover:shadow-lg
                    active:translate-y-0">
          Reset
        </button>
      </footer>
    </main>
  );
}
