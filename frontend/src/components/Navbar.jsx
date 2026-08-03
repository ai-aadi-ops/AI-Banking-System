import { Link } from "react-router-dom";
import { Landmark, LogIn } from "lucide-react";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-10 py-6 border-b border-slate-800">
      <div className="flex items-center gap-3">
        <Landmark className="text-cyan-400" size={32} />
        <h1 className="text-2xl font-bold text-cyan-400">
          AI Finance Platform
        </h1>
      </div>

      <div className="flex gap-4">
        <Link
          to="/login"
          className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-2 font-semibold text-white transition hover:bg-cyan-600"
        >
          <LogIn size={18} />
          Login
        </Link>
      </div>
    </nav>
  );
}
