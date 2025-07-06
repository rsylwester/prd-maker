"""Main Streamlit UI page."""

import streamlit as st
import uuid
from datetime import datetime
from ..models.project import Project, ProjectStep
from ..core.project_storage import ProjectStorage
from ..core.llm_manager import LLMManager
from .steps import (
    render_project_idea_step,
    render_project_description_step,
    render_planning_session_step,
    render_planning_summary_step,
    render_prd_document_step
)


def initialize_session():
    """Initialize session state variables."""
    if "llm_manager" not in st.session_state:
        st.session_state.llm_manager = LLMManager()
    
    if "current_project" not in st.session_state:
        st.session_state.current_project = None


def render_sidebar():
    """Render the sidebar with project management and AI configuration."""
    st.sidebar.header("🔧 Configuration")
    
    # AI Model Selection
    llm_manager = st.session_state.llm_manager
    available_models = llm_manager.list_models()
    
    if available_models:
        selected_model = st.sidebar.selectbox(
            "Select AI Model",
            available_models,
            index=0 if available_models else None,
            help="Choose the AI model to use for PRD generation"
        )
        
        if selected_model:
            llm_manager.set_current_model(selected_model)
            current_project = st.session_state.current_project
            if current_project:
                current_project.ai_model = selected_model
                ProjectStorage.save_project(current_project)
    else:
        st.sidebar.error("No AI models available. Please configure API keys.")
    
    st.sidebar.markdown("---")
    
    # Project Management
    st.sidebar.header("📂 Projects")
    
    # New Project Button
    if st.sidebar.button("🆕 New Project", use_container_width=True):
        new_project = Project(
            id=str(uuid.uuid4()),
            name=f"Project {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ai_model=llm_manager._current_model if llm_manager._current_model else "gpt-4"
        )
        ProjectStorage.save_project(new_project)
        st.session_state.current_project = new_project
        st.rerun()
    
    # Project List
    projects = ProjectStorage.list_projects()
    if projects:
        st.sidebar.subheader("Recent Projects")
        for project in projects[:5]:  # Show last 5 projects
            col1, col2 = st.sidebar.columns([3, 1])
            
            with col1:
                if st.button(
                    f"📋 {project['name'][:20]}...",
                    key=f"load_{project['id']}",
                    help=f"Progress: {project['progress']:.0f}%"
                ):
                    loaded_project = ProjectStorage.load_project(project['id'])
                    if loaded_project:
                        st.session_state.current_project = loaded_project
                        st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{project['id']}", help="Delete project"):
                    ProjectStorage.delete_project(project['id'])
                    if (st.session_state.current_project and 
                        st.session_state.current_project.id == project['id']):
                        st.session_state.current_project = None
                    st.rerun()


def render_progress_bar(project: Project):
    """Render progress bar showing current step and completion."""
    steps = list(ProjectStep)
    current_step_index = steps.index(project.current_step)
    
    # Create progress indicator
    progress_cols = st.columns(len(steps))
    
    step_names = {
        ProjectStep.PROJECT_IDEA: "💡 Idea",
        ProjectStep.PROJECT_DESCRIPTION: "📝 Description",
        ProjectStep.PLANNING_SESSION: "🗣️ Planning",
        ProjectStep.ANSWER_QUESTIONS: "❓ Questions",
        ProjectStep.PLANNING_SUMMARY: "📋 Summary",
        ProjectStep.PRD_DOCUMENT: "📄 PRD"
    }
    
    for i, (step, col) in enumerate(zip(steps, progress_cols)):
        with col:
            if i < current_step_index:
                st.success(f"✅ {step_names[step]}")
            elif i == current_step_index:
                st.info(f"🔄 {step_names[step]}")
            else:
                st.empty()
                st.write(f"⏳ {step_names[step]}")
    
    # Progress percentage
    progress = project.get_progress_percentage()
    st.progress(progress / 100, text=f"Progress: {progress:.0f}%")


