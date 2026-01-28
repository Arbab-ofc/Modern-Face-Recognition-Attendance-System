import React, { useState } from "react";
import DashboardView from "./views/DashboardView.jsx";
import RegisterView from "./views/RegisterView.jsx";
import AttendanceView from "./views/AttendanceView.jsx";
import RecordsView from "./views/RecordsView.jsx";

const VIEWS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "register", label: "Register" },
  { key: "attendance", label: "Attendance" },
  { key: "records", label: "Records" }
];

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-title">Face Attendance</div>
          <div className="brand-subtitle">Retro Control Grid</div>
        </div>
        <nav className="nav">
          {VIEWS.map((view) => (
            <button
              key={view.key}
              className={`nav-item ${activeView === view.key ? "active" : ""}`}
              onClick={() => setActiveView(view.key)}
            >
              {view.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">Version 1.0.0</div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div className="topbar-title">{VIEWS.find((v) => v.key === activeView)?.label}</div>
          <div className="topbar-status">System Online</div>
        </header>
        <section className="content-area">
          {activeView === "dashboard" && <DashboardView />}
          {activeView === "register" && <RegisterView />}
          {activeView === "attendance" && <AttendanceView />}
          {activeView === "records" && <RecordsView />}
        </section>
      </main>
    </div>
  );
}
