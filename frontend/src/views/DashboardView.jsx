import React, { useEffect, useState } from "react";
import { fetchAttendance, fetchStudents } from "../services/api.js";

function getTodayDate() {
  return new Date().toISOString().split("T")[0];
}

export default function DashboardView() {
  const [stats, setStats] = useState({
    total: 0,
    present: 0,
    rate: 0,
    pending: 0
  });
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [students, attendance] = await Promise.all([
          fetchStudents(),
          fetchAttendance(getTodayDate())
        ]);
        const total = students.length;
        const present = attendance.length;
        const rate = total > 0 ? ((present / total) * 100).toFixed(1) : 0;
        const pending = Math.max(total - present, 0);
        setStats({ total, present, rate, pending });
        setRecent(attendance.slice(0, 8));
      } catch (error) {
        console.error(error);
      }
    }

    loadData();
  }, []);

  return (
    <div className="content-stack">
      <div className="panel">
        <div className="panel-header">System Overview</div>
        <div className="grid-2">
          <div className="stat-card">
            <div className="stat-label">Total Students</div>
            <div className="stat-value">{stats.total}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Present Today</div>
            <div className="stat-value">{stats.present}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Attendance Rate</div>
            <div className="stat-value">{stats.rate}%</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Pending</div>
            <div className="stat-value">{stats.pending}</div>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">Recent Attendance</div>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>ID</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((record) => (
              <tr key={`${record.student_id}-${record.time}`}>
                <td>{record.name}</td>
                <td>{record.student_id}</td>
                <td>{record.time}</td>
                <td>{record.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {recent.length === 0 && <div className="notice">No attendance records yet.</div>}
      </div>
    </div>
  );
}
