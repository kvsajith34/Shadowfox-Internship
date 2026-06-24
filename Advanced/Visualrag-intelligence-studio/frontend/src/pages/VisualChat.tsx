import { useState, useRef, useEffect } from "react";
import { Card } from "../components/ui/Card";
import { 
  ImageIcon, Share2, Download, Search, ZoomIn, ZoomOut, 
  BrainCircuit, User, Bot, ThumbsUp, ThumbsDown, Copy, 
  Paperclip, Send, Brain, Eye, Loader, AlertCircle
} from "lucide-react";
import { sendVisualChatMessage, VisualChatResult, ChatMessage, getErrorMessage, uploadFile } from "../api/client";
import { cn } from "../utils";

interface Message {
  role: 'user' | 'assistant';
  content: string;
  result?: VisualChatResult;
  loading?: boolean;
  error?: string;
}

export default function VisualChat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Upload an image or PDF and ask me anything about it. I can analyze diagrams, charts, documents, and more.' }
  ]);
  const [input, setInput] = useState('');
  const [fileId, setFileId] = useState<string | null>(null);
  const [sessionFile, setSessionFile] = useState<string>('No file selected');
  const [uploading, setUploading] = useState(false);
  const [lastResult, setLastResult] = useState<VisualChatResult | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  async function handleFileUpload(file: File) {
    setUploading(true);
    try {
      const result = await uploadFile(file, 'visual_chat');
      setFileId(result.file_id);
      setSessionFile(file.name);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `File uploaded: **${file.name}** (${result.file_type.toUpperCase()}, ${(result.size_bytes / 1024).toFixed(1)} KB). Ready to analyze. Ask your question.`
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Upload failed: ${getErrorMessage(err)}`, error: getErrorMessage(err) }]);
    } finally {
      setUploading(false);
    }
  }

  async function handleSend() {
    const msg = input.trim();
    if (!msg) return;
    setInput('');
    const history: ChatMessage[] = messages
      .filter(m => !m.loading && !m.error)
      .map(m => ({ role: m.role, content: m.content }));

    setMessages(prev => [...prev, { role: 'user', content: msg }, { role: 'assistant', content: '', loading: true }]);

    try {
      const result = await sendVisualChatMessage({ file_id: fileId || undefined, message: msg, provider: 'mock', history });
      setLastResult(result);
      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1 ? { role: 'assistant', content: result.answer, result } : m
      ));
    } catch (err) {
      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1 ? { role: 'assistant', content: `Error: ${getErrorMessage(err)}`, error: getErrorMessage(err) } : m
      ));
    }
  }

  const QUICK_PROMPTS = ['Extract text from image', 'Summarize architecture', 'Identify bottlenecks', 'Describe key components'];

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col gap-6 animate-in fade-in duration-500">
      {/* Top Header */}
      <div className="glass-panel h-14 rounded-lg flex items-center justify-between px-6 shrink-0 border-outline-variant/20">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-on-surface">Visual Chat</h2>
          <div className="h-4 w-px bg-outline-variant/30" />
          <span className="text-xs font-medium text-outline uppercase tracking-wider bg-surface-variant px-2 py-1 rounded">
            Session: {sessionFile}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <input ref={fileInputRef} type="file" accept=".pdf,.png,.jpg,.jpeg" className="hidden"
            onChange={e => e.target.files?.[0] && handleFileUpload(e.target.files[0])} />
          <button onClick={() => fileInputRef.current?.click()} disabled={uploading}
            className="text-on-surface-variant hover:text-primary transition-colors">
            {uploading ? <Loader size={18} className="animate-spin" /> : <Paperclip size={18} />}
          </button>
          <button className="text-on-surface-variant hover:text-primary transition-colors"><Share2 size={18} /></button>
          <button className="text-on-surface-variant hover:text-primary transition-colors"><Download size={18} /></button>
        </div>
      </div>

      <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0 overflow-hidden">
        {/* Left: Source File */}
        <section className="flex-[0.8] lg:flex-1 flex flex-col glass-panel rounded-lg overflow-hidden border-outline-variant/20">
          <div className="px-4 py-3 border-b border-outline-variant/20 flex justify-between items-center bg-surface-container-high/50">
            <div className="flex items-center gap-2">
              <ImageIcon className="text-outline" size={16} />
              <h3 className="text-sm font-medium text-on-surface">Source Diagram</h3>
            </div>
            <div className="flex gap-2 text-outline">
              <button className="hover:text-primary"><ZoomIn size={16} /></button>
              <button className="hover:text-primary"><ZoomOut size={16} /></button>
            </div>
          </div>
          <div className="flex-1 p-4 bg-surface-container-lowest/50 flex items-center justify-center relative group overflow-hidden">
            {fileId ? (
              <div className="text-center">
                <CheckCircle size={48} className="text-tertiary mx-auto mb-3" />
                <p className="text-sm text-on-surface font-medium">{sessionFile}</p>
                <p className="text-xs text-on-surface-variant mt-1">File ID: {fileId.slice(0, 16)}...</p>
              </div>
            ) : (
              <div
                className="flex flex-col items-center gap-4 cursor-pointer"
                onClick={() => fileInputRef.current?.click()}>
                <div className="w-24 h-24 rounded-full bg-primary/10 border-2 border-dashed border-primary/30 flex items-center justify-center">
                  {uploading ? <Loader size={32} className="text-primary animate-spin" /> : <ImageIcon size={32} className="text-primary/60" />}
                </div>
                <p className="text-sm text-on-surface-variant text-center">Click to upload an image or PDF<br/><span className="text-xs opacity-60">or type a question without a file</span></p>
              </div>
            )}
          </div>
        </section>

        {/* Center: Chat Window */}
        <section className="flex-[1.2] lg:flex-[1.5] flex flex-col glass-panel rounded-lg overflow-hidden border-t-2 border-t-primary !border-x-outline-variant/20">
          <div className="px-4 py-3 border-b border-outline-variant/20 bg-surface-container-high/50 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <BrainCircuit className="text-primary" size={16} />
              <h3 className="text-sm font-medium text-on-surface">Analysis Session</h3>
            </div>
            <span className="text-[10px] text-outline bg-surface-variant px-2 py-0.5 rounded-full uppercase tracking-wider">
              {fileId ? 'File Loaded' : 'Mock Mode'}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={cn("flex gap-4", msg.role === 'user' ? "max-w-[85%] ml-auto justify-end" : "max-w-[90%]")}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center shrink-0 border border-primary/30 shadow-[0_0_10px_rgba(173,198,255,0.2)]">
                    {msg.loading ? <Loader size={14} className="text-primary animate-spin" /> : <Bot size={14} className="text-primary" />}
                  </div>
                )}
                <div className={cn(
                  "px-4 py-3 rounded-lg shadow-sm relative overflow-hidden",
                  msg.role === 'user' ? "bg-surface-variant/80 border border-outline-variant/20 rounded-tr-sm" :
                  "bg-surface-container-high/40 border border-outline-variant/10 rounded-tl-sm",
                  msg.error && "border-error/30 bg-error/5"
                )}>
                  {msg.loading ? (
                    <div className="flex items-center gap-2 text-xs text-outline">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  ) : msg.error ? (
                    <p className="text-sm text-error flex items-center gap-2"><AlertCircle size={14} /> {msg.content}</p>
                  ) : (
                    <p className="text-sm text-on-surface whitespace-pre-wrap">{msg.content}</p>
                  )}
                  {msg.result && (
                    <div className="mt-2 pt-2 border-t border-outline-variant/10 flex gap-3 text-xs font-mono text-outline">
                      <span>Conf: {(msg.result.confidence_score * 100).toFixed(0)}%</span>
                      <span className={msg.result.hallucination_risk === 'low' ? 'text-tertiary' : 'text-error'}>
                        Risk: {msg.result.hallucination_risk}
                      </span>
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center shrink-0 border border-outline-variant/30">
                    <User size={14} className="text-on-secondary-container" />
                  </div>
                )}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="p-4 border-t border-outline-variant/20 bg-surface-container-lowest/50">
            <div className="flex flex-wrap gap-2 mb-3">
              {QUICK_PROMPTS.map(p => (
                <button key={p} onClick={() => setInput(p)}
                  className="px-3 py-1.5 rounded-full border border-outline-variant/30 bg-surface/50 hover:border-primary/50 hover:text-primary text-xs font-medium text-outline transition-colors">
                  {p}
                </button>
              ))}
            </div>
            <div className="relative bg-surface-container rounded-md border border-outline-variant/30 focus-within:border-primary focus-within:shadow-[0_0_10px_rgba(59,130,246,0.2)] transition-all flex items-end p-2">
              <textarea 
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }}}
                className="w-full bg-transparent border-none text-sm text-on-surface focus:ring-0 resize-none py-2 px-2 min-h-[40px] max-h-32" 
                placeholder="Ask about this image..." 
                rows={1}
              />
              <button onClick={handleSend} disabled={!input.trim()}
                className="p-2 text-primary hover:bg-primary/20 bg-primary/10 rounded ml-2 transition-colors shrink-0 disabled:opacity-40">
                <Send size={18} />
              </button>
            </div>
          </div>
        </section>

        {/* Right: Scores */}
        <section className="flex-1 lg:flex-[0.8] flex flex-col gap-6 min-h-0 overflow-hidden">
          <Card className="flex-shrink-0">
            <div className="px-4 py-3 border-b border-outline-variant/20 flex items-center gap-2 bg-surface-container-high/50">
              <Brain className="text-tertiary" size={16} />
              <h3 className="text-sm font-medium text-on-surface">Evaluation Score</h3>
            </div>
            <div className="p-6 flex justify-around items-center">
              <ScoreRing value={lastResult ? Math.round((lastResult.evaluation as any)?.relevance_score * 100 || 98) : 98} label="Relevance" color="#4cd7f6" />
              <ScoreRing value={lastResult ? Math.round((1 - (lastResult.hallucination_risk === 'high' ? 0.5 : 0)) * 100) : 100} label="Safety" color="#adc6ff" />
            </div>
          </Card>

          <Card className="flex-1 flex flex-col min-h-0">
            <div className="px-4 py-3 border-b border-outline-variant/20 flex items-center gap-2 bg-surface-container-high/50">
              <Eye className="text-outline" size={16} />
              <h3 className="text-sm font-medium text-on-surface">Evidence</h3>
            </div>
            <div className="p-4 overflow-y-auto space-y-3">
              {lastResult?.evidence?.length ? (
                lastResult.evidence.map((e, i) => (
                  <div key={i} className="rounded border border-outline-variant/20 bg-surface-container-lowest p-3">
                    <p className="text-xs text-on-surface-variant">{e}</p>
                  </div>
                ))
              ) : (
                <p className="text-xs font-mono text-outline">Evidence will appear after analysis...</p>
              )}
              {lastResult?.suggested_followups?.length ? (
                <div className="mt-3">
                  <p className="text-xs font-mono text-outline mb-2">Suggested follow-ups:</p>
                  {lastResult.suggested_followups.map((s, i) => (
                    <button key={i} onClick={() => setInput(s)}
                      className="block text-xs text-primary hover:text-primary-fixed transition-colors mb-1 text-left">
                      → {s}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}

function CheckCircle({ size, className }: { size: number; className?: string }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className}><polyline points="20 6 9 17 4 12"/></svg>;
}

function ScoreRing({ value, label, color }: { value: number, label: string, color: string }) {
  const radius = 16;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-20 h-20">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
          <circle cx="18" cy="18" r={radius} fill="none" stroke={color} strokeWidth="2.5"
            strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
            className="transition-all duration-1000 ease-out" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center flex-col">
          <span className="text-xl font-bold text-on-surface">{value}<span className="text-[10px] text-outline font-normal">%</span></span>
        </div>
      </div>
      <span className="text-[10px] font-medium text-outline mt-2 uppercase tracking-wider">{label}</span>
    </div>
  );
}
