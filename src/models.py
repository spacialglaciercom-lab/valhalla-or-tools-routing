"""Pydantic models for structured drift reports."""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Severity levels for drift detection."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DatasetMetadata(BaseModel):
    """Metadata about the baseline and current datasets."""
    baseline_rows: int = Field(..., description="Number of rows in baseline dataset")
    current_rows: int = Field(..., description="Number of rows in current dataset")
    baseline_columns: int = Field(..., description="Number of columns in baseline dataset")
    current_columns: int = Field(..., description="Number of columns in current dataset")
    common_columns: List[str] = Field(..., description="List of columns present in both datasets")


class SchemaDiff(BaseModel):
    """Schema differences between baseline and current datasets."""
    added_columns: List[str] = Field(default_factory=list, description="Columns added in current dataset")
    removed_columns: List[str] = Field(default_factory=list, description="Columns removed from baseline dataset")
    type_changes: Dict[str, str] = Field(default_factory=dict, description="Dictionary mapping column names to type change descriptions")


class ColumnMetrics(BaseModel):
    """Metrics for a single column."""
    column_name: str = Field(..., description="Name of the column")
    data_type: str = Field(..., description="Data type of the column")
    psi: float = Field(..., description="Population Stability Index")
    severity: SeverityLevel = Field(..., description="Severity level of drift")
    missing_delta: Optional[float] = Field(None, description="Change in missing value percentage")
    ks_pvalue: Optional[float] = Field(None, description="Kolmogorov-Smirnov test p-value")
    js_divergence: Optional[float] = Field(None, description="Jensen-Shannon divergence")
    
    # Statistics deltas for numeric columns
    mean_delta: Optional[float] = Field(None, description="Change in mean value")
    median_delta: Optional[float] = Field(None, description="Change in median value")
    std_delta: Optional[float] = Field(None, description="Change in standard deviation")


class TopChangedColumn(BaseModel):
    """Information about a top changed column."""
    column_name: str = Field(..., description="Name of the column")
    psi: float = Field(..., description="PSI value")
    severity: SeverityLevel = Field(..., description="Severity level")


class DriftReport(BaseModel):
    """Complete drift detection report."""
    dataset_metadata: DatasetMetadata = Field(..., description="Metadata about the datasets")
    schema_diff: SchemaDiff = Field(..., description="Schema differences")
    per_column_metrics: Dict[str, ColumnMetrics] = Field(..., description="Metrics for each column")
    top_changed_columns: List[TopChangedColumn] = Field(default_factory=list, description="Top changed columns sorted by PSI")
    summary: Dict[str, any] = Field(default_factory=dict, description="Summary statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_metadata": {
                    "baseline_rows": 1000,
                    "current_rows": 1000,
                    "baseline_columns": 10,
                    "current_columns": 10,
                    "common_columns": ["col1", "col2"]
                },
                "schema_diff": {
                    "added_columns": [],
                    "removed_columns": [],
                    "type_changes": {}
                },
                "per_column_metrics": {},
                "top_changed_columns": [],
                "summary": {}
            }
        }


class LLMSummaryOutput(BaseModel):
    """Structured output for LLM-generated summary."""
    executive_summary: str = Field(..., description="A concise executive summary of the drift report.")
    key_risks: List[str] = Field(..., description="List of key risks identified from the drift report.")
    recommended_actions: List[str] = Field(..., description="List of recommended actions based on the drift report.")
    top_issues: List[str] = Field(..., description="List of top 5 issues, formatted as 'column_name - Severity (PSI: value)'.")

