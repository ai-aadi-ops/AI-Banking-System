import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../config";
import { t, ALL_LANGUAGES } from "../utils/i18n";
import {
  UploadCloud,
  FileText,
  FileSpreadsheet,
  Image as ImageIcon,
  CheckCircle,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Globe,
  Landmark,
} from "lucide-react";

export default function UploadStatement() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("hi");
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successResult, setSuccessResult] = useState(null);
  const [isRefreshState, setIsRefreshState] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/login");
      return;
    }
    const parsedUser = JSON.parse(storedUser);
    setUser(parsedUser);

    const savedLang = localStorage.getItem("preferred_language") || parsedUser.preferred_language || "hi";
    setLang(savedLang);

    // Check if redirected due to page refresh
    if (sessionStorage.getItem("refresh_redirect") === "true") {
      setIsRefreshState(true);
      sessionStorage.removeItem("refresh_redirect");
    }
  }, [navigate]);

  const handleLanguageChange = (newLang) => {
    setLang(newLang);
    localStorage.setItem("preferred_language", newLang);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    if (e) e.preventDefault();
    if (!file || !user) {
      setError("Please select a file to upload.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("customer_id", user.customer_id || user.id);
    formData.append("country", user.country || "India");

    try {
      const res = await fetch(`${API_BASE}/statements/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to process bank statement");
      }

      setSuccessResult(data);

      // Update user with detected currency
      const updatedUser = {
        ...user,
        currency_code: data.currency_code,
        currency_symbol: data.currency_symbol,
      };
      localStorage.setItem("user", JSON.stringify(updatedUser));
      sessionStorage.setItem("hasActiveStatement", "true");

      setTimeout(() => {
        navigate("/dashboard");
      }, 1200);
    } catch (err) {
      setError(err.message || "Failed to parse bank statement. Please try another file or try sample data.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async () => {
    if (!user) return;
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/statements/sample`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: user.customer_id || user.id,
          currency: user.currency_code || "INR",
          country: user.country || "India",
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to load sample statement");
      }

      setSuccessResult(data);

      const updatedUser = {
        ...user,
        currency_code: data.currency_code,
        currency_symbol: data.currency_symbol,
      };
      localStorage.setItem("user", JSON.stringify(updatedUser));
      sessionStorage.setItem("hasActiveStatement", "true");

      setTimeout(() => {
        navigate("/dashboard");
      }, 1000);
    } catch (err) {
      setError(err.message || "Failed to load sample data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col justify-between">
      {/* Top Navbar */}
      <nav className="flex justify-between items-center px-6 md:px-12 py-5 border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Landmark size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-cyan-400">
              {t("appTitle", lang)}
            </h1>
            <p className="text-xs text-slate-400">
              {user ? `User: ${user.full_name} (${user.country || "India"})` : ""}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-300">
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

          <button
            onClick={() => {
              localStorage.removeItem("isLoggedIn");
              localStorage.removeItem("user");
              sessionStorage.removeItem("hasActiveStatement");
              navigate("/login");
            }}
            className="text-xs bg-slate-800 hover:bg-slate-700 px-3 py-2 rounded-xl text-slate-300 transition"
          >
            {t("logout", lang)}
          </button>
        </div>
      </nav>

      {/* Main Container */}
      <main className="max-w-3xl w-full mx-auto px-6 py-10">
        {/* Refresh Notice Alert if redirected */}
        {isRefreshState && (
          <div className="mb-6 p-4 bg-amber-500/15 border border-amber-500/40 rounded-2xl flex items-start gap-3 text-amber-200">
            <AlertCircle size={22} className="shrink-0 mt-0.5 text-amber-400" />
            <div>
              <p className="font-semibold text-sm">
                {t("refreshNotice", lang)}
              </p>
            </div>
          </div>
        )}

        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white">
            {t("uploadStatement", lang)}
          </h2>
          <p className="mt-3 text-slate-400 text-base max-w-xl mx-auto">
            {t("uploadPrompt", lang)}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/15 border border-red-500/40 rounded-2xl flex items-center gap-3 text-red-300 text-sm">
            <AlertCircle size={20} className="shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {successResult && (
          <div className="mb-6 p-4 bg-green-500/15 border border-green-500/40 rounded-2xl flex items-center gap-3 text-green-300 text-sm">
            <CheckCircle size={20} className="shrink-0 text-green-400" />
            <span>
              {successResult.message} Redirecting to your dashboard...
            </span>
          </div>
        )}

        {/* Drag & Drop Card */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-3xl p-8 md:p-12 text-center transition-all bg-slate-900/60 ${
            dragActive
              ? "border-cyan-400 bg-cyan-950/20 scale-[1.01]"
              : "border-slate-700 hover:border-slate-600"
          }`}
        >
          <input
            type="file"
            id="statement-file-input"
            onChange={handleFileChange}
            accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg,.webp"
            className="hidden"
          />

          <div className="flex justify-center mb-4">
            <div className="p-4 bg-gradient-to-tr from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-2xl text-cyan-400">
              <UploadCloud size={44} />
            </div>
          </div>

          <label
            htmlFor="statement-file-input"
            className="text-lg font-semibold text-white block cursor-pointer hover:text-cyan-400 transition"
          >
            {file ? file.name : t("dragDropText", lang)}
          </label>

          <p className="mt-2 text-xs text-slate-400 max-w-md mx-auto">
            {t("acceptedFormats", lang)}
          </p>

          {/* Format Badges */}
          <div className="flex justify-center gap-3 mt-6">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 border border-slate-700">
              <FileText size={14} className="text-red-400" /> PDF Document
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 border border-slate-700">
              <FileSpreadsheet size={14} className="text-green-400" /> Excel / CSV
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 border border-slate-700">
              <ImageIcon size={14} className="text-blue-400" /> Screenshot
            </span>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
            <button
              onClick={() => document.getElementById("statement-file-input").click()}
              type="button"
              className="px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm border border-slate-700 transition cursor-pointer"
            >
              Browse Computer
            </button>

            {file && (
              <button
                onClick={handleUpload}
                disabled={loading}
                className="px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading ? t("processingStatement", lang) : "Upload & Analyze"}
                <ArrowRight size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Quick Sample / Demo Option */}
        <div className="mt-8 p-6 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-850 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-yellow-500/10 border border-yellow-500/30 rounded-xl text-yellow-400">
              <Sparkles size={22} />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">
                Don't have a PDF statement handy?
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Load a realistic statement formatted in your country's currency ({user?.currency_symbol || "₹"}{user?.currency_code || "INR"}).
              </p>
            </div>
          </div>

          <button
            onClick={handleLoadSample}
            disabled={loading}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-300 border border-yellow-500/40 text-xs font-bold transition disabled:opacity-50 cursor-pointer whitespace-nowrap"
          >
            {loading ? "Loading..." : t("sampleButton", lang)}
          </button>
        </div>
      </main>

      <footer className="text-center py-6 text-xs text-slate-600 border-t border-slate-900">
        AI Banking Demo Platform • Multi-Currency • Multi-Tenant Data Isolation
      </footer>
    </div>
  );
}
