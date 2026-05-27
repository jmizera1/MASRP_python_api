"""
Example 01: View Available Metrics
----------------------------------
Before uploading data, it's helpful to know what metrics are available
in the database and what their exact names are.
"""

from research.client import ResearchClient

API_KEY = "YOUR_API_KEY_HERE"


def main():
    print("Connecting to the MAS Research Platform...")

    with ResearchClient(api_key=API_KEY) as client:
        # Fetch the mapping of exact names to database IDs
        metrics = client.get_metric_mapping_by_name()

        print("\nAvailable Metrics:")
        print("-" * 30)
        for name, metric_id in metrics.items():
            print(f"ID: {metric_id:2d} | {name}")


if __name__ == "__main__":
    main()
