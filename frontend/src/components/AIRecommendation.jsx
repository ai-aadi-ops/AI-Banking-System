import { API_BASE } from "../config";
import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

import { t } from "../utils/i18n";

export default function AIRecommendation({
  customerId = 1,
  currencySymbol = "$",
  lang = "en",
}) {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/ai/financial-health/${customerId}`)
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(console.error);
  }, [customerId]);

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
          {t("aiRecommendation", lang)}
        </h2>
      </div>

      <div className="mt-6 grid md:grid-cols-2 gap-6 text-white">

        <div>
          <p className="text-slate-200">
            {t("healthScore", lang)}
          </p>

          <h2 className="text-5xl font-bold">
            {health.financial_health_score}/100
          </h2>

          <p className="mt-2 text-yellow-200 font-medium">
            {health.status}
          </p>
        </div>

        <div>
          <p>{t("savingsRatio", lang)}</p>
          <h3 className="text-2xl font-bold">
            {health.savings_ratio || 0}%
          </h3>

          <p className="mt-4">
            {t("spendingRatio", lang)}
          </p>

          <h3 className="text-2xl font-bold">
            {health.spending_ratio || 0}%
          </h3>
        </div>

      </div>


      <div className="mt-8">

        <h3 className="font-bold text-xl text-white mb-3">
          AI Advice
        </h3>

    <ul className="space-y-2">
      {(health.advice || []).map((item, index) => (
        <li key={index} className="text-slate-100">
          ✔ {item}
        </li>
      ))}

      {(!health.advice || health.advice.length === 0) && (
        <li className="text-slate-200">
          No AI advice available yet.
        </li>
      )}
    </ul>

      </div>

    </div>
  );
}
