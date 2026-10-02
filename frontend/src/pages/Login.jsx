import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE } from "../config";
import { t, ALL_LANGUAGES } from "../utils/i18n";
import { Landmark, Mail, Lock, Globe, Sparkles } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [lang, setLang] = useState("hi");
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedLang = localStorage.getItem("preferred_language") || "hi";
    setLang(savedLang);
  }, []);

  const handleLanguageChange = (newLang) => {
    setLang(newLang);
    localStorage.setItem("preferred_language", newLang);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Invalid login credentials");
      }

      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("preferred_language", data.user.preferred_language || lang);

      // If demo user Robert Wilson, go straight to dashboard
      if (data.user.email === "robert.wilson@demo.com") {
        sessionStorage.setItem("hasActiveStatement", "true");
        navigate("/dashboard");
      } else {
        // For new user, redirect to statement upload
        navigate("/upload-statement");
      }
    } catch (err) {
      setError(err.message || "Failed to log in. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setDemoLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "robert.wilson@demo.com",
          password: "demo_password",
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Demo login failed");
      }

      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("preferred_language", data.user.preferred_language || "en");
      sessionStorage.setItem("hasActiveStatement", "true");

      navigate("/dashboard");
    } catch (err) {
      setError("Unable to initialize demo user. Please try again.");
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-between px-6 py-8">
      {/* Top language bar */}
      <div className="flex justify-end">
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
          <Globe size={14} className="text-cyan-400" />
          <select
            value={lang}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="bg-transparent outline-none cursor-pointer text-white"
          >
            {ALL_LANGUAGES.map((l) => (
              <option key={l.code} value={l.code} className="bg-slate-900">
                {l.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="w-full max-w-md mx-auto rounded-3xl bg-slate-900 border border-slate-800 p-8 shadow-2xl">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400">
            <Landmark size={36} />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-cyan-400 text-center">
          {t("appTitle", lang)}
        </h1>

        <p className="text-center text-slate-400 mt-2 text-sm">
          {t("signIn", lang)}
        </p>

        {error && (
          <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              {t("emailPlaceholder", lang)}
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-4 text-slate-500" size={18} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
                className="w-full rounded-xl bg-slate-800 py-3.5 pl-12 pr-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                {t("passwordPlaceholder", lang)}
              </label>
              <Link
                to="/forgot-password"
                className="text-xs text-cyan-400 hover:underline"
              >
                {t("forgotPassword", lang)}
              </Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-4 text-slate-500" size={18} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-xl bg-slate-800 py-3.5 pl-12 pr-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-4 font-bold text-white shadow-lg shadow-cyan-500/25 hover:from-cyan-600 hover:to-blue-700 transition disabled:opacity-50 cursor-pointer mt-2"
          >
            {loading ? "Signing in..." : t("login", lang)}
          </button>
        </form>

        {/* Create Account option */}
        <div className="mt-5 text-center">
          <Link
            to="/register"
            className="w-full inline-block py-3 rounded-xl border border-slate-700 hover:border-cyan-500 text-slate-300 hover:text-white font-semibold text-sm transition"
          >
            {t("createAccount", lang)} →
          </Link>
        </div>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-slate-900 px-3 text-slate-500">Or</span>
          </div>
        </div>

        {/* Instant Demo Login Button */}
        <button
          onClick={handleDemoLogin}
          disabled={demoLoading}
          className="w-full rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-yellow-500/50 py-3.5 px-4 text-sm font-semibold text-yellow-300 flex items-center justify-center gap-2 transition cursor-pointer"
        >
          <Sparkles size={16} className="text-yellow-400" />
          {demoLoading ? "Loading Demo..." : t("orLoginDemo", lang)}
        </button>

        <div className="mt-6 text-center">
          <Link to="/" className="text-xs text-slate-500 hover:text-slate-400">
            {t("backToHome", lang)}
          </Link>
        </div>
      </div>

      <div className="text-center text-xs text-slate-600 py-2">
        AI Banking Platform • Powered by Gemini AI
      </div>
    </div>
  );
}
