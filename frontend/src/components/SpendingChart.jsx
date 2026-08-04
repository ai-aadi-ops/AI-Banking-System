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

export default function SpendingChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/spending-chart`)
      .then((res) => res.json())
      .then((result) => {
        setData(result);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">
          📈 Monthly Spending Trend
        </h2>

        <span className="text-cyan-400 text-sm">
          Live Data
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
