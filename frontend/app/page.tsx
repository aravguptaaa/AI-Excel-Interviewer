'use client';

import { useState, FormEvent, useRef, useEffect } from 'react';

// --- Type Definitions ---
interface Evaluation { score: number; evaluation: string; }
interface Message { text: string; isUser: boolean; evaluation?: Evaluation; isQuestion?: boolean; }
interface ReportData {
  overall_recommendation: string;
  proficiency_score: number;
  key_strengths: string;
  areas_for_improvement: string;
  summary: string;
}

const API_BASE_URL = "http://127.0.0.1:8000";

const ReportCard = ({ report, onClose }: { report: ReportData, onClose: () => void }) => (
  <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
    <div className="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl relative text-white">
      <button onClick={onClose} className="absolute top-2 right-4 text-gray-400 hover:text-white text-2xl">&times;</button>
      <h2 className="text-2xl font-bold mb-4 border-b border-gray-600 pb-2">Candidate Performance Report</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-400">Overall Recommendation</p>
          {/* --- FIX START: Safely handle potentially missing data --- */}
          <p className={`text-xl font-bold ${(report.overall_recommendation || '').includes('Hire') ? 'text-green-400' : 'text-yellow-400'}`}>{report.overall_recommendation || 'N/A'}</p>
          {/* --- FIX END --- */}
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-400">Proficiency Score</p>
          <p className="text-xl font-bold text-blue-400">{report.proficiency_score} / 100</p>
        </div>
      </div>
      <div className="mt-6">
        <h3 className="font-semibold mb-2 text-lg">Summary</h3>
        <p className="text-gray-300">{report.summary}</p>
      </div>
      <div className="mt-6">
        <h3 className="font-semibold mb-2 text-lg">Key Strengths</h3>
        <pre className="text-green-300 bg-gray-900 p-3 rounded whitespace-pre-wrap font-sans">{report.key_strengths}</pre>
      </div>
      <div className="mt-6">
        <h3 className="font-semibold mb-2 text-lg">Areas for Improvement</h3>
        <pre className="text-yellow-300 bg-gray-900 p-3 rounded whitespace-pre-wrap font-sans">{report.areas_for_improvement}</pre>
      </div>
    </div>
  </div>
);


export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isComplete, setIsComplete] = useState(false);
  const [report, setReport] = useState<ReportData | null>(null);
  const [isReportLoading, setIsReportLoading] = useState(false);
  
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => { startNewInterview(); }, []);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const startNewInterview = async () => {
    setIsLoading(true);
    const response = await fetch(`${API_BASE_URL}/interview/start`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ candidate_name: "Test Candidate" }), });
    const data = await response.json();
    setSessionId(data.session_id);
    setMessages([ { text: "Hello! I am your AI interviewer. Let's begin.", isUser: false }, { text: data.first_question, isUser: false, isQuestion: true } ]);
    setIsLoading(false);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || isComplete) return;

    const userMessage: Message = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const response = await fetch(`${API_BASE_URL}/interview/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId, answer: input }), });
    const data = await response.json();
    
    setMessages(prev => [...prev, { text: '', isUser: false, evaluation: data.evaluation }]);

    if (data.is_complete) {
      setIsComplete(true);
      setMessages(prev => [...prev, { text: "Thank you. Your interview is now complete.", isUser: false }]);
    } else {
      setMessages(prev => [...prev, { text: data.next_question, isUser: false, isQuestion: true }]);
    }
    setIsLoading(false);
  };

  const handleGenerateReport = async () => {
    if (!sessionId) return;
    setIsReportLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/interview/report/${sessionId}`);
      if (!response.ok) { throw new Error('Network response was not ok'); }
      const data = await response.json();
      setReport(data);
    } catch (error) {
      console.error("Failed to fetch report:", error);
      alert("Failed to generate report. The AI model may be overloaded or returned an invalid format.");
    } finally {
      setIsReportLoading(false);
    }
  };
  
  return (
    <>
      {report && <ReportCard report={report} onClose={() => setReport(null)} />}
      <div className="flex flex-col h-screen bg-gray-900 text-white">
        <header className="bg-gray-800 p-4 shadow-md"><h1 className="text-xl font-bold text-center">AI Excel Interviewer</h1></header>
        <main className="flex-1 overflow-y-auto p-4">
          <div className="max-w-3xl mx-auto">
            {messages.map((msg, index) => (
              <div key={index} className={`my-2 ${msg.isUser ? 'text-right' : 'text-left'}`}>
                <div className={`inline-block p-3 rounded-lg ${msg.isUser ? 'bg-blue-600' : 'bg-gray-700'}`}>
                  {msg.isQuestion && <p className="font-bold mb-2">Question:</p>}
                  {msg.text && <p className={msg.isQuestion ? 'italic' : ''}>{msg.text}</p>}
                  {msg.evaluation && ( <div> <p className="font-bold border-b border-gray-500 pb-2 mb-2">Evaluation:</p> <p className="mb-2"><span className="font-semibold">Score:</span> {msg.evaluation.score}/5</p> <p><span className="font-semibold">Rationale:</span> {msg.evaluation.evaluation}</p> </div> )}
                </div>
              </div>
            ))}
            {isComplete && ( <div className="text-center my-4"> <button onClick={handleGenerateReport} disabled={isReportLoading} className="bg-green-600 text-white font-bold py-2 px-4 rounded hover:bg-green-700 disabled:bg-gray-500"> {isReportLoading ? 'Generating...' : 'Generate Final Report'} </button> </div> )}
            {isLoading && messages.length > 2 && (<div className="text-left"><div className="inline-block p-3 rounded-lg bg-gray-700 animate-pulse">Evaluating...</div></div>)}
            <div ref={messagesEndRef} />
          </div>
        </main>
        <footer className="bg-gray-800 p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} className="flex-1 p-2 rounded-l-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder={isComplete ? "Interview complete." : isLoading ? "Evaluating..." : "Type your answer..."} disabled={isLoading || isComplete} />
            <button type="submit" disabled={isLoading || isComplete} className="bg-blue-600 text-white p-2 rounded-r-lg hover:bg-blue-700 disabled:bg-gray-500">Send</button>
          </form>
        </footer>
      </div>
    </>
  );
}
