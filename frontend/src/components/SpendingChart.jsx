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
}) {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/spending-chart?customer_id=${customerId}`)
      .then((res) => res.json())
      .then((result) => {
        setData(Array.isArray(result) ? result : []);
      })
      .catch(console.error);
  }, [customerId]);

  return (
    <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">
          📈 {t("monthlySpendingTrend", lang)}
        </h2>

        <span className="text-cyan-400 text-sm">
          {t("liveData", lang)}
        </span>
      </div>


      <div className="h-80">

        <ResponsiveContainer width="100%" height="100%">

          <AreaChart data={data}>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
            />

            <XAxis
              dataKey="month"
              stroke="#94a3b8"
            />

            <Tooltip />

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
