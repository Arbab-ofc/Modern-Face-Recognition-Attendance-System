import React from "react";
import PublicShell from "../components/PublicShell.jsx";

export default function HomeView({ onSignIn, onSignUp }) {
  return (
    <PublicShell
      actions={
        <>
          <button className="button" type="button" onClick={onSignIn}>
            Sign in
          </button>
          <button className="button primary" type="button" onClick={onSignUp}>
            Create account
          </button>
        </>
      }
    >
      <div className="home-hero">
        <div className="home-hero-grid">
          <div className="home-hero-copy">
            <div className="home-pill">No login required to explore</div>
            <h1>See attendance in real time. Audit it in seconds.</h1>
            <p>
              A face-recognition attendance hub built for campuses, labs, and teams. Verify
              check-ins instantly, reduce manual errors, and keep communities aligned.
            </p>
            <div className="home-hero-actions">
              <button className="button primary" type="button" onClick={onSignUp}>
                Start free setup
              </button>
              <button className="button" type="button" onClick={onSignIn}>
                Admin login
              </button>
            </div>
            <div className="home-meta">
              <div>
                <strong>96%</strong>
                <span> faster roll call</span>
              </div>
              <div>
                <strong>4x</strong>
                <span> fewer disputes</span>
              </div>
              <div>
                <strong>Live</strong>
                <span> status dashboard</span>
              </div>
            </div>
          </div>
          <div className="home-hero-panel">
            <div className="home-panel-title">Command Preview</div>
            <div className="home-panel-card">
              <div className="home-panel-row">
                <span>Camera Node A12</span>
                <span className="status-pill success">Active</span>
              </div>
              <div className="home-panel-row">
                <span>Scan Queue</span>
                <span>08 pending</span>
              </div>
              <div className="home-panel-row">
                <span>Recent Match</span>
                <span>03:42 PM</span>
              </div>
            </div>
            <div className="home-panel-card">
              <div className="home-panel-row">
                <span>Community Health</span>
                <span className="status-pill neutral">Stable</span>
              </div>
              <div className="home-panel-row">
                <span>New Registrations</span>
                <span>+14 today</span>
              </div>
              <div className="home-panel-row">
                <span>Exports</span>
                <span>2 reports</span>
              </div>
            </div>
          </div>
        </div>

        <section className="home-grid">
          <div className="home-card">
            <div className="home-card-title">Smart registration</div>
            <p>Capture faces once and manage roles, permissions, and access trails.</p>
          </div>
          <div className="home-card">
            <div className="home-card-title">Instant attendance</div>
            <p>Mark presence automatically with confidence scoring and audit logs.</p>
          </div>
          <div className="home-card">
            <div className="home-card-title">Community controls</div>
            <p>Admins create spaces, invite members, and run exports in one place.</p>
          </div>
          <div className="home-card">
            <div className="home-card-title">Private by design</div>
            <p>Strong access policies keep data scoped to each community.</p>
          </div>
        </section>

        <section className="home-steps">
          <div>
            <h2>Launch in three moves</h2>
            <p>Give your team a clean onboarding flow and a dashboard that never sleeps.</p>
          </div>
          <div className="home-step-grid">
            <div className="home-step">
              <span>01</span>
              <h3>Invite admins</h3>
              <p>Set roles, permissions, and community settings in minutes.</p>
            </div>
            <div className="home-step">
              <span>02</span>
              <h3>Register members</h3>
              <p>Capture faces securely and tag them to the right group.</p>
            </div>
            <div className="home-step">
              <span>03</span>
              <h3>Track sessions</h3>
              <p>Watch attendance update live and export records when needed.</p>
            </div>
          </div>
        </section>

        <section className="home-cta">
          <div>
            <h2>Ready to pilot your community?</h2>
            <p>Preview the system now and sign in when you are ready.</p>
          </div>
          <div className="home-cta-actions">
            <button className="button primary" type="button" onClick={onSignUp}>
              Create account
            </button>
            <button className="button" type="button" onClick={onSignIn}>
              Sign in
            </button>
          </div>
        </section>
      </div>
    </PublicShell>
  );
}
