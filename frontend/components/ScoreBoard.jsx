"use client";
import { forwardRef, use, useImperativeHandle, useState } from "react";

const ScoreView = forwardRef(({ warpedImage, boxes }, ref) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useImperativeHandle(ref, () => ({
    score: handleScore
  }));

  async function handleScore() {
    if (!warpedImage || boxes.length === 0) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("image_base64", warpedImage);
    formData.append("boxes", JSON.stringify(boxes));

    const res = await fetch("http://localhost:8000/api/score", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <button
        onClick={handleScore}
        className="w-full rounded-xl bg-green-600 px-4 py-2 text-white"
      >
        {loading ? "Đang tính..." : "TÍNH ĐIỂM"}
      </button>
      {result && (
        <div className="mt-4 space-y-2 text-black">
          <p><b>Tâm bia:</b> ({result.center.x}, {result.center.y})</p>
          <p><b>Tổng điểm:</b> {result.total_score}</p>

          <hr />
          <div className="max-h-[200px] overflow-y-auto space-y-1 pr-2">
            {result.shots.map((s, i) => (
              <div key={i} className="flex justify-between rounded-md bg-gray-100 px-2 py-1 text-sm">
                <span>Phát {i + 1}</span>
                <span>{s.score} điểm</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});
ScoreView.displayName = "ScoreView";
export default ScoreView;
