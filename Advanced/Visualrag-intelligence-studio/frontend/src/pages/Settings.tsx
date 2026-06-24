import { useState, useEffect } from "react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import {
  Settings2, Save, Key, Database, Shield, Cpu,
  Loader, CheckCircle, AlertCircle, AlertTriangle, Info, RotateCcw, Terminal, ChevronDown, ChevronUp,
  Wifi, Network
} from "lucide-react";
import {
  getSettings, saveSettings, SettingsData, SaveSettingsPayload, getErrorMessage,
  getCustomBackendSetting, setCustomBackendSetting, testBackendConnection,
} from "../api/client";

// ─── Provider / Model catalogue ───────────────────────────────────────────────

const PROVIDERS = [
  { value: "mock",         label: "Mock (No API Key Required)" },
  { value: "openai",       label: "OpenAI" },
  { value: "gemini",       label: "Google Gemini" },
  { value: "huggingface",  label: "Hugging Face" },
] as const;

const MODELS: Record<string, { value: string; label: string }[]> = {
  mock: [
    { value: "mock-visualrag", label: "mock-visualrag (built-in)" },
  ],
  openai: [
    { value: "gpt-4o-mini",  label: "gpt-4o-mini (fast, cheap)" },
    { value: "gpt-4.1-mini", label: "gpt-4.1-mini" },
    { value: "gpt-4o",       label: "gpt-4o (full)" },
  ],
  gemini: [
    { value: "gemini-1.5-flash", label: "gemini-1.5-flash (fast)" },
    { value: "gemini-1.5-pro",   label: "gemini-1.5-pro (full)" },
    { value: "gemini-2.0-flash", label: "gemini-2.0-flash (latest)" },
  ],
  huggingface: [
    { value: "Qwen/Qwen2.5-VL-3B-Instruct",        label: "Qwen2.5-VL-3B (small)" },
    { value: "Qwen/Qwen2.5-VL-7B-Instruct",        label: "Qwen2.5-VL-7B (medium)" },
    { value: "microsoft/phi-4-multimodal-instruct", label: "Phi-4 Multimodal" },
  ],
};

const DEFAULT_MODEL_FOR: Record<string, string> = {
  mock:         "mock-visualrag",
  openai:       "gpt-4o-mini",
  gemini:       "gemini-1.5-flash",
  huggingface:  "Qwen/Qwen2.5-VL-3B-Instruct",
};

// ─── Initial state ────────────────────────────────────────────────────────────

