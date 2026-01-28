import React, { useRef, useState } from "react";
import { registerStudent } from "../services/api.js";

export default function RegisterView() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [studentId, setStudentId] = useState("");
  const [name, setName] = useState("");
  const [status, setStatus] = useState("Idle");
  const [snapshotUrl, setSnapshotUrl] = useState("");

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

  const captureSnapshot = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) {
      return;
    }
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg");
    setSnapshotUrl(dataUrl);
    setStatus("Snapshot captured");
  };

  const handleRegister = async () => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }
    if (!studentId || !name) {
      setStatus("Student ID and name are required");
      return;
    }

    canvas.toBlob(async (blob) => {
      if (!blob) {
        setStatus("Capture failed");
        return;
      }
      try {
        const formData = new FormData();
        formData.append("student_id", studentId);
        formData.append("name", name);
        formData.append("image", blob, "capture.jpg");
        const response = await registerStudent(formData);
        setStatus(response.message || "Registered");
        setStudentId("");
        setName("");
      } catch (error) {
        setStatus(error.message || "Registration failed");
      }
    }, "image/jpeg");
  };

  return (
    <div className="grid-2">
      <div className="panel">
        <div className="panel-header">Capture Station</div>
        <video className="video-frame" ref={videoRef} autoPlay playsInline />
        <canvas ref={canvasRef} style={{ display: "none" }} />
        {snapshotUrl && <img className="video-frame" src={snapshotUrl} alt="Snapshot" />}
        <div style={{ display: "flex", gap: "10px", marginTop: "16px" }}>
          <button className="button primary" onClick={startCamera}>Start Camera</button>
          <button className="button" onClick={captureSnapshot}>Capture</button>
          <button className="button danger" onClick={stopCamera}>Stop</button>
        </div>
        <div className="notice" style={{ marginTop: "12px" }}>{status}</div>
      </div>

      <div className="panel">
        <div className="panel-header">Student Registration</div>
        <div style={{ display: "grid", gap: "12px" }}>
          <label>
            <div className="notice">Student ID</div>
            <input value={studentId} onChange={(e) => setStudentId(e.target.value)} />
          </label>
          <label>
            <div className="notice">Full Name</div>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <button className="button primary" onClick={handleRegister}>Register Student</button>
          <div className="notice">Capture a clear face before registration.</div>
        </div>
      </div>
    </div>
  );
}
