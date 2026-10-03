import { API_BASE } from "../config";
import { formatCurrency, t } from "../utils/i18n";
import {
  Wallet,
  ArrowUpCircle,
  ArrowDownCircle,
  PiggyBank,
} from "lucide-react";
import { useEffect, useState } from "react";

export default function DashboardCards({
  customerId = 1,
  currencySymbol = "$",
  currencyCode = "USD",
  lang = "en",
  cleared = false,
  onDashboardLoaded,
}) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!customerId) return;
    let isMounted = true;
    setLoading(true);

    fetch(`${API_BASE}/dashboard?customer_id=${customerId}${cleared ? "&cleared=true" : ""}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        if (!isMounted) return;
        if (data && typeof data === "object" && !data.detail) {
          setDashboard(data);
          if (onDashboardLoaded) {
            onDashboardLoaded(data);
          }
        } else {
          setDashboard(null);
        }
      })
      .catch((err) => {
        console.warn("Dashboard fetch error:", err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [customerId, cleared]);

  const activeSym = dashboard?.currency_symbol || currencySymbol;
  const balanceVal = dashboard?.balance ?? 0;
  const incomeVal = dashboard?.income ?? 0;
  const expensesVal = dashboard?.expenses ?? 0;
  const savingsVal = dashboard?.savings ?? 0;

  const isZeroLiquidity = Number(balanceVal) <= 0 && Number(savingsVal) <= 0;
  const rawScore = Number(dashboard?.health_score) || 0;
  const healthScore = isZeroLiquidity ? Math.min(rawScore, 20) : rawScore;
  const healthStatus = isZeroLiquidity
    ? "Poor"
    : dashboard?.health_status || (healthScore >= 85 ? "Excellent" : healthScore >= 70 ? "Good" : healthScore >= 50 ? "Average" : "Poor");

  const isPoor = healthStatus === "Poor" || healthScore < 50;
  const isAverage = healthStatus === "Average" || (healthScore >= 50 && healthScore < 70);

  const scoreTextColor = isPoor
    ? "text-red-400"
    : isAverage
    ? "text-amber-400"
    : "text-green-400";

  const statusBadgeColor = isPoor
    ? "text-red-400"
    : isAverage
    ? "text-amber-300"
    : "text-emerald-300";

  const barGradient = isPoor
    ? "from-red-600 to-orange-500"
    : isAverage
    ? "from-amber-500 to-yellow-400"
    : "from-green-500 to-cyan-400";

  const cards = [
    {
      title: t("totalBalance", lang),
      value: formatCurrency(balanceVal, activeSym, currencyCode),
      icon: Wallet,
      color: "text-cyan-400",
    },
    {
      title: t("monthlyIncome", lang),
      value: formatCurrency(incomeVal, activeSym, currencyCode),
      icon: ArrowUpCircle,
      color: "text-green-400",
    },
    {
      title: t("monthlyExpenses", lang),
      value: formatCurrency(expensesVal, activeSym, currencyCode),
      icon: ArrowDownCircle,
      color: "text-red-400",
    },
    {
      title: t("savings", lang),
      value: formatCurrency(savingsVal, activeSym, currencyCode),
      icon: PiggyBank,
      color: "text-yellow-400",
    },
  ];

  return (
    <>
      <div className="grid gap-6 mt-6 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card, index) => {
          const Icon = card.icon;

          return (
            <div
              key={index}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-cyan-500 transition shadow-lg shadow-black/20"
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-slate-400 text-sm">{card.title}</p>

                  <h2 className="text-2xl md:text-3xl font-bold mt-2 text-white">
                    {loading && !dashboard ? (
                      <span className="inline-block w-24 h-7 bg-slate-800 animate-pulse rounded"></span>
                    ) : (
                      card.value
                    )}
                  </h2>
                </div>

                <Icon className={card.color} size={36} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mt-8">
        <div className="bg-slate-900 border border-cyan-800/60 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
            <span>📊</span>
            <span>{t("financialHealth", lang)}</span>
          </h2>

          <div className={`text-6xl font-extrabold ${scoreTextColor} mt-6`}>
            {healthScore}
            <span className="text-xl text-slate-500 font-normal">/100</span>
          </div>

          <p className={`text-xl mt-2 font-semibold ${statusBadgeColor}`}>
            {healthStatus}
          </p>

          <div className="w-full h-4 bg-slate-800 rounded-full mt-6 overflow-hidden">
            <div
              className={`bg-gradient-to-r ${barGradient} h-4 rounded-full transition-all duration-500`}
              style={{
                width: `${Math.min(100, Math.max(5, healthScore))}%`,
              }}
            />
          </div>
        </div>

        <div className="bg-slate-900 border border-cyan-800/60 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
            <span>🤖</span>
            <span>{t("aiInsights", lang)}</span>
          </h2>

          <div className="space-y-4 mt-6 text-base md:text-lg text-slate-200">
            <p>✅ {dashboard?.insights?.balance || "Statement liquidity verified"}</p>
            <p>📈 {dashboard?.insights?.income || "Monthly cash flow tracked"}</p>
            <p>⚠ {dashboard?.insights?.expenses || "Spending patterns monitored"}</p>
            <p>💰 {dashboard?.insights?.savings || "Emergency fund active"}</p>
          </div>
        </div>
      </div>
    </>
  );
}
