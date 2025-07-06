"""Individual step implementations for the PRD creation process."""

import streamlit as st
from ..models.project import Project
from ..core.project_storage import ProjectStorage


def render_project_idea_step(project: Project):
    """Render the Project Idea input step."""
    st.header("💡 Project Idea")
    st.markdown("Start by describing your project idea. This can be a basic concept that you want to develop into a full PRD.")
    
    # Project idea input
    project_idea = st.text_area(
        "Describe your project idea:",
        value=project.project_idea,
        height=200,
        placeholder="Example: Create a mobile app that helps users track their daily water intake and reminds them to stay hydrated...",
        help="Enter at least 50 characters to describe your project concept"
    )
    
    # Update project if changed
    if project_idea != project.project_idea:
        project.project_idea = project_idea
        ProjectStorage.save_project(project)
    
    # Validation
    if len(project_idea.strip()) < 50:
        st.warning("Please provide at least 50 characters to describe your project idea.")
    else:
        st.success("✅ Project idea looks good! You can proceed to the next step.")


def render_project_description_step(project: Project):
    """Render the Project Description generation step."""
    st.header("📝 Project Description")
    st.markdown("Generate a detailed project description based on your initial idea.")
    
    # Show the original idea
    if project.project_idea:
        with st.expander("📋 Original Project Idea"):
            st.write(project.project_idea)
    
    # Generate description button
    if not project.project_description and project.project_idea:
        if st.button("🚀 Generate Project Description", type="primary"):
            with st.spinner("Generating detailed project description..."):
                try:
                    llm_manager = st.session_state.llm_manager
                    description = llm_manager.generate_project_description(project.project_idea)
                    project.project_description = description
                    ProjectStorage.save_project(project)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating description: {str(e)}")
    
    # Show/edit generated description
    if project.project_description:
        st.subheader("Generated Description:")
        
        # Edit description
        new_description = st.text_area(
            "Edit project description:",
            value=project.project_description,
            height=300,
            help="You can edit the generated description to better match your vision"
        )
        
        if new_description != project.project_description:
            project.project_description = new_description
            ProjectStorage.save_project(project)
        
        # Regenerate option
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Regenerate Description"):
                with st.spinner("Regenerating description..."):
                    try:
                        llm_manager = st.session_state.llm_manager
                        description = llm_manager.generate_project_description(project.project_idea)
                        project.project_description = description
                        ProjectStorage.save_project(project)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error regenerating description: {str(e)}")
        
        st.success("✅ Project description is ready! You can proceed to the planning session.")


def render_planning_session_step(project: Project):
    """Render the Planning Session interactive Q&A step."""
    st.header("🗣️ Planning Session")
    st.markdown("Answer questions to clarify your project requirements. The AI will generate targeted questions based on your project description.")
    
    # Show project description
    if project.project_description:
        with st.expander("📋 Project Description"):
            st.write(project.project_description)
    
    # Generate questions if not already generated
    if not project.planning_questions and project.project_description:
        if st.button("🎯 Generate Planning Questions", type="primary"):
            with st.spinner("Generating planning questions..."):
                try:
                    llm_manager = st.session_state.llm_manager
                    questions = llm_manager.generate_questions(project.project_description)
                    project.planning_questions = [{"question": q, "id": i} for i, q in enumerate(questions)]
                    ProjectStorage.save_project(project)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")
    
    # Show Q&A interface
    if project.planning_questions:
        st.subheader("Planning Questions")
        
        # Initialize answers if not present
        if not hasattr(project, 'planning_answers') or not project.planning_answers:
            project.planning_answers = []
        
        # Convert to dict for easier access
        answers_dict = {ans.get("question_id", ans.get("id", 0)): ans.get("answer", "") for ans in project.planning_answers}
        
        # Display questions and collect answers
        for i, q_data in enumerate(project.planning_questions):
            question = q_data["question"]
            question_id = q_data.get("id", i)
            
            st.markdown(f"**Question {i+1}:**")
            st.write(question)
            
            # Answer input
            answer = st.text_area(
                "Your answer:",
                value=answers_dict.get(question_id, ""),
                key=f"answer_{question_id}",
                height=100,
                help="Provide as much detail as possible"
            )
            
            # Update answer if changed
            if answer != answers_dict.get(question_id, ""):
                # Update or add answer
                found = False
                for ans in project.planning_answers:
                    if ans.get("question_id", ans.get("id", 0)) == question_id:
                        ans["answer"] = answer
                        found = True
                        break
                
                if not found:
                    project.planning_answers.append({
                        "question_id": question_id,
                        "question": question,
                        "answer": answer
                    })
                
                ProjectStorage.save_project(project)
            
            st.markdown("---")
        
        # Summary of progress
        answered_questions = sum(1 for ans in project.planning_answers if ans.get("answer", "").strip())
        total_questions = len(project.planning_questions)
        
        st.info(f"Progress: {answered_questions}/{total_questions} questions answered")
        
        # Option to add more questions
        st.subheader("Additional Questions")
        additional_question = st.text_input("Add your own question:", placeholder="Enter a custom question...")
        
        if st.button("➕ Add Question") and additional_question:
            new_id = len(project.planning_questions)
            project.planning_questions.append({
                "question": additional_question,
                "id": new_id
            })
            ProjectStorage.save_project(project)
            st.rerun()
        
        # Finish session button
        if answered_questions > 0:
            st.subheader("Complete Planning Session")
            if st.button("✅ Finish Planning Session", type="primary"):
                st.success("Planning session completed! You can now proceed to the summary step.")
        else:
            st.warning("Please answer at least one question before proceeding.")


