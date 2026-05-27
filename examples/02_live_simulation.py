"""
Example 02: Live Simulation Upload
----------------------------------
How to build an experiment payload incrementally inside a Python script,
perfect for when you are actively running simulations in a for-loop.
"""

from research.client import ResearchClient
from research.models import ExperimentPayload, ResultRow, MetricValue

API_KEY = "YOUR_API_KEY_HERE"


def main():
    rows = []

    print("Running simulations...")

    # Imagine this loop is running your actual MAS framework (JADE, SPADE, etc.)
    for agent_count in [32, 64, 128]:
        print(f" - Simulating {agent_count} agents...")

        # ... your simulation logic happens here ...
        # mock_creation_time = run_sim()

        # 1. Build a validated row for this simulation run
        row = ResultRow(
            platform_name="spade",
            workload="inform",
            number_of_agents=agent_count,
            number_of_repetitions=5,
            number_of_containers=1,
            message_size=1024,
            group_size=0,
            ram=2048.0,
            vcpu="2",
            metrics=[
                MetricValue(metric_id=1, value=4.5),  # Agent creation time
                MetricValue(metric_id=11, value=2.14),  # CPU util
            ],
        )
        rows.append(row)

    # 2. Package all rows into a single experiment payload
    payload = ExperimentPayload(
        name="SPADE Scaling Test",
        description="Live simulation results testing 32 to 128 agents.",
        selected_metric_ids=[1, 11],
        rows=rows,
    )

    # 3. Upload to the platform
    print("\nUploading to database...")
    with ResearchClient(api_key=API_KEY) as client:
        result = client.create_full_experiment(payload)
        print(f"Success! Experiment created with ID: {result['experiment_id']}")


if __name__ == "__main__":
    main()
