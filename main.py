import streamlit as st

pages = [
    st.Page("Parents/pages/ParentLandingPage.py", title = "Parents"), 
    st.Page("Kids/pages/play_with_ai.py", title = "Kids"), 
    # st.Page("Parents/pages/kids_dashboard_and_alimentary_plan.py", title = "Parents - My kids alimentary plan"), 
    st.Page("memory_game_st.py", title = "Memory_game"), 
    # st.Page("AI-API_keys.py", title = "API Key")
]

st.navigation(pages).run()