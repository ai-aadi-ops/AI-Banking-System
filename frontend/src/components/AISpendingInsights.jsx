import { API_BASE } from "../config";
import { useEffect, useState } from "react";
import { PieChart } from "lucide-react";
import { formatCurrency, t } from "../utils/i18n";

export default function AISpendingInsights({
  customerId = 1,
  currencySymbol = "$",
  currencyCode = "USD",
  lang = "en",
  cleared = false,
}) {
  const [data, setData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    fetch(`${API_BASE}/ai/analyze/${customerId}${cleared ? "?cleared=true" : ""}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((result) => {
        if (!isMounted) return;
        if (result && !result.detail) {
          setData(result);
        }
      })
      .catch((err) => {
        console.warn("AISpendingInsights fetch error:", err);
      });

    return () => {
      isMounted = false;
    };
  }, [customerId, cleared]);

  if (!data || data.detail) return null;

  return (
    <div className="mt-10 rounded-2xl bg-slate-900 border border-slate-800 p-8">
      <div className="flex items-center gap-3">
        <PieChart className="text-cyan-400" size={30} />
        <h2 className="text-3xl font-bold">
          {t("aiSpendingInsights", lang)}
        </h2>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mt-8">
        <div>
          <p className="text-slate-400">Total Spent</p>
          <h2 className="text-4xl font-bold mt-2">
            {formatCurrency(data.total_spent || 0, currencySymbol, currencyCode)}
          </h2>

          <div className="mt-6">
            <p className="text-slate-400">
              {t("highestCategory", lang)}
            </p>

            <h3 className="text-2xl font-semibold text-cyan-400">
              {data.highest_spending_category || "None"}
            </h3>

            <p className="text-slate-300">
              {formatCurrency(data.highest_category_amount || 0, currencySymbol, currencyCode)}
            </p>
          </div>

          <div className="mt-6">
            <p className="text-slate-400">
              {t("favoriteMerchant", lang)}
            </p>

            <h3 className="text-2xl font-semibold text-green-400">
              {data.favorite_merchant || "None"}
            </h3>

            <p className="text-slate-300">
              {formatCurrency(data.merchant_spending || 0, currencySymbol, currencyCode)}
            </p>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-bold mb-4">
            {t("categoryBreakdown", lang)}
          </h3>

          {Object.entries(data.category_breakdown || {}).map(([cat, amt]) => (
            <div
              key={cat}
              className="flex justify-between border-b border-slate-700 py-3 text-sm md:text-base"
            >
              <span>{cat}</span>
              <span className="font-semibold text-cyan-300">
                {formatCurrency(amt, currencySymbol, currencyCode)}
              </span>
            </div>
          ))}

          {(!data.category_breakdown || Object.keys(data.category_breakdown).length === 0) && (
            <p className="text-slate-400 text-sm py-4">No category spending data available yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