const INITIAL: SettingsData = {
  selected_provider:     "mock",
  active_provider:       "mock",
  default_provider:      "mock",
  default_model:         "mock-visualrag",
  selected_model:        "mock-visualrag",
  vision_model:          "gemini-1.5-flash",
  chunk_size:            512,
  similarity_threshold:  0.7,
  mock_mode:             true,
  storage_backend:       "local",
  evaluation_sensitivity: 0.5,
  api_key_status:        { openai: false, gemini: false, huggingface: false, anthropic: false },
  fallback_reason:       null,
  debug_safe_config: {
    env_loaded: false,
    mock_mode_raw: "",
    mock_mode_parsed: true,
    openai_key_present: false,
    gemini_key_present: false,
    hf_token_present: false,
  },
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function Settings() {
  const [s, setS] = useState<SettingsData>(INITIAL);
  const [loading, setLoading]   = useState(true);
  const [saving, setSaving]     = useState(false);
  const [resetting, setResetting] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [toast, setToast]       = useState<{ type: 'success' | 'error' | 'warn'; msg: string } | null>(null);

  // ── Custom backend URL (Network Connection) ─────────────────────────────────
  const [useCustomBackend, setUseCustomBackend] = useState(false);
  const [customBackendUrl, setCustomBackendUrl] = useState("");
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionResult, setConnectionResult] = useState<{ ok: boolean; message: string } | null>(null);

  // ── Load on mount ──────────────────────────────────────────────────────────
  useEffect(() => {
    getSettings()
      .then(loaded => setS(loaded))
      .catch(() => { /* keep defaults */ })
      .finally(() => setLoading(false));

    const saved = getCustomBackendSetting();
    setUseCustomBackend(saved.enabled);
    setCustomBackendUrl(saved.url);
  }, []);

  // ── Network connection handlers ──────────────────────────────────────────────
  function handleToggleCustomBackend() {
    const next = !useCustomBackend;
    setUseCustomBackend(next);
    setCustomBackendSetting(next, customBackendUrl);
    setConnectionResult(null);
  }

  function handleCustomBackendUrlChange(url: string) {
    setCustomBackendUrl(url);
    setCustomBackendSetting(useCustomBackend, url);
    setConnectionResult(null);
  }

  async function handleTestConnection() {
    setTestingConnection(true);
    setConnectionResult(null);
    try {
      const result = await testBackendConnection(customBackendUrl);
      setConnectionResult(result);
    } finally {
      setTestingConnection(false);
    }
  }

  // ── Provider change — auto-pick a sensible default model ──────────────────
  function handleProviderChange(provider: string) {
    const defaultModel = DEFAULT_MODEL_FOR[provider] || "mock-visualrag";
    setS(prev => ({
      ...prev,
      selected_provider: provider,
      default_provider:  provider,
      default_model:     defaultModel,
      selected_model:    defaultModel,
      // Toggling to mock implicitly turns mock_mode on; toggling away keeps
      // mock_mode as-is (user can flip the toggle separately).
      mock_mode: provider === "mock" ? true : prev.mock_mode,
    }));
  }

  // ── Save ──────────────────────────────────────────────────────────────────
  async function handleSave() {
    setSaving(true);
    const payload: SaveSettingsPayload = {
      default_provider:      s.selected_provider,
      default_model:         s.default_model,
      vision_model:          s.vision_model,
      chunk_size:            s.chunk_size,
      similarity_threshold:  s.similarity_threshold,
      mock_mode:             s.mock_mode,
      storage_backend:       s.storage_backend,
      evaluation_sensitivity: s.evaluation_sensitivity,
    };
    try {
      const saved = await saveSettings(payload);
      setS(saved);
      if (saved.fallback_reason) {
        setToast({ type: 'warn', msg: saved.fallback_reason });
      } else {
        setToast({ type: 'success', msg: `Settings saved — active provider: ${saved.active_provider}` });
      }
    } catch (err) {
      setToast({ type: 'error', msg: getErrorMessage(err) });
    } finally {
      setSaving(false);
      setTimeout(() => setToast(null), 6000);
    }
  }

  // ── Reset to .env defaults ──────────────────────────────────────────────────
  async function handleReset() {
    setResetting(true);
    try {
      const saved = await saveSettings({ reset_to_env: true });
      setS(saved);
      setToast({ type: 'success', msg: `Reset to .env defaults — provider: ${saved.selected_provider}, mock mode: ${saved.mock_mode ? 'on' : 'off'}` });
    } catch (err) {
      setToast({ type: 'error', msg: getErrorMessage(err) });
    } finally {
      setResetting(false);
      setTimeout(() => setToast(null), 6000);
    }
  }

  // ── Derived values ────────────────────────────────────────────────────────
  const modelOptions    = MODELS[s.selected_provider] ?? MODELS.mock;
  const selectedChanged = s.selected_provider !== s.active_provider;
  const keyStatus       = s.api_key_status ?? {};

  return (
    <div className="flex flex-col gap-8 animate-in fade-in duration-500 max-w-4xl mx-auto w-full pb-10">

      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border shadow-xl text-sm font-medium max-w-[420px]
          ${toast.type === 'success' ? 'bg-tertiary/10 text-tertiary border-tertiary/30'
          : toast.type === 'warn'    ? 'bg-secondary/10 text-secondary border-secondary/30'
          :                            'bg-error/10 text-error border-error/30'}`}>
          {toast.type === 'success' ? <CheckCircle size={16} />
          : toast.type === 'warn'   ? <AlertTriangle size={16} />
          :                           <AlertCircle size={16} />}
          <span>{toast.msg}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex flex-col">
          <h2 className="text-3xl font-bold text-on-surface flex items-center gap-2">
            <Settings2 className="text-primary" size={28} /> System Settings
          </h2>
          <p className="text-on-surface-variant mt-1">
            Configure global platform models and security defaults.
            {loading && <span className="ml-2 text-xs animate-pulse">Loading...</span>}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Button variant="ghost" onClick={handleReset} disabled={resetting || loading} title="Reset provider settings to backend/.env defaults">
            {resetting ? <Loader size={16} className="animate-spin" /> : <RotateCcw size={16} />}
            Reset to .env
          </Button>
          <Button onClick={handleSave} disabled={saving || loading}>
            {saving ? <Loader size={18} className="animate-spin" /> : <Save size={18} />}
            {saving ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </div>

      {/* Selected / Active / Key Status — exact, unambiguous labels */}
      {!loading && (
        <Card className="p-4 grid grid-cols-1 sm:grid-cols-3 gap-4 border-outline-variant/20">
          <div className="flex flex-col gap-1">
            <span className="text-[11px] uppercase tracking-wider text-on-surface-variant">Selected Provider</span>
            <span className="text-sm font-semibold text-on-surface capitalize">{s.selected_provider}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[11px] uppercase tracking-wider text-on-surface-variant">Active Runtime Provider</span>
            <span className={`text-sm font-semibold capitalize ${selectedChanged ? 'text-secondary' : 'text-tertiary'}`}>
              {s.active_provider}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[11px] uppercase tracking-wider text-on-surface-variant">API Key Status</span>
            <span className={`text-sm font-semibold ${s.selected_provider === 'mock' || keyStatus[s.selected_provider] ? 'text-tertiary' : 'text-error'}`}>
              {s.selected_provider === 'mock' ? 'Not required' : keyStatus[s.selected_provider] ? 'Configured' : 'Missing'}
            </span>
          </div>
        </Card>
      )}

      {/* Missing key / mock-runtime explanation — compact info banner, not an error */}
      {!loading && s.fallback_reason && (
        <div className="flex items-start gap-3 px-4 py-3 rounded-lg border border-outline-variant/30 bg-surface-container/60 text-sm text-on-surface-variant">
          <Info size={15} className="shrink-0 mt-0.5 text-outline" />
          <span>{s.fallback_reason}</span>
        </div>
      )}

      {/* Help text — always visible */}
      <div className="flex items-start gap-2 px-4 py-3 rounded-lg border border-outline-variant/20 bg-surface-container/40 text-xs text-on-surface-variant">
        <Info size={13} className="shrink-0 mt-0.5 text-outline" />
        <span>
          To use real OpenAI/Gemini/Hugging Face responses, add the provider API key to <code className="font-mono bg-surface-variant px-1 rounded">backend/.env</code>,
          set <code className="font-mono bg-surface-variant px-1 rounded">MOCK_MODE=false</code>, and restart the backend.
          Mock mode is the safe default and works without any API keys. Use <strong>Reset to .env</strong> any time to clear a saved override.
        </span>
      </div>

      <div className="space-y-6">

        {/* ── Model Configuration ─────────────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-2 mb-3">
            <Cpu size={18} className="text-outline" />
            <h3 className="text-sm font-semibold text-on-surface uppercase tracking-wider">Model Configuration</h3>
          </div>
          <Card className="flex flex-col gap-5 p-6 border-outline-variant/20">

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Provider dropdown */}
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-on-surface-variant">AI Provider</label>
                <select
                  value={s.selected_provider}
                  onChange={e => handleProviderChange(e.target.value)}
                  className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary"
                >
                  {PROVIDERS.map(p => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
                {s.selected_provider !== "mock" && !keyStatus[s.selected_provider] && (
                  <p className="text-xs text-secondary flex items-center gap-1">
                    <AlertTriangle size={11} /> No API key — set in backend/.env, then restart.
                  </p>
                )}
              </div>

              {/* Model dropdown — options change per provider */}
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-on-surface-variant">Model</label>
                <select
                  value={s.default_model}
                  onChange={e => setS(prev => ({ ...prev, default_model: e.target.value }))}
                  className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary"
                >
                  {modelOptions.map(m => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Vision model */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-on-surface-variant">Vision / Multimodal Model</label>
              <select
                value={s.vision_model}
                onChange={e => setS(prev => ({ ...prev, vision_model: e.target.value }))}
                className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary max-w-sm"
              >
                <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                <option value="gemini-1.5-pro">gemini-1.5-pro</option>
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4o-mini">gpt-4o-mini</option>
              </select>
            </div>

            <div className="h-px bg-outline-variant/10" />

            {/* API Key reminder */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-on-surface-variant flex items-center gap-2">
                <Key size={14} className="text-outline" /> API Keys
                <span className="text-[10px] bg-secondary/10 text-secondary border border-secondary/20 px-1.5 rounded">Server-side only</span>
              </label>
              <div className="relative">
                <input type="password" value="Set in backend/.env — never exposed to browser" readOnly
                  className="w-full bg-surface-container-highest border border-outline-variant/20 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none font-mono opacity-60" />
              </div>
            </div>

            {/* Mock Mode toggle */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-surface-container/50 border border-outline-variant/20">
              <div>
                <h4 className="text-sm font-medium text-on-surface">Mock Mode</h4>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  Override all providers with built-in mock responses (no API keys needed).
                  {s.selected_provider !== "mock" && !s.mock_mode && (
                    <span className="ml-1 text-secondary">
                      Turn on to test without API keys.
                    </span>
                  )}
                </p>
              </div>
              <button
                onClick={() => setS(prev => ({ ...prev, mock_mode: !prev.mock_mode }))}
                className={`w-10 h-5 rounded-full relative transition-colors shrink-0 ${s.mock_mode ? 'bg-tertiary' : 'bg-surface-container-highest border border-outline-variant/20'}`}>
                <div className={`absolute top-[2px] w-4 h-4 bg-white rounded-full transition-all ${s.mock_mode ? 'right-[2px]' : 'left-[1px]'}`} />
              </button>
            </div>
          </Card>
        </section>

        {/* ── Provider Status Cards ───────────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-2 mb-3">
            <Key size={18} className="text-outline" />
            <h3 className="text-sm font-semibold text-on-surface uppercase tracking-wider">Provider API Key Status</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <ProviderCard name="Mock"         id="mock"         active={s.active_provider === "mock"}         selected={s.selected_provider === "mock"} hasKey={true}                      />
            <ProviderCard name="OpenAI"       id="openai"       active={s.active_provider === "openai"}       selected={s.selected_provider === "openai"} hasKey={keyStatus.openai ?? false}     />
            <ProviderCard name="Gemini"       id="gemini"       active={s.active_provider === "gemini"}       selected={s.selected_provider === "gemini"} hasKey={keyStatus.gemini ?? false}     />
            <ProviderCard name="Hugging Face" id="huggingface"  active={s.active_provider === "huggingface"}  selected={s.selected_provider === "huggingface"} hasKey={keyStatus.huggingface ?? false} />
          </div>
        </section>

        {/* ── Network Connection (custom backend URL) ─────────────────────── */}
        <section>
          <div className="flex items-center gap-2 mb-3 mt-2">
            <Network size={18} className="text-outline" />
            <h3 className="text-sm font-semibold text-on-surface uppercase tracking-wider">Network Connection</h3>
          </div>
          <Card className="flex flex-col gap-4 p-6 border-outline-variant/20">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-on-surface">Use Custom Backend URL</h4>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  Point this app at a backend on a different host — e.g. <code className="font-mono bg-surface-variant px-1 rounded">http://10.155.121.181:8000</code> or
                  a deployed backend URL. Takes effect immediately, no rebuild needed.
                </p>
              </div>
              <button
                onClick={handleToggleCustomBackend}
                className={`w-10 h-5 rounded-full relative transition-colors shrink-0 ${useCustomBackend ? 'bg-tertiary' : 'bg-surface-container-highest border border-outline-variant/20'}`}>
                <div className={`absolute top-[2px] w-4 h-4 bg-white rounded-full transition-all ${useCustomBackend ? 'right-[2px]' : 'left-[1px]'}`} />
              </button>
            </div>

            {useCustomBackend && (
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-on-surface-variant">Backend URL</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customBackendUrl}
                    onChange={e => handleCustomBackendUrlChange(e.target.value)}
                    placeholder="http://10.155.121.181:8000"
                    className="flex-1 bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                  <Button variant="secondary" onClick={handleTestConnection} disabled={testingConnection || !customBackendUrl}>
                    {testingConnection ? <Loader size={16} className="animate-spin" /> : <Wifi size={16} />}
                    Test Connection
                  </Button>
                </div>
                {connectionResult && (
                  <div className={`flex items-center gap-2 text-xs px-3 py-2 rounded-lg border
                    ${connectionResult.ok ? 'bg-tertiary/10 text-tertiary border-tertiary/20' : 'bg-error/10 text-error border-error/20'}`}>
                    {connectionResult.ok ? <CheckCircle size={13} /> : <AlertCircle size={13} />}
                    {connectionResult.message}
                  </div>
                )}
                <p className="text-[11px] text-outline mt-1">
                  Saved to this browser only. Backend must be started with <code className="font-mono bg-surface-variant px-1 rounded">--host 0.0.0.0</code> for
                  other devices to reach it, and its CORS settings must allow this page's origin.
                </p>
              </div>
            )}
          </Card>
        </section>

        {/* ── Vector DB & Retrieval ───────────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-2 mb-3 mt-2">
            <Database size={18} className="text-outline" />
            <h3 className="text-sm font-semibold text-on-surface uppercase tracking-wider">Vector DB & Retrieval</h3>
          </div>
          <Card className="grid grid-cols-1 sm:grid-cols-2 gap-6 p-6 border-outline-variant/20">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-on-surface-variant">Chunk Size (Tokens)</label>
              <input
                type="number"
                value={s.chunk_size}
                onChange={e => setS(prev => ({ ...prev, chunk_size: parseInt(e.target.value) || 512 }))}
                className="bg-surface-container border border-outline-variant/30 rounded-md py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary font-mono"
              />
              <p className="text-xs text-outline mt-1">Controls the granularity of document segmentation.</p>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-on-surface-variant">
                Similarity Threshold: <span className="font-mono text-primary">{s.similarity_threshold.toFixed(2)}</span>
              </label>
              <div className="flex items-center gap-3 mt-1">
                <input
                  type="range" min="0" max="100"
                  value={Math.round(s.similarity_threshold * 100)}
                  onChange={e => setS(prev => ({ ...prev, similarity_threshold: parseInt(e.target.value) / 100 }))}
                  className="w-full accent-primary"
                />
                <span className="font-mono text-sm text-on-surface-variant w-10">{s.similarity_threshold.toFixed(2)}</span>
              </div>
            </div>
          </Card>
        </section>

        {/* ── Security ────────────────────────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-2 mb-3 mt-2">
            <Shield size={18} className="text-outline" />
            <h3 className="text-sm font-semibold text-on-surface uppercase tracking-wider">Security & Permissions</h3>
          </div>
          <Card className="flex flex-col gap-4 p-6 border-error/20 bg-error/5">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-on-surface">Strict PII Redaction</h4>
                <p className="text-xs text-on-surface-variant mt-1">Automatically mask SSNs, credit cards, and addresses before generation.</p>
              </div>
              <div className="w-10 h-5 bg-tertiary rounded-full relative cursor-pointer shadow-inner shrink-0">
                <div className="absolute top-[2px] right-[2px] w-4 h-4 bg-white rounded-full" />
              </div>
            </div>
            <div className="h-px bg-outline-variant/10" />
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-on-surface">Allow External File URLs</h4>
                <p className="text-xs text-on-surface-variant mt-1">Permit users to analyze files from arbitrary public URLs.</p>
              </div>
              <div className="w-10 h-5 bg-surface-container-highest rounded-full relative cursor-pointer shadow-inner border border-outline-variant/20 shrink-0">
                <div className="absolute top-[1px] left-[1px] w-4 h-4 bg-outline rounded-full" />
              </div>
            </div>
          </Card>
        </section>

        {/* ── Debug Info (safe — booleans only, never shows key values) ──── */}
        <section>
          <button
            onClick={() => setShowDebug(v => !v)}
            className="flex items-center gap-2 mb-3 text-sm font-semibold text-on-surface-variant uppercase tracking-wider hover:text-on-surface transition-colors"
          >
            <Terminal size={16} className="text-outline" />
            Debug Info
            {showDebug ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {showDebug && (
            <Card className="p-4 border-outline-variant/20 font-mono text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-on-surface-variant">
                <DebugRow label="env_loaded" value={String(s.debug_safe_config.env_loaded)} />
                <DebugRow label="mock_mode_raw" value={s.debug_safe_config.mock_mode_raw} />
                <DebugRow label="mock_mode_parsed" value={String(s.debug_safe_config.mock_mode_parsed)} />
                <DebugRow label="openai_key_present" value={String(s.debug_safe_config.openai_key_present)} />
                <DebugRow label="gemini_key_present" value={String(s.debug_safe_config.gemini_key_present)} />
                <DebugRow label="hf_token_present" value={String(s.debug_safe_config.hf_token_present)} />
              </div>
              <p className="text-[10px] text-outline mt-3 normal-case font-sans">
                Booleans only — actual API key values are never sent to the browser.
                Full snapshot also available at <code className="bg-surface-variant px-1 rounded">GET /api/v1/provider-debug</code>.
              </p>
            </Card>
          )}
        </section>

      </div>
    </div>
  );
}

function DebugRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-2 px-2 py-1 rounded bg-surface-container/50">
      <span className="text-outline">{label}</span>
      <span className="text-on-surface">{value}</span>
    </div>
  );
}

// ─── Provider Status Card ─────────────────────────────────────────────────────

function ProviderCard({
  name, id, active, selected, hasKey
}: {
  name: string; id: string; active: boolean; selected: boolean; hasKey: boolean;
}) {
  const isAlwaysAvailable = id === "mock";
  const available = isAlwaysAvailable || hasKey;

  return (
    <div className={`flex flex-col gap-2 p-3 rounded-lg border transition-colors
      ${active   ? 'border-tertiary/40 bg-tertiary/5'
      : selected ? 'border-primary/30 bg-primary/5'
      :            'border-outline-variant/20 bg-surface-container/30'}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-on-surface">{name}</span>
        <span className={`w-2 h-2 rounded-full ${available ? 'bg-tertiary' : 'bg-error'}`} />
      </div>
      <div className="flex flex-col gap-1">
        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border w-fit
          ${available ? 'text-tertiary border-tertiary/20 bg-tertiary/10' : 'text-error border-error/20 bg-error/10'}`}>
          {isAlwaysAvailable ? "always available" : available ? "key configured" : "missing key"}
        </span>
        {active && (
          <span className="text-[10px] font-mono text-primary border border-primary/20 bg-primary/10 px-1.5 py-0.5 rounded w-fit">
            ▶ active
          </span>
        )}
        {selected && !active && (
          <span className="text-[10px] font-mono text-secondary border border-secondary/20 bg-secondary/10 px-1.5 py-0.5 rounded w-fit">
            selected
          </span>
        )}
      </div>
    </div>
  );
}
