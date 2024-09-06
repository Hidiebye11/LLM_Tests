from urllib.error import URLError

import altair as alt
import pandas as pd
from groq import Groq
import streamlit as st
from streamlit.hello.utils import show_code
import openai


def hide_viewer_badge():
    hide_script = """
    <script>
    window.addEventListener('load', function() {
        var elementsToHide = document.querySelectorAll('[class^="viewerBadge"]');
        elementsToHide.forEach(function(element) {
            element.style.display = 'none';
        });
    });
    </script>
    """
    st.markdown(hide_script, unsafe_allow_html=True)


#Remove sidebar
st.set_page_config(
        page_title="GHG Guru Bot",
        page_icon="🌿",
        initial_sidebar_state="collapsed",
        layout="wide",
    )

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
    [class*="viewerBadge"] {
    display: none !important;}
</style>

""",
    unsafe_allow_html=True,
)


hide_viewer_badge()


# Initialize OpenAI API
#openai.api_key = st.secrets["OPENAI"]
openai.api_key = "sk-proj-tjFnCMeeftEL21dnCP3PT3BlbkFJH9csMMDIpGXt14GGyrnk"
assistantID = "asst_TuFXyBrxmjK1BhtfueaHK6YM"



def generate_response(prompt):
    message = openai.beta.threads.messages.create(
    thread_id=st.session_state.thread.id,
    role="user",
    content=prompt)

    run = openai.beta.threads.runs.create(
    thread_id=st.session_state.thread.id,
    assistant_id=assistantID,
    )
    while run.status != 'completed':
        run = openai.beta.threads.runs.retrieve(
        thread_id=st.session_state.thread.id,
        run_id=run.id
        )
    else:
        messages = openai.beta.threads.messages.list(
        thread_id=st.session_state.thread.id,
        order = "asc",
        after = message.id
        )
        result = messages.data[0].content[0].text.value
        return result

if "thread" not in st.session_state.keys():
    st.session_state.thread = openai.beta.threads.create()

if "assistant" not in st.session_state.keys():
    st.session_state.assistant = openai.beta.assistants.retrieve("asst_TuFXyBrxmjK1BhtfueaHK6YM")

if "dmessages" not in st.session_state.keys():
    st.session_state.dmessages = [{"role": "assistant", "content": "How may I help you?"}]

st.header("GHG Guru AI Demo")

# Display chat messages
for message in st.session_state.dmessages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"],  unsafe_allow_html=True)

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.dmessages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.dmessages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt) 
            st.markdown(response, unsafe_allow_html=True) 
    message = {"role": "assistant", "content": response}
    st.session_state.dmessages.append(message)