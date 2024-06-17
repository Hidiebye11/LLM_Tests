# Import the required libraries
import streamlit as st
from phi.assistant import Assistant

from phi.tools.yfinance import YFinanceTools
from groq import Groq

# Set up the Streamlit app
st.title("AI Investment Agent 📈🤖")
st.caption("This app allows you to compare the performance of two stocks and generate detailed reports.")

groq_api = st.secrets["GROQ"]

client = Groq(
    api_key=groq_api,
)
def generate_response(prompt_input):
    userPrompt = {
        "role": "user",
        "content": "Using all the financial tools and financial knowledge you have"
        + ", compare the following stocks and give appropriate financial advise on what to do with the stock:"
        + prompt_input,
    }
    messageLog = [userPrompt]

    try:
        chat_completion = client.chat.completions.create(
            messages=messageLog,
            model="llama3-8b-8192",
        )

    except:
        return "Sorry I cannot repond right now!"
    return chat_completion.choices[0].message.content


# Input fields for the stocks to compare
stock1 = st.text_input("Enter the first stock symbol")
stock2 = st.text_input("Enter the second stock symbol")

if stock1 and stock2:
    # Get the response from the assistant
    query = f"Compare {stock1} to {stock2}. Use every tool you have."
    response = generate_response(query)
    st.write(response)