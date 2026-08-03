import AISpendingInsights from "../components/AISpendingInsights";
import DashboardHeader from "../components/DashboardHeader";
import DashboardCards from "../components/DashboardCards";
import SpendingChart from "../components/SpendingChart";
import RecentTransactions from "../components/RecentTransactions";
import AIRecommendation from "../components/AIRecommendation";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <nav className="flex justify-between items-center px-10 py-6 border-b border-slate-800">
        <h1 className="text-3xl font-bold text-cyan-400">
          AI Finance Platform
        </h1>

        <button className="bg-cyan-500 hover:bg-cyan-600 px-5 py-2 rounded-xl font-semibold">
          Login
        </button>
      </nav>

      <section className="max-w-7xl mx-auto px-10 py-10">
        <DashboardHeader />
	
	<DashboardCards />
	
	<SpendingChart />
	
	<RecentTransactions />

	<AIRecommendation />

	<AISpendingInsights />
      </section>

    </div>
  )
}
