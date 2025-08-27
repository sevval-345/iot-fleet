// src/App.tsx
import { Routes, Route, Link } from "react-router-dom";
import FleetPage from "./pages/FleetPage";
import SimDetailPage from "./pages/SimDetailPage";

export default function App() {
  return (
    <div className="min-h-screen max-w-7xl mx-auto p-4 space-y-6 dark:bg-gray-900 dark:text-gray-100">
      <header className="flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">IoT Fleet UI</Link>
      </header>
      <Routes>
        <Route path="/" element={<FleetPage />} />
        <Route path="/sim/:simId" element={<SimDetailPage />} />
      </Routes>
    </div>
  );
}
