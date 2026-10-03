import { useEffect, useState } from "react";
import {
  ShoppingBag,
  Coffee,
  ArrowDownLeft,
  Fuel,
  Tv,
  Home,
} from "lucide-react";
import { API_BASE } from "../config";
import { formatCurrency, t } from "../utils/i18n";

const getIcon = (category) => {
  switch (category) {
    case "Food":
      return Coffee;
    case "Fuel":
      return Fuel;
    case "Entertainment":
      return Tv;
    case "Rent":
      return Home;
    case "Salary":
      return ArrowDownLeft;
    default:
      return ShoppingBag;
  }
};

export default function RecentTransactions({
  customerId = 1,
  currencySymbol = "$",
  currencyCode = "USD",
  lang = "en",
  cleared = false,
}) {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    let isMounted = true;
    fetch(`${API_BASE}/transactions?customer_id=${customerId}${cleared ? "&cleared=true" : ""}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!isMounted) return;
        if (Array.isArray(data)) {
          const latest = [...data]
            .sort(
              (a, b) =>
                new Date(b.transaction_date) -
                new Date(a.transaction_date)
            )
            .slice(0, 10);

          setTransactions(latest);
        } else {
          setTransactions([]);
        }
      })
      .catch((err) => {
        console.warn("RecentTransactions fetch error:", err);
        if (isMounted) setTransactions([]);
      });

    return () => {
      isMounted = false;
    };
  }, [customerId, cleared]);

  return (
    <div className="mt-10 rounded-2xl bg-slate-900 border border-slate-800 p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">
          {t("recentTransactions", lang)}
        </h2>
        <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
          {transactions.length} items
        </span>
      </div>

      {transactions.length === 0 ? (
        <div className="text-center py-8 text-slate-400 text-sm">
          No transactions found for this account. Upload a statement to get started.
        </div>
      ) : (
        <div className="space-y-4">
          {transactions.map((item, idx) => {
            const Icon = getIcon(item.category);
            const isCredit = item.transaction_type === "Credit";

            return (
              <div
                key={item.transaction_id || `tx-${idx}`}
                className="flex items-center justify-between border-b border-slate-800 pb-4"
              >
                <div className="flex items-center gap-4">
                  <div className="bg-slate-800 p-3 rounded-xl">
                    <Icon size={20} className="text-cyan-400" />
                  </div>

                  <div>
                    <p className="font-semibold text-white text-sm md:text-base">
                      {item.merchant_name}
                    </p>

                    <p className="text-slate-400 text-xs">
                      {item.transaction_date} • {item.category}
                    </p>
                  </div>
                </div>

                <span
                  className={`font-bold text-sm md:text-base ${
                    isCredit ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {isCredit ? "+" : "-"}
                  {formatCurrency(item.amount, currencySymbol, currencyCode)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
