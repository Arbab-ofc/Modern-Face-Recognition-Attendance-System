import React, { useState } from "react";
import { fetchAttendanceRange } from "../services/api.js";

function formatDate(date) {
  return date.toISOString().split("T")[0];
}

export default function RecordsView() {
  const [startDate, setStartDate] = useState(formatDate(new Date()));
  const [endDate, setEndDate] = useState(formatDate(new Date()));
  const [records, setRecords] = useState([]);
  const [status, setStatus] = useState("Ready");

  const handleSearch = async () => {
    try {
      const data = await fetchAttendanceRange(startDate, endDate);
      setRecords(data);
      setStatus(`Loaded ${data.length} records`);
    } catch (error) {
      setStatus(error.message || "Failed to load records");
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">Attendance Records</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", marginBottom: "16px" }}>
        <label>
          <div className="notice">Start Date</div>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </label>
        <label>
          <div className="notice">End Date</div>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </label>
        <button className="button primary" onClick={handleSearch}>Search</button>
        <div className="notice" style={{ alignSelf: "center" }}>{status}</div>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Student ID</th>
            <th>Name</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record, index) => (
            <tr key={`${record.student_id}-${index}`}>
              <td>{record.date}</td>
              <td>{record.time}</td>
              <td>{record.student_id}</td>
              <td>{record.name}</td>
              <td>{record.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {records.length === 0 && <div className="notice">No records found for this range.</div>}
    </div>
  );
}
