import { useEffect, useState } from "react";
import {
  ShoppingBag,
  Coffee,
  CreditCard,
  ArrowDownLeft,
  ArrowUpRight,
  Fuel,
  Tv,
  Home,
} from "lucide-react";
import { API_BASE } from "../config";

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

export default function RecentTransactions() {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/transactions`)
      .then((res) => res.json())
      .then((data) => {
        const latest = data
          .sort(
            (a, b) =>
              new Date(b.transaction_date) -
              new Date(a.transaction_date)
          )
          .slice(0, 10);

        setTransactions(latest);
      });
  }, []);

  return (
    <div className="mt-10 rounded-2xl bg-slate-900 border border-slate-800 p-6">
      <h2 className="text-2xl font-bold mb-6">
        Recent Transactions
      </h2>

      <div className="space-y-5">
        {transactions.map((item) => {
          const Icon = getIcon(item.category);

          return (
            <div
              key={item.transaction_id}
              className="flex items-center justify-between border-b border-slate-800 pb-4"
            >
              <div className="flex items-center gap-4">
                <div className="bg-slate-800 p-3 rounded-xl">
                  <Icon size={22} />
                </div>

                <div>
                  <p className="font-semibold">
                    {item.merchant_name}
                  </p>

                  <p className="text-slate-400 text-sm">
                    {item.transaction_date}
                  </p>
                </div>
              </div>

              <span
                className={`font-bold ${
                  item.transaction_type === "Credit"
                    ? "text-green-400"
                    : "text-red-400"
                }`}
              >
                {item.transaction_type === "Credit" ? "+" : "-"}$
                {Number(item.amount).toFixed(2)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
