# Run Guide (Windows)

## 1. Open project folder
```bat
cd path\to\store-sales-profit-analysis
```

## 2. Create virtual environment
```bat
python -m venv venv
```

## 3. Activate virtual environment
```bat
venv\Scripts\activate
```

## 4. Install requirements
```bat
pip install -r requirements.txt
```

## 5. Add dataset into data folder
Place the file here:
`data\Sample - Superstore.csv`

## 6. Run full analysis pipeline
```bat
python main.py
```

## 7. Run Streamlit dashboard
```bat
streamlit run app/streamlit_app.py
```

## Output locations
- Cleaned data: `outputs\cleaned_data\cleaned_superstore.csv`
- Report: `outputs\reports\final_analysis_report.md`
- Charts: `outputs\charts\*.html`
