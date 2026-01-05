"use client";
import { useEffect, useRef } from "react";

export default function useCamera() {
  const videoRef = useRef(null);

  useEffect(() => {
    let stream;

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(s => {
        stream = s;
        if (videoRef.current) videoRef.current.srcObject = s;
      });

    return () => stream?.getTracks().forEach(t => t.stop());
  }, []);

  return videoRef;
}
