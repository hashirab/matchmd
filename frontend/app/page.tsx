"use client";
import { useState } from "react";

interface ChatMessage {
  role: "user" | "ai";
  content: string;
  intent?: string;
  programs?: string[];
}

export default function Home() {
  const [form, setForm] = useState({
    step2_score: "",
    specialty: "",
    grad_type: "",
  });
  const [result, setResult] = useState("");
  const [programs, setPrograms] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { role: "ai", content: "Hi! I can help you find residency programs, answer visa questions, or give application advice. What would you like to know?" }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setResult("");
    setPrograms([]);
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
    setPrograms(data.programs_used || []);
    setLoading(false);
  };

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatInput("");
    setChatMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setChatLoading(true);
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userMsg,
        specialty: form.specialty || ""
      }),
    });
    const data = await res.json();
    setChatMessages(prev => [...prev, {
      role: "ai",
      content: data.result,
      intent: data.intent,
      programs: data.programs_used
    }]);
    setChatLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">MatchMD</h1>
        <p className="text-gray-500 mb-2">AI-powered residency match advisor</p>
        <div className="inline-flex items-center gap-2 bg-purple-50 border border-purple-200 rounded-full px-3 py-1 text-xs text-purple-700 font-medium mb-8">
          <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
          RAG-powered · Intent classifier · 1,062 real NRMP 2026 programs
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <h2 className="text-sm font-medium text-gray-700 mb-4">Match Finder</h2>
          <div className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Step 2 CK Score</label>
              <input
                type="number"
                placeholder="e.g. 240"
                className="w-full border rounded-lg px-3 py-2 text-sm text-gray-900 bg-white"
                value={form.step2_score}
                onChange={(e) => setForm({ ...form, step2_score: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Desired Specialty</label>
              <input
                type="text"
                placeholder="e.g. Internal Medicine"
                className="w-full border rounded-lg px-3 py-2 text-sm text-gray-900 bg-white"
                value={form.specialty}
                onChange={(e) => setForm({ ...form, specialty: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Graduate Type</label>
              <select
                className="w-full border rounded-lg px-3 py-2 text-sm text-gray-900 bg-white"
                value={form.grad_type}
                onChange={(e) => setForm({ ...form, grad_type: e.target.value })}
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
              {loading ? "Analysing your profile..." : "Find My Best-Match Programs"}
            </button>
          </div>
        </div>

        {programs.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border p-4 mb-4">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
              Programs retrieved from NRMP 2026 database
            </p>
            <div className="flex flex-wrap gap-2">
              {programs.map((p, i) => (
                <span key={`prog-${i}`} className="bg-purple-50 border border-purple-200 text-purple-700 text-xs px-3 py-1 rounded-full">
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}

        {result && (
          <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
              Your Match Analysis
            </h2>
            <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">{result}</p>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-sm font-medium text-gray-700">Ask Anything</h2>
            <p className="text-xs text-gray-400 mt-1">Visa questions · Program search · Application strategy</p>
          </div>
          <div className="p-4 flex flex-col gap-3 min-h-64 max-h-96 overflow-y-auto">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-gray-900 text-white rounded-br-sm"
                    : "bg-gray-100 text-gray-800 rounded-bl-sm"
                }`}>
                  {msg.content}
                </div>
                {msg.intent && (
                  <span className="text-xs text-gray-400 mt-1 px-1">
                    Intent: {msg.intent}
                  </span>
                )}
                {msg.programs && msg.programs.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1 max-w-xs lg:max-w-md">
                    {msg.programs.map((p, j) => (
                      <span key={`chat-prog-${i}-${j}`} className="text-xs bg-purple-50 text-purple-600 border border-purple-200 px-2 py-0.5 rounded-full">
                        {p}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {chatLoading && (
              <div className="flex items-start">
                <div className="bg-gray-100 text-gray-400 text-sm px-4 py-2 rounded-2xl rounded-bl-sm italic">
                  Thinking...
                </div>
              </div>
            )}
          </div>
          <div className="p-4 border-t flex gap-2">
            <input
              type="text"
              placeholder="Ask about programs, visas, strategy..."
              className="flex-1 border rounded-lg px-3 py-2 text-sm text-gray-900 bg-white"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") sendChat(); }}
            />
            <button
              onClick={sendChat}
              disabled={chatLoading || !chatInput.trim()}
              className="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-700 disabled:opacity-40"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
