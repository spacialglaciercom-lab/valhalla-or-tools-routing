# Data Drift Sentinel

A Streamlit application for monitoring data drift between baseline and current datasets using Population Stability Index (PSI) and other statistical measures.

🔗 **Repository**: [https://github.com/spacialglaciercom-lab/data-drift-sentinel](https://github.com/spacialglaciercom-lab/data-drift-sentinel)

## Features

- **Deterministic Statistics Report**: Comprehensive statistical comparison between baseline and current datasets
- **PSI Calculation**: Population Stability Index for measuring data drift
- **Severity Thresholds**: Configurable thresholds for drift severity classification
- **Pydantic Models**: Structured, serializable `DriftReport` model with schema validation
- **Optional Metrics**: KS test p-values and Jensen-Shannon divergence
- **Optional LLM Summary**: AI-powered summary grounded in computed JSON facts (optional feature)

## Project Structure

```
data-drift-sentinel/
├── src/
│   ├── __init__.py
│   ├── compute_drift.py       # Main compute_drift function
│   ├── models.py              # Pydantic models for DriftReport
│   ├── config.py              # Configuration management
│   ├── psi_calculator.py      # PSI calculation implementation
│   ├── statistics.py          # Statistical measures and comparisons
│   ├── metrics.py             # Additional metrics (KS test, JS divergence)
│   ├── report_builder.py      # Build DriftReport from detection results
│   ├── llm_summary.py         # Optional LLM-based summary generation
│   ├── drift_detector.py      # Legacy DriftDetector class
│   └── utils.py               # Utility functions
├── app/
│   ├── __init__.py
│   ├── main.py                # Streamlit main application
│   ├── components.py          # UI components
│   └── utils.py               # Streamlit utilities
├── pages/
│   ├── 1_📤_Upload.py
│   ├── 2_🔍_Schema_Quality.py
│   ├── 3_📊_Drift_Report.py
│   ├── 4_🤖_LLM_Summary.py
│   └── 5_💾_Export.py
├── tests/
│   ├── __init__.py
│   ├── test_psi_synthetic.py
│   ├── test_severity_mapping.py
│   └── test_schema_diff.py
├── .streamlit/
│   └── secrets.toml.example
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### LLM API Key (Optional)

For LLM summary generation, configure your API key using one of these methods:

**Recommended: Streamlit Secrets**
1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Add your API key: `LLM_API_KEY = "your-api-key-here"`
3. Restart Streamlit

**Alternative: Environment Variable**
- Set `OPENAI_API_KEY` or `LLM_API_KEY` environment variable
- Or use `.env` file (copy `.env.example` to `.env` and add your key)

The app will automatically detect the API key and enable LLM summary features. If no API key is found, you'll see: "LLM summary disabled — add API key to Streamlit secrets."

## Usage

Run the Streamlit multipage application:

```bash
streamlit run app/main.py
```

The app will automatically detect the `pages/` directory and create a navigation menu with:
- **📤 Upload** - Upload baseline and current datasets
- **🔍 Schema & Quality** - View schema differences and configure drift detection
- **📊 Drift Report** - Compute and visualize drift with interactive charts
- **🤖 LLM Summary** - Generate AI-powered summaries (optional)
- **💾 Export** - Export results as JSON or CSV

## Testing

```bash
pytest tests/
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to GitHub.

Quick start:
```bash
git init
git add .
git commit -m "Initial commit: Data Drift Sentinel"
# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/data-drift-sentinel.git
git branch -M main
git push -u origin main
```

## compute_drift Function

The main `compute_drift` function provides comprehensive drift detection:

```python
from src.compute_drift import compute_drift
from src.config import DriftConfig, SeverityThresholds

# With default config
report = compute_drift(baseline_df, current_df)

# With custom config
config = DriftConfig(
    bins=15,
    min_bins=5,
    max_categories=10,
    include_ks=True,
    include_js=True,
    binning_method="adaptive"
)

thresholds = SeverityThresholds(
    low_threshold=0.1,
    medium_threshold=0.25,
    high_threshold=0.5
)

report = compute_drift(baseline_df, current_df, config, thresholds)
```

**Features:**
- **Numeric columns**: PSI (with robust binning), KS test p-value, JS divergence, missing delta, summary stats deltas
- **Categorical columns**: PSI using top K categories + 'other' bucket, JS divergence, missing delta
- **Robust binning**: Adapts to small sample sizes
- **Schema diff**: Detects added/removed columns and type changes

## DriftReport Model

The `DriftReport` Pydantic model provides a structured, serializable JSON output with:

- **Dataset Metadata**: Row/column counts, common columns
- **Schema Diff**: Added/removed columns, type changes
- **Per-Column Metrics**: PSI, missing delta, severity, optional KS p-value and JS divergence, summary stats deltas
- **Top Changed Columns**: List of columns with highest drift, sorted by PSI

Example usage:

```python
from src.compute_drift import compute_drift
import pandas as pd

# Load your data
baseline_df = pd.read_csv('baseline.csv')
current_df = pd.read_csv('current.csv')

# Compute drift
report = compute_drift(baseline_df, current_df)

# Serialize to JSON (stable, deterministic)
json_output = report.model_dump_json()

# Access structured data
print(report.dataset_metadata.baseline_rows)
print(report.per_column_metrics['age'].psi)
print(report.top_changed_columns[0].column_name)
```

## License

See LICENSE file for details.
