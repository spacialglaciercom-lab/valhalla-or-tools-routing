"""Configuration management for drift detection."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DriftConfig:
    """Configuration for drift detection parameters."""
    
    # PSI calculation
    bins: int = 10
    min_bins: int = 5
    max_categories: int = 20
    top_n: int = 10
    
    # Optional metrics
    include_ks: bool = True
    include_js: bool = True
    
    # Binning method
    binning_method: str = "quantile"  # quantile, uniform, or adaptive


@dataclass
class SeverityThresholds:
    """Severity thresholds for drift classification."""
    
    low_threshold: float = 0.1
    medium_threshold: float = 0.25
    high_threshold: float = 0.5


@dataclass
class LLMConfig:
    """Configuration for optional LLM summary feature."""
    
    enabled: bool = False
    provider: str = "openai"  # openai, anthropic, etc.
    model: str = "gpt-4"
    api_key: Optional[str] = None
    temperature: float = 0.0  # Low temperature for deterministic output
    
    def __post_init__(self):
        """Load API key from Streamlit secrets or environment if not provided."""
        if self.enabled and self.api_key is None:
            # Try Streamlit secrets first (recommended)
            try:
                import streamlit as st
                if hasattr(st, 'secrets'):
                    if 'LLM_API_KEY' in st.secrets:
                        self.api_key = st.secrets["LLM_API_KEY"]
                    elif 'OPENAI_API_KEY' in st.secrets:
                        self.api_key = st.secrets["OPENAI_API_KEY"]
            except (ImportError, RuntimeError, AttributeError):
                # Not in Streamlit context, continue to environment variables
                pass
            
            # Fallback to environment variables
            if self.api_key is None:
                self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")

