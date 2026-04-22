"use client";
import { useState } from "react";

export default function Home() {
  const [form, setForm] = useState({
    step2_score: "",
    specialty: "",
    grad_type: "",
  });
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setResult("");
    const res = await fetch("http://localhost:8000/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        step2_score: parseInt(form.step2_score),
      }),
    });
    const data = await res.json();
    setResult(data.result);
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">MatchMD</h1>
        <p className="text-gray-500 mb-8">AI-powered residency match advisor</p>

        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <div className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                Step 2 CK Score
              </label>
              <input
                type="number"
                placeholder="e.g. 240"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={form.step2_score}
                onChange={(e) =>
                  setForm({ ...form, step2_score: e.target.value })
                }
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                Desired Specialty
              </label>
              <input
                type="text"
                placeholder="e.g. Internal Medicine"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={form.specialty}
                onChange={(e) =>
                  setForm({ ...form, specialty: e.target.value })
                }
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                Graduate Type
              </label>
              <select
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={form.grad_type}
                onChange={(e) =>
                  setForm({ ...form, grad_type: e.target.value })
                }
              >
                <option value="">Select...</option>
                <option>IMG — Non-US/Canadian school</option>
                <option>IMG — US citizen (USIMG)</option>
                <option>US MD graduate</option>
                <option>US DO graduate</option>
              </select>
            </div>
            <button
              onClick={handleSubmit}
              disabled={loading || !form.step2_score || !form.specialty || !form.grad_type}
              className="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? "Finding matches..." : "Find My Best-Match Programs"}
            </button>
          </div>
        </div>

        {result && (
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
              Your Match Analysis
            </h2>
            <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
              {result}
            </p>
          </div>
        )}
      </div>
    </main>
  );
}