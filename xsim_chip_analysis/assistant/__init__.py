"""Evidence-grounded retrieval and optional local Hugging Face tool calling.

Importing this package does not import torch or download a model.
"""

from .agent import InspectionAssistant, InspectionCase
from .knowledge import KnowledgeIndex
from .reports import normalize_report, render_markdown

__all__ = ["InspectionAssistant", "InspectionCase", "KnowledgeIndex",
           "normalize_report", "render_markdown"]
