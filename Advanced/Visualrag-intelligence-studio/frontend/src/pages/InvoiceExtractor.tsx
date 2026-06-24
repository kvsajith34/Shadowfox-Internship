import { useState, useRef } from "react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Receipt, Download, Check, AlertTriangle, FileText, CheckCircle2, Loader, Upload } from "lucide-react";
import { extractInvoice, InvoiceResult, getErrorMessage } from "../api/client";

export default function InvoiceExtractor() {
  const [result, setResult] = useState<InvoiceResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    setFilename(file.name);
    try {
      const res = await extractInvoice(file);
      setResult(res);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  function downloadJSON() {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'invoice_extraction.json'; a.click();
  }

  const confidencePct = result ? Math.round(result.confidence_score * 100) : 0;

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col gap-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
         <div className="flex flex-col">
            <h2 className="text-xl font-bold text-on-surface flex items-center gap-2">
              <Receipt className="text-primary" /> Invoice Data Extraction
            </h2>
            <p className="text-sm text-on-surface-variant">
              {filename ? `Structured output from ${filename}` : "Upload an invoice PDF or image"}
            </p>
         </div>
         <div className="flex gap-3">
            <Button variant="secondary" className="hidden sm:flex" onClick={downloadJSON} disabled={!result}>
              <Download size={16} /> JSON Export
            </Button>
            <Button className="bg-tertiary hover:bg-tertiary/90 text-on-tertiary" disabled={!result}>
              <Check size={16} /> Approve & Sync
            </Button>
         </div>
      </div>

      <input ref={fileInputRef} type="file" accept=".pdf,.png,.jpg,.jpeg" className="hidden"
        onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />

      <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
        {/* Left: Upload Zone / Document View */}
        <section className="flex-1 flex flex-col glass-panel rounded-lg overflow-hidden border-outline-variant/20">
          <div className="px-4 py-3 border-b border-outline-variant/20 flex justify-between items-center bg-surface-container-high/50">
            <div className="flex items-center gap-2">
              <FileText className="text-outline" size={16} />
              <h3 className="text-sm font-medium text-on-surface">Original PDF</h3>
            </div>
            <span className="text-xs font-mono text-outline border border-outline-variant/30 px-2 rounded bg-surface">
              {result ? `Confidence: ${confidencePct}%` : "No file"}
            </span>
          </div>
          <div
            className="flex-1 flex items-center justify-center p-8 cursor-pointer hover:bg-primary/5 transition-colors"
            onClick={() => fileInputRef.current?.click()}>
            {loading ? (
              <div className="text-center">
                <Loader size={48} className="text-primary animate-spin mx-auto mb-3" />
                <p className="text-sm text-on-surface-variant">Extracting invoice data...</p>
              </div>
            ) : error ? (
              <div className="text-center">
                <AlertTriangle size={48} className="text-error mx-auto mb-3" />
                <p className="text-sm text-error">{error}</p>
                <p className="text-xs text-on-surface-variant mt-2">Click to try another file</p>
              </div>
            ) : result ? (
              <div className="bg-white w-full max-w-[440px] rounded-lg shadow-2xl p-6 text-gray-800">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-lg font-bold">{result.vendor_name || 'Vendor'}</h3>
                    <p className="text-xs text-gray-500">INVOICE</p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-sm font-bold">{result.invoice_number}</p>
                    <p className="text-xs text-gray-500">{result.invoice_date}</p>
                  </div>
                </div>
                <div className="space-y-1 text-sm border-t pt-3 mb-4">
                  {result.line_items.map((item, i) => (
                    <div key={i} className="flex justify-between">
                      <span>{item.description} × {item.quantity}</span>
                      <span className="font-mono">${item.total.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
                <div className="border-t pt-3 space-y-1 text-sm">
                  <div className="flex justify-between text-gray-600"><span>Subtotal</span><span>${result.subtotal.toFixed(2)}</span></div>
                  <div className="flex justify-between text-gray-600"><span>Tax</span><span>${result.tax_amount.toFixed(2)}</span></div>
                  <div className="flex justify-between font-bold text-base"><span>TOTAL</span><span>${result.total_amount.toFixed(2)}</span></div>
                </div>
              </div>
            ) : (
              <div className="text-center">
                <Upload size={48} className="text-primary/60 mx-auto mb-3" />
                <h3 className="text-lg font-bold text-on-surface mb-2">Upload Invoice</h3>
                <p className="text-sm text-on-surface-variant">Click to upload a PDF or image invoice</p>
              </div>
            )}
          </div>
        </section>

        {/* Right: Extracted Fields */}
        <section className="flex-1 flex flex-col gap-4 overflow-y-auto">
          {result ? (
            <>
              <ExtractedField label="Vendor Name" value={result.vendor_name} confidence={result.confidence_score} />
              <ExtractedField label="Invoice Number" value={result.invoice_number} confidence={result.confidence_score} />
              <ExtractedField label="Invoice Date" value={result.invoice_date} confidence={result.confidence_score} />
              <ExtractedField label="Due Date" value={result.due_date || "—"} confidence={result.confidence_score} />
              <ExtractedField label="Subtotal" value={`$${result.subtotal.toFixed(2)}`} confidence={result.confidence_score} />
              <ExtractedField label="Tax Amount" value={`$${result.tax_amount.toFixed(2)}`} confidence={result.confidence_score} />
              <ExtractedField label="Total Amount" value={`$${result.total_amount.toFixed(2)}`} confidence={result.confidence_score} highlight />
              <ExtractedField label="Currency" value={result.currency} confidence={result.confidence_score} />
              <ExtractedField label="Payment Status" value={result.payment_status} confidence={result.confidence_score} />
              {result.missing_fields.length > 0 && (
                <Card className="p-4 border-error/20 bg-error/5">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle size={14} className="text-error" />
                    <span className="text-sm font-medium text-error">Missing Fields</span>
                  </div>
                  <ul className="space-y-1">
                    {result.missing_fields.map(f => (
                      <li key={f} className="text-xs text-on-surface-variant font-mono">• {f}</li>
                    ))}
                  </ul>
                </Card>
              )}
            </>
          ) : (
            <Card className="flex-1 flex items-center justify-center p-8">
              <div className="text-center text-on-surface-variant">
                <Receipt size={32} className="mx-auto mb-3 opacity-30" />
                <p className="text-sm">Upload an invoice to see extracted fields here</p>
              </div>
            </Card>
          )}
        </section>
      </div>
    </div>
  );
}

function ExtractedField({ label, value, confidence, highlight }: { label: string; value: string; confidence: number; highlight?: boolean }) {
  const pct = Math.round(confidence * 100);
  return (
    <Card className={`p-4 ${highlight ? 'border-primary/30 bg-primary/5' : 'border-outline-variant/20'}`}>
      <div className="flex justify-between items-center">
        <div>
          <p className="text-xs text-on-surface-variant mb-0.5">{label}</p>
          <p className={`font-mono font-semibold ${highlight ? 'text-primary text-lg' : 'text-on-surface'}`}>{value}</p>
        </div>
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-mono border
          ${pct >= 90 ? 'bg-tertiary/10 text-tertiary border-tertiary/20' : pct >= 70 ? 'bg-secondary/10 text-secondary border-secondary/20' : 'bg-error/10 text-error border-error/20'}`}>
          {pct >= 90 ? <CheckCircle2 size={10} /> : <AlertTriangle size={10} />}
          {pct}%
        </div>
      </div>
    </Card>
  );
}
