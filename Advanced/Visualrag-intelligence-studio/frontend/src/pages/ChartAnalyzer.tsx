import { useState, useRef } from "react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { BarChart, Share2, Download, TrendingUp, Presentation, ZoomIn, ZoomOut, BrainCircuit, Activity, Upload, Loader, AlertCircle } from "lucide-react";
import { analyzeChart, ChartResult, getErrorMessage } from "../api/client";

export default function ChartAnalyzer() {
  const [result, setResult] = useState<ChartResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [filename, setFilename] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    setFilename(file.name);
    setPreviewUrl(URL.createObjectURL(file));
    try {
      const res = await analyzeChart(file, question || undefined);
      setResult(res);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col gap-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
         <div className="flex flex-col">
            <h2 className="text-xl font-bold text-on-surface flex items-center gap-2">
              <BarChart className="text-secondary" /> Chart Analyzer
            </h2>
            <p className="text-sm text-on-surface-variant flex items-center gap-2">
              {filename ? <>Interpreting <span className="font-mono text-xs bg-surface-variant px-1.5 py-0.5 rounded text-outline">{filename}</span></> : "Upload a chart image to analyze"}
            </p>
         </div>
         <div className="flex gap-3">
            <Button variant="ghost" className="hidden sm:flex"><Share2 size={16} /> Share</Button>
            <Button className="bg-primary hover:bg-primary-fixed hover:text-black" disabled={!result}>
              <Download size={16} /> Export Data
            </Button>
         </div>
      </div>

      <input ref={fileInputRef} type="file" accept=".png,.jpg,.jpeg" className="hidden"
        onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />

      <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
        {/* Left: Source Image */}
        <section className="flex-1 flex flex-col gap-6 min-h-0">
          <Card className="flex-[1.2] flex flex-col border-outline-variant/20 overflow-hidden">
            <div className="px-4 py-3 border-b border-outline-variant/20 flex justify-between items-center bg-surface-container-high/50">
              <div className="flex items-center gap-2">
                <Presentation className="text-outline" size={16} />
                <h3 className="text-sm font-medium text-on-surface">Original Chart</h3>
              </div>
              <div className="flex gap-2 text-outline">
                <button className="hover:text-primary"><ZoomIn size={16} /></button>
                <button className="hover:text-primary"><ZoomOut size={16} /></button>
              </div>
            </div>
            <div className="flex-1 p-4 flex items-center justify-center cursor-pointer" onClick={() => fileInputRef.current?.click()}>
              {loading ? (
                <div className="text-center">
                  <Loader size={40} className="text-primary animate-spin mx-auto mb-3" />
                  <p className="text-sm text-on-surface-variant">Analyzing chart...</p>
                </div>
              ) : previewUrl ? (
                <img src={previewUrl} alt="Chart" className="max-w-full max-h-full object-contain rounded border border-outline-variant/20 shadow-lg" />
              ) : (
                <div className="text-center">
                  <Upload size={40} className="text-primary/60 mx-auto mb-3" />
                  <p className="text-sm text-on-surface-variant">Click to upload a chart image</p>
                </div>
              )}
            </div>
          </Card>

          {/* Question input */}
          <Card className="p-4 border-outline-variant/20">
            <label className="text-xs font-medium text-on-surface-variant uppercase tracking-wider mb-2 block">Ask a specific question (optional)</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                placeholder="e.g. What is the highest value in Q3?"
                className="flex-1 bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary"
              />
              <Button onClick={() => fileInputRef.current?.click()} disabled={loading}>
                {loading ? <Loader size={16} className="animate-spin" /> : <Upload size={16} />}
                Analyze
              </Button>
            </div>
          </Card>
        </section>

        {/* Right: Analysis Results */}
        <section className="flex-1 flex flex-col gap-4 min-h-0 overflow-y-auto">
          {error && (
            <Card className="p-4 border-error/30 bg-error/5">
              <div className="flex items-center gap-2 text-error text-sm"><AlertCircle size={16} />{error}</div>
            </Card>
          )}

          {result ? (
            <>
              <Card className="p-4 border-outline-variant/20">
                <div className="flex items-center gap-2 mb-3">
                  <BrainCircuit className="text-primary" size={16} />
                  <h3 className="text-sm font-semibold text-on-surface">AI Analysis</h3>
                  <span className="ml-auto text-xs font-mono text-outline">Conf: {Math.round(result.confidence_score * 100)}%</span>
                </div>
                <p className="text-sm text-on-surface">{result.answer}</p>
              </Card>

              <div className="grid grid-cols-2 gap-4">
                <Card className="p-4 border-outline-variant/20">
                  <p className="text-xs text-on-surface-variant mb-1">Chart Type</p>
                  <p className="font-mono text-sm text-on-surface font-medium">{result.chart_type || "—"}</p>
                </Card>
                <Card className="p-4 border-outline-variant/20">
                  <p className="text-xs text-on-surface-variant mb-1">Main Trend</p>
                  <p className="font-mono text-sm text-on-surface font-medium">{result.main_trend || "—"}</p>
                </Card>
                <Card className="p-4 border-tertiary/20 bg-tertiary/5">
                  <p className="text-xs text-on-surface-variant mb-1">Highest Value</p>
                  <p className="font-mono text-sm text-tertiary font-bold">{result.highest_value || "—"}</p>
                </Card>
                <Card className="p-4 border-error/20 bg-error/5">
                  <p className="text-xs text-on-surface-variant mb-1">Lowest Value</p>
                  <p className="font-mono text-sm text-error font-bold">{result.lowest_value || "—"}</p>
                </Card>
              </div>

              {result.key_insights?.length > 0 && (
                <Card className="p-4 border-outline-variant/20">
                  <div className="flex items-center gap-2 mb-3">
                    <Activity className="text-secondary" size={16} />
                    <h3 className="text-sm font-semibold text-on-surface">Key Insights</h3>
                  </div>
                  <ul className="space-y-2">
                    {result.key_insights.map((insight, i) => (
                      <li key={i} className="text-sm text-on-surface flex gap-2">
                        <span className="text-primary shrink-0">→</span>{insight}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {result.possible_limitations?.length > 0 && (
                <Card className="p-4 border-secondary/20">
                  <h3 className="text-xs font-medium text-on-surface-variant uppercase tracking-wider mb-2">Possible Limitations</h3>
                  <ul className="space-y-1">
                    {result.possible_limitations.map((l, i) => (
                      <li key={i} className="text-xs text-on-surface-variant">• {l}</li>
                    ))}
                  </ul>
                </Card>
              )}
            </>
          ) : (
            <Card className="flex-1 flex items-center justify-center p-8">
              <div className="text-center text-on-surface-variant">
                <TrendingUp size={32} className="mx-auto mb-3 opacity-30" />
                <p className="text-sm">Upload a chart image to see AI analysis</p>
              </div>
            </Card>
          )}
        </section>
      </div>
    </div>
  );
}
