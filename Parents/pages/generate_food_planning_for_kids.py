import streamlit as st
from pydantic import ValidationError
from Classes.ParentsAI import create_recipe_graph, State  # Replace with the correct module name
import os
from dotenv import load_dotenv

_ = load_dotenv('../../.env')
api_key = os.getenv("GROQ_API_KEY")

# # Configure the app
# st.set_page_config(
#     page_title="Child Meal Planner",
#     page_icon="🍽️",
#     layout="wide"
# )


def generate_meal_plan():
    # App title
    st.title("Child Meal Planner 🍽️")
    st.write("Enter your child's details and get a personalized meal plan with detailed recipes.")


    # Parent's request input
    st.subheader("Request")
    request = st.text_area(
        "Describe your child (age, weight, height) and their dietary preferences. Feel free to specify any special needs.",
        placeholder="For example: My child is 12 years old, weighs about 45kg, and is 150cm tall. They like broth, chicken, pasta..."
    )


    # Generate meal plan button
    if st.button("Generate Meal Plan"):
        # Create the recipe graph
        graph = create_recipe_graph(api_key)

        # Execute the graph
        initial_state = State(request=request)
        try:
            result = graph.invoke(initial_state)

            # Display results
            st.subheader("Results")

            # Weight status
            st.markdown("### Child's Weight Status")
            st.write(f"**Status:** {result.weight_status.child_weight}")

            # Meal plan
            st.markdown("### Meal Plan")
            st.write(f"**Menu Description:** {result.meal_plan.menu_description}")
            st.write(f"**First Course:** {result.meal_plan.first_course}")
            st.write(f"**Second Course:** {result.meal_plan.second_course}")
            st.write(f"**Reason for This Menu:** {result.meal_plan.why_this_menu}")

            # Detailed recipes
            st.markdown("### Detailed Recipes")
            for course_name, recipe in result.detailed_menu.recipes.items():
                st.markdown(f"#### {course_name.replace('_', ' ').capitalize()}")
                st.markdown(f"**Dish Name:** {recipe.name}")
                st.markdown("**Instructions:**")
                for idx, step in enumerate(recipe.instructions, start=1):
                    st.write(f"{idx}. {step}")
                st.write(f"**Cooking Time:** {recipe.cooking_time}")
                st.write("**Chef's Tips:**")
                for tip in recipe.tips:
                    st.write(f"- {tip}")

        except ValidationError as e:
            st.error("Validation error occurred while processing the generated data.")
            st.error(str(e))
        except Exception as e:
            st.error("An error occurred while processing your request.")
            st.error(str(e))
