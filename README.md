# Financial Model - Streamlit App

Interactive financial modeling application for projecting company financials, cap table, and exit scenarios.

## Features

- **P&L Projections**: Revenue, expenses, and profitability forecasts
- **Cash Flow**: Operating, investing, and financing cash flows
- **Balance Sheet**: Assets, liabilities, and equity positions
- **Cap Table**: Equity ownership breakdown by investor
- **Exit Waterfall**: Distribution analysis for exit scenarios
- **Key Metrics**: Rule of 40, revenue per employee, and more

## Deployment to Streamlit Community Cloud

### Prerequisites
- GitHub account
- All project files in a GitHub repository

### Steps to Deploy

1. **Push to GitHub**
   - Create a new repository on GitHub
   - Upload all files from this project
   - Ensure `Python_Financial_Model_Structure.xlsx` is included

2. **Deploy on Streamlit**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Configure:
     - Repository: Your GitHub repository
     - Branch: `main` (or your default branch)
     - Main file path: `streamlit_app_improved.py`
   - Click "Deploy"

3. **Access Your App**
   - You'll receive a URL like: `https://your-app-name.streamlit.app`
   - Share this URL with anyone who needs access
   - The app is read-only for viewers

### Required Files

- `streamlit_app_improved.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `config_assumptions.py` - Model assumptions
- `financial_model.py` - Core financial model
- `pl_projector.py` - P&L projections
- `cf_projector.py` - Cash flow projections
- `bs_projector.py` - Balance sheet projections
- `other_metrics_projector.py` - Additional metrics
- `cap_table.py` - Cap table management
- `exit_waterfall.py` - Exit scenario calculations
- `data_loader.py` - Historical data loader
- `Python_Financial_Model_Structure.xlsx` - Historical data

### Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app_improved.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

The app loads with default assumptions and displays:
- Financial projections (2025-2030)
- Key metrics and visualizations
- Cap table with ownership percentages
- Exit waterfall showing investor returns

All projections are based on the assumptions defined in `config_assumptions.py`.

## Notes for Viewers

- The app is interactive but read-only
- Viewers can navigate between tabs and explore data
- No modifications to underlying assumptions or data are possible
- Each viewer session is independent

## Support

For questions or issues, contact the model administrator.
