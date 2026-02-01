from forecasting.sarima_forecast import ForecastConfig, run_pipeline

if __name__ == "__main__":
    cfg = ForecastConfig(
        backtest_horizon=6,
        forecast_horizon=6,
        write_to_postgres=True,  # set False if you only want CSV artifacts
        output_dir="data/processed",
    )

    result = run_pipeline(cfg=cfg)

    print("\nBacktest metrics:")
    print("Baseline:", result["metrics"]["baseline"])
    print("SARIMA:", result["metrics"]["sarima"])
