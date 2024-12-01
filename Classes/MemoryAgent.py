from typing import List, Literal, Dict, Optional
from pydantic import BaseModel, Field
from langgraph.graph import Graph, END, START
import streamlit as st

from Classes.AIBackend import AIAssistant
# from Prompts.KidsPrompts import KIDS_PROMPTS

KIDS_PROMPTS = {
    "Feed me!" : """
    Talk to a kid and ask them to feed you.
    The kid will tell you what they want to cook for you.
    You can respond that you like it or not, and why.
    Generally, if they tell you something you do not like, it means they are approaching you with a bad food for your diet.
    This behaviour will be used to teach them what is good and what is bad to eat in a balanced diet.
    ***
    {history}
    ***
    {chat_input}
    """,
    "Let's make a recipe!" : """
        Create a dish based on what a children tells you to cook. 
        You need to provide in a json the following informations keys:
        emoji : An emoji to describe the dish and to present to a card as Frontend
        name : A name you want to give to the dish
        what_i_like_about_it : what you like as a tamagochi being of this dish. Make this with a personal tpuch remembering that you are talking to a 5/6 y.o kid in general
        indications : An educational part where you can explain the pros and cons of the dish on a diet based on the ingredients, nutrients and so on. They are a string, and not a json
    Return only the json, without no other text
    ***
    {history}
    ***
    {chat_input}
    """, 
    "Let's chat!" : """
    You are a tamagochi, you need to talk with a children. 
    Reply to them in a polite way and make them feel comfortable. 
    You can talk about what you want to eat, and what you like.

    Of course, you can't use bad words!
    You cannot event talk about inappropriate content, harmful indications porn and so on!
    ***
    {history}
    ***
    {chat_input}
    """, 
}

# Pydantic models
class DishDescription(BaseModel):
    emoji: str = Field(description="Emoji of what the meal will be like")
    name: str = Field(description="The name of the dish")
    what_i_like_about_it: str = Field(description="A description of what the Tamagochi thinks about this dish")
    indications: str = Field(description="The pros and cons of the dish on a diet")

# State models
class State(BaseModel):
    chat_input: str = Field(description="Original user request")
    dishes: Optional[List[DishDescription] | DishDescription] = Field(description="Dishes to be cooked", default=None)
    history: Optional[str] = Field(description="Original user request", default="")
    error: str = None

class TamagochiGraph:
    def __init__(self, model : str = "llama-3.1-70b-versatile"):
        self.model = model
        self.prompts: Dict[Literal["Feed me!", "Let's make a recipe!", "Let's chat!"], str] = KIDS_PROMPTS
        self.clients = {
            action : AIAssistant(prompt_template= prompt_template, model_str=model, max_retries = 3)
            for action, prompt_template in self.prompts.items()
        }

        # proprietà che ti dice quale grafo adoperare
    
    # Testato
    def generate_recipe(self, state: State) -> State:
        """Generate menu descriptions using Llama via Groq."""
        print("Generating menu...")
        client : AIAssistant = self.clients["Let's make a recipe!"]
        attempts = 0
        try:
            dish_description : DishDescription = client.chat({"chat_input" : state.chat_input, "history" : state.history}, [DishDescription])  
            print("Menu generated successfully.")
            return State(chat_input=state.chat_input,dishes=dish_description)
        except Exception as e:
            print(f"Failed to generate menu (attempt {attempts + 1}/3):", str(e))
            attempts += 1
        # Return empty menu after 3 failed attempts
        return State(
            chat_input=state.chat_input,
            dishes=DishDescription(emoji = "", name = "", what_i_like_about_it = "", indications = "")
        )

    # da testare
    def feed_tamagochi(self, state: State) -> State:
        """Generate detailed recipes using Llama via Groq."""
        if state.error:return state
        client : AIAssistant = self.clients["Let's make a recipe!"]
        try:
            dish_description : DishDescription = client.chat({"chat_input":state.chat_input, "history":state.history}, [DishDescription])  
            print("Menu generated successfully.")
            return State(chat_input=state.chat_input,dishes=dish_description)
        except Exception as e:
            print(f"Failed to generate recipe (attempt {attempts + 1}/3):", str(e))
            temperature += 0.1
            attempts += 1
        return State(
            chat_input=state.chat_input,
            dishes=DishDescription(emoji = "", name = "", what_i_like_about_it = "", indications = "")
        )

    def create_recipe_graph(self):
        """Create the LangGraph workflow with conditional branching."""
        # Ritorno dell'errore in caso di mancata API key
        workflow = Graph()
        # Add nodes
        workflow.add_node("generate_recipe", self.generate_recipe)
        workflow.add_edge(START, "generate_recipe")
        workflow.add_edge("generate_recipe", END)
        # # Set entry point
        # workflow.set_entry_point(START)
        self.recipe_graph = workflow.compile()

    def create_feed_me_graph(self):
        """Create the LangGraph workflow with conditional branching."""
        workflow = Graph()
        # Add nodes
        workflow.add_node("feed_tamagochi", self.feed_tamagochi)
        workflow.add_edge(START, "feed_tamagochi")
        workflow.add_edge("feed_tamagochi", END)
        # Set entry point
        workflow.set_entry_point(START)
        self.feed_me_graph = workflow.compile()

    def process_recipe_graph(self, state : State) -> State:
        self.create_recipe_graph()
        new_state = self.recipe_graph.invoke(state)
        return new_state
        # self.state = new_state
        # return self.state

    def process_feed_me_graph(self, state : State) -> State:
        self.create_feed_me_graph()
        return self.feed_me_graph.invoke(state)
        # self.state = new_state
        # return self.state


if __name__ == "__main__":
    tamagochi = TamagochiGraph()
    print(
        tamagochi
            .generate_recipe(State(chat_input="I want to cook something that is like pizza with potatoes and ham")
        )
    )