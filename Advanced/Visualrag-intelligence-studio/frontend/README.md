# VisualRAG Intelligence Studio

## Overview
VisualRAG Intelligence Studio is an advanced multimodal AI dashboard frontend designed for processing images, PDFs, charts, invoices, to power RAG-based document Q&A and evaluation labs. This project forms the foundation of a sophisticated AI system, implementing a clean, responsive, dashboard-style interface. 

**Note**: This is a pure Frontend UI implementation based on designed screenshots. It serves as the foundation for a future full-stack architecture.

## Features
- **Dashboard Overview**: Metrics overview, recent analyses table, evaluation quality trends, and provider status.
- **Data Ingestion & Pipeline**: A comprehensive Upload & Analyze zone with queue tracking and active file details.
- **Visual Chat**: Contextual multimodal chat interface alongside visual evidence and cropping parameters.
- **PDF RAG Chat**: Interactive document Q&A featuring grounded snippets, confidence scores, and retrieved source chunks.
- **Invoice Extractor**: Specialized UI displaying bounding boxes overlays, header data extraction, and structured line items.
- **Chart Analyzer**: Data visualization interpreter with AI anomaly detection and insights.
- **Evaluation Lab**: Log monitoring with hallucination tracking and answer relevance scoring.
- **Pipeline Reports**: Compliance summaries and dataset performance metrics.
- **Settings**: System-level configurations mapping to API keys and models.

## Tech Stack
- React
- Vite
- Tailwind CSS
- TypeScript
- React Router (react-router-dom)
- Recharts (for Dashboard & Reports)
- Lucide React (for UI Icons)
- clsx / tailwind-merge

## Folder Structure
```text
├── src/
│   ├── api/
│   │   └── client.ts          # Centralized Axios client & mock API functions
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.tsx     # App wrapping layout
│   │   │   ├── Sidebar.tsx    # Left navigation
│   │   │   └── Topbar.tsx     # Mobile Top header
│   │   └── ui/
│   │       ├── Button.tsx     # Reusable buttons
│   │       ├── Card.tsx       # Reusable cards / panels
│   │       └── MetricCard.tsx # Dashboard metric cards
│   ├── data/
│   │   └── mockData.ts        # Sample realistic data payload for previews
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── UploadAnalyze.tsx
│   │   ├── VisualChat.tsx
│   │   ├── PdfRagChat.tsx
│   │   ├── InvoiceExtractor.tsx
│   │   ├── ChartAnalyzer.tsx
│   │   ├── EvaluationLab.tsx
│   │   ├── Reports.tsx
│   │   └── Settings.tsx
│   ├── App.tsx                # Client Routing logic
│   ├── index.css              # Custom font and tailwind imports
│   ├── main.tsx               # Entry Point
│   └── utils.ts               # cn() utility for css combining
```

## Setup & Run

### Install Dependencies
```bash
npm install
```

### Run Locally (Dev Server)
```bash
npm run dev
```
By default, the Vite server will run and display a localhost port you can access.

### Creating a Production Build
```bash
npm run build
```

## Backend Integration Note
The UI is currently running offline using decoupled mock data. Look at `/src/api/client.ts` to see predefined endpoints that can be mapped easily to a future FastAPI, Next.js, Noir, or Express application.

## Future Backend Endpoints
Based on the `client.ts` configuration, the following backend endpoints are expected:
- `GET /api/v1/health`
- `POST /api/v1/upload`
- `POST /api/v1/visual-chat`
- `POST /api/v1/pdf-rag-query`
- `POST /api/v1/extract-invoice`
- `POST /api/v1/analyze-chart`
- `POST /api/v1/evaluate`
- `GET /api/v1/metrics`
- `GET /api/v1/history`
- `GET /api/v1/reports`
- `POST /api/v1/settings`

## Screenshots Placeholder
*(Include your finalized screenshot previews here)*
