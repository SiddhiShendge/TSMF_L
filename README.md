# Thane Weather Forecast

A simple Streamlit app based on `mini_project_tsmf.ipynb` and the included weather CSV.

## Run

On Windows, double-click `setup.bat` once, then `star.bat`. Keep the launcher window open while using the app. Setup creates a project-local `.venv` and checks that the analysis libraries load.

Or run manually:

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt
.\.venv311\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed in the terminal (normally http://localhost:8501).

The app shows monthly weather charts, additive seasonal decomposition, and SARIMAX test predictions with MAE, RMSE, prediction intervals, and a downloadable CSV. Use the sidebar to reserve 3–12 months for testing; the default is the notebook's 12-month split.

It follows the notebook's March 2023–September 2026 monthly averages and SARIMAX (1,1,1) × (1,1,1,12) specification. Evaluation uses observed test-period humidity and wind speed. These are historical test predictions; future forecasting requires future exogenous inputs. Fitting warnings are displayed because the short series can yield unstable estimates.

## Public hosting

GitHub stores the source code. To run the Python app publicly, connect the repository to [Streamlit Community Cloud](https://share.streamlit.io/). Create an app, select the repository and branch, and use `app.py` as the entrypoint. Choose Python 3.11 in the advanced settings. The included CSV and `requirements.txt` must be in the repository root. See the [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

Do not upload `.venv` or secrets. Windows Application Control errors require administrator approval of the affected Python installation or library.