def main_page():
    """Render the main application page."""
    initialize_session()
    
    st.title("📋 PRD Maker")
    st.markdown("AI-powered Product Requirements Document generator")
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    current_project = st.session_state.current_project
    
    if not current_project:
        st.info("👈 Create a new project or select an existing one from the sidebar to get started.")
        
        # Show welcome content
        st.markdown("---")
        st.header("Welcome to PRD Maker")
        st.markdown("""
        PRD Maker guides you through a structured 6-step process to create comprehensive 
        Product Requirements Documents using AI assistance.
        
        **The Process:**
        1. **💡 Project Idea** - Start with your basic project concept
        2. **📝 Project Description** - AI generates detailed description
        3. **🗣️ Planning Session** - Interactive Q&A to clarify requirements
        4. **❓ Answer Questions** - Provide detailed answers to AI questions
        5. **📋 Planning Summary** - AI summarizes key decisions and requirements
        6. **📄 PRD Document** - Final comprehensive PRD generation
        """)
        
        with st.expander("🔧 Tech Stack"):
            st.markdown("""
            - **Python 3.13** - Core language
            - **Streamlit** - Web interface
            - **LangChain** - AI model integration
            - **Multiple AI Models** - GPT-4, Claude, Ollama
            """)
        
        return
    
    # Show project info
    st.header(f"📋 {current_project.name}")
    
    # Project name editing
    col1, col2 = st.columns([3, 1])
    with col1:
        new_name = st.text_input("Project Name", value=current_project.name, key="project_name")
        if new_name != current_project.name:
            current_project.name = new_name
            ProjectStorage.save_project(current_project)
    
    with col2:
        st.write(f"**Model:** {current_project.ai_model}")
    
    # Progress bar
    render_progress_bar(current_project)
    
    st.markdown("---")
    
    # Render current step
    if current_project.current_step == ProjectStep.PROJECT_IDEA:
        render_project_idea_step(current_project)
    elif current_project.current_step == ProjectStep.PROJECT_DESCRIPTION:
        render_project_description_step(current_project)
    elif current_project.current_step == ProjectStep.PLANNING_SESSION:
        render_planning_session_step(current_project)
    elif current_project.current_step == ProjectStep.ANSWER_QUESTIONS:
        render_planning_session_step(current_project)  # Same as planning session
    elif current_project.current_step == ProjectStep.PLANNING_SUMMARY:
        render_planning_summary_step(current_project)
    elif current_project.current_step == ProjectStep.PRD_DOCUMENT:
        render_prd_document_step(current_project)
    
    # Navigation buttons
    st.markdown("---")
    render_navigation_buttons(current_project)


def render_navigation_buttons(project: Project):
    """Render navigation buttons for moving between steps."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Previous step button
        steps = list(ProjectStep)
        current_index = steps.index(project.current_step)
        
        if current_index > 0:
            if st.button("⬅️ Previous Step", use_container_width=True):
                project.current_step = steps[current_index - 1]
                ProjectStorage.save_project(project)
                st.rerun()
    
    with col3:
        # Next step button (only if current step is complete)
        if current_index < len(steps) - 1:
            can_advance = False
            
            # Check if current step is complete
            if project.current_step == ProjectStep.PROJECT_IDEA:
                can_advance = bool(project.project_idea.strip())
            elif project.current_step == ProjectStep.PROJECT_DESCRIPTION:
                can_advance = bool(project.project_description.strip())
            elif project.current_step == ProjectStep.PLANNING_SESSION:
                can_advance = len(project.planning_answers) > 0
            elif project.current_step == ProjectStep.ANSWER_QUESTIONS:
                can_advance = len(project.planning_answers) > 0
            elif project.current_step == ProjectStep.PLANNING_SUMMARY:
                can_advance = bool(project.planning_summary.strip())
            elif project.current_step == ProjectStep.PRD_DOCUMENT:
                can_advance = bool(project.prd_document.strip())
            
            if st.button("Next Step ➡️", disabled=not can_advance, use_container_width=True):
                if project.advance_step():
                    ProjectStorage.save_project(project)
                    st.rerun()