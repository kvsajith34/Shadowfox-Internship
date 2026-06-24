import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import UploadAnalyze from "./pages/UploadAnalyze";
import VisualChat from "./pages/VisualChat";
import PdfRagChat from "./pages/PdfRagChat";
import InvoiceExtractor from "./pages/InvoiceExtractor";
import ChartAnalyzer from "./pages/ChartAnalyzer";
import EvaluationLab from "./pages/EvaluationLab";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="upload" element={<UploadAnalyze />} />
          <Route path="visual-chat" element={<VisualChat />} />
          <Route path="pdf-rag-chat" element={<PdfRagChat />} />
          <Route path="invoice-extractor" element={<InvoiceExtractor />} />
          <Route path="chart-analyzer" element={<ChartAnalyzer />} />
          <Route path="evaluation-lab" element={<EvaluationLab />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
