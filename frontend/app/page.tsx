// app/page.tsx

export default function Home() {
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
        <div className="lg:col-span-2 rounded-2xl bg-white p-4 shadow">
          <h2 className="mb-4 font-bold text-slate-800 flex items-center gap-2">VÙNG 1: LIVE VIEW</h2>
          <div className="flex h-[600px] items-center justify-center rounded-xl border border-dashed text-gray-400">
            Video gốc + Bounding Box (vùng hiển thị chính)
          </div>
        </div>

        {/* Right Side */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          {/* Zone 2: Warped View */}
          <div className="rounded-2xl bg-white p-4 shadow">
            <h2 className="mb-4 font-bold text-slate-800 flex items-center gap-2">VÙNG 2: WARPED VIEW</h2>
            <div className="flex h-100 items-center justify-center rounded-xl border border-dashed text-gray-400">
              Ảnh bia đã nắn thẳng
            </div>
          </div>

          {/* Zone 3: Scoreboard (Bottom Right) */}
          <div className="rounded-2xl bg-white p-4 shadow">
            <h2 className="mb-4 font-bold text-slate-800 flex items-center gap-2">VÙNG 3: BẢNG ĐIỂM</h2>
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200 text-slate-700">
                  <th className="py-2 text-left font-bold">STT</th>
                  <th className="py-2 text-left font-bold">Điểm</th>
                  <th className="py-2 text-left font-bold">Thời gian</th>
                </tr>
              </thead>
              <tbody className="text-slate-800">
                <tr>
                  <td>1</td>
                  <td>10</td>
                  <td>00:01</td>
                </tr>
                <tr>
                  <td>2</td>
                  <td>9</td>
                  <td>00:05</td>
                </tr>
              </tbody>
            </table>
            <div className="mt-4 p-3 bg-blue-50 rounded-lg font-bold text-blue-800 text-xl text-right">TỔNG: 19 điểm</div>
          </div>
        </div>
      </section>

      {/* Controls */}
      <footer className="mt-4 flex justify-center gap-4">
        <button className="rounded-xl bg-blue-600 px-4 py-2 text-white shadow">
          Load Video
        </button>
        <button className="rounded-xl bg-green-600 px-4 py-2 text-white shadow">
          Start
        </button>
        <button className="rounded-xl bg-red-600 px-4 py-2 text-white shadow">
          Reset
        </button>
      </footer>
    </main>
  );
}
