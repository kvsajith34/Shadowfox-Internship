import { useState, useRef, useEffect, Fragment } from "react";
import { Card } from "../components/ui/Card";
import { 
  FileText, Link2, BookOpen, AlertTriangle, User, Bot, 
  Paperclip, Send, FileIcon, Search,
  Loader, AlertCircle
} from "lucide-react";
import { askPdfRagQuestion, RagResult, uploadFile, getErrorMessage } from "../api/client";
import { cn } from "../utils";

// ─── Safety net: if the backend still accidentally sends raw JSON as the
// answer (e.g. during a provider upgrade), extract the text field locally
// so the user never sees a raw code-fenced blob.
function extractCleanAnswer(raw: string): string {
  if (!raw) return raw;
  const trimmed = raw.trim();
  if (!trimmed.startsWith('{') && !trimmed.startsWith('```')) return raw;
  try {
    const jsonText = trimmed.replace(/^```json?\n?/, '').replace(/\n?```$/, '').trim();
    const parsed = JSON.parse(jsonText);
    if (parsed && typeof parsed.answer === 'string') return parsed.answer;
  } catch {}
  return raw;
}

interface RagMessage {
  role: 'user' | 'assistant';
  content: string;
  result?: RagResult;
  loading?: boolean;
  error?: string;
}

function DatabaseStatus({ status }: { status: string }) {
  return <span className={`w-2 h-2 rounded-full ${status === 'active' ? 'bg-tertiary animate-pulse' : 'bg-outline'}`} />;
}

