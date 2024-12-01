import streamlit as st

from Parents.pages.Chat_with_AI import simple_chat_page
from Parents.pages.kids_dashboard_and_alimentary_plan import register_my_kid

def placeholder_function():pass

action = st.sidebar.selectbox(
    "What do you want to do?", 
    options := [
        "Manage My kids informations", 
        "Generate a recipe for my kid", 
        "Register a kid"
    ]
)

display_on_page = {
    option : func
    for option, func in zip(options, [simple_chat_page, placeholder_function, register_my_kid])
}

display_on_page[action]()

