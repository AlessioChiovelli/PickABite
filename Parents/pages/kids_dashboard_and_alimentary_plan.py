import streamlit as st
import os
from functools import partial
from PIL import Image
from openai import OpenAI
import PyPDF2
import docx
from toolhouse import Toolhouse
from openai import OpenAI
from load_css import load_custom_css

os.makedirs("Kids/imgs", exist_ok=True)
load_custom_css("assets/style.css")


client = OpenAI(
    api_key=os.environ.get('AI_ML_API_KEY'),
    # base_url="https://api.groq.com/openai/v1",
    base_url="https://api.aimlapi.com/v1",
  )
th = Toolhouse(access_token=os.getenv("TOOLHOUSE_API_KEY"))

def read_file_content(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfFileReader(uploaded_file)
        text = ""
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
        return text
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    else:
        return None

def register_my_kid():
    st.title("Register your kid!")
    st.write("Your details are required to enable access and use of the app.")
    imgs = {}
    for imgs_path in os.listdir(base_folder:="Parents/imgs/"):
        with Image.open(os.path.join(base_folder, imgs_path)) as f:
            img = f.resize((125, 125))
            imgs[os.path.basename(imgs_path).removesuffix('.png')] = img

    disposition = {
        "Row 1" : {
            "Kid-Fullname" : partial(st.text_input, label = "Fullname", key = "input-form-kid-name", help = "The name you will see in the app, that won't be seen by the llm"),
            "Kid-Nickname" : partial(st.text_input, label = "Nickname", key = "input-form-kid-nickname", help = "The name the llm will use to remember the kids info"),
            "Gender" : partial(st.selectbox, label = "Gender", options = ["Male", "Female", "Other"]),

        },
        "Row 2" :{
            "Age" : partial(st.number_input, label = "Age", min_value = 6, max_value = 13, key = "input-form-kid-age"),
            "Height" : partial(st.number_input, label = "Height (cm)", min_value = 0.0, max_value = 150.0,  key = "input-form-kid-height"),
            "Weight" : partial(st.number_input, label = "Weight (kg)", min_value = 0.0, max_value = 100.0,  key = "input-form-kid-weight"),
        },
        "Row 3" :{
            "Kid-Icon" : partial(st.selectbox, label = "Kid-Icon", options = ["pikachu", ]),
        },
        "Row 4" :{
            "Spacer-1" : partial(st.text, body = ""),
            "Child buddy img" : partial(
                st.image, 
                image = img,
                # label = "Food plan", 
                # key = "alimentary-plan-upload"
            ),
            "Spacer-2" : partial(st.text, body = ""),
        }
    }

    for row_name, row_elements in disposition.items():
        row_cols = st.columns(len(row_elements))
        for col, (element_name, element) in zip(row_cols, row_elements.items()):
            with col:st.session_state[element_name] = element()
            
    
    food_plan_loaded = st.file_uploader(
        label = "Food plan", 
        type = ["pdf", "docx", "txt", "csv", "xlsx"], 
        key = "alimentary-plan-upload"
    )

    if food_plan_loaded:

        with st.spinner("Processing file..."):
            file_content = read_file_content(food_plan_loaded)
            if file_content:st.text_area("File Content filtered from llm", file_content, height=200)
            
        continue_button = st.button("Upload and continue")
        Kid_Fullname = st.session_state["Kid-Fullname"]
        Kid_Nickname = st.session_state["Kid-Nickname"]
        Gender = st.session_state["Gender"]
        Age = st.session_state["Age"]
        Height = st.session_state["Height"]
        Weight = st.session_state["Weight"]
        Kid_Icon = st.session_state["Kid-Icon"]
        Child_buddy_img = st.session_state["Child buddy img"]
        st.session_state["food_plan_loaded"] = food_plan_loaded
        if continue_button:
            img.save(f"Kids/imgs/{Kid_Fullname} - {Kid_Nickname}.png")
            
            user_prompt = "\n\n".join([
                str(Kid_Nickname), 
                str(Gender), 
                str(Age), 
                str(Height), 
                str(Weight),
                file_content
            ])


            completion = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """
                            You are an agent responsible of storing health informations and an alimentary plan about a kid. 
                            Store the infos.
                        """
                    },
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                tools = th.get_tools(),
            )
            th.run_tools(completion)
            st.success("Your kid has been registered successfully!")
            st.balloons()
            st.write("Here you will see the 2 alimentary plan the llm will use to remember the kids info")
            st.text_area("Filtered alimentary plan", completion.choices[0].message.content, height=200)

# register_my_kid()