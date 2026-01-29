import React, { useEffect, useState } from "react";
import DashboardView from "./views/DashboardView.jsx";
import RegisterView from "./views/RegisterView.jsx";
import AttendanceView from "./views/AttendanceView.jsx";
import RecordsView from "./views/RecordsView.jsx";
import AuthView from "./views/AuthView.jsx";
import HomeView from "./views/HomeView.jsx";
import RoleSetupView from "./views/RoleSetupView.jsx";
import AdminCommunitySetupView from "./views/AdminCommunitySetupView.jsx";
import JoinCommunityView from "./views/JoinCommunityView.jsx";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./services/firebase.js";
import { signOutUser } from "./services/auth.js";
import { getUserProfile } from "./services/user.js";
import { getCommunityById } from "./services/community.js";

const VIEWS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "register", label: "Register" },
  { key: "attendance", label: "Attendance" },
  { key: "records", label: "Records" }
];

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [authUser, setAuthUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [community, setCommunity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState("");
  const [publicScreen, setPublicScreen] = useState("home");
  const [publicAuthMode, setPublicAuthMode] = useState("login");

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      try {
        setAuthError("");
        setAuthUser(user);
        if (user) {
          const data = await getUserProfile();
          setProfile(data);
        } else {
          setProfile(null);
          setCommunity(null);
        }
      } catch (error) {
        console.error(error);
        setAuthError(error?.message || "Unable to load your profile.");
        setProfile(null);
        setCommunity(null);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    async function loadCommunity() {
      if (profile?.communityId) {
        const data = await getCommunityById(profile.communityId);
        setCommunity(data);
      } else {
        setCommunity(null);
      }
    }

    loadCommunity();
  }, [profile?.communityId]);

  async function refreshProfile() {
    if (!authUser) return;
    const data = await getUserProfile();
    setProfile(data);
  }

  async function handleSignOut() {
    await signOutUser();
  }

  if (loading) {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <div className="auth-title">Loading...</div>
        </div>
      </div>
    );
  }

  if (authError) {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-title">Profile unavailable</div>
            <div className="auth-subtitle">Check Firestore rules or network access.</div>
          </div>
          <div className="form-error">{authError}</div>
          <button className="button" type="button" onClick={handleSignOut}>
            Sign out
          </button>
        </div>
      </div>
    );
  }

  if (!authUser) {
    if (publicScreen === "home") {
      return (
        <HomeView
          onSignIn={() => {
            setPublicAuthMode("login");
            setPublicScreen("auth");
          }}
          onSignUp={() => {
            setPublicAuthMode("signup");
            setPublicScreen("auth");
          }}
        />
      );
    }
    return <AuthView initialMode={publicAuthMode} onBack={() => setPublicScreen("home")} />;
  }

  if (!profile || !profile.role) {
    return <RoleSetupView user={authUser} onComplete={setProfile} />;
  }

  if (profile.role === "admin" && !profile.communityId) {
    return <AdminCommunitySetupView onComplete={refreshProfile} />;
  }

  if (profile.role === "user" && !profile.communityId) {
    return <JoinCommunityView onComplete={refreshProfile} />;
  }

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
          <div className="topbar-actions">
            <div className="topbar-meta">
              <div className="topbar-status">System Online</div>
              <div className="topbar-user">
                {profile.display_name || authUser.email}
                {profile.role && <span className="role-chip">{profile.role}</span>}
                {community?.name && <span className="role-chip">{community.name}</span>}
              </div>
            </div>
            <button className="button" type="button" onClick={handleSignOut}>
              Sign out
            </button>
          </div>
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
