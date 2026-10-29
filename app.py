"""Streamlit interface for mini_project_tsmf.ipynb."""

from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX


DATA_PATH = Path(__file__).with_name("thane_weather_2022_2026.csv")
COLUMNS = ["temp_c", "humidity_pct", "wind_speed_kmh"]


@st.cache_data
def load_monthly_data():
    daily = pd.read_csv(DATA_PATH, parse_dates=["date"])
    monthly = daily.sort_values("date").set_index("date").resample("MS")[COLUMNS].mean()
    return monthly.loc["2023-03":"2026-09"]


@st.cache_data(show_spinner=False)
def evaluate_model(monthly, test_months):
    train = monthly.iloc[:-test_months]
    test = monthly.iloc[-test_months:]
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model = SARIMAX(
            train["temp_c"],
            exog=train[["humidity_pct", "wind_speed_kmh"]],
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
        ).fit(disp=False)
        prediction = model.get_forecast(
            steps=test_months, exog=test[["humidity_pct", "wind_speed_kmh"]]
        )
    intervals = prediction.conf_int()
    comparison = pd.DataFrame({
        "Actual (°C)": test["temp_c"],
        "Predicted (°C)": np.asarray(prediction.predicted_mean),
        "Lower 95% (°C)": intervals.iloc[:, 0].to_numpy(),
        "Upper 95% (°C)": intervals.iloc[:, 1].to_numpy(),
    }, index=test.index)
    comparison.index.name = "Month"
    errors = comparison["Actual (°C)"] - comparison["Predicted (°C)"]
    messages = list(dict.fromkeys(str(item.message) for item in captured))
    return comparison, float(errors.abs().mean()), float(np.sqrt((errors ** 2).mean())), messages


def main():
    st.set_page_config(page_title="Thane Weather Forecast", page_icon="🌤️", layout="wide")
    st.title("🌤️ Thane Weather Forecast")
    st.write("Explore monthly weather and evaluate a seasonal temperature forecasting model.")

    try:
        monthly = load_monthly_data()
    except (OSError, ValueError, KeyError) as exc:
        st.error(f"Could not load the weather CSV: {exc}")
        st.stop()

    if len(monthly) < 36 or not np.isfinite(monthly.to_numpy()).all():
        st.error("The analysis needs at least 36 consecutive months with temperature, humidity, and wind speed values.")
        st.stop()

    with st.sidebar:
        st.header("Forecast settings")
        test_months = st.slider("Months reserved for testing", 3, min(12, len(monthly) - 24), 12)
        st.caption("The final months are held out to evaluate predictions on unseen temperatures.")
        st.write("**Model:** SARIMAX (1, 1, 1) × (1, 1, 1, 12)")
        st.write("**Inputs:** humidity and wind speed")
        st.caption("Monthly averages · March 2023–September 2026 · supplied Thane dataset")

    a, b, c = st.columns(3)
    a.metric("Months analyzed", len(monthly))
    b.metric("Average temperature", f"{monthly.temp_c.mean():.1f} °C")
    c.metric("Average humidity", f"{monthly.humidity_pct.mean():.1f}%")

    overview, seasonality, forecast = st.tabs(["Weather overview", "Seasonality", "Model evaluation"])
    with overview:
        labels = {"Temperature (°C)": "temp_c", "Humidity (%)": "humidity_pct", "Wind speed (km/h)": "wind_speed_kmh"}
        selected = st.selectbox("Weather measure", list(labels))
        st.line_chart(monthly[[labels[selected]]].rename(columns={labels[selected]: selected}))
        with st.expander("View monthly data"):
            st.dataframe(monthly, use_container_width=True)

    with seasonality:
        st.subheader("Temperature trend and annual seasonality")
        decomposition = seasonal_decompose(monthly.temp_c, model="additive", period=12)
        fig = decomposition.plot()
        fig.set_size_inches(11, 8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Additive decomposition with a 12-month seasonal cycle. Trend and residual gaps at the edges come from the centered moving average.")

    with forecast:
        st.subheader("Actual vs. predicted temperature")
        st.info("This is a historical test. Predictions use the observed humidity and wind speed in the test months, as in the notebook. Future forecasts would require future values for both inputs.")
        try:
            with st.spinner("Fitting the seasonal model…"):
                comparison, mae, rmse, messages = evaluate_model(monthly, test_months)
        except (ValueError, np.linalg.LinAlgError, RuntimeError) as exc:
            st.error(f"The model could not be fitted: {exc}")
            st.stop()
        a, b = st.columns(2)
        a.metric("Mean absolute error", f"{mae:.2f} °C")
        b.metric("Root mean squared error", f"{rmse:.2f} °C")
        st.caption("Lower errors indicate better agreement with the held-out temperatures.")
        if messages:
            st.warning("The model reported fitting warnings. This short monthly series can produce unstable seasonal estimates; interpret the results with care.")
            with st.expander("Model warnings"):
                for message in messages:
                    st.write(message)
        fig, ax = plt.subplots(figsize=(11, 4.5))
        train = monthly.iloc[:-test_months]
        ax.plot(train.index, train.temp_c, label="Training data", color="#64748b")
        ax.plot(comparison.index, comparison["Actual (°C)"], marker="o", label="Actual", color="#0284c7")
        ax.plot(comparison.index, comparison["Predicted (°C)"], marker="o", linestyle="--", label="Predicted", color="#f97316")
        ax.fill_between(comparison.index, comparison["Lower 95% (°C)"], comparison["Upper 95% (°C)"], alpha=0.12, color="#f97316", label="95% prediction interval")
        ax.set(xlabel="Month", ylabel="Temperature (°C)")
        ax.legend()
        ax.grid(alpha=0.2)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.dataframe(comparison.round(2), use_container_width=True)
        st.download_button("Download predictions", comparison.to_csv().encode("utf-8"), "thane_temperature_predictions.csv", "text/csv")


if __name__ == "__main__":
    main()
