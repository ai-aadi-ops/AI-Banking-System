import { useNavigate } from "react-router-dom";
import { t } from "../utils/i18n";
import { getUserSlug } from "../utils/userSlug";

export default function DashboardHeader({ user, lang = "en" }) {
  const navigate = useNavigate();

  const userName = user?.full_name || "Customer";
  const userSlug = getUserSlug(user);

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 className="text-3xl md:text-4xl font-bold">
          {t("welcomeBack", lang)}{" "}
          <span className="text-cyan-400">{userName} 👋</span>
        </h1>

        <p className="mt-2 text-slate-400 text-sm md:text-base">
          {t("financialOverview", lang)}
        </p>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(`/${userSlug}-dashboard/ai-advisor`)}
          className="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-3 font-semibold hover:from-cyan-600 hover:to-blue-700 transition shadow-lg shadow-cyan-500/25 flex items-center gap-2 cursor-pointer text-sm text-white"
        >
          <span>🤖</span>
          <span>{t("aiAdvisor", lang)}</span>
        </button>

        <div className="h-11 w-11 rounded-full border-2 border-cyan-400 bg-slate-800 flex items-center justify-center font-bold text-cyan-400">
          {userName.charAt(0).toUpperCase()}
        </div>
      </div>
    </div>
  );
}
