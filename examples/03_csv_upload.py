"""
Example 03: Pandas CSV Upload
-----------------------------
The fastest way to upload historical data. Load a CSV into a Pandas
DataFrame, map your columns, and the SDK handles the rest.
"""

import pandas as pd
from research.client import ResearchClient

API_KEY = "YOUR_API_KEY_HERE"


def main():
    # 1. Create a dummy DataFrame (in reality, you'd use pd.read_csv("results.csv"))
    data = {
        "Agents": [32, 64, 128],
        "Creation Time (ms)": [8.16, 5.69, 4.74],
        "Peak Mem (MB)": [64.91, 72.50, 87.69],
    }
    df = pd.DataFrame(data)
    print("Loaded DataFrame:")
    print(df.head())
    print("\nPreparing upload...")

    with ResearchClient(api_key=API_KEY) as client:
        # Fetch dynamic mapping so we don't hardcode metric IDs
        db_metrics = client.get_metric_mapping_by_name()

        result = client.create_experiment_from_dataframe(
            name="Historical Data Ingestion",
            description="Uploading old CSV results via Pandas.",
            df=df,
            # Map CSV columns -> Exact Database Metric Names
            metric_mapping={
                "Creation Time (ms)": db_metrics["Agent creation time (t_create)"],
                "Peak Mem (MB)": db_metrics["Memory consumption"],
            },
            # Fix CSV column names to match the API requirements
            column_mapping={"Agents": "number_of_agents"},
            # Apply these constant values to EVERY row in the CSV
            constant_params={
                "platform_name": "jade",
                "workload": "inform",
                "number_of_repetitions": 10,
                "number_of_containers": 1,
                "message_size": 1024,
                "group_size": 0,
                "ram": 8192.0,
                "vcpu": "8",
            },
        )
        print(f"Success! Uploaded Data as Experiment ID: {result['experiment_id']}")


if __name__ == "__main__":
    main()
