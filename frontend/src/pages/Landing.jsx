import Navbar from "../components/Navbar";


export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <section className="mx-auto flex max-w-7xl flex-col items-center px-8 py-24 text-center">
        <p className="mb-4 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-2 text-cyan-300">
          AI Powered Personal Finance Assistant
        </p>

        <h1 className="max-w-5xl text-6xl font-extrabold leading-tight">
          Intelligent Banking
          <br />
          for the Modern World
        </h1>

        <p className="mt-8 max-w-3xl text-xl text-slate-400">
          Analyze spending, predict future expenses, discover personalized
          banking offers and chat with your own AI financial advisor.
        </p>

        <div className="mt-10 flex gap-5">
          <button className="rounded-xl bg-cyan-500 px-8 py-4 text-lg font-bold hover:bg-cyan-600">
            Get Started
          </button>

          <button className="rounded-xl border border-slate-700 px-8 py-4 text-lg hover:border-cyan-500">
            Live Demo
          </button>
        </div>

      </section>
    </div>
  );
}
