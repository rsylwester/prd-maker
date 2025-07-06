"""PRD generation logic."""

from typing import Optional
from .llm_manager import LLMManager


class PRDGenerator:
    """Generates Product Requirements Documents using AI models."""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
    
    def generate_prd(self, 
                    product_name: str,
                    product_description: str,
                    target_audience: str,
                    key_features: list[str],
                    success_metrics: Optional[list[str]] = None,
                    **kwargs) -> str:
        """Generate a complete PRD based on input parameters."""
        
        prompt = self._build_prd_prompt(
            product_name=product_name,
            product_description=product_description,
            target_audience=target_audience,
            key_features=key_features,
            success_metrics=success_metrics or [],
            **kwargs
        )
        
        return self.llm_manager.generate_prd(prompt)
    
    def _build_prd_prompt(self, 
                         product_name: str,
                         product_description: str,
                         target_audience: str,
                         key_features: list[str],
                         success_metrics: list[str],
                         **kwargs) -> str:
        """Build the PRD generation prompt."""
        
        features_text = "\n".join([f"- {feature}" for feature in key_features])
        metrics_text = "\n".join([f"- {metric}" for metric in success_metrics]) if success_metrics else "To be defined"
        
        prompt = f"""
Create a comprehensive Product Requirements Document (PRD) for the following product:

**Product Name:** {product_name}

**Product Description:** {product_description}

**Target Audience:** {target_audience}

**Key Features:**
{features_text}

**Success Metrics:**
{metrics_text}

Please structure the PRD with the following sections:
1. Executive Summary
2. Product Overview
3. Target Audience & User Personas
4. Problem Statement
5. Solution Overview
6. Functional Requirements
7. Non-Functional Requirements
8. User Stories
9. Success Metrics & KPIs
10. Timeline & Milestones
11. Risk Assessment
12. Appendices

Make sure the PRD is detailed, professional, and actionable.
"""
        
        return prompt