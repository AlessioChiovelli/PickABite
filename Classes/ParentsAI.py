from typing import List, Literal, Dict
from pydantic import BaseModel, Field
from langgraph.graph import Graph, END
from groq import Groq
import json

# Prompts
WHAT_WEIGHT_PROMPT = \
"""You are a dietitian and nutritionist specialising in infant-oriented nutrition.
You have to help parents determine if their child is underweight, overweight or normal weight. 
Parents could give you as information their child height and weight, or his/her BMI or other metrics.
Parents could also directly tell you that their kid's weight status: in such case the response is trivial.

It is important that you return a response in JSON format with the following fields:
JSON format:
{{
    "child_weight": "Wheter the child is overweight, underweight or normal weight. This is a Literal['Overweight', 'Underweight', 'Normal']"    
}}

Here an example:
{{
    "child_weight": "Overweight"
}}

Now, it is your turn to determine the weight status of the child given the following request: {request}

For now, ignore the part about dinner. Only concentrate on determining whether the kid is overweight, underweight or of normal weight.
REMEMBER to output in JSON format. 
Do not say anything else in the response! Just the JSON format.
"""

MEAL_PLAN_4NORMAL_WEIGHT_CHILD_PROMPT = \
"""You are a dietitian and nutritionist specializing in infant-oriented nutrition.
You have to help the parents of children and assist them in creating meals for children of normal weight. 
You are also a professional chef creating a menu. 

Given this request by the parents of the normal weight child: {request}

Think step by step:
1. Consider the dietary requirements for a normal weight child, ensuring balanced nutrition to support growth and energy needs.
2. Consider preparation time.
3. Plan complementary dishes that are both nutritious and appealing to the child.

It is important that you return a response in JSON format with the following fields:
JSON format:
{{
    "menu_description": "description of the menu",
    "first_course": "description of first course",
    "second_course": "description of main dish",
    "why_this_menu": "description of dietary reasons for the creation of this menu"
}}

Keep descriptions brief but informative. Focus on the essence of each dish. 

Here is an example:
{{
    "menu_description": "A balanced two-course meal for a healthy and active child!",
    "first_course": "A bowl of creamy carrot and lentil soup served with a slice of whole-grain bread.",
    "second_course": "Grilled chicken breast with a side of roasted vegetables and a small serving of brown rice.",
    "why_this_menu": "This menu provides a balance of protein, whole grains, and vegetables to maintain energy levels and overall health for a normal weight child."
}}

Now it's your turn to create a healthy menu for the kid! 
REMEMBER to output in JSON format. 
Do not say anything else in the response! Just the JSON format.
"""

MEAL_PLAN_4OVERWEIGHT_CHILD_PROMPT = \
"""You are a dietitian and nutritionist specialising in infant-oriented nutrition.
You have to help the parents of children and assist them in creating meals for overweight children. 
You are also a professional chef creating a menu. 

Given this request by the parents of the overweight child: {request}

Think step by step:
1. Consider the dietary requirements for the overweight child
2. Consider preparation time
3. Plan complementary dishes

It is important that you return a response in JSON format with the following fields:
JSON format:
{{
    "menu_description": "description of the menu",
    "first_course": "description of first course",
    "second_course": "description of main dish"
    "why_this_menu": "description of dietary reasons for the creation of this menu"
}}

Keep descriptions brief but informative. Focus on the essence of each dish. 

Here is an example:
{{
    "menu_description": "A delightful two-course meal!",
    "first_course": "A light and hearty vegetable-based soup that’s packed with fiber, vitamins, and minerals.",
    "second_course": "Grilled Chicken with Lemon and Herb Quinoa Salad",
    "why_this_menu": "This menu ensures the child feels satisfied and enjoys Italian cuisine while keeping the meal balanced and calorie-conscious."
}}

Now it's your turn to create a healthy menu for the kid! 
REMEMBER to output in JSON format. 
Do not say anything else in the response! Just the JSON format.
"""

MEAL_PLAN_4UNDERWEIGHT_CHILD_PROMPT = \
"""You are a dietitian and nutritionist specializing in infant-oriented nutrition.
You have to help the parents of children and assist them in creating meals for underweight children.
You are also a professional chef creating a menu.

Given the following request by the parents of the underweight child: {request}

Think step by step:
1. Consider the dietary requirements for the underweight child, focusing on calorie-dense and nutrient-rich foods.
2. Consider preparation time.
3. Plan complementary dishes that are appetizing and appealing to the child.

It is important that you return a response in JSON format with the following fields:
JSON format:
{{
    "menu_description": "description of the menu",
    "first_course": "description of first course",
    "second_course": "description of main dish",
    "why_this_menu": "description of dietary reasons for the creation of this menu"
}}

Keep descriptions brief but informative. Focus on the essence of each dish. 

Here is an example:
{{
    "menu_description": "A delicious and nourishing two-course meal designed to promote healthy weight gain!",
    "first_course": "Creamy tomato and lentil soup made with whole milk and served with a slice of whole-grain bread.",
    "second_course": "Baked salmon fillet with a side of mashed sweet potatoes and steamed broccoli, drizzled with olive oil.",
    "why_this_menu": "This menu provides a balance of protein, healthy fats, and carbohydrates to support weight gain and overall health in an underweight child."
}}

Now it's your turn to create a healthy menu for the kid! 
REMEMBER to output in JSON format. 
Do not say anything else in the response! Just the JSON format.
"""

