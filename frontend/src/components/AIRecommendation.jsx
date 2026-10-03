import { API_BASE } from "../config";
import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { t } from "../utils/i18n";

export default function AIRecommendation({
  customerId = 1,
  currencySymbol = "$",
  lang = "en",
  cleared = false,
}) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    fetch(`${API_BASE}/ai/financial-health/${customerId}${cleared ? "?cleared=true" : ""}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!isMounted) return;
        if (data && !data.detail) {
          setHealth(data);
        }
      })
      .catch((err) => {
        console.warn("AI Recommendation fetch error:", err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [customerId, cleared]);

  const score = health?.financial_health_score ?? (loading ? "..." : 80);
  const status = health?.status ?? (loading ? "Evaluating..." : "Good Standing");
  const savingsRatio = health?.savings_ratio ?? 0;
  const spendingRatio = health?.spending_ratio ?? 0;
  const adviceList = Array.isArray(health?.advice) && health.advice.length > 0
    ? health.advice
    : [
        "Maintain adequate liquidity for emergencies.",
        "Track monthly variable expenses to optimize budget.",
        "Investment allocation recommended for long-term growth.",
      ];

  return (
    <div className="mt-10 rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-700 p-8 shadow-xl">
      <div className="flex items-center gap-3">
        <Sparkles className="text-yellow-300" size={30} />
        <h2 className="text-3xl font-bold text-white">
          {t("aiRecommendation", lang)}
        </h2>
      </div>

      <div className="mt-6 grid md:grid-cols-2 gap-6 text-white">
        <div>
          <p className="text-slate-200">
            {t("healthScore", lang)}
          </p>
          <h2 className="text-5xl font-bold">
            {score}/100
          </h2>
          <p className="mt-2 text-yellow-200 font-medium">
            {status}
          </p>
        </div>

        <div>
          <p>{t("savingsRatio", lang)}</p>
          <h3 className="text-2xl font-bold">
            {savingsRatio}%
          </h3>

          <p className="mt-4">
            {t("spendingRatio", lang)}
          </p>
          <h3 className="text-2xl font-bold">
            {spendingRatio}%
          </h3>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="font-bold text-xl text-white mb-3">
          AI Advice
        </h3>

        <ul className="space-y-2">
          {adviceList.map((item, index) => (
            <li key={index} className="text-slate-100 flex items-start gap-2">
              <span className="text-cyan-200 font-bold">✔</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
