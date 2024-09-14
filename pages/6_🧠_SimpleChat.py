import streamlit as st
import requests
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


#if not check_password():
    st.stop() 



API_URL = "https://agents.ideaatoms.com/api/v1/prediction/29777652-d56e-4a58-af53-609d66780e16"

def query(payload):
    headers = {"Authorization": "Bearer ioOxThzoUOISZGIe1MDKyz/ohO1V6KPjNVeW1tDa8HQ="}
    response = requests.post(API_URL, json=payload, headers=headers)

    return response.json()

st.title('Simple Chat App with the OpenAI model 4.o')

user_input = st.text_input("Type your message here...")
button_clicked = st.button('Send')

if button_clicked and user_input:
    output = query({
        "question": user_input,
    })
    st.write(output['text'])
else:
    st.write("Welcome to the Simple Chat App. Please type your message and click 'Send'. It's a very basic app, don't expect too much! What it is demonstrating is calling a backend API to another service that proxies the Open AI model.")