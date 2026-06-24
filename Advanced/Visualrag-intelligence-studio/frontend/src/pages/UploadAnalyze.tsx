import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { 
  CloudUpload, FileSearch, Receipt, BarChart2, Database,
  FileIcon, Image as ImageIcon, X, Info, CheckCircle, AlertCircle, Loader
} from "lucide-react";
import { cn } from "../utils";
import { uploadFile, UploadResult, getErrorMessage } from "../api/client";

type AnalysisType = 'general' | 'ocr' | 'chart' | 'rag';
type FileStatus = 'idle' | 'uploading' | 'done' | 'error';

interface QueuedFile {
  id: string;
  file: File;
  status: FileStatus;
  result?: UploadResult;
  error?: string;
}

const ANALYSIS_TYPE_MAP: Record<AnalysisType, string> = {
  general: 'general',
  ocr: 'invoice',
  chart: 'chart',
  rag: 'rag',
};

export default function UploadAnalyze() {
  const [activeConfig, setActiveConfig] = useState<AnalysisType>('general');
  const [queue, setQueue] = useState<QueuedFile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const configs = [
    { id: 'general' as const, title: 'General Analysis', desc: 'Default multimodal extraction', icon: FileSearch },
    { id: 'ocr' as const, title: 'Invoice OCR', desc: 'Structured financial data', icon: Receipt },
    { id: 'chart' as const, title: 'Chart Interpretation', desc: 'Data visualization insights', icon: BarChart2 },
    { id: 'rag' as const, title: 'RAG Indexing', desc: 'Vector database embedding', icon: Database },
  ];

  function addFiles(files: FileList | null) {
    if (!files) return;
    const newItems: QueuedFile[] = Array.from(files).map(f => ({
      id: `${Date.now()}-${f.name}`,
      file: f,
      status: 'idle',
    }));
    setQueue(prev => [...prev, ...newItems]);
    // Auto-upload
    newItems.forEach(item => startUpload(item, activeConfig));
  }

  function startUpload(item: QueuedFile, config: AnalysisType) {
    setQueue(prev => prev.map(q => q.id === item.id ? { ...q, status: 'uploading' } : q));
    uploadFile(item.file, ANALYSIS_TYPE_MAP[config])
      .then(result => {
        setQueue(prev => prev.map(q => q.id === item.id ? { ...q, status: 'done', result } : q));
      })
      .catch(err => {
        setQueue(prev => prev.map(q => q.id === item.id ? { ...q, status: 'error', error: getErrorMessage(err) } : q));
      });
  }

  function removeItem(id: string) {
    setQueue(prev => prev.filter(q => q.id !== id));
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    setDragOver(false);
    addFiles(e.dataTransfer.files);
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    addFiles(e.target.files);
    e.target.value = '';
  }

  const activeFile = queue.find(q => q.status === 'uploading' || q.status === 'done');

  return (
    <div className="flex flex-col lg:flex-row gap-8 h-full animate-in fade-in duration-500">
      {/* Left Column */}
      <div className="flex-1 flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold text-on-surface">Data Ingestion</h2>
          <p className="text-on-surface-variant">Initialize multimodal analysis pipeline.</p>
        </div>

        {/* Drag Drop Zone */}
        <Card
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "p-8 flex flex-col items-center justify-center min-h-[300px] border-2 border-dashed transition-all cursor-pointer group relative",
            dragOver ? "border-primary bg-primary/10" : "border-outline-variant/30 hover:border-primary hover:bg-primary/5"
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.csv,.txt"
            multiple
            className="hidden"
            onChange={handleFileChange}
          />
          <CloudUpload className="text-primary w-16 h-16 mb-4 transform group-hover:-translate-y-2 transition-transform" strokeWidth={1.5} />
          <h3 className="text-xl font-bold text-on-surface mb-2">Drag & Drop PDF, Images, or Reports</h3>
          <p className="text-sm text-on-surface-variant mb-6 text-center max-w-md">
            or click to browse local files. Supported formats: .pdf, .png, .jpg, .csv (Max 50MB per file)
          </p>
          <Button variant="secondary" className="rounded-full !px-8 text-primary hover:text-white border-primary/20 bg-primary/10 hover:bg-primary">
            Select Files
          </Button>
        </Card>

        {/* Analysis Config */}
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-medium tracking-wider text-on-surface-variant uppercase">Analysis Configuration</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {configs.map((conf) => {
              const active = activeConfig === conf.id;
              return (
                <div 
                  key={conf.id}
                  onClick={() => setActiveConfig(conf.id)}
                  className={cn(
                    "p-4 rounded-lg cursor-pointer transition-all border flex flex-col gap-3",
                    active ? "border-primary bg-primary/10" : "glass-panel hover:bg-surface-variant/30 border-outline-variant/20"
                  )}
                >
                  <div className="flex justify-between items-start">
                    <div className={cn(
                      "w-8 h-8 rounded flex items-center justify-center",
                      active ? "bg-primary/20 text-primary" : "bg-surface-variant/50 text-on-surface-variant"
                    )}>
                      <conf.icon size={18} />
                    </div>
                    <div className={cn(
                      "w-4 h-4 rounded-full border flex items-center justify-center",
                      active ? "border-primary" : "border-outline-variant"
                    )}>
                      {active && <div className="w-2 h-2 rounded-full bg-primary" />}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-on-surface text-sm mb-1">{conf.title}</h4>
                    <p className="text-xs text-on-surface-variant/80">{conf.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Queue */}
        {queue.length > 0 && (
          <div className="flex flex-col gap-4">
            <h3 className="text-sm font-medium tracking-wider text-on-surface-variant uppercase">Queue</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {queue.map(item => (
                <div key={item.id} className={cn(
                  "glass-panel rounded-lg p-4 flex items-center gap-4 relative overflow-hidden group",
                  item.status === 'uploading' ? "border-primary/30" : item.status === 'done' ? "border-tertiary/30" : "border-error/30"
                )}>
                  {item.status === 'uploading' && (
                    <>
                      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_4%,rgba(255,255,255,0.1)_25%,rgba(255,255,255,0.05)_36%)] animate-[shimmer_2s_infinite_linear] [background-size:1000px_100%] z-0 opacity-50" />
                      <div className="absolute bottom-0 left-0 h-1 bg-primary w-2/3 z-10" />
                    </>
                  )}
                  <div className={cn(
                    "w-10 h-10 rounded flex items-center justify-center shrink-0 z-10",
                    item.file.type.includes('image') ? "bg-secondary-container/20 text-secondary" : "bg-primary/10 text-primary"
                  )}>
                    {item.file.type.includes('image') ? <ImageIcon size={20} /> : <FileIcon size={20} />}
                  </div>
                  <div className="flex-1 min-w-0 z-10">
                    <h4 className="text-sm font-medium text-on-surface truncate">{item.file.name}</h4>
                    <div className="flex items-center gap-1.5 mt-1">
                      {item.status === 'uploading' && <><span className="w-2 h-2 rounded-full bg-tertiary animate-pulse" /><span className="font-mono text-xs text-tertiary">Uploading...</span></>}
                      {item.status === 'done' && <><CheckCircle size={12} className="text-tertiary" /><span className="font-mono text-xs text-tertiary">Done · {item.result?.file_id?.slice(0, 8)}</span></>}
                      {item.status === 'error' && <><AlertCircle size={12} className="text-error" /><span className="font-mono text-xs text-error">{item.error}</span></>}
                      {item.status === 'idle' && <span className="font-mono text-xs text-on-surface-variant">Queued</span>}
                    </div>
                  </div>
                  <button onClick={() => removeItem(item.id)} className="text-outline-variant hover:text-error transition-colors z-10">
                    <X size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Right Column Context Sidebar */}
      <div className="w-full lg:w-80 flex flex-col gap-6 shrink-0 lg:border-l lg:border-outline-variant/10 lg:pl-8">
        <Card className="p-4 flex flex-col gap-3 border-tertiary/20">
          <div className="flex justify-between items-center">
            <h3 className="font-medium text-sm text-on-surface">Pipeline Status</h3>
            <span className={cn(
              "px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider border",
              queue.some(q => q.status === 'uploading') ? "bg-primary/10 text-primary border-primary/20" :
              queue.some(q => q.status === 'done') ? "bg-tertiary/10 text-tertiary border-tertiary/20" :
              "bg-outline/10 text-outline border-outline/20"
            )}>
              {queue.some(q => q.status === 'uploading') ? "Processing" : queue.some(q => q.status === 'done') ? "Complete" : "Ready"}
            </span>
          </div>
          <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden mt-1">
            <div className={cn(
              "h-full bg-primary relative transition-all duration-500",
              queue.length === 0 ? "w-0" : queue.some(q => q.status === 'uploading') ? "w-[65%]" : "w-full"
            )}>
              {queue.some(q => q.status === 'uploading') && <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite_linear]" />}
            </div>
          </div>
          <div className="flex justify-between font-mono text-xs text-on-surface-variant">
            <span>{queue.filter(q => q.status === 'done').length} of {queue.length} done</span>
            <span>{queue.length === 0 ? "0%" : `${Math.round((queue.filter(q => q.status === 'done').length / queue.length) * 100)}%`}</span>
          </div>
        </Card>

        <Card className="p-4 flex flex-col flex-1">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-outline-variant/10">
            <Info className="text-primary" size={18} />
            <h3 className="font-medium text-sm text-on-surface">Active File Details</h3>
          </div>
          <div className="flex flex-col gap-3">
            {activeFile?.result ? (
              <>
                <DetailRow label="File ID" value={activeFile.result.file_id.slice(0, 12) + "..."} />
                <DetailRow label="File Name" value={activeFile.result.filename} />
                <DetailRow label="Format" value={activeFile.result.file_type.toUpperCase()} />
                <DetailRow label="Size" value={`${(activeFile.result.size_bytes / 1024).toFixed(1)} KB`} />
                <DetailRow label="Status" value={activeFile.result.status} />
                {activeFile.result.summary && (
                  <div className="mt-2">
                    <span className="text-xs font-medium text-on-surface-variant">Summary</span>
                    <p className="text-xs font-mono text-on-surface mt-1 opacity-70 line-clamp-4">{activeFile.result.summary}</p>
                  </div>
                )}
              </>
            ) : (
              <>
                <DetailRow label="File Name" value="No file selected" />
                <DetailRow label="Size" value="—" />
                <DetailRow label="Format" value="—" />
                <DetailRow label="Uploaded" value="—" />
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string, value: string }) {
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-xs font-medium text-on-surface-variant">{label}</span>
      <span className="text-xs font-mono text-on-surface truncate max-w-[140px] text-right" title={value}>{value}</span>
    </div>
  );
}
