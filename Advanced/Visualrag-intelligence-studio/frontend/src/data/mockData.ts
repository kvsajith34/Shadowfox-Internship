export const MOCK_DASHBOARD_METRICS = {
  totalFiles: 1284,
  filesGrowth: "+12%",
  queriesHandled: 8432,
  avgFaithfulness: 0.94,
  hallucinations: 3,
};

export const MOCK_RECENT_ANALYSES = [
  { id: '1', filename: 'Q3_Earnings_Report.pdf', type: 'PDF', provider: 'OpenAI', safety: 'Pass' },
  { id: '2', filename: 'Architecture_Diagram.png', type: 'IMG', provider: 'Gemini', safety: 'Pass' },
  { id: '3', filename: 'User_Manual_v2.pdf', type: 'PDF', provider: 'OpenAI', safety: 'Flagged' },
  { id: '4', filename: 'Meeting_Notes.txt', type: 'TXT', provider: 'HF', safety: 'Pass' },
];

export const MOCK_INVOICE_DATA = {
  id: "INV-2023-0042.pdf",
  dueDate: "Oct 28, 2023",
  dueDays: 2,
  vendorName: "Acme Corporation Ltd.",
  vendorConf: "99%",
  invoiceDate: "2023-10-15",
  invoiceDateConf: "98%",
  taxAmount: "$125.50",
  taxConf: "85%",
  totalAmount: "$1,380.50",
  totalConf: "99%",
  lineItems: [
    { id: 1, desc: "Enterprise Server Rack", qty: 2, price: "$450.00", total: "$900.00", conf: "high" },
    { id: 2, desc: "Network Switch", qty: 1, price: "$355.00", total: "$355.00", conf: "low" },
    { id: 3, desc: "Installation Service Fee", qty: 1, price: "$125.50", total: "$125.50", conf: "high" },
  ]
};

export const MOCK_RAG_LOGS = [
  { id: "#Q-8902", model: "GPT-4-Turbo", query: "Summarize the Q3 revenue findings compared to Q2.", faithfulnessScore: 0.98, relevanceScore: 0.92, verdict: "Pass" },
  { id: "#Q-8901", model: "Llama-3-70b", query: "What are the main bottlenecks shown in this diagram?", faithfulnessScore: 0.76, relevanceScore: 0.85, verdict: "Investigate" },
  { id: "#Q-8900", model: "Claude-3-Opus", query: "Can you list the total tax amount from the invoice?", faithfulnessScore: 0.94, relevanceScore: 0.96, verdict: "Pass" },
  { id: "#Q-8899", model: "Mistral-Large", query: "What is the retention rate for Mar 2023 at Month 2?", faithfulnessScore: 0.45, relevanceScore: 0.55, verdict: "Fail" },
];
