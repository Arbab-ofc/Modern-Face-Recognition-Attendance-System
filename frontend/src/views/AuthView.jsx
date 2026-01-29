import React, { useState } from "react";
import { signInWithEmail, signInWithGoogle, signUpWithEmail } from "../services/auth.js";
import { createUserProfile } from "../services/user.js";
import PublicShell from "../components/PublicShell.jsx";

const ROLE_OPTIONS = [
  { value: "admin", label: "Administrator" },
  { value: "user", label: "User" }
];

export default function AuthView({ initialMode = "login", onBack }) {
  const [mode, setMode] = useState(initialMode);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("user");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isSignup = mode === "signup";

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }

    if (isSignup) {
      if (!displayName) {
        setError("Display name is required.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }

    try {
      setLoading(true);
      if (isSignup) {
        await signUpWithEmail({ email, password, displayName });
        await createUserProfile({
          display_name: displayName,
          role
        });
      } else {
        await signInWithEmail({ email, password });
      }
    } catch (err) {
      setError(err.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSignIn() {
    setError("");
    try {
      setLoading(true);
      await signInWithGoogle();
    } catch (err) {
      setError(err.message || "Google sign-in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <PublicShell
      actions={
        onBack ? (
          <button type="button" className="text-link" onClick={onBack}>
            ← Back to home
          </button>
        ) : (
          <button type="button" className="button" onClick={() => setMode("login")}>
            Back to sign in
          </button>
        )
      }
    >
      <div className="auth-shell">
        <div className="auth-card modern-auth">
          <div className="auth-side">
            <div className="auth-kicker">{isSignup ? "Create your space" : "Welcome back"}</div>
            <div className="auth-title">Face Attendance</div>
            <p className="auth-subtitle">
              {isSignup
                ? "Launch communities with clean onboarding, instant verification, and live tracking."
                : "Sign in to monitor attendance, manage roles, and export records."}
            </p>
            <div className="auth-side-stats">
              <div>
                <strong>Secure</strong>
                <span> Role-based access</span>
              </div>
              <div>
                <strong>Live</strong>
                <span> Session visibility</span>
              </div>
            </div>
          </div>
          <div className="auth-main">
            <div className="auth-header">
              <div className="auth-title">{isSignup ? "Create account" : "Sign in"}</div>
              <div className="auth-subtitle">
                {isSignup ? "Set up your admin or user access in one step." : "Use your account credentials."}
              </div>
            </div>

            <div className="auth-toggle">
              <button
                type="button"
                className={`button ${!isSignup ? "primary" : ""}`}
                onClick={() => setMode("login")}
              >
                Login
              </button>
              <button
                type="button"
                className={`button ${isSignup ? "primary" : ""}`}
                onClick={() => setMode("signup")}
              >
                Sign Up
              </button>
            </div>

            <form className="form-stack" onSubmit={handleSubmit}>
              {isSignup && (
                <label className="form-field">
                  <span>Display Name</span>
                  <input
                    type="text"
                    value={displayName}
                    onChange={(event) => setDisplayName(event.target.value)}
                    placeholder="Your name"
                  />
                </label>
              )}

              <label className="form-field">
                <span>Email</span>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@example.com"
                />
              </label>

              <label className="form-field">
                <span>Password</span>
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="••••••••"
                />
              </label>

              {isSignup && (
                <label className="form-field">
                  <span>Confirm Password</span>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    placeholder="••••••••"
                  />
                </label>
              )}

              {isSignup && (
                <label className="form-field">
                  <span>Role</span>
                  <select value={role} onChange={(event) => setRole(event.target.value)}>
                    {ROLE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              )}

              {error && <div className="form-error">{error}</div>}

              <button className="button primary" type="submit" disabled={loading}>
                {loading ? "Please wait..." : isSignup ? "Create Account" : "Login"}
              </button>
            </form>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <button className="button" type="button" onClick={handleGoogleSignIn} disabled={loading}>
              Continue with Google
            </button>

            <div className="auth-footnote">
              Community access is managed by administrators.
            </div>
          </div>
        </div>
      </div>
    </PublicShell>
  );
}