export default function PdfRagChat() {
  const [messages, setMessages] = useState<RagMessage[]>([
    { role: 'assistant', content: 'Upload a PDF and ask questions. I will retrieve relevant chunks and answer with citations.' }
  ]);
  const [input, setInput] = useState('');
  const [fileId, setFileId] = useState<string | null>(null);
  const [indexName, setIndexName] = useState('No index loaded');
  const [uploading, setUploading] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Stale-response guard: increment on every new send so that if the user
  // fires two requests quickly (or switches provider mid-flight) only the
  // last response's state update is applied.
  const requestCounter = useRef<number>(0);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  async function handleFileUpload(file: File) {
    setUploading(true);
    try {
      const result = await uploadFile(file, 'rag');
      setFileId(result.file_id);
      setIndexName(file.name.replace(/\.[^/.]+$/, '') + '-index');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✓ PDF indexed: **${file.name}** · ${result.metadata?.page_count ?? '?'} pages · File ID: ${result.file_id.slice(0, 12)}... Now ask your questions.`
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Upload failed: ${getErrorMessage(err)}`, error: getErrorMessage(err) }]);
    } finally {
      setUploading(false);
    }
  }

  async function handleSend() {
    const msg = input.trim();
    if (!msg || !fileId) return;
    setInput('');

    // Capture the request sequence number BEFORE the async call.
    const thisRequest = ++requestCounter.current;

    setMessages(prev => [...prev,
      { role: 'user', content: msg },
      { role: 'assistant', content: '', loading: true }
    ]);

    try {
      const result = await askPdfRagQuestion(
        { file_id: fileId, question: msg, provider: 'mock', use_rag: useRag },
        String(thisRequest),
      );

      // Discard this response if a newer request has already been dispatched —
      // prevents stale OpenAI/Gemini answers appearing after provider switch.
      if (thisRequest !== requestCounter.current) return;

      const cleanAnswer = extractCleanAnswer(result.answer);

      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1
          ? { role: 'assistant', content: cleanAnswer, result: { ...result, answer: cleanAnswer } }
          : m
      ));
    } catch (err) {
      if (thisRequest !== requestCounter.current) return;
      setMessages(prev => prev.map((m, i) =>
        i === prev.length - 1
          ? { role: 'assistant', content: `Error: ${getErrorMessage(err)}`, error: getErrorMessage(err) }
          : m
      ));
    }
  }

  const lastResult = [...messages].reverse().find(m => m.result)?.result;

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col gap-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-on-surface flex items-center gap-2">
          <FileText className="text-secondary" /> PDF RAG Chat
        </h2>
        <div className="flex gap-2 items-center">
          <span className="flex items-center gap-1.5 px-3 py-1 bg-surface-variant/40 rounded-full text-xs font-medium text-outline border border-outline-variant/20">
            <DatabaseStatus status={fileId ? 'active' : 'idle'} /> Index: {indexName}
          </span>
          <span className="flex items-center gap-1.5 px-3 py-1 bg-surface-variant/40 rounded-full text-xs font-medium text-outline border border-outline-variant/20">
            <Search size={12} /> Top K: 4
          </span>
          <button
            onClick={() => setUseRag(v => !v)}
            className={cn("px-3 py-1 rounded-full text-xs font-medium border transition-colors",
              useRag ? "bg-primary/10 text-primary border-primary/20" : "bg-surface-variant/40 text-outline border-outline-variant/20")}>
            RAG: {useRag ? 'ON' : 'OFF'}
          </button>
          <input ref={fileInputRef} type="file" accept=".pdf,.txt,.csv" className="hidden"
            onChange={e => e.target.files?.[0] && handleFileUpload(e.target.files[0])} />
          <button onClick={() => fileInputRef.current?.click()} disabled={uploading}
            className="flex items-center gap-1.5 px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-xs font-medium hover:bg-primary/20 transition-colors">
            {uploading ? <Loader size={12} className="animate-spin" /> : <Paperclip size={12} />}
            {uploading ? 'Indexing...' : 'Upload PDF'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
        {/* Left: Chat Window */}
        <section className="flex-1 lg:flex-[1.5] flex flex-col glass-panel rounded-lg overflow-hidden border-outline-variant/20">
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={cn("flex gap-4", msg.role === 'user' ? "max-w-[85%] ml-auto justify-end" : "max-w-[90%]")}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center shrink-0 border border-secondary/30 shadow-[0_0_10px_rgba(173,198,255,0.1)]">
                    {msg.loading ? <Loader size={14} className="text-secondary animate-spin" /> : <Bot size={14} className="text-secondary" />}
                  </div>
                )}
                <div className={cn("flex flex-col gap-2", msg.role === 'user' ? "" : "max-w-full")}>
                  {msg.loading ? (
                    <div className="bg-surface-container-high/40 px-4 py-3 rounded-lg rounded-tl-sm border border-secondary/20">
                      <div className="flex items-center gap-2 text-xs font-mono text-outline">
                        <div className="w-4 h-4 rounded-full border-2 border-t-secondary border-r-transparent border-b-transparent border-l-transparent animate-spin" />
                        Retrieving chunks...
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className={cn(
                        "px-4 py-3 rounded-lg shadow-sm relative overflow-hidden",
                        msg.role === 'user'
                          ? "bg-surface-variant/80 border border-outline-variant/20 rounded-tr-sm"
                          : "bg-surface-container-high/40 border border-secondary/20 rounded-tl-sm",
                        msg.error && "border-error/30 bg-error/5"
                      )}>
                        {msg.role === 'assistant' && !msg.error && (
                          <div className="absolute top-0 left-0 w-1 h-full bg-secondary/50" />
                        )}
                        {msg.error
                          ? <p className="text-sm text-error flex items-center gap-2"><AlertCircle size={14} />{msg.content}</p>
                          : <p className="text-sm text-on-surface leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                        }
                      </div>

                      {/* Scores inline below assistant answer */}
                      {msg.result && (
                        <div className="flex flex-wrap gap-2 ml-1">
                          <ScorePill label="Faithfulness" value={msg.result.faithfulness_score} />
                          <ScorePill label="Relevance" value={msg.result.relevance_score} />
                          <span className={cn("text-xs font-mono px-2 py-0.5 rounded border",
                            msg.result.hallucination_risk === 'low'
                              ? "text-tertiary border-tertiary/20 bg-tertiary/5"
                              : "text-error border-error/20 bg-error/5")}>
                            Risk: {msg.result.hallucination_risk}
                          </span>
                          {msg.result.response_provider && (
                            <span className="text-xs font-mono px-2 py-0.5 rounded border text-outline border-outline-variant/20 bg-surface-variant/30">
                              via {msg.result.response_provider}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Fallback warning — compact, not scary */}
                      {msg.result?.fallback_reason && (
                        <div className="ml-1 flex items-start gap-1.5 text-xs text-secondary px-2 py-1.5 rounded border border-secondary/20 bg-secondary/5">
                          <AlertTriangle size={11} className="shrink-0 mt-0.5" />
                          <span>{msg.result.fallback_reason}</span>
                        </div>
                      )}

                      {/* Retrieved chunk previews */}
                      {msg.result?.retrieved_chunks && msg.result.retrieved_chunks.length > 0 && (
                        <div className="ml-1 space-y-1">
                          {msg.result.retrieved_chunks.slice(0, 3).map((chunk: any, ci) => (
                            <div key={ci} className="text-xs bg-surface-container/60 border border-outline-variant/10 rounded px-3 py-2 flex items-start gap-2">
                              <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-surface-variant text-[9px] shrink-0 border border-outline-variant/30">{ci + 1}</span>
                              <span className="text-on-surface-variant line-clamp-2">{chunk.text || chunk.content || JSON.stringify(chunk).slice(0, 100)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </>
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

          {/* Input */}
          <div className="p-4 border-t border-outline-variant/20 bg-surface-container-lowest/50">
            {!fileId && (
              <div className="mb-3 text-xs text-outline font-mono flex items-center gap-2 text-center justify-center">
                <AlertTriangle size={12} className="text-secondary" /> Upload a PDF first to enable RAG queries
              </div>
            )}
            <div className="flex gap-2">
              <div className="flex-1 relative bg-surface-container rounded-md border border-outline-variant/30 focus-within:border-secondary focus-within:shadow-[0_0_10px_rgba(147,197,253,0.15)] transition-all flex items-end p-2">
                <textarea
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }}}
                  className="w-full bg-transparent border-none text-sm text-on-surface focus:ring-0 resize-none py-2 px-2 min-h-[40px] max-h-24"
                  placeholder={fileId ? "Ask about the document..." : "Upload a PDF first..."}
                  rows={1}
                  disabled={!fileId}
                />
              </div>
              <button
                onClick={handleSend}
                disabled={!input.trim() || !fileId}
                className="px-4 bg-secondary/10 hover:bg-secondary/20 text-secondary border border-secondary/20 rounded-md transition-colors disabled:opacity-40">
                <Send size={18} />
              </button>
            </div>
          </div>
        </section>

        {/* Right: Scores & Sources */}
        <section className="flex-1 lg:flex-[0.7] flex flex-col gap-4 min-h-0 overflow-y-auto">
          {/* RAG Quality scores panel */}
          <Card className="flex-shrink-0">
            <div className="px-4 py-3 border-b border-outline-variant/20 flex items-center gap-2 bg-surface-container-high/50">
              <BookOpen className="text-secondary" size={16} />
              <h3 className="text-sm font-medium text-on-surface">RAG Quality</h3>
              {lastResult?.response_provider && (
                <span className="ml-auto text-[10px] font-mono text-outline border border-outline-variant/20 px-1.5 py-0.5 rounded">
                  {lastResult.response_provider}
                </span>
              )}
            </div>
            <div className="p-4 space-y-3">
              <QualityBar label="Faithfulness" value={lastResult?.faithfulness_score ?? 0} color="secondary" />
              <QualityBar label="Relevance" value={lastResult?.relevance_score ?? 0} color="primary" />
              {lastResult?.hallucination_risk && (
                <div className="flex items-center justify-between text-xs mt-2">
                  <span className="text-on-surface-variant">Hallucination Risk</span>
                  <span className={cn("font-mono px-2 py-0.5 rounded border",
                    lastResult.hallucination_risk === 'low'
                      ? "text-tertiary border-tertiary/20 bg-tertiary/5"
                      : "text-error border-error/20 bg-error/5")}>
                    {lastResult.hallucination_risk}
                  </span>
                </div>
              )}
              {/* Fallback reason in the side panel — only when present */}
              {lastResult?.fallback_reason && (
                <div className="mt-2 flex items-start gap-1.5 text-xs text-secondary px-2 py-2 rounded border border-secondary/20 bg-secondary/5">
                  <AlertTriangle size={11} className="shrink-0 mt-0.5" />
                  <span>{lastResult.fallback_reason}</span>
                </div>
              )}
            </div>
          </Card>

          {/* Sources */}
          <Card className="flex-1 flex flex-col min-h-0">
            <div className="px-4 py-3 border-b border-outline-variant/20 flex items-center gap-2 bg-surface-container-high/50">
              <Link2 className="text-outline" size={16} />
              <h3 className="text-sm font-medium text-on-surface">Sources</h3>
              {lastResult?.sources && (
                <span className="ml-auto text-xs text-outline">{lastResult.sources.length} refs</span>
              )}
            </div>
            <div className="p-4 overflow-y-auto space-y-3">
              {lastResult?.sources?.length ? (
                lastResult.sources.map((src: any, i: number) => (
                  <Fragment key={i}><SourceCard index={i + 1} source={src} /></Fragment>
                ))
              ) : lastResult?.retrieved_chunks?.length ? (
                lastResult.retrieved_chunks.slice(0, 4).map((chunk: any, i: number) => (
                  <Fragment key={i}><SourceCard index={i + 1} source={chunk} /></Fragment>
                ))
              ) : (
                <div className="text-center py-6">
                  <FileIcon size={24} className="text-outline mx-auto mb-2 opacity-40" />
                  <p className="text-xs text-on-surface-variant">Sources appear after a RAG query</p>
                </div>
              )}
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}

function ScorePill({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <span className={cn("text-xs font-mono px-2 py-0.5 rounded border",
      pct >= 80 ? "text-tertiary border-tertiary/20 bg-tertiary/5" :
      pct >= 60 ? "text-secondary border-secondary/20 bg-secondary/5" :
      "text-error border-error/20 bg-error/5")}>
      {label}: {pct}%
    </span>
  );
}

function QualityBar({ label, value, color }: { label: string; value: number; color: string }) {
  const pct = Math.round(value * 100);
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-xs text-on-surface-variant">{label}</span>
        <span className="text-xs font-mono text-on-surface">{pct}%</span>
      </div>
      <div className="h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
        <div className={`h-full bg-${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function SourceCard({ index, source }: { index: number; source: any }) {
  return (
    <div className="rounded-lg border border-secondary/20 bg-secondary/5 p-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="w-5 h-5 rounded-full bg-secondary/20 text-secondary text-[10px] font-bold flex items-center justify-center">{index}</span>
        <span className="text-xs font-mono text-on-surface-variant truncate">
          {source.page ? `Page ${source.page}` : source.source || source.filename || `Chunk ${index}`}
        </span>
        {source.score && (
          <span className="ml-auto text-[10px] font-mono text-secondary">sim: {(source.score).toFixed(2)}</span>
        )}
      </div>
      <p className="text-xs text-on-surface line-clamp-3">
        {source.text || source.content || source.chunk || JSON.stringify(source).slice(0, 120)}
      </p>
    </div>
  );
}
