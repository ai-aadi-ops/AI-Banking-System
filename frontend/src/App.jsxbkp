import { Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Advisor from "./pages/Advisor";
import Offers from "./pages/Offers";
import NotFound from "./pages/NotFound";

function App() {
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
