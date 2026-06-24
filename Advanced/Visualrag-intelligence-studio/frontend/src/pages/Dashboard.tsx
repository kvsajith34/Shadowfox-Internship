import { useEffect, useState, Fragment } from "react";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { MetricCard } from "../components/ui/MetricCard";
import { MOCK_DASHBOARD_METRICS, MOCK_RECENT_ANALYSES } from "../data/mockData";
import { getMetrics, getHistory, MetricsResult, HistoryItem, getErrorMessage } from "../api/client";
import { 
  UploadCloud, MessageSquare, FileText, Search, ShieldCheck, 
  AlertTriangle, Router, ArrowRight, FileIcon, BarChart, Wifi, WifiOff
} from "lucide-react";
import { LineChart, Line, ResponsiveContainer } from "recharts";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<MetricsResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [m, h] = await Promise.all([getMetrics(), getHistory()]);
        setMetrics(m);
        setHistory(h);
        setApiOnline(true);
      } catch {
        setApiOnline(false);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Merge backend data with fallback mock data
  const totalFiles = metrics?.totalFiles ?? MOCK_DASHBOARD_METRICS.totalFiles;
  const filesGrowth = metrics ? `+${((metrics.filesGrowth || 0) * 100).toFixed(0)}%` : MOCK_DASHBOARD_METRICS.filesGrowth;
  const queriesHandled = metrics?.queriesHandled ?? MOCK_DASHBOARD_METRICS.queriesHandled;
  const avgFaithfulness = metrics?.avgFaithfulness ?? MOCK_DASHBOARD_METRICS.avgFaithfulness;
  const hallucinations = metrics?.hallucinations ?? MOCK_DASHBOARD_METRICS.hallucinations;

  const trendData = metrics?.evaluationTrend?.length
    ? metrics.evaluationTrend.map(v => ({ val: v * 100 }))
    : [{ val: 20 }, { val: 40 }, { val: 50 }, { val: 65 }, { val: 75 }, { val: 82 }, { val: 94 }];

  const recentAnalyses = history.length > 0
    ? history.slice(0, 6).map(h => ({
        id: h.id,
        filename: h.filename || h.id,
        type: (h.task_type || h.type || "").toUpperCase().slice(0, 3),
        provider: h.provider,
        safety: h.safety === "passed" ? "Pass" : h.safety === "flagged" ? "Flagged" : h.safety,
      }))
    : MOCK_RECENT_ANALYSES;

  const providerStatus = metrics?.providerStatus ?? { OpenAI: "Online", Gemini: "Online", "Hugging Face": "Degraded" };

  return (
    <div className="flex flex-col gap-10 animate-in fade-in duration-500">
      {/* Hero */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <h1 className="text-4xl md:text-5xl lg:text-[56px] font-bold tracking-tight text-on-surface glow-text">
            VisualRAG Intelligence Studio
          </h1>
          {apiOnline !== null && (
            <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono border shrink-0 mt-2
              ${apiOnline ? "bg-tertiary/10 text-tertiary border-tertiary/20" : "bg-error/10 text-error border-error/20"}`}>
              {apiOnline ? <Wifi size={12} /> : <WifiOff size={12} />}
              {apiOnline ? "API Online" : "Mock Mode"}
            </span>
          )}
        </div>
        <p className="text-lg text-on-surface-variant max-w-3xl mb-8 opacity-80">
          Multimodal Document Intelligence, RAG, and Answer Evaluation
        </p>
        <div className="flex flex-wrap gap-4">
          <Button onClick={() => navigate("/upload")}>
            <UploadCloud size={20} /> Upload New File
          </Button>
          <Button variant="ghost" onClick={() => navigate("/visual-chat")}>
            <MessageSquare size={20} /> Start Visual Chat
          </Button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="Total Files" 
          value={totalFiles.toLocaleString()}
          icon={FileText}
          trend={filesGrowth}
          trendColor="tertiary"
          highlightIconColor="text-primary"
        />
        <MetricCard 
          title="Queries Handled" 
          value={queriesHandled.toLocaleString()}
          icon={Search}
          highlightIconColor="text-secondary"
        />
        <MetricCard 
          title="Avg. Faithfulness" 
          value={typeof avgFaithfulness === "number" ? avgFaithfulness.toFixed(2) : avgFaithfulness}
          icon={ShieldCheck}
          progress={Math.round((avgFaithfulness as number) * 100)}
          highlightIconColor="text-primary-container"
        />
        <MetricCard 
          title="Hallucinations" 
          value={hallucinations}
          icon={AlertTriangle}
          trend="Low"
          trendColor="outline"
          highlightIconColor="text-error"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Analyses Table */}
        <Card className="lg:col-span-8 flex flex-col">
          <div className="p-6 border-b border-white/5 flex justify-between items-center bg-surface-container-low/30">
            <h2 className="text-xl font-semibold text-on-surface">Recent Analyses
              {loading && <span className="ml-2 text-xs text-outline animate-pulse">Loading...</span>}
            </h2>
            <button
              onClick={() => navigate("/evaluation-lab")}
              className="text-primary hover:text-primary-fixed transition-colors text-sm font-medium flex items-center gap-1">
              View All <ArrowRight size={16} />
            </button>
          </div>
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 bg-surface-container-low/30 text-on-surface-variant text-sm">
                  <th className="py-4 px-6 font-medium">Filename</th>
                  <th className="py-4 px-6 font-medium">Type</th>
                  <th className="py-4 px-6 font-medium">Provider</th>
                  <th className="py-4 px-6 font-medium text-right">Safety</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.map((item) => (
                  <tr key={item.id} className="border-b last:border-0 border-white/5 hover:bg-white/5 transition-colors group">
                    <td className="py-4 px-6 flex items-center gap-3 text-sm">
                      <div className="w-8 h-8 rounded bg-surface-container flex items-center justify-center text-primary group-hover:bg-primary/10 transition-colors">
                         <FileIcon size={16} />
                      </div>
                      <span className="text-on-surface group-hover:text-primary transition-colors truncate max-w-[200px]" title={item.filename}>
                        {item.filename}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-sm text-on-surface-variant font-mono">{item.type}</td>
                    <td className="py-4 px-6 text-sm text-on-surface-variant">{item.provider}</td>
                    <td className="py-4 px-6 text-right">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border
                        ${item.safety === 'Pass' || item.safety === 'passed' ? 'bg-tertiary/10 text-tertiary border-tertiary/20' : 'bg-error/10 text-error border-error/20'}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${item.safety === 'Pass' || item.safety === 'passed' ? 'bg-tertiary' : 'bg-error'}`} /> 
                        {item.safety}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Side Panel */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <Card className="p-6">
            <h3 className="text-xl font-semibold text-on-surface mb-6 flex items-center justify-between">
              Provider Status <Router size={20} className="text-outline-variant" />
            </h3>
            <div className="flex flex-col gap-4">
              {Object.entries(providerStatus).map(([name, status]) => {
                const statusStr = String(status);
                return (
                  <Fragment key={name}>
                    <ProviderItem
                      short={name.slice(0, 3).toUpperCase()}
                      name={name}
                      status={statusStr}
                      color={statusStr === "Online" || statusStr === "active" ? "tertiary" : "error"}
                    />
                  </Fragment>
                );
              })}
              {Object.keys(providerStatus).length === 0 && (
                <>
                  <ProviderItem short="OAI" name="OpenAI" status="Online" color="tertiary" />
                  <ProviderItem short="GEM" name="Gemini" status="Online" color="tertiary" />
                  <ProviderItem short="HF" name="Hugging Face" status="Degraded" color="error" />
                </>
              )}
            </div>
          </Card>

          <Card className="p-6 h-[200px] flex flex-col">
            <h3 className="text-sm font-medium text-on-surface-variant uppercase tracking-wider mb-4 flex items-center gap-2">
              <BarChart size={16} /> Eval Quality Trend
            </h3>
            <div className="flex-1 w-full overflow-hidden relative border-l border-b border-outline-variant/30">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <Line 
                    type="monotone" 
                    dataKey="val" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={false}
                    className="drop-shadow-[0_0_5px_rgba(59,130,246,0.8)]"
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 bg-blue-500/10 [mask-image:linear-gradient(to_bottom,transparent,black)] bottom-0"></div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function ProviderItem({ short, name, status, color }: { short: string, name: string, status: string, color: 'tertiary' | 'error' }) {
  return (
    <div className={`flex items-center justify-between p-3 rounded-lg bg-surface-container/50 border ${color === 'error' ? 'border-error/20 bg-error/5' : 'border-white/5'}`}>
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-surface-container flex items-center justify-center border border-outline-variant/10">
          <span className="text-on-surface font-mono text-xs font-medium">{short}</span>
        </div>
        <span className="text-sm text-on-surface font-medium">{name}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full shadow-[0_0_8px_currentColor] ${color === 'error' ? 'bg-error text-error' : 'bg-tertiary text-tertiary'}`} />
        <span className={`text-xs font-mono font-medium ${color === 'error' ? 'text-error' : 'text-on-surface-variant'}`}>{status}</span>
      </div>
    </div>
  );
}
