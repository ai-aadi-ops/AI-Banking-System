import { useEffect, useState } from "react";
import { API_BASE } from "../config";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { t } from "../utils/i18n";

export default function SpendingChart({
  customerId = 1,
  currencySymbol = "$",
  lang = "en",
  cleared = false,
}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    fetch(`${API_BASE}/spending-chart?customer_id=${customerId}${cleared ? "&cleared=true" : ""}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((result) => {
        if (!isMounted) return;
        setData(Array.isArray(result) ? result : []);
      })
      .catch((err) => {
        console.warn("Spending chart fetch error:", err);
        if (isMounted) setData([]);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [customerId, cleared]);

  const chartData = data && data.length > 0 ? data : [
    { month: "Jan", expense: 0 },
    { month: "Feb", expense: 0 },
    { month: "Mar", expense: 0 },
  ];

  return (
    <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">
          📈 {t("monthlySpendingTrend", lang)}
        </h2>

        <span className="text-cyan-400 text-sm font-medium">
          {t("liveData", lang)}
        </span>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "12px",
                color: "#fff",
              }}
              formatter={(val) => [`${currencySymbol}${Number(val).toLocaleString()}`, "Expense"]}
            />
            <Area
              type="monotone"
              dataKey="expense"
              stroke="#06b6d4"
              fill="#0891b2"
              fillOpacity={0.4}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
