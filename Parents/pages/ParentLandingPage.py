import streamlit as st

from Parents.pages.Chat_with_AI import simple_chat_page
from Parents.pages.kids_dashboard_and_alimentary_plan import register_my_kid
from Parents.pages.generate_food_planning_for_kids import generate_meal_plan

def placeholder_function():pass

action = st.sidebar.selectbox(
    "What do you want to do?", 
    options := [
        "Register a kid",
        "Manage My kids informations", 
        "Generate a recipe for my kid", 
    ]
)

display_on_page = {
    option : func
    for option, func in zip(options, [
        register_my_kid,
        simple_chat_page, 
        generate_meal_plan
        ])
}

display_on_page[action]()

