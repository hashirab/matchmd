"use client";
import { useState } from "react";

interface ChatMessage {
  role: "user" | "ai";
  content: string;
  intent?: string;
  programs?: string[];
}

export default function Home() {
  const [form, setForm] = useState({ step2_score: "", specialty: "", grad_type: "" });
  const [result, setResult] = useState("");
  const [programs, setPrograms] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [matchProb, setMatchProb] = useState<{percentage: string, tier: string} | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { role: "ai", content: "Hi! I can help you find residency programs, answer visa questions, or give application advice. What would you like to know?" }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setResult("");
    setPrograms([]);
    setMatchProb(null);
    const res = await fetch("https://matchmd-production.up.railway.app/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, step2_score: parseInt(form.step2_score) }),
    });
    const data = await res.json();
    setResult(data.result);
    setPrograms(data.programs_used || []);
    if (data.match_percentage) setMatchProb({ percentage: data.match_percentage, tier: data.tier });
    setLoading(false);
  };

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatInput("");
    setChatMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setChatLoading(true);
    const res = await fetch("https://matchmd-production.up.railway.app/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg, specialty: form.specialty || "" }),
    });
    const data = await res.json();
    setChatMessages(prev => [...prev, {
      role: "ai", content: data.result, intent: data.intent, programs: data.programs_used
    }]);
    setChatLoading(false);
  };

  const tierColor = (tier: string) => {
    if (tier === "strong") return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (tier === "moderate") return "text-yellow-400 border-yellow-500/30 bg-yellow-500/10";
    return "text-red-400 border-red-500/30 bg-red-500/10";
  };

  return (
    <main className="min-h-screen" style={{background: '#0a0a0f'}}>

      {/* Hero */}
      <div className="hero-glow">
        <div className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium mb-6"
            style={{background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)', color: '#a78bfa'}}>
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
            RAG-powered · 1,062 real NRMP 2026 programs · XGBoost ML model
          </div>
          <h1 className="text-5xl font-bold mb-4 tracking-tight">
            <span className="gradient-text">MatchMD</span>
          </h1>
          <p className="text-xl mb-3" style={{color: 'rgba(255,255,255,0.7)'}}>
            AI-powered residency match advisor for USMLE graduates
          </p>
          <p className="text-sm" style={{color: 'rgba(255,255,255,0.35)'}}>
            Real program data · Intent-classified chat · ML match probability
          </p>

          {/* Stats */}
          <div className="flex justify-center gap-8 mt-10">
            {[
              {num: "1,062", label: "NRMP Programs"},
              {num: "0.96", label: "Model AUC"},
              {num: "10/10", label: "Eval Score"},
              {num: "6", label: "Intent Types"},
            ].map((s, i) => (
              <div key={i} className="text-center">
                <div className="text-2xl font-bold gradient-text">{s.num}</div>
                <div className="text-xs mt-1" style={{color: 'rgba(255,255,255,0.4)'}}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-3xl mx-auto px-6 pb-20">

        {/* Match Finder */}
        <div className="card-dark rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{background: 'rgba(124,58,237,0.2)'}}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <div>
              <h2 className="font-semibold text-white text-sm">Match Finder</h2>
              <p className="text-xs" style={{color: 'rgba(255,255,255,0.4)'}}>Enter your profile to find best-match programs</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs font-medium mb-1.5 block" style={{color: 'rgba(255,255,255,0.5)'}}>Step 2 CK Score</label>
              <input
                type="number"
                placeholder="e.g. 240"
                className="input-dark w-full rounded-xl px-4 py-2.5 text-sm"
                value={form.step2_score}
                onChange={(e) => setForm({ ...form, step2_score: e.target.value })}
              />
            </div>
            <div>
              <label className="text-xs font-medium mb-1.5 block" style={{color: 'rgba(255,255,255,0.5)'}}>Desired Specialty</label>
              <input
                type="text"
                placeholder="e.g. Internal Medicine"
                className="input-dark w-full rounded-xl px-4 py-2.5 text-sm"
                value={form.specialty}
                onChange={(e) => setForm({ ...form, specialty: e.target.value })}
              />
            </div>
          </div>

          <div className="mb-5">
            <label className="text-xs font-medium mb-1.5 block" style={{color: 'rgba(255,255,255,0.5)'}}>Graduate Type</label>
            <select
              className="input-dark w-full rounded-xl px-4 py-2.5 text-sm"
              value={form.grad_type}
              onChange={(e) => setForm({ ...form, grad_type: e.target.value })}
            >
              <option style={{background:'#1a1a2e'}}>IMG — Non-US/Canadian school (international citizen, foreign medical school)</option>
              <option style={{background:'#1a1a2e'}}>IMG — US citizen (USIMG) (US citizen, foreign medical school)</option>
              <option style={{background:'#1a1a2e'}}>US MD graduate (US/Canadian allopathic medical school)</option>
              <option style={{background:'#1a1a2e'}}>US DO graduate (US osteopathic medical school)</option>
            </select>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !form.step2_score || !form.specialty || !form.grad_type}
            className="btn-primary w-full rounded-xl py-3 text-sm font-semibold text-white cursor-pointer"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="white" strokeWidth="4"/>
                  <path className="opacity-75" fill="white" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Analysing your profile...
              </span>
            ) : "Find My Best-Match Programs →"}
          </button>
        </div>

        {/* Programs retrieved */}
        {programs.length > 0 && (
          <div className="card-dark rounded-2xl p-4 mb-4">
            <p className="text-xs font-medium mb-3" style={{color: 'rgba(255,255,255,0.4)'}}>
              PROGRAMS RETRIEVED FROM NRMP 2026 DATABASE
            </p>
            <div className="flex flex-wrap gap-2">
              {programs.map((p, i) => (
                <span key={`prog-${i}`} className="text-xs px-3 py-1 rounded-full font-medium"
                  style={{background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)', color: '#a78bfa'}}>
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Match result */}
        {result && (
          <div className="card-dark rounded-2xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs font-medium" style={{color: 'rgba(255,255,255,0.4)'}}>YOUR MATCH ANALYSIS</p>
              {matchProb && (
                <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${tierColor(matchProb.tier)}`}>
                  ML: {matchProb.percentage} match probability
                </span>
              )}
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{color: 'rgba(255,255,255,0.8)'}}>
              {result}
            </p>
          </div>
        )}

        {/* Chatbot */}
        <div className="card-dark rounded-2xl overflow-hidden">
          <div className="px-6 py-4" style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{background: 'rgba(124,58,237,0.2)'}}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-white text-sm">Ask Anything</h2>
                <p className="text-xs" style={{color: 'rgba(255,255,255,0.4)'}}>Visa questions · Program search · Application strategy</p>
              </div>
            </div>
          </div>

          <div className="p-4 flex flex-col gap-3 overflow-y-auto scrollbar-hide" style={{minHeight: '280px', maxHeight: '420px'}}>
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`max-w-sm px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user" ? "chat-user text-white rounded-br-sm" : "chat-ai rounded-bl-sm"
                }`} style={msg.role === "ai" ? {color: 'rgba(255,255,255,0.8)'} : {}}>
                  {msg.content}
                </div>
                {msg.intent && (
                  <span className="text-xs mt-1 px-1" style={{color: 'rgba(255,255,255,0.25)'}}>
                    intent: {msg.intent}
                  </span>
                )}
                {msg.programs && msg.programs.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1.5 max-w-sm">
                    {msg.programs.map((p, j) => (
                      <span key={`chat-${i}-${j}`} className="text-xs px-2 py-0.5 rounded-full"
                        style={{background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)', color: '#a78bfa'}}>
                        {p}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {chatLoading && (
              <div className="flex items-start">
                <div className="chat-ai px-4 py-2.5 rounded-2xl rounded-bl-sm text-sm italic"
                  style={{color: 'rgba(255,255,255,0.4)'}}>
                  Thinking...
                </div>
              </div>
            )}
          </div>

          <div className="px-4 py-3 flex gap-2" style={{borderTop: '1px solid rgba(255,255,255,0.06)'}}>
            <input
              type="text"
              placeholder="Ask about programs, visas, strategy..."
              className="input-dark flex-1 rounded-xl px-4 py-2.5 text-sm"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") sendChat(); }}
            />
            <button
              onClick={sendChat}
              disabled={chatLoading || !chatInput.trim()}
              className="btn-primary px-5 py-2.5 rounded-xl text-sm font-semibold text-white"
            >
              Send
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs" style={{color: 'rgba(255,255,255,0.2)'}}>
            Built with FastAPI · Next.js · pgvector · XGBoost · Llama 3.3
          </p>
        </div>
      </div>
    </main>
  );
}
