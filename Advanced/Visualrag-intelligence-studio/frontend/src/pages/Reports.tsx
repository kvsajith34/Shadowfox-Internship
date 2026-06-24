import { useEffect, useState } from "react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { FileBarChart, Download, Share2, Printer, CheckCircle2, LayoutTemplate, Loader } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getReports, ReportsResult, getErrorMessage } from "../api/client";

const FALLBACK_PERF = [
  { name: 'Invoice', processingTime: 1.2, accuracy: 98 },
  { name: 'Charts', processingTime: 2.5, accuracy: 94 },
  { name: 'PDFs', processingTime: 4.8, accuracy: 91 },
  { name: 'Images', processingTime: 0.9, accuracy: 99 },
];

export default function Reports() {
  const [data, setData] = useState<ReportsResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getReports()
      .then(d => setData(d))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const summary = (data?.summary as any) || {};
  const safetyAudit = (data?.safety_audit as any) || {};
  const qualityReport = (data?.quality_report as any) || {};

  const totalAnalyses = summary.total_analyses ?? 42;
  const avgQuality = summary.avg_quality_score ?? 0.94;
  const flaggedItems = summary.flagged_count ?? 3;

  const performanceData = qualityReport.by_type
    ? Object.entries(qualityReport.by_type).map(([name, val]: [string, any]) => ({
        name, processingTime: val.avg_time ?? 1.5, accuracy: Math.round((val.avg_quality ?? 0.9) * 100)
      }))
    : FALLBACK_PERF;

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-500 max-w-6xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
           <h2 className="text-3xl font-bold text-on-surface flex items-center gap-2">
             <FileBarChart className="text-primary" size={28} /> Pipeline Reports
             {loading && <Loader size={20} className="text-outline animate-spin ml-2" />}
           </h2>
           <p className="text-on-surface-variant mt-1">Exportable summaries of Intelligence Studio operations.</p>
        </div>
        <div className="flex gap-3">
           <Button variant="secondary" className="px-3"><Printer size={18} /></Button>
           <Button variant="secondary" className="px-3"><Share2 size={18} /></Button>
           <Button><Download size={18} /> Generate PDF</Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 border-primary/20 bg-primary/5">
          <p className="text-xs text-on-surface-variant mb-1">Total Analyses</p>
          <p className="text-3xl font-bold text-on-surface">{totalAnalyses}</p>
          <p className="text-xs text-on-surface-variant mt-1">This reporting period</p>
        </Card>
        <Card className="p-4 border-tertiary/20 bg-tertiary/5">
          <p className="text-xs text-on-surface-variant mb-1">Avg. Quality Score</p>
          <p className="text-3xl font-bold text-tertiary">{(avgQuality * 100).toFixed(0)}%</p>
          <p className="text-xs text-on-surface-variant mt-1">Across all task types</p>
        </Card>
        <Card className="p-4 border-error/20 bg-error/5">
          <p className="text-xs text-on-surface-variant mb-1">Flagged Items</p>
          <p className="text-3xl font-bold text-error">{flaggedItems}</p>
          <p className="text-xs text-on-surface-variant mt-1">Require manual review</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Chart */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="flex flex-col">
            <div className="px-6 py-4 border-b border-outline-variant/10 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-on-surface">Performance by Task Type</h2>
            </div>
            <div className="p-6 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                  <XAxis dataKey="name" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff', fontSize: 12 }}
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  />
                  <Bar dataKey="accuracy" name="Accuracy %" fill="#adc6ff" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="processingTime" name="Time (s)" fill="#4cd7f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Safety Audit */}
          <Card className="p-6">
            <h3 className="font-semibold text-on-surface mb-4">Safety Audit Summary</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-tertiary">{safetyAudit.passed ?? 39}</p>
                <p className="text-xs text-on-surface-variant mt-1">Passed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-secondary">{safetyAudit.reviewed ?? 2}</p>
                <p className="text-xs text-on-surface-variant mt-1">Reviewed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-error">{safetyAudit.flagged ?? flaggedItems}</p>
                <p className="text-xs text-on-surface-variant mt-1">Flagged</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Export Options */}
        <div className="flex flex-col gap-4">
          <Card className="p-6">
            <h3 className="font-semibold text-on-surface mb-4 flex items-center gap-2">
              <LayoutTemplate size={18} className="text-primary" /> Export Reports
            </h3>
            <div className="flex flex-col gap-3">
              {[
                { label: 'Full Quality Report', fmt: 'PDF', badge: 'tertiary' },
                { label: 'Safety Audit Log', fmt: 'CSV', badge: 'secondary' },
                { label: 'RAG Performance', fmt: 'JSON', badge: 'primary' },
                { label: 'Evaluation Traces', fmt: 'JSONL', badge: 'outline' },
              ].map(({ label, fmt, badge }) => (
                <div key={label} className="flex items-center justify-between p-3 rounded-lg bg-surface-container/50 border border-outline-variant/10 hover:bg-surface-variant/20 transition-colors cursor-pointer">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 size={16} className="text-tertiary" />
                    <span className="text-sm text-on-surface">{label}</span>
                  </div>
                  <span className={`text-[10px] font-mono border px-1.5 py-0.5 rounded bg-${badge}/10 text-${badge} border-${badge}/20`}>{fmt}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6 border-outline-variant/20">
            <h3 className="text-sm font-semibold text-on-surface mb-3">Report Period</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-on-surface-variant">From</span><span className="font-mono text-on-surface">30 days ago</span></div>
              <div className="flex justify-between"><span className="text-on-surface-variant">To</span><span className="font-mono text-on-surface">Today</span></div>
              <div className="flex justify-between"><span className="text-on-surface-variant">Status</span>
                <span className="font-mono text-tertiary flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-pulse" /> Live
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
