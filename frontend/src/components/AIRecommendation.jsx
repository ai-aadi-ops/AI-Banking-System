import { API_BASE } from "../config";
import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

export default function AIRecommendation() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/ai/financial-health/1`)
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(console.error);
  }, []);

  if (!health) {
    return (
      <div className="mt-10 rounded-2xl bg-slate-900 p-8 text-white">
        Loading AI Analysis...
      </div>
    );
  }

  return (
    <div className="mt-10 rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-700 p-8 shadow-xl">

      <div className="flex items-center gap-3">
        <Sparkles className="text-yellow-300" size={30} />

        <h2 className="text-3xl font-bold text-white">
          AI Financial Health
        </h2>
      </div>

      <div className="mt-6 grid md:grid-cols-2 gap-6 text-white">

        <div>
          <p className="text-slate-200">
            Health Score
          </p>

          <h2 className="text-5xl font-bold">
            {health.financial_health_score}/100
          </h2>

          <p className="mt-2 text-yellow-200">
            {health.status}
          </p>
        </div>

        <div>
          <p>Savings Ratio</p>
          <h3 className="text-2xl font-bold">
            {health.savings_ratio}%
          </h3>

          <p className="mt-4">
            Spending Ratio
          </p>

          <h3 className="text-2xl font-bold">
            {health.spending_ratio}%
          </h3>
        </div>

      </div>

      <div className="mt-8">

        <h3 className="font-bold text-xl text-white mb-3">
          AI Advice
        </h3>

        <ul className="space-y-2">

          {health.advice.map((item, index) => (
            <li key={index} className="text-slate-100">
              ✔ {item}
            </li>
          ))}

        </ul>

      </div>

    </div>
  );
}
