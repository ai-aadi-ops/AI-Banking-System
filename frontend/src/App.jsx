import { Routes, Route, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import ErrorBoundary from "./components/ErrorBoundary";
import { getUserSlug } from "./utils/userSlug";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import UploadStatement from "./pages/UploadStatement";
import Dashboard from "./pages/Dashboard";
import Advisor from "./pages/Advisor";
import Offers from "./pages/Offers";
import NotFound from "./pages/NotFound";

/**
 * Redirect /dashboard to the personalized /{userSlug}-dashboard URL
 */
function DashboardRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) {
        const user = JSON.parse(stored);
        const slug = getUserSlug(user);
        navigate(`/${slug}-dashboard`, { replace: true });
        return;
      }
    } catch (e) {
      console.error("DashboardRedirect error:", e);
    }
    navigate("/login", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">
      <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );
}

/**
 * Redirect /advisor to the personalized /{userSlug}-dashboard/ai-advisor URL
 */
function AdvisorRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) {
        const user = JSON.parse(stored);
        const slug = getUserSlug(user);
        navigate(`/${slug}-dashboard/ai-advisor`, { replace: true });
        return;
      }
    } catch (e) {
      console.error("AdvisorRedirect error:", e);
    }
    navigate("/login", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">
      <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Public Authentication & Onboarding Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/upload-statement" element={<UploadStatement />} />
        <Route path="/offers" element={<Offers />} />

        {/* Personalized Dynamic User Routes */}
        <Route path="/:userSlug-dashboard" element={<Dashboard />} />
        <Route path="/:userSlug_dashboard" element={<Dashboard />} />
        <Route path="/:userSlug-dashboard/ai-advisor" element={<Advisor />} />
        <Route path="/:userSlug_dashboard/ai-advisor" element={<Advisor />} />
        <Route path="/:userSlug-dashboard/ai-advisior" element={<Advisor />} />
        <Route path="/:userSlug_dashboard/ai-advisior" element={<Advisor />} />
        <Route path="/:userSlug-dashboard/upload-statement" element={<UploadStatement />} />
        <Route path="/:userSlug_dashboard/upload-statement" element={<UploadStatement />} />

        {/* Legacy route redirects */}
        <Route path="/dashboard" element={<DashboardRedirect />} />
        <Route path="/advisor" element={<AdvisorRedirect />} />

        {/* 404 Fallback */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
