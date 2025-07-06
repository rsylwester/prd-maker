"""Main Streamlit application for PRD Maker."""

import streamlit as st
from src.prd_maker.ui.main import main_page


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PRD Maker",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    main_page()


if __name__ == "__main__":
    main()