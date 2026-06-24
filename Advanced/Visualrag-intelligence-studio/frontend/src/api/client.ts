/**
 * VisualRAG Intelligence Studio — API Client
 * Single source of truth for all backend communication.
 *
 * Base URL strategy (resolved fresh on EVERY request, no rebuild needed):
 *   1. Runtime custom backend URL — set via Settings → Network Connection,
 *      persisted in localStorage. Use this to point the frontend at a
 *      backend on a different host/IP (e.g. http://10.155.121.181:8000)
 *      without rebuilding or even reloading the app.
 *   2. VITE_API_BASE_URL — build-time env var for deployed frontends
 *      (e.g. https://your-backend.onrender.com).
 *   3. Empty string '' — relative URLs, handled by the Vite dev-server
 *      proxy to http://localhost:8000. This is the default local mode:
 *      any device on the LAN can open the Vite network URL
 *      (e.g. http://192.168.x.x:5173) and uploads work because the
 *      browser talks to the Vite server, not directly to :8000.
 *
 * All endpoints return: { success, message, data, mock_mode, provider, timestamp }
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// ─── Custom Backend URL (runtime override, persisted in localStorage) ─────────

const CUSTOM_BACKEND_ENABLED_KEY = 'visualrag:useCustomBackendUrl';
const CUSTOM_BACKEND_URL_KEY = 'visualrag:customBackendUrl';

export interface CustomBackendSetting {
  enabled: boolean;
  url: string;
}

export function getCustomBackendSetting(): CustomBackendSetting {
  try {
    const enabled = localStorage.getItem(CUSTOM_BACKEND_ENABLED_KEY) === 'true';
    const url = localStorage.getItem(CUSTOM_BACKEND_URL_KEY) || '';
    return { enabled, url };
  } catch {
    // localStorage unavailable (private browsing, SSR, etc.) — safe default
    return { enabled: false, url: '' };
  }
}

export function setCustomBackendSetting(enabled: boolean, url: string): void {
  try {
    localStorage.setItem(CUSTOM_BACKEND_ENABLED_KEY, String(enabled));
    localStorage.setItem(CUSTOM_BACKEND_URL_KEY, url.trim().replace(/\/+$/, ''));
  } catch {
    // localStorage unavailable — silently no-op, falls back to other base URL sources
  }
}

/** Resolved fresh on every request: custom URL > VITE_API_BASE_URL > '' (proxy). */
function resolveApiBaseUrl(): string {
  const custom = getCustomBackendSetting();
  if (custom.enabled && custom.url) return custom.url;
  return import.meta.env.VITE_API_BASE_URL || '';
}

/**
 * Test connectivity to a candidate backend URL by calling its health
 * endpoint directly (bypasses the shared axios instance/interceptor so it
 * always tests exactly the URL passed in, not the currently-saved one).
 */
export async function testBackendConnection(url: string): Promise<{ ok: boolean; message: string }> {
  const base = url.trim().replace(/\/+$/, '');
  if (!base) return { ok: false, message: 'Enter a backend URL first.' };
  try {
    const res = await fetch(`${base}/api/v1/health`, { method: 'GET' });
    if (!res.ok) return { ok: false, message: `Backend responded with HTTP ${res.status}.` };
    const body = await res.json();
    if (body?.success) {
      return { ok: true, message: `Connected — ${body?.data?.app_name || 'backend'} is healthy.` };
    }
    return { ok: false, message: 'Backend reachable but health check did not return success.' };
  } catch (err) {
    return { ok: false, message: err instanceof Error ? err.message : 'Could not reach backend.' };
  }
}

// ─── Axios Instance ───────────────────────────────────────────────────────────

