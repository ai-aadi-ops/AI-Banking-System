import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE } from "../config";
import { t } from "../utils/i18n";
import { KeyRound, Mail, Lock, CheckCircle2 } from "lucide-react";

export default function ForgotPassword() {
  const navigate = useNavigate();
  const currentLang = localStorage.getItem("preferred_language") || "en";

  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleReset = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !newPassword) {
      setError("Please provide both email and a new password.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          new_password: newPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Password reset failed");
      }

      setSuccess(true);
    } catch (err) {
      setError(err.message || "Failed to update password. Please check your email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6">
      <div className="w-full max-w-md rounded-3xl bg-slate-900 border border-slate-800 p-8 shadow-2xl">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400">
            <KeyRound size={36} />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-cyan-400 text-center">
          {t("resetPassword", currentLang)}
        </h1>

        <p className="text-center text-slate-400 mt-2 text-sm">
          Enter your registered email and set a new password
        </p>

        {error && (
          <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm text-center">
            {error}
          </div>
        )}

        {success ? (
          <div className="mt-6 text-center space-y-4">
            <div className="flex justify-center text-green-400">
              <CheckCircle2 size={48} />
            </div>
            <p className="text-green-300 font-medium">
              Password has been successfully updated!
            </p>
            <p className="text-slate-400 text-sm">
              You can now log in using your new password.
            </p>
            <button
              onClick={() => navigate("/login")}
              className="w-full rounded-xl bg-cyan-500 py-3.5 font-bold hover:bg-cyan-600 transition mt-4"
            >
              {t("backToLogin", currentLang)}
            </button>
          </div>
        ) : (
          <form onSubmit={handleReset} className="mt-6 space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                {t("emailPlaceholder", currentLang)}
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-4 text-slate-500" size={18} />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@example.com"
                  className="w-full rounded-xl bg-slate-800 py-3.5 pl-12 pr-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-4 text-slate-500" size={18} />
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                  className="w-full rounded-xl bg-slate-800 py-3.5 pl-12 pr-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3.5 font-bold text-white shadow-lg shadow-cyan-500/25 hover:from-cyan-600 hover:to-blue-700 transition disabled:opacity-50 cursor-pointer mt-2"
            >
              {loading ? "Updating Password..." : "Update Password"}
            </button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link to="/login" className="text-cyan-400 hover:underline text-sm font-medium">
            {t("backToLogin", currentLang)}
          </Link>
        </div>
      </div>
    </div>
  );
}