RECIPE_PROMPT = \
"""Create a single detailed recipe for this dish description:

{dish_description}

You must provide:
1. A brief name for the recipe
2. Step-by-step instructions
3. Cooking time
4. Chef's tips

It is important that you return a response in JSON format with the following fields:
JSON format:
{{
    "name": "name of the dish",
    "instructions": ["step 1", "step 2", "step 3"],
    "cooking_time": "time to cook the dish",
    "tips": ["tip 1", "tip 2"]
}}

Here is an example:
{{
    "name": "Baked Salmon with Sweet Potatoes and Broccoli",
    "instructions": [
        "Preheat the oven to 400°F (200°C).",
        "Season the salmon fillets with salt, pepper, and a drizzle of olive oil.",
        "Peel and dice the sweet potatoes, then toss them with olive oil, salt, and pepper.",
        "Spread the sweet potatoes on a baking sheet and roast for 15 minutes.",
        "Add the salmon fillets to the baking sheet and roast for another 12-15 minutes, or until the salmon is cooked through.",
        "Steam the broccoli in a pot or microwave until tender but still bright green.",
        "Plate the salmon with a side of mashed sweet potatoes and steamed broccoli, and drizzle with a little more olive oil before serving."
    ],
    "cooking_time": "30 minutes",
    "tips": [
        "Use fresh salmon for the best flavor and texture.",
        "To make the sweet potatoes extra creamy, mash them with a small amount of butter or whole milk."
    ]
}}

Now it's your turn to create delicious, healthy recipes! 
REMEMBER to output in JSON format. 
Do not say anything else in the response. Just the JSON format.
"""


# Pydantic models
class MealPlan(BaseModel):
    menu_description: str =  Field(description="Description of the menu")
    first_course: str =      Field(description="Description of the first course")
    second_course: str =     Field(description="Description of the second course")
    why_this_menu: str =     Field(description="Description of dietary reasons for the creation of this menu")

class WeightStatus(BaseModel):
    child_weight: Literal['Overweight', 'Underweight', 'Normal'] = \
        Field(description="Type of weight status, choose: 'Overweight', 'Underweight' or 'Normal'")

class Recipe(BaseModel):
    name: str =                Field(description="Name of the dish")
    instructions: List[str] =  Field(description="Step-by-step instructions")
    cooking_time: str =        Field(description="Time to cook the dish")
    tips: List[str] =          Field(description="Chef's tips")

class Menu(BaseModel):
    recipes: Dict[str, Recipe] = {}

class State(BaseModel):
    request:       str = Field(description="Original user request")
    weight_status: WeightStatus = None
    meal_plan:     MealPlan = None
    detailed_menu: Menu = None
    error:         str = None

# ------------- Graph section ---------------------------------------------

