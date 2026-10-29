import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


try:
    _icon = Image.open('logo_mr.png')
except Exception:
    _icon = "🖼️"
st.set_page_config(page_title="Análisis de Imagen · Miguel Ruiz", page_icon=_icon, layout="centered", initial_sidebar_state="collapsed")

# ---- Estilo personalizado: paleta azul petróleo + terracota (Miguel Ruiz) ----
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&family=Inter:wght@300;400;600&display=swap');
    .stApp {
        background: linear-gradient(135deg, #1b3a4b 0%, #14303d 100%);
        color: #e8eef0;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stToolbar"] { right: 1rem; }
    .stApp, .stApp p, .stApp li, .stApp span, .stApp label,
    .stMarkdown, [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {
        color: #e8eef0 !important;
    }
    h1, h2, h3, h4 { font-family: 'Montserrat', sans-serif !important; color: #e07a5f !important; }
    .stTextInput input, .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input {
        background-color: #f3f6f7 !important; color: #14303d !important;
    }
    input::placeholder, textarea::placeholder { color: #5c7079 !important; }
    [data-testid="stNotification"] * { color: #14303d !important; }
    section[data-testid="stSidebar"] { background: #12272f; }
    section[data-testid="stSidebar"] * { color: #e8eef0 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #e07a5f !important; }
    .stButton>button {
        background-color: #e07a5f; color: #fff !important; border-radius: 10px; border: none; font-weight: 600;
    }
    .stButton>button:hover { background-color: #c9583c; color: #fff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit page setup
st.markdown("<h2 style=\"font-family:'Montserrat', sans-serif; font-weight:700; color:#f2cc8f; margin-bottom:0;\">Miguel Ruiz</h2>", unsafe_allow_html=True)
st.title("Análisis de Imagen 🤖🏞️")
image = Image.open('OIG4.jpg')
st.image(image, width=350)
with st.sidebar:
    st.subheader("Este agente analiza el contenido de la imagen y responde tus preguntas.")
ke = st.text_input('Ingresa tu Clave de OpenAI', type="password")
#os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = ke


# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Carga una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded = True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Adiciona detalles sobre la imagen", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Adiciona contexto de la imagen aqui:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        # Optimized prompt for additional clarity and detail
        #prompt_text = (
        #    "You are a highly knowledgeable scientific image analysis expert. "
        #   "Your task is to examine the following image in detail. "
        #    "Provide a comprehensive, factual, and scientifically accurate explanation of what the image depicts. "
        #    "Highlight key elements and their significance, and present your analysis in clear, well-structured markdown format. "
        #    "If applicable, include any relevant scientific terminology to enhance the explanation. "
        #    "Assume the reader has a basic understanding of scientific concepts."
        #    "Create a detailed image caption in bold explaining in short."
        #    "The data is about electrical energy consumption and demand."
        #    "Write when occurs the major and minor consumption, date and hour when this be possible."
        #    "Explain always in spanish."
        #)

        prompt_text = ("Describe what you see in the image in spanish")
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            )
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model= "gpt-4o",
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/jpeg;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=300,
              )
            #response.choices[0].message.content
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
    
            # Display the response in the app
            #st.write(response.choices[0])
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
