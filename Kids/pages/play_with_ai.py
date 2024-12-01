import streamlit as st
import os
from functools import partial
from PIL import Image

from Classes.KidsAgents import State, TamagochiGraph, DishDescription

tamagochi = TamagochiGraph()

def header():
    imgs = {}
    for imgs_path in (images_names_with_ext := os.listdir(base_folder:="Kids/imgs/")):
        with Image.open(os.path.join(base_folder, imgs_path)) as f:
            img = f.resize((125, 125))
            imgs[os.path.basename(imgs_path).removesuffix('.png')] = img

    st.title("Pikabite")
    cols = st.columns(3)
    with cols[0]:
        icon_name = st.selectbox(label = "KID", options = [img_no_ext.removesuffix('.png') for img_no_ext in images_names_with_ext])
        st.session_state.nickname = icon_name
    with cols[1]:st.image(image = imgs[icon_name])
    with cols[2]:st.header("LET'S PLAY TOGETHER!")

def agent_button_to_choose():
    cols = st.columns(2)
    agent_choosed = st.selectbox("What will we do?", ["Let's make a recipe!", "Feed me!"])
    pass

def show_llm_recipe(dish : DishDescription):
    st.title(dish.emoji + "\n" + dish.name)
    st.text_area("What i think about this recipe", dish.what_i_like_about_it, disabled=True)
    st.text_area("Indications 4 a diet", dish.indications, disabled=True)

def chat():
    # Initialize chat history
    # Display chat messages from history on app rerun
    if "state" not in st.session_state:
        
        st.session_state.state = State(
            nickname = st.session_state.nickname,
            chat_input = "",
            dishes = []
            # history: str | None = "",
            # error: str = None
        )

    for dish in st.session_state.state.dishes:
        show_llm_recipe(dish)
    # React to user input
    if chat_message := st.chat_input("Fai una domanda all'AI?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(chat_message)
        # Add user message to chat history
        with st.spinner("Thinking..."):
            actual_state = st.session_state.state
            actual_state.chat_input = chat_message

            new_state = tamagochi.process_recipe_graph(actual_state)
            st.session_state.new_state = new_state
            show_llm_recipe(new_state.dishes[-1])
            st.balloons()
    
    # st.write('Salvare la ricetta?')
    # cols = st.columns(2)
    # with cols[0]:
    #     if st.button("Sì"):
    #         st.session_state.state = st.session_state.new_state
    #         st.balloons()
    #         from time import sleep
    #         sleep(2)
    #         st.rerun()
    # with cols[1]:
    #     if st.button("No"):
    #         st.rerun()

header()
agent_button_to_choose()
chat()

    