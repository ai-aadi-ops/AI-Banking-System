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
}) {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/dashboard?customer_id=${customerId}`)
      .then((res) => res.json())
      .then((data) => {
        setDashboard(data);
      })
      .catch(console.error);
  }, [customerId]);

  const cards = [
    {
      title: t("totalBalance", lang),
      value: dashboard ? formatCurrency(dashboard.balance, dashboard.currency_symbol || currencySymbol, currencyCode) : formatCurrency(0, currencySymbol, currencyCode),
      icon: Wallet,
      color: "text-cyan-400",
    },
    {
      title: t("monthlyIncome", lang),
      value: dashboard ? formatCurrency(dashboard.income, dashboard.currency_symbol || currencySymbol, currencyCode) : formatCurrency(0, currencySymbol, currencyCode),
      icon: ArrowUpCircle,
      color: "text-green-400",
    },
    {
      title: t("monthlyExpenses", lang),
      value: dashboard ? formatCurrency(dashboard.expenses, dashboard.currency_symbol || currencySymbol, currencyCode) : formatCurrency(0, currencySymbol, currencyCode),
      icon: ArrowDownCircle,
      color: "text-red-400",
    },
    {
      title: t("savings", lang),
      value: dashboard ? formatCurrency(dashboard.savings, dashboard.currency_symbol || currencySymbol, currencyCode) : formatCurrency(0, currencySymbol, currencyCode),
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
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-cyan-500 transition"
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-slate-400 text-sm">{card.title}</p>

                  <h2 className="text-2xl md:text-3xl font-bold mt-2 text-white">
                    {card.value}
                  </h2>
                </div>

                <Icon className={card.color} size={36} />
              </div>
            </div>
          );
        })}
      </div>

      {dashboard && (
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <div className="bg-slate-900 border border-cyan-800/60 rounded-2xl p-6">
            <h2 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
              <span>📊</span>
              <span>{t("financialHealth", lang)}</span>
            </h2>

            <div className="text-6xl font-extrabold text-green-400 mt-6">
              {dashboard.health_score}
              <span className="text-xl text-slate-500 font-normal">/100</span>
            </div>

            <p className="text-xl mt-2 font-medium text-slate-200">
              {dashboard.health_status}
            </p>

            <div className="w-full h-4 bg-slate-800 rounded-full mt-6 overflow-hidden">
              <div
                className="bg-gradient-to-r from-green-500 to-cyan-400 h-4 rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(100, Math.max(5, dashboard.health_score))}%`,
                }}
              />
            </div>
          </div>

          <div className="bg-slate-900 border border-cyan-800/60 rounded-2xl p-6">
            <h2 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
              <span>🤖</span>
              <span>{t("aiInsights", lang)}</span>
            </h2>

            <div className="space-y-4 mt-6 text-base md:text-lg">
              <p>✅ {dashboard.insights.balance}</p>
              <p>📈 {dashboard.insights.income}</p>
              <p>⚠ {dashboard.insights.expenses}</p>
              <p>💰 {dashboard.insights.savings}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