class RecipeGraph:
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model  # TODO mettere modello cambiabile da utente?

    def generate_weight_status(self, state: State) -> State:
        """Generate weight status for the child using Llama via Groq."""
        print("Choosing food plan...")
        temperature = 0
        attempts = 0

        while attempts < 3:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": WHAT_WEIGHT_PROMPT.format(request=state.request)
                    }],
                    temperature=temperature,
                    max_tokens=50
                )
                kid_data = json.loads(response.choices[0].message.content)
                weight_status = WeightStatus(**kid_data)
                print("Child weight status determined successfully!")
                print(f"Your child is: {weight_status}")
                return State(
                    request=state.request,
                    weight_status=weight_status
                )
            except Exception as e:
                print(f"Failed to generate menu (attempt {attempts + 1}/3):", str(e))
                try:
                    print(response.choices[0].message.content)
                except:
                    pass
                temperature += 0.1
                attempts += 1
        # after 3 attempts, return empty status
        empty_weight = WeightStatus(
            weight_status = "Normal"   # default value
        )
        return State(
            request=state.request,
            weight_status=empty_weight  # just return the empty weight with "Normal" default value
        )

    def generate_meal(self, state: State) -> State:
        """Generate menu descriptions using Llama via Groq."""
        print("Generating a menu tailored for your child...")
        temperature = 0
        attempts = 0

        # setting request content based on the child weight status
        if state.weight_status.child_weight == "Normal":
            content = MEAL_PLAN_4NORMAL_WEIGHT_CHILD_PROMPT.format(request=state.request)
        elif state.weight_status.child_weight == "Overweight":
            content = MEAL_PLAN_4OVERWEIGHT_CHILD_PROMPT.format(request=state.request)
        elif state.weight_status.child_weight == "Underweight":
            content = MEAL_PLAN_4UNDERWEIGHT_CHILD_PROMPT.format(request=state.request)
        else:
            raise NotImplementedError

        while attempts < 3:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": content,
                    }],
                    temperature=temperature,
                    max_tokens=2000
                )
                menu_data = json.loads(response.choices[0].message.content)
                meal_plan = MealPlan(**menu_data)
                print("Menu generated successfully.")
                return State(
                    request=state.request,
                    weight_status= state.weight_status,
                    meal_plan=meal_plan,
                )
            except Exception as e:
                print(f"Failed to generate menu (attempt {attempts + 1}/3):", str(e))
                print(response.choices[0].message.content)
                temperature += 0.1
                attempts += 1

        # empty meal
        empty_meal = MealPlan(
            menu_description= "",
            first_course= "",
            second_course= "",
            why_this_menu= ""
        )

        # Return empty menu after 3 failed attempts
        return State(
            request=state.request,
            weight_status=state.weight_status,
            meal_plan=empty_meal,
        )

    def generate_recipes(self, state: State) -> State:
        """Generate detailed recipes using Llama via Groq."""
        if state.error:
            return state

        menu = Menu()
        print("Generating recipes...")

        for course_name, description in [
            ("first_course", state.meal_plan.first_course),
            ("second_course", state.meal_plan.second_course)
        ]:
            print(f"Generating recipe for {course_name}...")
            temperature = 0
            attempts = 0

            while attempts < 3:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{
                            "role": "user",
                            "content": RECIPE_PROMPT.format(
                                dish_description=description
                            )
                        }],
                        temperature=temperature,
                        max_tokens=2000
                    )
                    recipe_data = json.loads(response.choices[0].message.content)
                    menu.recipes[course_name] = Recipe(**recipe_data)
                    break
                except Exception as e:
                    print(f"Failed to generate recipe (attempt {attempts + 1}/3):", str(e))
                    print(response.choices[0].message.content)
                    temperature += 0.1
                    attempts += 1

            if attempts == 3:
                # Add empty recipe if all attempts failed
                menu.recipes[course_name] = Recipe(
                    name="",
                    instructions=[],
                    cooking_time="",
                    tips=[]
                )

        print("Recipes generation completed.")
        return State(
            request=state.request,
            weight_status=state.weight_status,
            meal_plan=state.meal_plan,
            detailed_menu=menu
        )

def create_recipe_graph(api_key: str):
    """Create the LangGraph workflow with conditional branching."""
    food_graph = RecipeGraph(api_key)  # here could input another model name
    workflow = Graph()

    # Add nodes
    workflow.add_node('generate_weight_status', food_graph.generate_weight_status)
    workflow.add_node('generate_meal', food_graph.generate_meal)
    workflow.add_node('generate_recipes', food_graph.generate_recipes)

    #
    # # Add edges with conditional branching
    # workflow.add_edge("generate_meal", "generate_recipes")
    # workflow.add_conditional_edges(
    #     "generate_recipes",
    #     is_wine,
    #     {
    #         True: "recommend_wine",
    #         False: "recommend_beer"
    #     }
    # )
    #
    # workflow.add_edge("recommend_wine", END)
    # workflow.add_edge("recommend_beer", END)
    #
    # # Set entry point
    # workflow.set_entry_point("generate_menu")

    # Edging the graph
    workflow.set_entry_point('generate_weight_status') # START
    workflow.add_edge('generate_weight_status', 'generate_meal')
    workflow.add_edge('generate_meal', 'generate_recipes')
    workflow.add_edge('generate_recipes', END)

    return workflow.compile()


# Example usage
def main():
    api_key = ""
    graph = create_recipe_graph(api_key)

    request = \
    """My kid is 12, weighs about 45kg and he's 150cm tall. I'd like to cook for him something good! 
    He likes broth, chicken, pasta, potatoes, lentils. I don't have more than 1 hour for cooking. 
    What would you recommend me?"""

    initial_state = State(request=request)
    result = graph.invoke(initial_state)

    for attribute, value in result.__dict__.items():
        print(f"{attribute}: {value}")


if __name__ == "__main__":
    main()