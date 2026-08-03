import { useEffect, useState } from "react";
import { PieChart } from "lucide-react";

export default function AISpendingInsights() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://34.100.134.172:8000/ai/analyze/1")
      .then((res) => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data) return null;

  return (
    <div className="mt-10 rounded-2xl bg-slate-900 border border-slate-800 p-8">
      <div className="flex items-center gap-3">
        <PieChart className="text-cyan-400" size={30} />
        <h2 className="text-3xl font-bold">
          AI Spending Insights
        </h2>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mt-8">

        <div>
          <p className="text-slate-400">Total Spent</p>
          <h2 className="text-4xl font-bold mt-2">
            ${data.total_spent}
          </h2>

          <div className="mt-6">
            <p className="text-slate-400">
              Highest Spending Category
            </p>

            <h3 className="text-2xl font-semibold text-cyan-400">
              {data.highest_spending_category}
            </h3>

            <p className="text-slate-300">
              ${data.highest_category_amount}
            </p>
          </div>

          <div className="mt-6">
            <p className="text-slate-400">
              Favorite Merchant
            </p>

            <h3 className="text-2xl font-semibold text-green-400">
              {data.favorite_merchant}
            </h3>

            <p className="text-slate-300">
              ${data.merchant_spending}
            </p>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-bold mb-4">
            Category Breakdown
          </h3>

          {Object.entries(data.category_breakdown).map(([cat, amt]) => (
            <div
              key={cat}
              className="flex justify-between border-b border-slate-700 py-3"
            >
              <span>{cat}</span>
              <span className="font-semibold">
                ${amt}
              </span>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
