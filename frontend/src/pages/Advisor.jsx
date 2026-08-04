import { useState } from "react";
import { API_BASE } from "../config";
import ReactMarkdown from "react-markdown";

export default function Advisor() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
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
    } catch (err) {
      setAnswer("Unable to connect to AI Advisor.");
    }

    setLoading(false);
  }

  return (
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
            background:
              "linear-gradient(135deg,#0ea5e9,#2563eb)",
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
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            placeholder="Example: Can I buy a laptop worth ₹80,000 this month?"
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
        </div>
      </div>
    </div>
  );
}
