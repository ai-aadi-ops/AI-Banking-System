import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
	  e.preventDefault();

	  localStorage.setItem("isLoggedIn", "true");

	  navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6">

      <div className="w-full max-w-md rounded-3xl bg-slate-900 border border-slate-800 p-8 shadow-2xl">

        <h1 className="text-4xl font-bold text-cyan-400 text-center">
          AI Finance Platform
        </h1>

        <p className="text-center text-slate-400 mt-3">
          Sign in to continue
        </p>

        <form onSubmit={handleLogin} className="mt-8 space-y-5">

          <input
            type="email"
            placeholder="Email Address"
            className="w-full rounded-xl bg-slate-800 p-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
          />

          <input
            type="password"
            placeholder="Password"
            className="w-full rounded-xl bg-slate-800 p-4 text-white outline-none border border-slate-700 focus:border-cyan-500"
          />

          <button
            type="submit"
            className="w-full rounded-xl bg-cyan-500 py-4 font-bold hover:bg-cyan-600"
          >
            Login
          </button>

        </form>

        <p className="mt-6 text-center text-slate-400">
          Demo User:
          <span className="text-cyan-400"> Robert Wilson</span>
        </p>

        <div className="mt-6 text-center">
          <Link
            to="/"
            className="text-cyan-400 hover:underline"
          >
            ← Back to Home
          </Link>
        </div>

      </div>

    </div>
  );
}
