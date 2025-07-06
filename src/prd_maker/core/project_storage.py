"""Project storage and persistence using browser localStorage."""

import json
import streamlit as st
from typing import Dict, List, Optional
from ..models.project import Project, ProjectStep


class ProjectStorage:
    """Handles project persistence in browser localStorage."""
    
    STORAGE_KEY = "prd_maker_projects"
    CURRENT_PROJECT_KEY = "prd_maker_current_project"
    
    @classmethod
    def save_project(cls, project: Project) -> None:
        """Save a project to localStorage."""
        projects = cls.load_all_projects()
        projects[project.id] = project.model_dump()
        
        # Store in session state (Streamlit's persistent storage)
        st.session_state[cls.STORAGE_KEY] = projects
        
        # Also set as current project
        st.session_state[cls.CURRENT_PROJECT_KEY] = project.id
    
    @classmethod
    def load_project(cls, project_id: str) -> Optional[Project]:
        """Load a specific project from localStorage."""
        projects = cls.load_all_projects()
        if project_id in projects:
            return Project(**projects[project_id])
        return None
    
    @classmethod
    def load_all_projects(cls) -> Dict[str, dict]:
        """Load all projects from localStorage."""
        if cls.STORAGE_KEY not in st.session_state:
            st.session_state[cls.STORAGE_KEY] = {}
        return st.session_state[cls.STORAGE_KEY]
    
    @classmethod
    def get_current_project(cls) -> Optional[Project]:
        """Get the currently active project."""
        if cls.CURRENT_PROJECT_KEY not in st.session_state:
            return None
        
        project_id = st.session_state[cls.CURRENT_PROJECT_KEY]
        return cls.load_project(project_id)
    
    @classmethod
    def set_current_project(cls, project_id: str) -> None:
        """Set the current active project."""
        st.session_state[cls.CURRENT_PROJECT_KEY] = project_id
    
    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        """Delete a project from localStorage."""
        projects = cls.load_all_projects()
        if project_id in projects:
            del projects[project_id]
            st.session_state[cls.STORAGE_KEY] = projects
            
            # Clear current project if it was deleted
            if (cls.CURRENT_PROJECT_KEY in st.session_state and 
                st.session_state[cls.CURRENT_PROJECT_KEY] == project_id):
                del st.session_state[cls.CURRENT_PROJECT_KEY]
            
            return True
        return False
    
    @classmethod
    def list_projects(cls) -> List[Dict[str, str]]:
        """List all projects with basic info."""
        projects = cls.load_all_projects()
        project_list = []
        
        for project_id, project_data in projects.items():
            project_list.append({
                "id": project_id,
                "name": project_data.get("name", "Unnamed Project"),
                "created_at": project_data.get("created_at", ""),
                "updated_at": project_data.get("updated_at", ""),
                "current_step": project_data.get("current_step", ""),
                "progress": len(project_data.get("completed_steps", [])) / len(ProjectStep) * 100
            })
        
        # Sort by updated_at (most recent first)
        project_list.sort(key=lambda x: x["updated_at"], reverse=True)
        return project_list
    
    @classmethod
    def export_project(cls, project_id: str) -> Optional[str]:
        """Export project as JSON string."""
        project = cls.load_project(project_id)
        if project:
            return project.model_dump_json(indent=2)
        return None
    
    @classmethod
    def import_project(cls, json_data: str) -> Optional[Project]:
        """Import project from JSON string."""
        try:
            project_data = json.loads(json_data)
            project = Project(**project_data)
            cls.save_project(project)
            return project
        except Exception:
            return None
    
    @classmethod
    def clone_as_template(cls, project_id: str, new_name: str) -> Optional[Project]:
        """Clone a project as a template."""
        original = cls.load_project(project_id)
        if not original:
            return None
        
        # Create new project with same structure but reset data
        import uuid
        new_project = Project(
            id=str(uuid.uuid4()),
            name=new_name,
            ai_model=original.ai_model,
            is_template=True,
            # Reset process data
            project_idea="",
            project_description="",
            planning_questions=[],
            planning_answers=[],
            planning_summary="",
            prd_document="",
            current_step=ProjectStep.PROJECT_IDEA,
            completed_steps=[]
        )
        
        cls.save_project(new_project)
        return new_project