const client: AxiosInstance = axios.create({
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

// Resolve the base URL fresh on every outgoing request — this is what makes
// toggling "Use custom backend URL" in Settings take effect immediately,
// with no app rebuild or reload required.
client.interceptors.request.use((config) => {
  config.baseURL = resolveApiBaseUrl();
  return config;
});

// ─── Response Envelope Unwrapper ─────────────────────────────────────────────

interface ApiEnvelope<T = unknown> {
  success: boolean;
  message: string;
  data: T;
  mock_mode: boolean;
  provider: string;
  timestamp: string;
}

function unwrap<T>(envelope: ApiEnvelope<T>): T {
  if (!envelope.success) throw new Error(envelope.message || 'API error');
  return envelope.data;
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function healthCheck() {
  const res = await client.get<ApiEnvelope>('/api/v1/health');
  return res.data; // Return full envelope for health display
}

// ─── Upload ───────────────────────────────────────────────────────────────────

export interface UploadResult {
  file_id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  storage_path: string;
  analysis_type: string;
  status: string;
  summary: string;
  metadata: Record<string, unknown>;
  next_suggested_actions: string[];
}

export async function uploadFile(file: File, analysisType: string = 'general'): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('analysisType', analysisType);
  const res = await client.post<ApiEnvelope<UploadResult>>('/api/v1/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return unwrap(res.data);
}

// ─── Visual Chat ──────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface VisualChatPayload {
  file_id?: string;
  message: string;
  provider?: string;
  history?: ChatMessage[];
}

export interface VisualChatResult {
  answer: string;
  evidence: string[];
  evaluation: Record<string, unknown>;
  confidence_score: number;
  safety_notes: string;
  hallucination_risk: string;
  suggested_followups: string[];
}

export async function sendVisualChatMessage(payload: VisualChatPayload): Promise<VisualChatResult> {
  const body = {
    file_id: payload.file_id || null,
    message: payload.message,
    provider: payload.provider || 'mock',
    history: payload.history || [],
  };
  const res = await client.post<ApiEnvelope<VisualChatResult>>('/api/v1/visual-chat', body);
  return unwrap(res.data);
}

// ─── PDF RAG Query ────────────────────────────────────────────────────────────

export interface RagPayload {
  file_id: string;
  question: string;
  provider?: string;
  use_rag?: boolean;
}

export interface RagResult {
  answer: string;
  sources: Array<Record<string, unknown>>;
  retrieved_chunks: Array<Record<string, unknown>>;
  faithfulness_score: number;
  relevance_score: number;
  direct_llm_comparison: string;
  rag_grounded_answer: string;
  hallucination_risk: string;
  // Provider transparency — always present in every backend response
  response_provider: string;
  selected_provider: string;
  fallback_reason: string | null;
  provider_error_type: string | null;
  // Stale-response tracking: echoed from the request envelope
  request_id?: string;
}

export async function askPdfRagQuestion(
  payload: RagPayload,
  clientRequestId?: string,
): Promise<RagResult> {
  const body = {
    file_id: payload.file_id,
    question: payload.question,
    provider: payload.provider || 'mock',
    use_rag: payload.use_rag !== undefined ? payload.use_rag : true,
  };
  const res = await client.post<ApiEnvelope<RagResult>>('/api/v1/pdf-rag-query', body);
  const data = unwrap(res.data);
  // Attach the server-side request_id from the envelope (or the client-side
  // id if the server doesn't echo one) so the page can detect stale responses.
  data.request_id = (res.data as any).request_id ?? clientRequestId;
  return data;
}

// ─── Invoice Extraction ───────────────────────────────────────────────────────

export interface InvoiceLineItem {
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface InvoiceResult {
  vendor_name: string;
  customer_name: string;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  currency: string;
  payment_status: string;
  line_items: InvoiceLineItem[];
  missing_fields: string[];
  confidence_score: number;
  safety_note: string;
  raw_extracted_text: string;
}

export async function extractInvoice(file: File): Promise<InvoiceResult> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await client.post<ApiEnvelope<InvoiceResult>>('/api/v1/extract-invoice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return unwrap(res.data);
}

// ─── Chart Analysis ───────────────────────────────────────────────────────────

export interface ChartResult {
  chart_type: string;
  title: string;
  main_trend: string;
  highest_value: string;
  lowest_value: string;
  key_insights: string[];
  possible_limitations: string[];
  data_table: Array<Record<string, unknown>>;
  confidence_score: number;
  answer: string;
  evaluation: Record<string, unknown>;
}

export async function analyzeChart(file: File, question?: string): Promise<ChartResult> {
  const formData = new FormData();
  formData.append('file', file);
  if (question) formData.append('question', question);
  const res = await client.post<ApiEnvelope<ChartResult>>('/api/v1/analyze-chart', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return unwrap(res.data);
}

// ─── Evaluation ───────────────────────────────────────────────────────────────

export interface EvaluationPayload {
  question: string;
  answer: string;
  evidence?: string[];
  task_type?: string;
  provider?: string;
}

export interface EvaluationResult {
  relevance_score: number;
  faithfulness_score: number;
  completeness_score: number;
  safety_score: number;
  hallucination_risk: string;
  missing_evidence: string[];
  risk_explanation: string;
  improvement_suggestions: string[];
}

export async function evaluateAnswer(payload: EvaluationPayload): Promise<EvaluationResult> {
  const body = {
    question: payload.question,
    answer: payload.answer,
    evidence: payload.evidence || [],
    task_type: payload.task_type || 'visual_chat',
    provider: payload.provider || 'mock',
  };
  const res = await client.post<ApiEnvelope<EvaluationResult>>('/api/v1/evaluate', body);
  return unwrap(res.data);
}

// ─── Metrics ──────────────────────────────────────────────────────────────────

export interface MetricsResult {
  totalFiles: number;
  filesGrowth: number;
  queriesHandled: number;
  avgFaithfulness: number;
  hallucinations: number;
  providerStatus: Record<string, string>;
  evaluationTrend: number[];
  ragPerformance: Record<string, number>;
  safetyAudit: Record<string, number>;
}

export async function getMetrics(): Promise<MetricsResult> {
  const res = await client.get<ApiEnvelope<MetricsResult>>('/api/v1/metrics');
  return unwrap(res.data);
}

// ─── History ──────────────────────────────────────────────────────────────────

export interface HistoryItem {
  id: string;
  filename: string;
  type: string;
  provider: string;
  safety: string;
  created_at: string;
  task_type: string;
  summary: string;
}

export async function getHistory(): Promise<HistoryItem[]> {
  const res = await client.get<ApiEnvelope<HistoryItem[]>>('/api/v1/history');
  return unwrap(res.data);
}

// ─── Reports ──────────────────────────────────────────────────────────────────

export interface ReportsResult {
  summary?: Record<string, unknown>;
  quality_report?: Record<string, unknown>;
  safety_audit?: Record<string, unknown>;
  [key: string]: unknown;
}

export async function getReports(): Promise<ReportsResult> {
  const res = await client.get<ApiEnvelope<ReportsResult>>('/api/v1/reports');
  return unwrap(res.data);
}

// ─── Settings ─────────────────────────────────────────────────────────────────

export interface DebugSafeConfig {
  env_loaded: boolean;
  mock_mode_raw: string;
  mock_mode_parsed: boolean;
  openai_key_present: boolean;
  gemini_key_present: boolean;
  hf_token_present: boolean;
}

export interface SettingsData {
  // What the user selected in the UI (persisted to DB)
  selected_provider: string;
  // What is actually running (may be 'mock' if key is missing)
  active_provider: string;
  // Backward-compat alias for selected_provider
  default_provider: string;
  default_model: string;
  selected_model: string;
  vision_model: string;
  chunk_size: number;
  similarity_threshold: number;
  mock_mode: boolean;
  storage_backend: string;
  evaluation_sensitivity: number;
  // true = key is configured in backend/.env for that provider
  api_key_status: Record<string, boolean>;
  // Short reason when active_provider != selected_provider
  fallback_reason: string | null;
  // Booleans only — never contains actual key values
  debug_safe_config: DebugSafeConfig;
}

export interface SaveSettingsPayload {
  default_provider?: string;
  default_model?: string;
  vision_model?: string;
  chunk_size?: number;
  similarity_threshold?: number;
  mock_mode?: boolean;
  storage_backend?: string;
  evaluation_sensitivity?: number;
  // When true, ignores all other fields and resets to backend/.env defaults
  reset_to_env?: boolean;
}

export interface ProviderDebugData {
  env_loaded: boolean;
  mock_mode_raw: string;
  mock_mode_parsed: boolean;
  default_provider: string;
  selected_provider: string;
  active_provider: string;
  selected_model: string;
  api_key_status: Record<string, boolean>;
  fallback_reason: string | null;
  provider_service_available: Record<string, boolean>;
}

export async function getSettings(): Promise<SettingsData> {
  const res = await client.get<ApiEnvelope<SettingsData>>('/api/v1/settings');
  return unwrap(res.data);
}

export async function saveSettings(payload: SaveSettingsPayload): Promise<SettingsData> {
  const res = await client.post<ApiEnvelope<SettingsData>>('/api/v1/settings', payload);
  return unwrap(res.data);
}

export async function getProviderDebug(): Promise<ProviderDebugData> {
  const res = await client.get<ApiEnvelope<ProviderDebugData>>('/api/v1/provider-debug');
  return unwrap(res.data);
}

// ─── Error Helper ─────────────────────────────────────────────────────────────

export function getErrorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    return err.response?.data?.message || err.message || 'Network error';
  }
  if (err instanceof Error) return err.message;
  return 'Unknown error';
}

export default client;
