import {
  ShoppingBag,
  Coffee,
  CreditCard,
  ArrowDownLeft,
  ArrowUpRight,
} from "lucide-react";

const transactions = [
  {
    title: "Amazon Purchase",
    date: "Today",
    amount: "-$249.99",
    icon: ShoppingBag,
    color: "text-red-400",
  },
  {
    title: "Starbucks",
    date: "Yesterday",
    amount: "-$8.45",
    icon: Coffee,
    color: "text-red-400",
  },
  {
    title: "Salary",
    date: "1 Aug",
    amount: "+$5,800",
    icon: ArrowDownLeft,
    color: "text-green-400",
  },
  {
    title: "Credit Card Payment",
    date: "30 Jul",
    amount: "-$920",
    icon: CreditCard,
    color: "text-red-400",
  },
  {
    title: "Investment Return",
    date: "29 Jul",
    amount: "+$425",
    icon: ArrowUpRight,
    color: "text-green-400",
  },
];

export default function RecentTransactions() {
  return (
    <div className="mt-10 rounded-2xl bg-slate-900 border border-slate-800 p-6">
      <h2 className="text-2xl font-bold mb-6">
        Recent Transactions
      </h2>

      <div className="space-y-5">
        {transactions.map((item, index) => {
          const Icon = item.icon;

          return (
            <div
              key={index}
              className="flex items-center justify-between border-b border-slate-800 pb-4"
            >
              <div className="flex items-center gap-4">
                <div className="bg-slate-800 p-3 rounded-xl">
                  <Icon size={22} />
                </div>

                <div>
                  <p className="font-semibold">
                    {item.title}
                  </p>

                  <p className="text-slate-400 text-sm">
                    {item.date}
                  </p>
                </div>
              </div>

              <span className={`font-bold ${item.color}`}>
                {item.amount}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
