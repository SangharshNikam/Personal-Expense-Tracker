# Personal Expense Tracker

A Streamlit app for logging and analyzing daily expenses, backed by a free Supabase (Postgres) database, deployable for free so you can use it from your phone.

## 1. Set up the database (Supabase — free)
1. Go to https://supabase.com and create a free account + new project.
2. In your project, go to the **SQL Editor** and run the contents of `setup.sql` to create the `expenses` table.
3. Go to **Project Settings → API** and copy:
   - `Project URL` → this is `SUPABASE_URL`
   - `anon public` key → this is `SUPABASE_KEY`

## 2. Run locally (optional, to test first)
```bash
pip install -r requirements.txt
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your real Supabase URL and key
streamlit run app.py
```

## 3. Deploy for free (Streamlit Community Cloud)
1. Push this folder to a new GitHub repo (public or private).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, select your repo and `app.py` as the entry point.
4. In **Advanced settings → Secrets**, paste:
   ```
   SUPABASE_URL = "https://your-project-id.supabase.co"
   SUPABASE_KEY = "your-anon-public-key"
   ```
5. Click **Deploy**. You'll get a URL like `https://your-app.streamlit.app`.

## 4. Use it on your phone
1. Open the deployed URL in your phone's browser.
2. Tap the browser menu → **Add to Home Screen**.
3. It now opens like an app, and your data persists in Supabase across sessions and devices.

## App structure
- **Add Expense tab**: category-based entry (Food, Household, Transport, Bills & Utilities, Entertainment, Other), amount, payment method, date, description.
- **Analysis tab**: daily/monthly spend trends, category-wise and payment-method breakdowns, top 5 highest expenses, budget vs. actual tracking.
- **History tab**: full log, filterable by month, with delete support.

## Possible next steps
- Add expense category auto-classification from the description text (XGBoost/NLP).
- Add next-month spend forecasting per category.
- Connect Power BI directly to the Supabase Postgres database for a richer dashboard.
