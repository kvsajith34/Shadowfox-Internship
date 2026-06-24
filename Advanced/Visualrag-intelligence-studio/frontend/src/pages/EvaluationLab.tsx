import { useState, useEffect, ReactNode } from "react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { FlaskConical, Filter, Play, CheckCircle2, XCircle, AlertCircle, Search, Loader } from "lucide-react";
import { MOCK_RAG_LOGS } from "../data/mockData";
import { evaluateAnswer, EvaluationResult, getHistory, HistoryItem, getErrorMessage } from "../api/client";

export default function EvaluationLab() {
  const [question, setQuestion] = useState('What are the main bottlenecks in the system?');
  const [answer, setAnswer] = useState('Based on the analysis, the primary bottleneck is the database cluster with 3x load factor.');
  const [evidence, setEvidence] = useState('The database handles 10,000 concurrent connections with 95th percentile latency of 2.3s.');
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    getHistory().then(h => setHistory(h)).catch(() => {});
  }, []);

  async function runEval() {
    setLoading(true);
    try {
      const r = await evaluateAnswer({
        question, answer, evidence: evidence ? [evidence] : [], task_type: 'visual_chat', provider: 'mock'
      });
      setResult(r);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const displayLogs = history.length > 0
    ? history.slice(0, 6).map(h => ({
        id: '#' + h.id.slice(0, 6),
        model: h.provider,
        query: h.summary || h.type,
        faithfulnessScore: 0.9,
        relevanceScore: 0.85,
        verdict: h.safety === 'passed' ? 'Pass' : h.safety === 'flagged' ? 'Fail' : 'Pass',
      }))
    : MOCK_RAG_LOGS;

  const filtered = displayLogs.filter(l =>
    !search || l.query.toLowerCase().includes(search.toLowerCase()) || l.model.toLowerCase().includes(search.toLowerCase())
  );

  const avgFaithfulness = result ? (result.faithfulness_score * 100).toFixed(1) : "96.2";
  const avgRelevance = result ? (result.relevance_score * 100).toFixed(1) : "91.5";
  const completeness = result ? (result.completeness_score * 100).toFixed(1) : "88.9";

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
         <div className="flex flex-col">
            <h2 className="text-3xl font-bold text-on-surface flex items-center gap-3">
              <FlaskConical className="text-tertiary" size={28} /> Evaluation Lab
            </h2>
            <p className="text-on-surface-variant mt-1">Audit RAG traces for hallucination, faithfulness, and relevance.</p>
         </div>
         <div className="flex gap-3">
            <Button variant="secondary"><Filter size={16} /> Filters</Button>
            <Button className="bg-tertiary hover:bg-tertiary/90 text-on-tertiary" onClick={runEval} disabled={loading}>
              {loading ? <Loader size={16} className="animate-spin" /> : <Play size={16} />}
              {loading ? "Running..." : "Run Auto-Eval"}
            </Button>
         </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ScoreCard title="Avg. Faithfulness" score={`${avgFaithfulness}%`}
          trend={result ? `${result.faithfulness_score >= 0.9 ? '+' : ''}${((result.faithfulness_score - 0.9) * 100).toFixed(1)}%` : "+1.2%"}
          status={result && result.faithfulness_score < 0.7 ? "bad" : "good"} />
        <ScoreCard title="Answer Relevance" score={`${avgRelevance}%`}
          trend={result ? `${result.relevance_score >= 0.9 ? '+' : '-'}${Math.abs((result.relevance_score - 0.9) * 100).toFixed(1)}%` : "-0.4%"}
          status={result && result.relevance_score < 0.7 ? "bad" : "warning"} />
        <ScoreCard title="Completeness" score={`${completeness}%`}
          trend={result ? "+3.1%" : "+3.1%"}
          status="good" />
      </div>

      {/* Manual Evaluation Panel */}
      <Card className="p-6 border-outline-variant/20">
        <h3 className="font-semibold text-on-surface mb-4 flex items-center gap-2">
          <FlaskConical size={16} className="text-tertiary" /> Manual Evaluation
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-medium text-on-surface-variant">Question</label>
            <textarea value={question} onChange={e => setQuestion(e.target.value)} rows={3}
              className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-tertiary resize-none" />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-medium text-on-surface-variant">AI Answer</label>
            <textarea value={answer} onChange={e => setAnswer(e.target.value)} rows={3}
              className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-tertiary resize-none" />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-xs font-medium text-on-surface-variant">Evidence / Context</label>
            <textarea value={evidence} onChange={e => setEvidence(e.target.value)} rows={3}
              className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-tertiary resize-none" />
          </div>
        </div>

        {result && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 rounded-lg bg-surface-container/50 border border-outline-variant/10">
            <EvalMetric label="Relevance" value={result.relevance_score} />
            <EvalMetric label="Faithfulness" value={result.faithfulness_score} />
            <EvalMetric label="Completeness" value={result.completeness_score} />
            <EvalMetric label="Safety" value={result.safety_score} />
            {result.hallucination_risk !== 'low' && (
              <div className="col-span-full">
                <div className="flex items-center gap-2 text-sm text-error">
                  <AlertCircle size={14} />
                  <span>Hallucination Risk: <strong>{result.hallucination_risk}</strong> — {result.risk_explanation}</span>
                </div>
              </div>
            )}
            {result.improvement_suggestions?.length > 0 && (
              <div className="col-span-full">
                <p className="text-xs font-medium text-on-surface-variant mb-1">Suggestions:</p>
                <ul className="space-y-0.5">
                  {result.improvement_suggestions.map((s, i) => (
                    <li key={i} className="text-xs text-on-surface">• {s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Eval Logs Table */}
      <Card className="flex flex-col overflow-hidden">
        <div className="p-4 border-b border-outline-variant/10 flex justify-between items-center bg-surface-container-low/30">
           <div className="flex items-center gap-2">
             <h3 className="font-semibold text-on-surface">Recent Eval Logs</h3>
             <span className="text-xs bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-full border border-outline-variant/20">{filtered.length} records</span>
           </div>
           <div className="relative">
             <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-outline" size={14} />
             <input type="text" placeholder="Search logs..." value={search} onChange={e => setSearch(e.target.value)}
               className="pl-8 pr-4 py-1.5 text-sm bg-surface-container border border-outline-variant/30 rounded-md focus:outline-none focus:border-tertiary text-on-surface" />
           </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/5 text-on-surface-variant text-xs uppercase tracking-wider">
                <th className="py-3 px-4 font-medium">ID</th>
                <th className="py-3 px-4 font-medium">Model</th>
                <th className="py-3 px-4 font-medium">Query</th>
                <th className="py-3 px-4 font-medium text-right">Faithfulness</th>
                <th className="py-3 px-4 font-medium text-right">Relevance</th>
                <th className="py-3 px-4 font-medium text-right">Verdict</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(log => (
                <tr key={log.id} className="border-b last:border-0 border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4 font-mono text-xs text-outline">{log.id}</td>
                  <td className="py-3 px-4 text-xs text-on-surface-variant">{log.model}</td>
                  <td className="py-3 px-4 text-sm text-on-surface max-w-[260px] truncate">{log.query}</td>
                  <td className="py-3 px-4 text-right font-mono text-xs">
                    <span className={log.faithfulnessScore >= 0.8 ? 'text-tertiary' : log.faithfulnessScore >= 0.6 ? 'text-secondary' : 'text-error'}>
                      {(log.faithfulnessScore * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-xs">
                    <span className={log.relevanceScore >= 0.8 ? 'text-tertiary' : log.relevanceScore >= 0.6 ? 'text-secondary' : 'text-error'}>
                      {(log.relevanceScore * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <VerdictBadge verdict={log.verdict} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function EvalMetric({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div>
      <p className="text-xs text-on-surface-variant mb-1">{label}</p>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
          <div className="h-full bg-primary rounded-full" style={{ width: `${pct}%` }} />
        </div>
        <span className="text-xs font-mono text-on-surface w-10 text-right">{pct}%</span>
      </div>
    </div>
  );
}

function ScoreCard({ title, score, trend, status }: { title: string; score: string; trend: string; status: 'good' | 'warning' | 'bad' }) {
  const colors = { good: 'text-tertiary border-tertiary/20 bg-tertiary/5', warning: 'text-secondary border-secondary/20 bg-secondary/5', bad: 'text-error border-error/20 bg-error/5' };
  return (
    <Card className={`p-6 border ${colors[status]}`}>
      <p className="text-sm text-on-surface-variant mb-1">{title}</p>
      <p className="text-3xl font-bold text-on-surface">{score}</p>
      <p className={`text-xs font-mono mt-1 ${status === 'bad' ? 'text-error' : status === 'warning' ? 'text-secondary' : 'text-tertiary'}`}>{trend} vs last week</p>
    </Card>
  );
}

function VerdictBadge({ verdict }: { verdict: string }) {
  const map: Record<string, { icon: ReactNode; className: string }> = {
    Pass: { icon: <CheckCircle2 size={10} />, className: 'bg-tertiary/10 text-tertiary border-tertiary/20' },
    Fail: { icon: <XCircle size={10} />, className: 'bg-error/10 text-error border-error/20' },
    Investigate: { icon: <AlertCircle size={10} />, className: 'bg-secondary/10 text-secondary border-secondary/20' },
  };
  const v = map[verdict] || map['Investigate'];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium border ${v.className}`}>
      {v.icon} {verdict}
    </span>
  );
}
