import { Wallet, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function BalanceCard() {

  const [dashboard, setDashboard] = useState({
    balance: 0,
    income: 0,
    expenses: 0,
    savings: 0,
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/dashboard")
      .then((res) => res.json())
      .then((data) => setDashboard(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      transition={{ duration: 0.3 }}
      className="relative overflow-hidden rounded-3xl border border-cyan-500/20 bg-white/10 p-8 backdrop-blur-xl shadow-2xl"
    >
      <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-cyan-500/20 blur-3xl" />

      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-lg">
              Available Balance
            </p>

            <h1 className="mt-3 text-5xl font-extrabold">
              ${dashboard.balance.toLocaleString()}
            </h1>

            <div className="mt-5 flex items-center gap-2 text-green-400">
              <TrendingUp size={18} />
              <span>Live from PostgreSQL</span>
            </div>
          </div>

          <div className="rounded-2xl bg-cyan-500/20 p-5">
            <Wallet
              size={52}
              className="text-cyan-300"
            />
          </div>
        </div>

        <div className="mt-10 flex justify-between">

          <div>
            <p className="text-slate-500">
              Income
            </p>

            <h3 className="text-2xl font-bold text-green-400">
              ${dashboard.income.toLocaleString()}
            </h3>
          </div>

          <div>
            <p className="text-slate-500">
              Expenses
            </p>

            <h3 className="text-2xl font-bold text-red-400">
              ${dashboard.expenses.toLocaleString()}
            </h3>
          </div>

        </div>
      </div>
    </motion.div>
  );
}
