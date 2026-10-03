import { useState, useEffect } from "react";
import { API_BASE } from "../config";
import ReactMarkdown from "react-markdown";
import { useNavigate, useParams } from "react-router-dom";
import { formatCurrency } from "../utils/i18n";
import {
  getUserSlug,
  DEMO_ROBERT_USER,
  resolveInitialUserForSlug,
  saveUserSession,
} from "../utils/userSlug";

export default function Advisor() {
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

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [offer, setOffer] = useState(null);
  const [accepting, setAccepting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [deleteStage, setDeleteStage] = useState("none");

  useEffect(() => {
    let isMounted = true;

    if (userSlug === "robert") {
      setUser(DEMO_ROBERT_USER);
      setLang("en");
      return;
    }

    const localCandidate = resolveInitialUserForSlug(userSlug);
    if (localCandidate) {
      setUser(localCandidate);
      const savedLang = localStorage.getItem("preferred_language") || localCandidate.preferred_language || "en";
      setLang(savedLang);
    }

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
            }
          }
        })
        .catch((err) => {
          console.warn("Advisor slug resolve warning:", err);
        });
    }

    return () => {
      isMounted = false;
    };
  }, [userSlug]);

  const activeSlug = userSlug || getUserSlug(user) || "user";
  const currencySymbol = user?.currency_symbol || (activeSlug === "robert" ? "$" : "₹");
  const currencyCode = user?.currency_code || (activeSlug === "robert" ? "USD" : "INR");
  const customerId = user?.customer_id || user?.id || (activeSlug === "robert" ? 1 : 8);
  const isDemoAccount = activeSlug === "robert" || Number(customerId) === 1;

  const sampleAmount = currencySymbol === "₹" ? "80,000" : "1,200";

  const suggestions = lang === "hi" ? [
    `क्या मैं इस महीने ${currencySymbol}${sampleAmount} का स्मार्टफोन खरीद सकता हूँ?`,
    "मैं अपने बैंक खाते से अधिक पैसे कैसे बचा सकता हूँ?",
    "क्या मुझे व्यक्तिगत ऋण (Personal Loan) लेना चाहिए?",
    "मेरी वित्तीय स्थिति के अनुसार मुझे निवेश सलाह दें।",
    "मेरा खाता हटाएं (Delete my account)",
  ] : [
    `Can I afford a smartphone worth ${currencySymbol}${sampleAmount} this month?`,
    "How can I save more money every month?",
    "Should I apply for a personal loan?",
    "Give me investment advice based on my balance.",
    "Delete my account",
  ];

  async function askAI(q = question) {
    if (!q.trim()) return;

    setQuestion(q);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          customer_id: customerId,
          question: q,
          language: lang,
          delete_stage: deleteStage,
        }),
      });

      const data = await res.json();
      setAnswer(data.answer || data.reply || "No response received from AI Advisor.");
      setOffer(data.offer || null);

      if (data.delete_step) {
        setDeleteStage(data.delete_step);
        if (data.delete_step !== "none") {
          setQuestion("");
        }
      }

      if (data.account_deleted || data.delete_step === "deleted") {
        localStorage.removeItem("isLoggedIn");
        localStorage.removeItem("user");
        localStorage.removeItem(`user_by_slug_${activeSlug}`);
        sessionStorage.removeItem("hasActiveStatement");
        sessionStorage.removeItem(`active_customer_id_${activeSlug}`);
        setTimeout(() => {
          navigate("/register");
        }, 1600);
      }
    } catch (err) {
      console.warn("Advisor chat error:", err);
      setAnswer("Unable to connect to AI Advisor. Please try again.");
      setOffer(null);
    }

    setLoading(false);
  }

  async function acceptOffer() {
    if (!offer) return;
    setAccepting(true);

    try {
      const res = await fetch(`${API_BASE}/offers/accept`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          customer_id: customerId,
          offer,
        }),
      });

      const data = await res.json();

      if (data.status === "SUCCESS") {
        navigate(data.redirect_url);
      } else if (data.status === "LOAN_RECOMMENDED") {
        setOffer(data.offer);
        setAnswer(`${answer}\n\n${data.message}`);
      } else {
        setAnswer(`${answer}\n\n${data.message || "Offer could not be completed."}`);
      }
    } catch (err) {
      console.warn("Accept offer error:", err);
      setAnswer(`${answer}\n\nUnable to complete the demo offer right now.`);
    }

    setAccepting(false);
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#08111F",
        color: "white",
        padding: "40px 24px",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "auto",
        }}
      >
        <div className="mb-6 flex items-center justify-between flex-wrap gap-4">
          <button
            onClick={() => navigate(`/${activeSlug}-dashboard`)}
            className="rounded-xl bg-gradient-to-r from-red-600 to-red-500 px-5 py-2 font-semibold text-white shadow-lg shadow-red-500/40 hover:from-red-700 hover:to-red-600 transition-all duration-300 cursor-pointer flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>

          {user && (
            <span className="text-sm text-cyan-300 bg-slate-900 border border-slate-700 px-4 py-1.5 rounded-full">
              Account: <strong>{user.full_name}</strong> ({currencySymbol} {currencyCode})
            </span>
          )}
        </div>

        <div
          style={{
            background: "linear-gradient(135deg,#0ea5e9,#2563eb)",
            borderRadius: "18px",
            padding: "30px",
            marginBottom: "30px",
            boxShadow: "0 10px 40px rgba(0,0,0,.3)",
          }}
        >
          <h1 style={{ margin: 0, fontSize: 36 }}>
            🤖 AI Financial Advisor
          </h1>

          <p
            style={{
              opacity: 0.9,
              marginTop: 10,
              fontSize: 18,
            }}
          >
            Ask anything about spending, savings, investments, loans and financial planning.
          </p>
        </div>

        <h3>💡 Suggested Questions</h3>

        <div
          style={{
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
            marginBottom: 35,
          }}
        >
          {suggestions.map((item) => (
            <button
              key={item}
              onClick={() => askAI(item)}
              style={{
                background: item.toLowerCase().includes("delete") ? "#450a0a" : "#172554",
                color: "white",
                border: item.toLowerCase().includes("delete") ? "1px solid #ef4444" : "none",
                borderRadius: "25px",
                padding: "10px 18px",
                cursor: "pointer",
              }}
            >
              {item}
            </button>
          ))}
        </div>

        <div
          style={{
            background: "#101827",
            padding: 25,
            borderRadius: 15,
            boxShadow: "0 0 20px rgba(0,0,0,.3)",
          }}
        >
          <h2>💬 Ask Your AI Advisor</h2>

          {deleteStage === "convinced_once" && (
            <div className="mt-3 mb-2 rounded-xl bg-amber-500/15 border border-amber-500/40 p-3 text-sm text-amber-200 flex items-center justify-between flex-wrap gap-2">
              <span>⚠️ AI Advisor asked you to reconsider deleting your account. Still want to delete?</span>
              <div className="flex gap-2">
                <button
                  onClick={() => askAI("Yes, delete my account")}
                  className="rounded-lg bg-red-600 hover:bg-red-700 px-3 py-1 text-xs font-bold text-white cursor-pointer"
                >
                  Yes, Still Delete Account
                </button>
                <button
                  onClick={() => askAI("cancel")}
                  className="rounded-lg bg-slate-700 hover:bg-slate-600 px-3 py-1 text-xs font-semibold text-white cursor-pointer"
                >
                  Keep My Account
                </button>
              </div>
            </div>
          )}

          {deleteStage === "awaiting_password" && (
            <div className="mt-3 mb-2 rounded-xl bg-red-500/15 border border-red-500/40 p-3 text-sm text-red-200">
              {isDemoAccount
                ? "🛡️ Demo Account Protection: Enter the Admin Password below and click Ask AI to delete the demo account (or type 'cancel')."
                : "🔐 Security Verification: Enter your account login password below and click Ask AI to permanently delete your account (or type 'cancel')."}
            </div>
          )}

          <textarea
            rows="5"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={
              deleteStage === "awaiting_password"
                ? isDemoAccount
                  ? "Enter Admin Password to confirm Demo Account deletion..."
                  : "Enter your account login password to confirm deletion..."
                : `Example: Can I buy a laptop worth ${currencySymbol}${sampleAmount} this month?`
            }
            style={{
              width: "100%",
              borderRadius: 12,
              padding: 15,
              fontSize: 16,
              marginTop: 15,
              background: "#1e293b",
              color: "#fff",
              border: deleteStage === "awaiting_password" ? "1px solid #ef4444" : "1px solid #334155",
            }}
          />

          <button
            onClick={() => askAI()}
            disabled={loading}
            style={{
              marginTop: 20,
              padding: "14px 35px",
              background: deleteStage === "awaiting_password" ? "#dc2626" : "#06b6d4",
              color: "white",
              border: "none",
              borderRadius: 10,
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: 17,
              fontWeight: "bold",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading
              ? "🤖 Thinking..."
              : deleteStage === "awaiting_password"
              ? "🔐 Verify Password & Delete Account"
              : "🚀 Ask AI"}
          </button>

          {answer && (
            <div
              style={{
                marginTop: 35,
                background: "#1E293B",
                borderRadius: 15,
                padding: 25,
              }}
            >
              <h3 style={{ color: "#22d3ee" }}>
                🤖 AI Recommendation
              </h3>

              <div
                style={{
                  lineHeight: 1.8,
                  fontSize: 16,
                }}
              >
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            </div>
          )}

          {offer && (
            <div
              style={{
                marginTop: 25,
                background:
                  offer.type === "loan"
                    ? "linear-gradient(135deg,#7c2d12,#ea580c)"
                    : "linear-gradient(135deg,#064e3b,#059669)",
                borderRadius: 15,
                padding: 25,
                border: "1px solid rgba(255,255,255,.18)",
              }}
            >
              <p style={{ opacity: 0.85, margin: 0 }}>
                {offer.type === "loan"
                  ? "Low balance detected"
                  : "Personalized AI offer"}
              </p>

              <h3 style={{ fontSize: 28, margin: "8px 0" }}>
                {offer.title}
              </h3>

              <p style={{ lineHeight: 1.7 }}>
                {offer.reason}
              </p>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: 14,
                  marginTop: 18,
                }}
              >
                <div style={offerStatStyle}>
                  <p style={offerLabelStyle}>Amount</p>
                  <h2 style={offerValueStyle}>
                    {formatCurrency(offer.amount, currencySymbol, currencyCode)}
                  </h2>
                </div>

                {offer.discount_percent > 0 && (
                  <div style={offerStatStyle}>
                    <p style={offerLabelStyle}>Discount</p>
                    <h2 style={offerValueStyle}>
                      {offer.discount_percent}%
                    </h2>
                  </div>
                )}

                {offer.type === "loan" && offer.monthly_emi > 0 && (
                  <div style={offerStatStyle}>
                    <p style={offerLabelStyle}>Monthly Deduction</p>
                    <h2 style={offerValueStyle}>
                      {formatCurrency(offer.monthly_emi, currencySymbol, currencyCode)}
                    </h2>
                  </div>
                )}
              </div>

              <button
                onClick={acceptOffer}
                disabled={accepting}
                style={{
                  marginTop: 20,
                  padding: "14px 26px",
                  borderRadius: 12,
                  border: "none",
                  background: "white",
                  color: "#0f172a",
                  fontWeight: 800,
                  cursor: accepting ? "not-allowed" : "pointer",
                }}
              >
                {accepting ? "Redirecting..." : `${offer.cta} → Fake Checkout`}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const offerStatStyle = {
  background: "rgba(15,23,42,.55)",
  border: "1px solid rgba(255,255,255,.16)",
  borderRadius: 14,
  padding: 16,
};

const offerLabelStyle = {
  margin: 0,
  opacity: 0.8,
};

const offerValueStyle = {
  margin: "6px 0 0",
  fontSize: 26,
};
