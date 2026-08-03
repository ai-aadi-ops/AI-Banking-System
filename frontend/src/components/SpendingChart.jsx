import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  Tooltip,
} from "recharts";

const data = [
  { month: "Jan", expense: 1200 },
  { month: "Feb", expense: 1850 },
  { month: "Mar", expense: 1600 },
  { month: "Apr", expense: 2400 },
  { month: "May", expense: 2100 },
  { month: "Jun", expense: 2750 },
];

export default function SpendingChart() {
  return (
    <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-6 text-2xl font-bold">
        Monthly Spending
      </h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <XAxis dataKey="month" stroke="#94a3b8" />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="expense"
              stroke="#06b6d4"
              fill="#0891b2"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
