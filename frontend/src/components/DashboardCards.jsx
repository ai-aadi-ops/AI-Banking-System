import {
  Wallet,
  ArrowUpCircle,
  ArrowDownCircle,
  PiggyBank,
} from "lucide-react";

import { useEffect, useState } from "react";

export default function DashboardCards() {

  const [cards, setCards] = useState([
    {
      title: "Total Balance",
      value: "$0",
      icon: Wallet,
      color: "text-cyan-400",
    },
    {
      title: "Monthly Income",
      value: "$0",
      icon: ArrowUpCircle,
      color: "text-green-400",
    },
    {
      title: "Monthly Expenses",
      value: "$0",
      icon: ArrowDownCircle,
      color: "text-red-400",
    },
    {
      title: "Savings",
      value: "$0",
      icon: PiggyBank,
      color: "text-yellow-400",
    },
  ]);

  useEffect(() => {
    fetch("http://34.100.134.172:8000/dashboard")
      .then((res) => res.json())
      .then((data) => {
        setCards([
          {
            title: "Total Balance",
            value: `$${data.balance.toLocaleString()}`,
            icon: Wallet,
            color: "text-cyan-400",
          },
          {
            title: "Monthly Income",
            value: `$${data.income.toLocaleString()}`,
            icon: ArrowUpCircle,
            color: "text-green-400",
          },
          {
            title: "Monthly Expenses",
            value: `$${data.expenses.toLocaleString()}`,
            icon: ArrowDownCircle,
            color: "text-red-400",
          },
          {
            title: "Savings",
            value: `$${data.savings.toLocaleString()}`,
            icon: PiggyBank,
            color: "text-yellow-400",
          },
        ]);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="grid gap-6 mt-10 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, index) => {
        const Icon = card.icon;

        return (
          <div
            key={index}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-cyan-500 transition"
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="text-slate-400">{card.title}</p>

                <h2 className="text-3xl font-bold mt-2">
                  {card.value}
                </h2>
              </div>

              <Icon className={card.color} size={38} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
