import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { API_BASE } from "../config";
import { t, ALL_LANGUAGES } from "../utils/i18n";
import {
  getUserSlug,
  DEMO_ROBERT_USER,
  resolveInitialUserForSlug,
  saveUserSession,
} from "../utils/userSlug";
import AISpendingInsights from "../components/AISpendingInsights";
import DashboardHeader from "../components/DashboardHeader";
import DashboardCards from "../components/DashboardCards";
import SpendingChart from "../components/SpendingChart";
import RecentTransactions from "../components/RecentTransactions";
import AIRecommendation from "../components/AIRecommendation";
import { Globe, Trash2, UploadCloud, LogOut, Landmark } from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const params = useParams();
  const rawSlug = params.userSlug || params["userSlug-dashboard"] || params["userSlug_dashboard"] || "";
  const userSlug = rawSlug.replace(/[-_]dashboard$/i, "").toLowerCase();

  const [user, setUser] = useState(() => resolveInitialUserForSlug(userSlug));

  const [lang, setLang] = useState(() => {
    try {
      const initialU = resolveInitialUserForSlug(userSlug);
      if (userSlug === "robert") return "en";
      return localStorage.getItem("preferred_language") || initialU?.preferred_language || "en";
    } catch {
      return "en";
    }
  });

  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    let isMounted = true;

    // 1. Direct Robert Wilson demo route: /robert-dashboard
    if (userSlug === "robert") {
      setUser(DEMO_ROBERT_USER);
      setLang("en");
      sessionStorage.setItem("hasActiveStatement", "true");
      return;
    }

    // 2. Synchronize initial user for this slug
    const localCandidate = resolveInitialUserForSlug(userSlug);
    if (localCandidate) {
      setUser(localCandidate);
      const savedLang = localStorage.getItem("preferred_language") || localCandidate.preferred_language || "en";
      setLang(savedLang);
      sessionStorage.setItem("hasActiveStatement", "true");
    }

    // 3. Query backend /auth/resolve-slug/{userSlug} to ensure we use the profile with uploaded transactions
    if (userSlug) {
      const activeSessionCid = sessionStorage.getItem(`active_customer_id_${userSlug}`);
      fetch(`${API_BASE}/auth/resolve-slug/${encodeURIComponent(userSlug)}`)
        .then((res) => (res.ok ? res.json() : null))
        .then((resolved) => {
          if (!isMounted) return;
          if (resolved && resolved.customer_id) {
            if (!activeSessionCid || !localCandidate || localCandidate.customer_id === 1) {
              setUser(resolved);
              saveUserSession(resolved);
              sessionStorage.setItem("hasActiveStatement", "true");
            }
          } else if (!localCandidate) {
            navigate("/login");
          }
        })
        .catch(() => {
          if (!isMounted) return;
          if (!localCandidate) {
            navigate("/login");
          }
        });
    } else if (!localCandidate) {
      navigate("/login");
    }

    return () => {
      isMounted = false;
    };
  }, [userSlug, navigate]);

  const handleLanguageChange = (newLang) => {
    setLang(newLang);
    localStorage.setItem("preferred_language", newLang);
  };

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("user");
    sessionStorage.removeItem("hasActiveStatement");
    navigate("/login");
  };

  const activeSlug = userSlug || getUserSlug(user) || "user";

  const handleClearData = async () => {
    if (!user) return;
    const confirm = window.confirm(t("confirmClear", lang));
    if (!confirm) return;

    setClearing(true);
    try {
      await fetch(`${API_BASE}/statements/clear`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: user.customer_id || user.id,
        }),
      });

      sessionStorage.removeItem("hasActiveStatement");
      navigate(`/${activeSlug}-dashboard/upload-statement`);
    } catch (err) {
      console.error("Failed to clear data:", err);
    } finally {
      setClearing(false);
    }
  };

  // Safe fallback UI if user is still synchronizing
  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white px-6">
        <div className="w-10 h-10 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-slate-400 text-sm">Loading your banking dashboard...</p>
      </div>
    );
  }

  const customerId = user.customer_id || user.id || 1;
  const currencySymbol = user.currency_symbol || "$";
  const currencyCode = user.currency_code || "USD";

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Navbar */}
      <nav className="flex flex-wrap justify-between items-center px-6 md:px-10 py-5 border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-50 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Landmark size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-cyan-400">
              {t("appTitle", lang)}
            </h1>
            <p className="text-xs text-slate-400">
              {user.country ? `${user.country} • Currency: ${currencySymbol} (${currencyCode})` : ""}
            </p>
          </div>
        </div>

        {/* Right Nav Actions */}
        <div className="flex items-center gap-3">
          {/* Language Switcher */}
          <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300">
            <Globe size={15} className="text-cyan-400" />
            <select
              value={lang}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="bg-transparent outline-none cursor-pointer text-white font-medium"
            >
              {ALL_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code} className="bg-slate-900 text-white">
                  {l.name}
                </option>
              ))}
            </select>
          </div>

          {/* Upload New Statement Button */}
          <button
            onClick={() => navigate(`/${activeSlug}-dashboard/upload-statement`)}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold transition cursor-pointer"
            title="Upload new statement"
          >
            <UploadCloud size={15} className="text-cyan-400" />
            <span className="hidden sm:inline">{t("uploadStatement", lang)}</span>
          </button>

          {/* Remove / Clear Data Button */}
          <button
            onClick={handleClearData}
            disabled={clearing}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-red-950/60 border border-slate-700 hover:border-red-600/50 text-slate-300 hover:text-red-300 px-3.5 py-2 rounded-xl text-xs font-semibold transition cursor-pointer disabled:opacity-50"
            title="Clear all statement data"
          >
            <Trash2 size={15} className="text-red-400" />
            <span className="hidden sm:inline">{clearing ? "Clearing..." : t("clearData", lang)}</span>
          </button>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 bg-red-600 hover:bg-red-700 px-4 py-2 rounded-xl text-xs font-semibold transition cursor-pointer text-white shadow-md shadow-red-600/20"
          >
            <LogOut size={15} />
            {t("logout", lang)}
          </button>
        </div>
      </nav>

      {/* Main Dashboard Section */}
      <section className="max-w-7xl mx-auto px-6 md:px-10 py-8">
        <DashboardHeader user={user} lang={lang} />

        <DashboardCards customerId={customerId} currencySymbol={currencySymbol} currencyCode={currencyCode} lang={lang} />

        <SpendingChart customerId={customerId} currencySymbol={currencySymbol} lang={lang} />

        <RecentTransactions customerId={customerId} currencySymbol={currencySymbol} currencyCode={currencyCode} lang={lang} />

        <AIRecommendation customerId={customerId} currencySymbol={currencySymbol} lang={lang} />

        <AISpendingInsights customerId={customerId} currencySymbol={currencySymbol} currencyCode={currencyCode} lang={lang} />
      </section>
    </div>
  );
}
