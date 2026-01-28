import React, { useRef, useState } from "react";
import { recognizeAndMark } from "../services/api.js";

export default function AttendanceView() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState("Idle");
  const [log, setLog] = useState([]);
  const [intervalId, setIntervalId] = useState(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setStatus("Camera active");
      }
    } catch (error) {
      setStatus("Camera access denied");
    }
  };

  const stopCamera = () => {
    const video = videoRef.current;
    if (video && video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
      setStatus("Camera stopped");
    }
  };

  const captureAndRecognize = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) {
      return;
    }
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) {
        return;
      }
      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");
      try {
        const response = await recognizeAndMark(formData);
        const timestamp = new Date().toLocaleTimeString();
        const entries = response.results.map((result) => ({
          time: timestamp,
          name: result.name,
          status: result.is_match ? "marked" : "unknown"
        }));
        if (entries.length > 0) {
          setLog((prev) => [...entries, ...prev].slice(0, 20));
        }
        setStatus("Recognition cycle complete");
      } catch (error) {
        setStatus(error.message || "Recognition failed");
      }
    }, "image/jpeg");
  };

  const startRecognition = () => {
    if (intervalId) {
      return;
    }
    captureAndRecognize();
    const id = setInterval(captureAndRecognize, 2000);
    setIntervalId(id);
    setStatus("Recognition running");
  };

  const stopRecognition = () => {
    if (intervalId) {
      clearInterval(intervalId);
      setIntervalId(null);
      setStatus("Recognition stopped");
    }
  };

  return (
    <div className="grid-2">
      <div className="panel">
        <div className="panel-header">Live Recognition</div>
        <video className="video-frame" ref={videoRef} autoPlay playsInline />
        <canvas ref={canvasRef} style={{ display: "none" }} />
        <div style={{ display: "flex", gap: "10px", marginTop: "16px" }}>
          <button className="button primary" onClick={startCamera}>Start Camera</button>
          <button className="button" onClick={startRecognition}>Start Recognition</button>
          <button className="button danger" onClick={stopRecognition}>Stop Recognition</button>
          <button className="button" onClick={stopCamera}>Stop Camera</button>
        </div>
        <div className="notice" style={{ marginTop: "12px" }}>{status}</div>
      </div>

      <div className="panel">
        <div className="panel-header">Attendance Log</div>
        <table className="table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {log.map((entry, index) => (
              <tr key={`${entry.time}-${index}`}>
                <td>{entry.time}</td>
                <td>{entry.name}</td>
                <td>{entry.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {log.length === 0 && <div className="notice">No attendance captured yet.</div>}
      </div>
    </div>
  );
}