def render_planning_summary_step(project: Project):
    """Render the Planning Summary generation step."""
    st.header("📋 Planning Summary")
    st.markdown("Generate a comprehensive summary of your planning session to prepare for PRD creation.")
    
    # Show Q&A summary
    if project.planning_answers:
        with st.expander("📝 Planning Session Q&A"):
            for ans in project.planning_answers:
                if ans.get("answer", "").strip():
                    st.write(f"**Q:** {ans['question']}")
                    st.write(f"**A:** {ans['answer']}")
                    st.markdown("---")
    
    # Generate summary button
    if not project.planning_summary and project.planning_answers:
        if st.button("📊 Generate Planning Summary", type="primary"):
            with st.spinner("Generating planning summary..."):
                try:
                    llm_manager = st.session_state.llm_manager
                    summary = llm_manager.generate_planning_summary(
                        project.project_description,
                        project.planning_answers
                    )
                    project.planning_summary = summary
                    ProjectStorage.save_project(project)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
    
    # Show/edit generated summary
    if project.planning_summary:
        st.subheader("Generated Planning Summary:")
        
        # Edit summary
        new_summary = st.text_area(
            "Edit planning summary:",
            value=project.planning_summary,
            height=400,
            help="You can edit the generated summary to add or clarify information"
        )
        
        if new_summary != project.planning_summary:
            project.planning_summary = new_summary
            ProjectStorage.save_project(project)
        
        # Regenerate option
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Regenerate Summary"):
                with st.spinner("Regenerating summary..."):
                    try:
                        llm_manager = st.session_state.llm_manager
                        summary = llm_manager.generate_planning_summary(
                            project.project_description,
                            project.planning_answers
                        )
                        project.planning_summary = summary
                        ProjectStorage.save_project(project)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error regenerating summary: {str(e)}")
        
        st.success("✅ Planning summary is ready! You can now generate the final PRD document.")


