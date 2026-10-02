import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE } from "../config";
import { COUNTRIES, INDIAN_LANGUAGES, ALL_LANGUAGES, t } from "../utils/i18n";
import { Globe, User, Mail, Lock, Landmark } from "lucide-react";

export default function Register() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [selectedCountry, setSelectedCountry] = useState(COUNTRIES[0]);
  const [selectedLanguage, setSelectedLanguage] = useState("hi");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCountryChange = (e) => {
    const found = COUNTRIES.find((c) => c.name === e.target.value) || COUNTRIES[0];
    setSelectedCountry(found);
    if (found.name === "India") {
      setSelectedLanguage("hi");
    } else {
      setSelectedLanguage(found.defaultLang || "en");
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!fullName || !email || !password) {
      setError("Please fill in all required fields.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName,
          email,
          password,
          country: selectedCountry.name,
          preferred_language: selectedLanguage,
          currency_code: selectedCountry.currency,
          currency_symbol: selectedCountry.symbol,
        }),
      });

      let data = {};
      try {
        data = await res.json();
      } catch (parseErr) {
        data = { detail: `Server responded with status ${res.status}` };
      }

      if (!res.ok) {
        throw new Error(data.detail || `Registration failed (${res.status})`);
      }

      // Save user session
      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("preferred_language", data.user.preferred_language || selectedLanguage);

      // Navigate to statement upload
      navigate("/upload-statement");
    } catch (err) {
      if (err.message && err.message.toLowerCase().includes("failed to fetch")) {
        setError("Unable to connect to the backend server. The free-tier service on Render may be waking up (cold-start takes ~20-30s). Please wait 15 seconds and click Sign Up again.");
      } else {
        setError(err.message || "Failed to create account. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const availableLanguages = selectedCountry.name === "India" ? INDIAN_LANGUAGES : ALL_LANGUAGES;

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-lg rounded-3xl bg-slate-900 border border-slate-800 p-8 shadow-2xl">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400">
            <Landmark size={36} />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-cyan-400 text-center">
          {t("registerTitle", selectedLanguage)}
        </h1>

        <p className="text-center text-slate-400 mt-2 text-sm">
          {t("appTitle", selectedLanguage)} - Sign up for your personalized banking profile
        </p>

        {error && (
          <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="mt-6 space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              {t("fullName", selectedLanguage)} *
            </label>
            <div className="relative">
              <User className="absolute left-4 top-4 text-slate-500" size={18} />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Aaditya Sharma"
                className="w-full rounded-xl bg-slate-800 py-3.5 pl-12 pr-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              {t("emailPlaceholder", selectedLanguage)} *
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-4 text-slate-500" size={18} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="aaditya@example.com"
                className="w-full rounded-xl bg-slate-800 py-3.5 pl-12 pr-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              {t("passwordPlaceholder", selectedLanguage)} *
            </label>
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

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                {t("country", selectedLanguage)}
              </label>
              <select
                value={selectedCountry.name}
                onChange={handleCountryChange}
                className="w-full rounded-xl bg-slate-800 py-3.5 px-3 text-white outline-none border border-slate-700 focus:border-cyan-500"
              >
                {COUNTRIES.map((c) => (
                  <option key={c.name} value={c.name}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                {t("currency", selectedLanguage)}
              </label>
              <div className="w-full rounded-xl bg-slate-800/60 py-3.5 px-4 text-cyan-400 font-bold border border-slate-700 flex items-center justify-between">
                <span>{selectedCountry.currency}</span>
                <span className="text-lg">{selectedCountry.symbol}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1 flex items-center gap-1.5">
              <Globe size={14} className="text-cyan-400" />
              {t("preferredLanguage", selectedLanguage)}
            </label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full rounded-xl bg-slate-800 py-3.5 px-3 text-white outline-none border border-slate-700 focus:border-cyan-500"
            >
              {availableLanguages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-4 font-bold text-white shadow-lg shadow-cyan-500/25 hover:from-cyan-600 hover:to-blue-700 transition disabled:opacity-50 mt-4 cursor-pointer"
          >
            {loading ? "Creating Profile..." : t("signUpButton", selectedLanguage)}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          {t("alreadyHaveAccount", selectedLanguage)}{" "}
          <Link to="/login" className="text-cyan-400 hover:underline font-semibold">
            {t("login", selectedLanguage)}
          </Link>
        </div>

        <div className="mt-4 text-center">
          <Link to="/" className="text-xs text-slate-500 hover:text-slate-400">
            {t("backToHome", selectedLanguage)}
          </Link>
        </div>
      </div>
    </div>
  );
}
