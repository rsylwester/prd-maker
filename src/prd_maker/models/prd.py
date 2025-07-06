"""PRD document data models."""

from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class UserStory(BaseModel):
    """Individual user story model."""
    
    id: str = Field(..., description="Unique identifier (e.g., US-001)")
    title: str = Field(..., description="User story title")
    description: str = Field(..., description="As a... I want... so that...")
    acceptance_criteria: List[str] = Field(default_factory=list)
    priority: str = Field(default="medium", description="Priority level")
    
    def to_markdown(self) -> str:
        """Convert user story to markdown format."""
        md = f"### {self.id}: {self.title}\n"
        md += f"**Tytuł**: {self.title}  \n"
        md += f"**Opis**: {self.description}  \n"
        md += "**Kryteria akceptacji**:\n"
        for criterion in self.acceptance_criteria:
            md += f"- {criterion}\n"
        md += "\n"
        return md


class PRDDocument(BaseModel):
    """Complete PRD document model."""
    
    # Document metadata
    title: str = Field(..., description="Document title")
    version: str = Field(default="1.0", description="Document version")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # PRD sections
    product_overview: str = Field(default="", description="Product overview section")
    user_problem: str = Field(default="", description="User problem description")
    functional_requirements: str = Field(default="", description="Functional requirements")
    product_boundaries: str = Field(default="", description="Product scope and boundaries")
    user_stories: List[UserStory] = Field(default_factory=list)
    success_metrics: str = Field(default="", description="Success metrics section")
    
    # Additional sections
    technical_considerations: str = Field(default="", description="Technical notes")
    assumptions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert PRD document to markdown format."""
        md = f"# {self.title}\n\n"
        md += f"**Wersja**: {self.version}  \n"
        md += f"**Data utworzenia**: {self.created_at.strftime('%Y-%m-%d')}  \n"
        md += f"**Ostatnia aktualizacja**: {self.updated_at.strftime('%Y-%m-%d')}  \n\n"
        
        md += "## 1. Przegląd produktu\n\n"
        md += f"{self.product_overview}\n\n"
        
        md += "## 2. Problem użytkownika\n\n"
        md += f"{self.user_problem}\n\n"
        
        md += "## 3. Wymagania funkcjonalne\n\n"
        md += f"{self.functional_requirements}\n\n"
        
        md += "## 4. Granice produktu\n\n"
        md += f"{self.product_boundaries}\n\n"
        
        md += "## 5. Historyjki użytkowników\n\n"
        for user_story in self.user_stories:
            md += user_story.to_markdown()
        
        md += "## 6. Metryki sukcesu\n\n"
        md += f"{self.success_metrics}\n\n"
        
        if self.technical_considerations:
            md += "## 7. Uwagi techniczne\n\n"
            md += f"{self.technical_considerations}\n\n"
        
        if self.assumptions:
            md += "## 8. Założenia\n\n"
            for assumption in self.assumptions:
                md += f"- {assumption}\n"
            md += "\n"
        
        if self.constraints:
            md += "## 9. Ograniczenia\n\n"
            for constraint in self.constraints:
                md += f"- {constraint}\n"
            md += "\n"
        
        return md
    
    def validate_completeness(self) -> Dict[str, bool]:
        """Validate if all required sections are filled."""
        return {
            "product_overview": bool(self.product_overview.strip()),
            "user_problem": bool(self.user_problem.strip()),
            "functional_requirements": bool(self.functional_requirements.strip()),
            "product_boundaries": bool(self.product_boundaries.strip()),
            "user_stories": len(self.user_stories) > 0,
            "success_metrics": bool(self.success_metrics.strip()),
        }
    
    def get_completion_score(self) -> float:
        """Get completion score as percentage."""
        validation = self.validate_completeness()
        completed = sum(validation.values())
        total = len(validation)
        return (completed / total) * 100