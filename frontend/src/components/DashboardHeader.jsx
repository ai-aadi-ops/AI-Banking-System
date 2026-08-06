import { useNavigate } from "react-router-dom";

export default function DashboardHeader() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-between mb-10">
      <div>
        <h1 className="text-4xl font-bold">
          Welcome back,
          <span className="text-cyan-400"> Robert Wilson 👋</span>
        </h1>

        <p className="mt-2 text-slate-400">
          Here's your financial overview for today.
        </p>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate("/advisor")}
          className="rounded-xl bg-cyan-500 px-5 py-3 font-semibold hover:bg-cyan-600 transition"
        >
          AI Advisor
        </button>

        <img
          src="https://i.pravatar.cc/100?img=12"
          alt="Profile"
          className="h-12 w-12 rounded-full border-2 border-cyan-400"
        />
      </div>
    </div>
  );
}
