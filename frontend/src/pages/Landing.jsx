import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { API_BASE } from "../config";
import { Play, Sparkles } from "lucide-react";

export default function Landing() {
  const navigate = useNavigate();
  const [demoLoading, setDemoLoading] = useState(false);

  const handleLiveDemo = async () => {
    setDemoLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "robert.wilson@demo.com",
          password: "demo_password",
        }),
      });

      let data = {};
      try {
        data = await res.json();
      } catch (e) {
        data = {};
      }

      const demoUser = (res.ok && data.user) ? data.user : {
        id: 1,
        customer_id: 1,
        full_name: "Robert Wilson",
        email: "robert.wilson@demo.com",
        country: "United States",
        preferred_language: "en",
        currency_code: "USD",
        currency_symbol: "$",
        is_demo: true,
      };

      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("user", JSON.stringify(demoUser));
      localStorage.setItem("preferred_language", "en");
      sessionStorage.setItem("hasActiveStatement", "true");

      navigate("/robert-dashboard");
    } catch (err) {
      // Offline fallback
      const demoUser = {
        id: 1,
        customer_id: 1,
        full_name: "Robert Wilson",
        email: "robert.wilson@demo.com",
        country: "United States",
        preferred_language: "en",
        currency_code: "USD",
        currency_symbol: "$",
        is_demo: true,
      };
      localStorage.setItem("isLoggedIn", "true");
      localStorage.setItem("user", JSON.stringify(demoUser));
      localStorage.setItem("preferred_language", "en");
      sessionStorage.setItem("hasActiveStatement", "true");
      navigate("/robert-dashboard");
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <section className="mx-auto flex max-w-7xl flex-col items-center px-8 py-24 text-center">
        <p className="mb-4 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-2 text-cyan-300">
          AI Powered Personal Finance Assistant
        </p>

        <h1 className="max-w-5xl text-6xl font-extrabold leading-tight">
          Intelligent Banking
          <br />
          for the Modern World
        </h1>

        <p className="mt-8 max-w-3xl text-xl text-slate-400">
          Analyze spending, predict future expenses, discover personalized
          banking offers and chat with your own AI financial advisor.
        </p>

        <div className="mt-10 flex flex-wrap justify-center gap-5">
          <Link
            to="/register"
            className="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-4 text-lg font-bold text-white hover:from-cyan-600 hover:to-blue-700 shadow-lg shadow-cyan-500/25 transition cursor-pointer"
          >
            Get Started Free
          </Link>

          <button
            onClick={handleLiveDemo}
            disabled={demoLoading}
            className="rounded-xl border border-slate-700 hover:border-cyan-500 px-8 py-4 text-lg font-medium text-slate-300 hover:text-white transition cursor-pointer flex items-center gap-2.5 bg-slate-900/60 disabled:opacity-60"
          >
            {demoLoading ? (
              <>
                <span className="inline-block w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></span>
                <span>Opening Demo...</span>
              </>
            ) : (
              <>
                <Play size={18} className="text-cyan-400 fill-cyan-400" />
                <span>Live Demo</span>
              </>
            )}
          </button>
        </div>
      </section>
    </div>
  );
}
