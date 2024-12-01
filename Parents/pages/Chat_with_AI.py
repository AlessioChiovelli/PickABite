from toolhouse import Toolhouse
from openai import OpenAI
import streamlit as st
import os


client = OpenAI(
    api_key=os.environ.get('AI_ML_API_KEY'),
    # base_url="https://api.groq.com/openai/v1",
    base_url="https://api.aimlapi.com/v1",
  )
def simple_chat_page():
    st.title("Manage the kids info with the LLM")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # React to user input
    if chat_message := st.chat_input("Fai una domanda all'AI?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(chat_message)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": chat_message})
        with st.spinner("Sto pensando..."):
            th = Toolhouse(access_token=os.getenv("TOOLHOUSE_API_KEY"))
            completion = client.chat.completions.create(
                    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": """
                            You need to manage the memory of the llm on the alimentary plan of the user's childrens.
                            Use the toolhouse to manage the memory of the llm.
                            You will most probably get passed the child nickname. 
                            Use it as the key to create, read, update or delete the memory of the llm.
                            If you can't find it or there is a problem, warn the user for the missing data.

                            Explain what you have done. 
                            
                            For example:
                                - If you have created a new memory, explain what you have stored.
                                - If you have deleted something a new memory, explain what you have deleted.
                                - If you have updated a memory, explain what you have updated.
                                - If you have read a memory, give a detailed summary of what yoy have read.

                            """
                        },
                        {"role": "user", "content": chat_message},
                    ],
                    temperature=0.7,
                    tools = th.get_tools(
                        # bundle = "bundle_name"
                    ),
                )
            result_tools = th.run_tools(completion)
            print(result_tools)
            response_completition = [str(msg.message.content) for msg in completion.choices]
            response_tools = [str(msg["content"]) for msg in result_tools]

            response = (
                client
                .chat
                .completions
                .create(
                    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                    messages=[
                        {"role": "user", "content": """
                        An LLM like you has done some actions on a DB, and it was asked for this:
                            - If it created a new memory, he had to explain what he did store.
                            - If it deleted something in his memory, he had to explain what he did deleted.
                            - If it updated something in his memory, he had to explain what he did update.
                            - If it read something in his memory, he had to explain what he read from it.
                        Summarize all these infos. Or propose a message that explains all the inputs you will be provided
                        If you don't have any, respond that you could't do the action you were asked for
                         
                        """},
                        {"role": "user", "content": "\n\n".join(response_completition + response_tools + [chat_message])}
                    ]
                )
                .choices[0]
                .message
                .content
            )
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
            # link_or_prompt_elements(keys_of_simulation_to_serve_to_ai)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})