def render_prd_document_step(project: Project):
    """Render the PRD Document generation and export step."""
    st.header("📄 PRD Document")
    st.markdown("Generate your final Product Requirements Document based on the planning summary.")
    
    # Show planning summary
    if project.planning_summary:
        with st.expander("📋 Planning Summary"):
            st.write(project.planning_summary)
    
    # Generate PRD button
    if not project.prd_document and project.planning_summary:
        if st.button("📄 Generate PRD Document", type="primary"):
            with st.spinner("Generating PRD document..."):
                try:
                    llm_manager = st.session_state.llm_manager
                    prd_doc = llm_manager.generate_prd_document(project.planning_summary)
                    project.prd_document = prd_doc
                    ProjectStorage.save_project(project)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating PRD: {str(e)}")
    
    # Show/edit generated PRD
    if project.prd_document:
        st.subheader("Generated PRD Document:")
        
        # Tab interface for editing and preview
        tab1, tab2 = st.tabs(["✏️ Edit", "👀 Preview"])
        
        with tab1:
            # Edit PRD
            new_prd = st.text_area(
                "Edit PRD document (Markdown format):",
                value=project.prd_document,
                height=600,
                help="Edit the PRD document. Uses Markdown formatting."
            )
            
            if new_prd != project.prd_document:
                project.prd_document = new_prd
                ProjectStorage.save_project(project)
            
            # Regenerate option
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔄 Regenerate PRD"):
                    with st.spinner("Regenerating PRD..."):
                        try:
                            llm_manager = st.session_state.llm_manager
                            prd_doc = llm_manager.generate_prd_document(project.planning_summary)
                            project.prd_document = prd_doc
                            ProjectStorage.save_project(project)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error regenerating PRD: {str(e)}")
        
        with tab2:
            # Preview PRD
            st.markdown(project.prd_document)
        
        # Export options
        st.subheader("📥 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as Markdown
            st.download_button(
                label="📝 Download as Markdown",
                data=project.prd_document,
                file_name=f"{project.name}_PRD.md",
                mime="text/markdown"
            )
        
        with col2:
            # Download as Text
            st.download_button(
                label="📄 Download as Text",
                data=project.prd_document,
                file_name=f"{project.name}_PRD.txt",
                mime="text/plain"
            )
        
        with col3:
            # Project export
            project_json = ProjectStorage.export_project(project.id)
            if project_json:
                st.download_button(
                    label="📦 Export Project",
                    data=project_json,
                    file_name=f"{project.name}_project.json",
                    mime="application/json"
                )
        
        st.success("✅ PRD document is complete! You can download it using the export options above.")
        
        # Quality metrics
        st.subheader("📊 Document Quality")
        word_count = len(project.prd_document.split())
        sections = project.prd_document.count('##')
        user_stories = project.prd_document.count('US-')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", word_count)
        with col2:
            st.metric("Sections", sections)
        with col3:
            st.metric("User Stories", user_stories)


def render_tech_stack_analysis_step(project: Project):
    """Render the Tech Stack Analysis step."""
    st.header("🏗️ Tech Stack Analysis")
    st.markdown("Define your technology stack and get AI analysis of its suitability for your PRD requirements.")
    
    # Show PRD summary
    if project.prd_document:
        with st.expander("📋 PRD Document Summary"):
            # Show first few sections of PRD
            prd_lines = project.prd_document.split('\n')
            preview_lines = prd_lines[:50]  # First 50 lines
            st.markdown('\n'.join(preview_lines) + "\n\n*[Click to see full PRD document]*")
    
    # Tech stack proposal input
    st.subheader("💻 Technology Stack Proposal")
    
    tech_stack_proposal = st.text_area(
        "Describe your proposed technology stack:",
        value=project.tech_stack_proposal,
        height=200,
        placeholder="""Example:
Frontend: React.js with TypeScript, Tailwind CSS
Backend: Node.js with Express.js, PostgreSQL database
Authentication: Auth0
Hosting: Vercel (frontend), Railway (backend)
Additional: Redis for caching, SendGrid for emails""",
        help="Describe the technologies, frameworks, databases, and services you plan to use"
    )
    
    # Update project if changed
    if tech_stack_proposal != project.tech_stack_proposal:
        project.tech_stack_proposal = tech_stack_proposal
        ProjectStorage.save_project(project)
    
    # Generate analysis button
    if not project.tech_stack_analysis and project.tech_stack_proposal.strip() and project.prd_document:
        if st.button("🔍 Analyze Tech Stack", type="primary"):
            with st.spinner("Analyzing technology stack against PRD requirements..."):
                try:
                    llm_manager = st.session_state.llm_manager
                    analysis = llm_manager.analyze_tech_stack(
                        project.prd_document,
                        project.tech_stack_proposal
                    )
                    project.tech_stack_analysis = analysis
                    ProjectStorage.save_project(project)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error analyzing tech stack: {str(e)}")
    
    # Show/edit generated analysis
    if project.tech_stack_analysis:
        st.subheader("📊 Tech Stack Analysis:")
        
        # Tab interface for editing and preview
        tab1, tab2 = st.tabs(["✏️ Edit Analysis", "👀 Preview"])
        
        with tab1:
            # Edit analysis
            new_analysis = st.text_area(
                "Edit tech stack analysis:",
                value=project.tech_stack_analysis,
                height=600,
                help="You can edit the generated analysis or add your own insights"
            )
            
            if new_analysis != project.tech_stack_analysis:
                project.tech_stack_analysis = new_analysis
                ProjectStorage.save_project(project)
            
            # Regenerate option
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔄 Regenerate Analysis"):
                    with st.spinner("Regenerating tech stack analysis..."):
                        try:
                            llm_manager = st.session_state.llm_manager
                            analysis = llm_manager.analyze_tech_stack(
                                project.prd_document,
                                project.tech_stack_proposal
                            )
                            project.tech_stack_analysis = analysis
                            ProjectStorage.save_project(project)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error regenerating analysis: {str(e)}")
        
        with tab2:
            # Preview analysis
            st.markdown(project.tech_stack_analysis)
        
        # Export options
        st.subheader("📥 Export Tech Stack Analysis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download analysis as Markdown
            st.download_button(
                label="📝 Download Analysis (MD)",
                data=project.tech_stack_analysis,
                file_name=f"{project.name}_TechStack_Analysis.md",
                mime="text/markdown"
            )
        
        with col2:
            # Download combined PRD + Tech Stack
            combined_document = f"{project.prd_document}\n\n---\n\n{project.tech_stack_analysis}"
            st.download_button(
                label="📄 Download PRD + Tech Stack",
                data=combined_document,
                file_name=f"{project.name}_Complete_PRD.md",
                mime="text/markdown"
            )
        
        with col3:
            # Project export
            project_json = ProjectStorage.export_project(project.id)
            if project_json:
                st.download_button(
                    label="📦 Export Full Project",
                    data=project_json,
                    file_name=f"{project.name}_complete_project.json",
                    mime="application/json"
                )
        
        st.success("✅ Tech stack analysis complete! Your PRD is now ready for development.")
        
    elif not project.tech_stack_proposal.strip():
        st.warning("Please provide a technology stack proposal to generate analysis.")
    elif not project.prd_document:
        st.warning("PRD document must be completed before tech stack analysis.")
    else:
        st.info("Click 'Analyze Tech Stack' to get AI analysis of your technology choices.")