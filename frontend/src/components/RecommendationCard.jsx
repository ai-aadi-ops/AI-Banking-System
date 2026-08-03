import { Sparkles, CreditCard } from "lucide-react";

export default function RecommendationCard() {
  return (
    <div className="bg-gradient-to-br from-cyan-500 to-blue-700 rounded-3xl p-6 shadow-2xl">
      <div className="flex justify-between items-center">
        <Sparkles size={42} />
        <CreditCard size={42} />
      </div>

      <h2 className="text-2xl font-bold mt-6">
        AI Recommendation
      </h2>

      <p className="mt-3 text-slate-100">
        Based on your spending habits,
        switching to our Platinum Cashback Card
        can save approximately ₹18,000 annually.
      </p>

      <button className="mt-6 bg-white text-cyan-700 px-6 py-3 rounded-xl font-bold hover:scale-105 transition">
        View Details
      </button>
    </div>
  );
}
