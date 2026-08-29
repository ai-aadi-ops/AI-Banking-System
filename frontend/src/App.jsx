import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";

import { API_BASE } from "./config";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Advisor from "./pages/Advisor";
import Offers from "./pages/Offers";
import NotFound from "./pages/NotFound";

function App() {
  const [demoReady, setDemoReady] = useState(false);

  useEffect(() => {
    async function resetDemo() {
      try {
        await fetch(`${API_BASE}/demo/reset/1`, {
          method: "POST",
        });
      } catch (error) {
        console.error("Demo reset failed:", error);
      } finally {
        setDemoReady(true);
      }
    }

    resetDemo();
  }, []);

  if (!demoReady) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#020617",
          color: "#ffffff",
          fontSize: "18px",
        }}
      >
        Initializing AI Finance Demo...
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/advisor" element={<Advisor />} />
      <Route path="/offers" element={<Offers />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
