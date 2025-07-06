"""Project data models."""

from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectStep(str, Enum):
    """Sequential steps in the PRD creation process."""
    PROJECT_IDEA = "project_idea"
    PROJECT_DESCRIPTION = "project_description"
    PLANNING_SESSION = "planning_session"
    ANSWER_QUESTIONS = "answer_questions"
    PLANNING_SUMMARY = "planning_summary"
    PRD_DOCUMENT = "prd_document"
    TECH_STACK_ANALYSIS = "tech_stack_analysis"


class Project(BaseModel):
    """Main project model containing all data for PRD generation."""
    
    # Basic project info
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(default="", description="Project name")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Process tracking
    current_step: ProjectStep = Field(default=ProjectStep.PROJECT_IDEA)
    completed_steps: List[ProjectStep] = Field(default_factory=list)
    
    # AI configuration
    ai_model: str = Field(default="gpt-4", description="Selected AI model")
    
    # Step data
    project_idea: str = Field(default="", description="Initial project idea")
    project_description: str = Field(default="", description="Generated project description")
    planning_questions: List[Dict[str, str]] = Field(default_factory=list)
    planning_answers: List[Dict[str, Any]] = Field(default_factory=list)
    planning_summary: str = Field(default="", description="Summary of planning session")
    prd_document: str = Field(default="", description="Generated PRD document")
    tech_stack_proposal: str = Field(default="", description="Proposed tech stack")
    tech_stack_analysis: str = Field(default="", description="Tech stack analysis and recommendations")
    
    # Additional metadata
    export_formats: List[str] = Field(default_factory=list)
    is_template: bool = Field(default=False)
    
    def advance_step(self) -> bool:
        """Advance to the next step if current step is complete."""
        steps = list(ProjectStep)
        current_index = steps.index(self.current_step)
        
        if current_index < len(steps) - 1:
            self.completed_steps.append(self.current_step)
            self.current_step = steps[current_index + 1]
            self.updated_at = datetime.now()
            return True
        return False
    
    def can_access_step(self, step: ProjectStep) -> bool:
        """Check if a step can be accessed based on completion."""
        steps = list(ProjectStep)
        step_index = steps.index(step)
        current_index = steps.index(self.current_step)
        
        # Can access current step or any completed step
        return step_index <= current_index or step in self.completed_steps
    
    def is_step_complete(self, step: ProjectStep) -> bool:
        """Check if a specific step is complete."""
        return step in self.completed_steps
    
    def get_progress_percentage(self) -> float:
        """Get completion percentage."""
        total_steps = len(ProjectStep)
        completed_count = len(self.completed_steps)
        return (completed_count / total_steps) * 100