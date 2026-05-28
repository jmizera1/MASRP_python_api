import httpx
import pandas as pd
from typing import List, Dict, Any, Optional

from .models import ResultRow, MetricValue, ExperimentPayload
from .exceptions import APIError


class ResearchClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=30.0,
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", e.response.text)
            except Exception:
                error_detail = e.response.text
            raise APIError(e.response.status_code, error_detail) from None

    def get_metrics(self) -> List[Dict]:
        response = self._client.get("/metrics")
        return self._handle_response(response)

    def create_full_experiment(self, experiment: ExperimentPayload, is_hidden: bool = True) -> Dict:
        """Post a strictly validated Pydantic experiment payload."""
        # model_dump() converts the Pydantic objects safely into a JSON-ready dict
        experiment.is_hidden = is_hidden
        response = self._client.post("/experiments/full", json=experiment.model_dump())
        return self._handle_response(response)

    def create_experiment_from_dataframe(
        self,
        name: str,
        description: str,
        df: pd.DataFrame,
        metric_mapping: Dict[str, int],
        constant_params: Optional[Dict[str, Any]] = None,
        column_mapping: Optional[Dict[str, str]] = None,
        is_hidden: bool = True,
    ) -> Dict:
        """
        Magically ingest a Pandas DataFrame into the database.

        :param df: The Pandas DataFrame.
        :param metric_mapping: Maps DF column names to Metric IDs (e.g., {"Mean latency": 13})
        :param constant_params: Values applied to EVERY row (e.g., {"platform_name": "JADE"})
        :param column_mapping: Maps DF base columns to expected names (e.g., {"No of agents": "number_of_agents"})
        :param is_hidden: Whether the experiment should be hidden
        """
        constant_params = constant_params or {}
        column_mapping = column_mapping or {}

        # 1. Rename base columns if mapping is provided
        working_df = df.rename(columns=column_mapping)

        # 2. Figure out which metrics we are tracking
        selected_metric_ids = list(metric_mapping.values())

        parsed_rows: List[ResultRow] = []

        # 3. Iterate over the DataFrame efficiently
        for record in working_df.to_dict(orient="records"):
            # Build the base row using constants first, then overriding with DF data
            base_data = {**constant_params}

            # Extract standard fields (ignore missing ones so Pydantic catches it)
            standard_fields = list(ResultRow.model_fields.keys())
            for field in standard_fields:
                if field in record and field != "metrics":
                    base_data[field] = record[field]

            # Extract metrics
            row_metrics = []
            for col_name, metric_id in metric_mapping.items():
                if col_name in record and pd.notna(record[col_name]):
                    row_metrics.append(
                        MetricValue(metric_id=metric_id, value=float(record[col_name]))
                    )

            base_data["metrics"] = row_metrics

            # Validate row via Pydantic and append
            parsed_rows.append(ResultRow(**base_data))

        # 4. Construct final payload and send
        payload = ExperimentPayload(
            name=name,
            description=description,
            selected_metric_ids=selected_metric_ids,
            rows=parsed_rows,
        )

        return self.create_full_experiment(payload, is_hidden=is_hidden)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_metric_mapping_by_name(self) -> Dict[str, int]:
        """
        Fetches all metrics from the database and creates a dictionary
        mapping the exact metric name to its database ID.

        Example return: {"Agent creation time (t_create)": 1, "CPU utilization (U_cpu)": 11}
        """
        metrics = self.get_metrics()

        return {m["name"]: m["metric_id"] for m in metrics}
