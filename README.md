# MASRP SDK

**Python API wrapper for the Multi-Agent Systems Research Platform (MASRP)**

This SDK provides a clean, pythonic interface for researchers to authenticate and programmatically upload their experiment results to the MASRP database. It includes built-in Pydantic validation, dynamic metric mapping, and native Pandas DataFrame ingestion.

---

## 📦 Installation

Since this package is distributed via Git, you can install or update it directly using `pip`:

```bash
pip install git+https://github.com/jmizera1/MASRP_python_api.git
```

> **Note:** To upgrade to the latest version later, run:
> `pip install --upgrade git+https://github.com/jmizera1/MASRP_python_api.git@main`

---

## 🚀 Quickstart: The Pandas Ingestion

The easiest way to upload an experiment is to load your results from a CSV into a Pandas DataFrame and let the SDK handle the rest.

```python
import pandas as pd
from research import ResearchClient

# 1. Load your results
df = pd.read_csv("jade_inform_results.csv")

# 2. Connect to the platform using your API key
API_KEY = "your_api_key_here"

with ResearchClient(api_key=API_KEY) as client:

    # 3. Dynamically fetch the database metric IDs so you don't have to hardcode them
    db_metrics = client.get_metric_mapping_by_name()

    # 4. Upload the DataFrame!
    result = client.create_experiment_from_dataframe(
        name="JADE Inform Workload Benchmark",
        description="Scaling test from 32 to 2048 agents.",
        df=df,

        # Map your CSV column names to the exact database metric names
        metric_mapping={
            "Mean agent creation time": db_metrics["Agent creation time (t_create)"],
            "p95 CPU": db_metrics["CPU utilization (U_cpu)"],
            "Platform Readiness time": db_metrics["Platform readiness time (t_ready)"]
        },

        # Fix base column names if your CSV doesn't match the database requirements
        column_mapping={
            "No of agents": "number_of_agents"
        },

        # Apply constant values to every row in this specific CSV
        constant_params={
            "platform_name": "jade",
            "workload": "inform",
            "number_of_repetitions": 10,
            "number_of_containers": 1,
            "message_size": 1024,
            "group_size": 0,
            "ram": 4096.0,
            "vcpu": "4"
        }
    )

    print(f"✅ Successfully uploaded! Experiment ID: {result['experiment_id']}")
```

---

## 📖 Advanced Usage

### 1. Fetching Available Metrics
It is highly recommended to fetch metric mappings dynamically rather than hardcoding IDs (which could change if the database is reset).

```python
with ResearchClient(api_key="YOUR_API_KEY") as client:
    # Returns a dictionary: {"Exact DB Name": Database_ID}
    mapping = client.get_metric_mapping_by_name()

    print("Available metrics:")
    for name, m_id in mapping.items():
        print(f" - {name} (ID: {m_id})")
```

### 2. Manual Pydantic Uploads (For Scripts & Loops)
If you are running live simulations in Python and want to build the payload incrementally, you can use the built-in Pydantic models for strict local validation.

```python
from research import ResearchClient
from research import ExperimentPayload, ResultRow, MetricValue

rows = []

# Example loop running your actual simulations
for agents in [32, 64, 128]:
    # ... run your simulation here ...

    # Construct a validated row
    row = ResultRow(
        platform_name="spade",
        workload="inform",
        number_of_agents=agents,
        number_of_repetitions=5,
        number_of_containers=1,
        message_size=512,
        group_size=0,
        ram=2048.0,
        vcpu="2",
        metrics=[
            MetricValue(metric_id=1, value=8.16),  # Creation time
            MetricValue(metric_id=11, value=1.58)  # CPU util
        ]
    )
    rows.append(row)

# Construct the final payload
payload = ExperimentPayload(
    name="Live Simulation Data",
    description="Uploading rows incrementally",
    selected_metric_ids=[1, 11],
    rows=rows
)

# Send to the backend
with ResearchClient(api_key="YOUR_API_KEY") as client:
    response = client.create_full_experiment(payload)
    print(f"Experiment created: {response['experiment_id']}")
```

---

## ⚠️ Error Handling

The SDK provides a custom `APIError` exception that cleanly catches HTTP errors and displays the specific validation message from the FastAPI backend.

```python
from research import APIError

try:
    client.create_full_experiment(bad_payload)
except APIError as e:
    print(f"Upload failed. Status: {e.status_code}")
    print(f"Details: {e.detail}")
```

---
*Developed by Jan Mizera, Adam Kurdybelski, & Błażej Michalak for the MAS Research Platform.*
