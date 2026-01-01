"""Main compute_drift function that orchestrates drift detection."""

import pandas as pd
import numpy as np
from typing import Dict, Optional

from .models import DriftReport, DatasetMetadata, SchemaDiff, ColumnMetrics, TopChangedColumn, SeverityLevel
from .config import DriftConfig, SeverityThresholds
from .psi_calculator import calculate_psi, calculate_psi_categorical
from .statistics import generate_statistics_report
from .metrics import calculate_schema_diff, calculate_missing_delta, calculate_ks_test, calculate_js_divergence


def _map_severity(psi: float, thresholds: SeverityThresholds) -> SeverityLevel:
    """Map PSI value to severity level."""
    if pd.isna(psi) or psi < thresholds.low_threshold:
        return SeverityLevel.NONE
    elif psi < thresholds.medium_threshold:
        return SeverityLevel.LOW
    elif psi < thresholds.high_threshold:
        return SeverityLevel.MEDIUM
    else:
        return SeverityLevel.HIGH


def _calculate_psi_categorical_top_k(baseline: pd.Series, current: pd.Series, 
                                      max_categories: int = 20) -> float:
    """Calculate PSI for categorical data using top-k categories."""
    return calculate_psi_categorical(baseline, current, max_categories)


def _robust_binning(baseline: pd.Series, current: pd.Series, 
                    target_bins: int, min_bins: int) -> int:
    """Determine robust binning strategy based on data characteristics."""
    n_samples = min(len(baseline.dropna()), len(current.dropna()))
    unique_values = len(pd.concat([baseline.dropna(), current.dropna()]).unique())
    
    if unique_values < target_bins:
        bins = max(min_bins, unique_values - 1)
    else:
        bins = min(target_bins, max(min_bins, n_samples // 10))
    
    return max(min_bins, bins)


def _calculate_summary_stats_deltas(baseline: pd.Series, current: pd.Series) -> Dict[str, Optional[float]]:
    """Calculate deltas in summary statistics for numeric columns."""
    if not (pd.api.types.is_numeric_dtype(baseline) and pd.api.types.is_numeric_dtype(current)):
        return {'mean_delta': None, 'median_delta': None, 'std_delta': None}
    
    baseline_clean = baseline.dropna()
    current_clean = current.dropna()
    
    if len(baseline_clean) == 0 or len(current_clean) == 0:
        return {'mean_delta': None, 'median_delta': None, 'std_delta': None}
    
    mean_delta = float(current_clean.mean() - baseline_clean.mean())
    median_delta = float(current_clean.median() - baseline_clean.median())
    std_delta = float(current_clean.std() - baseline_clean.std())
    
    return {
        'mean_delta': mean_delta,
        'median_delta': median_delta,
        'std_delta': std_delta
    }


def compute_drift(
    baseline_df: pd.DataFrame,
    current_df: pd.DataFrame,
    config: Optional[DriftConfig] = None,
    severity_thresholds: Optional[SeverityThresholds] = None
) -> DriftReport:
    """
    Compute drift between baseline and current datasets.
    
    Args:
        baseline_df: Baseline dataset
        current_df: Current dataset
        config: Drift detection configuration
        severity_thresholds: Severity threshold configuration
    
    Returns:
        DriftReport Pydantic model
    """
    if config is None:
        config = DriftConfig()
    if severity_thresholds is None:
        severity_thresholds = SeverityThresholds()
    
    # Generate statistics report
    stats_report = generate_statistics_report(baseline_df, current_df)
    
    # Calculate schema diff
    schema_diff_data = calculate_schema_diff(baseline_df, current_df)
    schema_diff = SchemaDiff(
        added_columns=schema_diff_data['added_columns'],
        removed_columns=schema_diff_data['removed_columns'],
        type_changes={k: f"{v['baseline']} -> {v['current']}" for k, v in schema_diff_data['type_changes'].items()}
    )
    
    # Dataset metadata
    common_columns = sorted(set(baseline_df.columns) & set(current_df.columns))
    dataset_metadata = DatasetMetadata(
        baseline_rows=len(baseline_df),
        current_rows=len(current_df),
        baseline_columns=len(baseline_df.columns),
        current_columns=len(current_df.columns),
        common_columns=common_columns
    )
    
    # Per-column metrics
    per_column_metrics = {}
    
    for col in common_columns:
        baseline_series = baseline_df[col]
        current_series = current_df[col]
        
        # Determine data type
        is_numeric = pd.api.types.is_numeric_dtype(baseline_series)
        data_type = str(baseline_series.dtype)
        
        # Calculate PSI
        if is_numeric:
            # Use robust binning for numeric
            bins = _robust_binning(baseline_series, current_series, config.bins, config.min_bins)
            psi = calculate_psi(baseline_series, current_series, bins=bins, 
                               min_bins=config.min_bins, binning_method=config.binning_method)
        else:
            # Categorical PSI
            psi = _calculate_psi_categorical_top_k(baseline_series, current_series, config.max_categories)
        
        # Map severity
        severity = _map_severity(psi, severity_thresholds)
        
        # Calculate missing delta
        missing_delta = calculate_missing_delta(baseline_series, current_series)
        
        # Optional metrics
        ks_pvalue = None
        js_divergence = None
        if config.include_ks and is_numeric:
            ks_pvalue = calculate_ks_test(baseline_series, current_series)
        if config.include_js:
            js_divergence = calculate_js_divergence(baseline_series, current_series, bins=config.bins)
        
        # Summary stats deltas for numeric
        stats_deltas = {}
        if is_numeric:
            stats_deltas = _calculate_summary_stats_deltas(baseline_series, current_series)
        
        # Create column metrics
        column_metrics = ColumnMetrics(
            column_name=col,
            data_type=data_type,
            psi=float(psi) if not pd.isna(psi) else 0.0,
            severity=severity,
            missing_delta=missing_delta,
            ks_pvalue=ks_pvalue,
            js_divergence=js_divergence,
            mean_delta=stats_deltas.get('mean_delta'),
            median_delta=stats_deltas.get('median_delta'),
            std_delta=stats_deltas.get('std_delta')
        )
        
        per_column_metrics[col] = column_metrics
    
    # Top changed columns
    top_changed = sorted(
        [TopChangedColumn(column_name=col, psi=metrics.psi, severity=metrics.severity) 
         for col, metrics in per_column_metrics.items()],
        key=lambda x: x.psi,
        reverse=True
    )[:10]
    
    # Summary statistics
    summary = {
        'total_columns': len(common_columns),
        'columns_with_drift': sum(1 for m in per_column_metrics.values() if m.severity != SeverityLevel.NONE),
        'high_severity_count': sum(1 for m in per_column_metrics.values() if m.severity == SeverityLevel.HIGH),
        'medium_severity_count': sum(1 for m in per_column_metrics.values() if m.severity == SeverityLevel.MEDIUM),
        'low_severity_count': sum(1 for m in per_column_metrics.values() if m.severity == SeverityLevel.LOW)
    }
    
    # Create and return report
    report = DriftReport(
        dataset_metadata=dataset_metadata,
        schema_diff=schema_diff,
        per_column_metrics=per_column_metrics,
        top_changed_columns=top_changed,
        summary=summary
    )
    
    return report

