export function warpPoint(x, y, H) {
  const denom = H[2][0] * x + H[2][1] * y + H[2][2];

  return {
    x: (H[0][0] * x + H[0][1] * y + H[0][2]) / denom,
    y: (H[1][0] * x + H[1][1] * y + H[1][2]) / denom
  };
}

export function warpBoundingBox(box, H) {
  const p1 = warpPoint(box.x1, box.y1, H);
  const p2 = warpPoint(box.x2, box.y1, H);
  const p3 = warpPoint(box.x2, box.y2, H);
  const p4 = warpPoint(box.x1, box.y2, H);

  const xs = [p1.x, p2.x, p3.x, p4.x];
  const ys = [p1.y, p2.y, p3.y, p4.y];

  return {
    x1: Math.min(...xs),
    y1: Math.min(...ys),
    x2: Math.max(...xs),
    y2: Math.max(...ys)
  };
}
