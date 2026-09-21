import json
import math
from datetime import datetime, timezone
from pathlib import Path
import tempfile

import pandas as pd
import plotly
import plotly.io as pio
from plotly.offline import get_plotlyjs_version

import data_loader
from analysis import calculate_sentiment
from charts import (
    build_overall_chart,
    build_spy_chart,
    build_vix_chart,
    build_safe_haven_chart,
    build_growth_value_chart,
    analyze_standardized_correlation,
    plot_recovery_boxplot,
    plot_multi_horizon_performance,
)

ROOT = Path(__file__).resolve().parent


def validate_prices(frame, name, required_columns):
    """Reject empty downloads, missing prices, and malformed date indexes."""
    if frame is None or frame.empty:
        raise ValueError(f"{name}: downloaded no data; previous export retained.")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError(f"{name}: expected a DatetimeIndex.")
    if frame.index.hasnans or not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise ValueError(f"{name}: dates must be valid, unique, and sorted.")
    flat = frame.copy()
    if isinstance(flat.columns, pd.MultiIndex):
        flat.columns = flat.columns.get_level_values(0)
    for column in required_columns:
        if column not in flat.columns:
            raise ValueError(f"{name}: missing {column}.")
        series = flat[column]
        if not isinstance(series, pd.Series):
            raise ValueError(f"{name}: ambiguous column {column}.")
        value = float(series.iloc[-1])
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name}: latest {column} price is invalid.")


def score_summary(frame, score_column, label_column):
    row = frame.iloc[-1]
    score = float(row[score_column])
    if not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError(f"Invalid latest score: {score_column}.")
    return {
        "score": score,
        "label": str(row[label_column]),
        "market_data_date": frame.index[-1].date().isoformat(),
    }


def build_dashboard(output_dir=None):
    output_dir = Path(output_dir) if output_dir is not None else ROOT / "site" / "data"
    spy = data_loader.get_spy_data()
    vix = data_loader.get_vix_data()
    safe_haven = data_loader.get_sh_data()
    growth_value = data_loader.get_gv_data()

    raw = {
        "spy": spy,
        "vix": vix,
        "safe_haven": safe_haven,
        "growth_value": growth_value,
    }

    for name, columns in {
        "spy": ["Close"], "vix": ["Close"],
        "safe_haven": ["SPY", "IEF"],
        "growth_value": ["SPY", "IVW", "IVE"],
    }.items():
        validate_prices(raw[name], name, columns)
        
    common_dates = raw["spy"].index
    
    for name in ("vix", "safe_haven", "growth_value"):
        common_dates = common_dates.intersection(raw[name].index)
    
    if common_dates.empty:
        raise ValueError("The downloaded datasets have no shared market date.")
    
    latest_common_date = common_dates.max()
    
    raw = {
        name: frame.loc[frame.index <= latest_common_date].copy()
        for name, frame in raw.items()
    }

    results = calculate_sentiment(
        raw["spy"], raw["vix"], raw["safe_haven"], raw["growth_value"]
    )
    combined = results["combined"]
    
    latest_components = combined.iloc[-1][
        ["spy_score", "vix_score", "sh_score", "gv_score"]
    ]
    if not all(
        math.isfinite(float(v)) and 0 <= float(v) <= 100
        for v in latest_components
    ):
        columns = ["spy_score", "vix_score", "sh_score", "gv_score"]
    
        details = combined[columns].tail(5).to_string()
    
        source_dates = "\n".join(
            f"{name}: {frame.index[-1]}"
            for name, frame in raw.items()
        )
    
        raise ValueError(
            "Latest aggregate lacks four valid indicator scores.\n\n"
            f"Last five rows:\n{details}\n\n"
            f"Latest downloaded dates:\n{source_dates}"
        )

    summary = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "plotly_python_version": plotly.__version__,
        "plotly_js_version": get_plotlyjs_version(),
        "overall": score_summary(combined, "overall_average_sentiment", "overall_label"),
        "indicators": {
            "spy": score_summary(results["spy"], "Score", "Sentiment"),
            "vix": score_summary(results["vix"], "Calculated_Score", "Sentiment"),
            "safe_haven": score_summary(results["safe_haven"], "Score", "Sentiment"),
            "growth_value": score_summary(results["growth_value"], "Score", "Sentiment"),
        },
        "charts": {},
    }
    figures = {
        "overall": build_overall_chart(combined),
        "spy": build_spy_chart(results["spy"]),
        "vix": build_vix_chart(results["vix"]),
        "safe_haven": build_safe_haven_chart(results["safe_haven"]),
        "growth_value": build_growth_value_chart(results["growth_value"]),
        "correlation": analyze_standardized_correlation(combined, results["spy"]),
        "recovery": plot_recovery_boxplot(combined),
        "forward_returns": plot_multi_horizon_performance(combined, results["spy"]),
    }

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".dashboard-build-", dir=output_dir.parent) as temp:
        stage = Path(temp) / "data"
        stage.mkdir()
        for name, fig in figures.items():
            if fig is None:
                # The recovery function returns None if no completed events exist.
                if name != "recovery":
                    raise ValueError(f"Missing chart: {name}")
                summary["charts"][name] = {
                    "file": None, "status": "unavailable",
                    "reason": "No completed extreme-fear recovery events.",
                }
                continue
            filename = f"{name}.json"
            pio.write_json(fig, stage / filename, validate=True)
            summary["charts"][name] = {"file": filename, "status": "ready"}
        (stage / "summary.json").write_text(
            json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        backup = Path(temp) / "previous-data"
        if output_dir.exists():
            output_dir.rename(backup)
        try:
            stage.rename(output_dir)
        except Exception:
            if backup.exists():
                backup.rename(output_dir)
            raise
    print(f"Export complete: {output_dir.resolve()}")
    return summary

if __name__ == "__main__":
    build_dashboard()
