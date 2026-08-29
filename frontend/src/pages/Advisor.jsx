import { useState } from "react";
import { API_BASE } from "../config";
import ReactMarkdown from "react-markdown";
import { useNavigate } from "react-router-dom";

export default function Advisor() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [offer, setOffer] = useState(null);
  const [accepting, setAccepting] = useState(false);
  const [loading, setLoading] = useState(false);

  const suggestions = [
    "Can I afford an iPhone?",
    "How can I save more money?",
    "Should I apply for a personal loan?",
    "Give me investment advice.",
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
          customer_id: 1,
          question: q,
        }),
      });

      const data = await res.json();

      setAnswer(data.answer);
      setOffer(data.offer);
    } catch (err) {
      setAnswer("Unable to connect to AI Advisor.");
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
          customer_id: 1,
          offer,
        }),
      });

      const data = await res.json();
      
      if (data.status === "SUCCESS") {
	      navigate(data.redirect_url);
      } else if (data.status === "LOAN_RECOMMENDED") {
	      setOffer(data.offer);
	      setAnswer(`${answer}\n\n${data.message}`);
      }
       else {
        setAnswer(`${answer}\n\n${data.message || "Offer could not be completed."}`);
      }
    } catch (err) {
      setAnswer(`${answer}\n\nUnable to complete the demo offer right now.`);
    }

    setAccepting(false);
  }

  return (
    <>
      <div className="mb-6">
        <button
          onClick={() => navigate("/dashboard")}
          className="rounded-xl bg-gradient-to-r from-red-600 to-red-500 px-5 py-2 font-semibold text-white shadow-lg shadow-red-500/40 hover:from-red-700 hover:to-red-600 transition-all duration-300"
        >
          ← Back to Dashboard
        </button>
      </div>

      <div
        style={{
          minHeight: "100vh",
          background: "#08111F",
          color: "white",
          padding: "40px",
        }}
      >
        <div
          style={{
            maxWidth: "1100px",
            margin: "auto",
          }}
        >
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
                opacity: .9,
                marginTop: 10,
                fontSize: 18,
              }}
            >
              Ask anything about spending, savings,
              investments, loans and financial planning.
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
                  background: "#172554",
                  color: "white",
                  border: "none",
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

            <textarea
              rows="5"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Example: Can I buy a laptop worth $8,000 this month?"
              style={{
                width: "100%",
                borderRadius: 12,
                padding: 15,
                fontSize: 16,
                marginTop: 15,
              }}
            />

            <button
              onClick={() => askAI()}
              style={{
                marginTop: 20,
                padding: "14px 35px",
                background: "#06b6d4",
                color: "white",
                border: "none",
                borderRadius: 10,
                cursor: "pointer",
                fontSize: 17,
                fontWeight: "bold",
              }}
            >
              {loading ? "🤖 Thinking..." : "🚀 Ask AI"}
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
                <p style={{ opacity: .85, margin: 0 }}>
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
                      ${Number(offer.amount).toLocaleString()}
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
                        ${Number(offer.monthly_emi).toLocaleString()}
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
    </>
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
  opacity: .8,
};

const offerValueStyle = {
  margin: "6px 0 0",
  fontSize: 26,
};

