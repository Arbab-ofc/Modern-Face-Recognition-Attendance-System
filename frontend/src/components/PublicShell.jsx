import React from "react";

export default function PublicShell({ children, actions }) {
  return (
    <div className="home-shell">
      <header className="home-header">
        <div className="home-nav">
          <div className="home-logo">
            <span className="home-logo-mark">FA</span>
            <div>
              <div className="home-logo-title">Face Attendance</div>
              <div className="home-logo-subtitle">Modern operations, human-friendly.</div>
            </div>
          </div>
          <div className="home-nav-links">
            <span>Features</span>
            <span>How it works</span>
            <span>Security</span>
          </div>
          <div className="home-nav-actions">{actions}</div>
        </div>
        <div className="home-header-banner">
          <span>New</span>
          <p>Community setup now includes instant member invites and role templates.</p>
        </div>
      </header>

      <main className="public-main">{children}</main>

      <footer className="home-footer">
        <div className="home-footer-grid">
          <div>
            <div className="home-footer-title">Face Attendance</div>
            <p>Next-gen face recognition attendance for modern teams.</p>
          </div>
          <div>
            <div className="home-footer-title">Product</div>
            <span>Dashboard</span>
            <span>Attendance logs</span>
            <span>Exports</span>
          </div>
          <div>
            <div className="home-footer-title">Security</div>
            <span>Access control</span>
            <span>Audit trails</span>
            <span>Privacy-first</span>
          </div>
          <div>
            <div className="home-footer-title">Contact</div>
            <span>support@faceattendance.io</span>
            <span>+1 (555) 210-8877</span>
          </div>
        </div>
        <div className="home-footer-bottom">
          <span>© 2026 Face Attendance. All rights reserved.</span>
          <span>Built for communities that need accountability.</span>
        </div>
      </footer>
    </div>
  );
}
