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

API_URL = "https://agents.ideaatoms.com/api/v1/prediction/6ad5b535-4fe0-4fba-9975-5818372c0ff2"
headers = {"Authorization": "Bearer ioOxThzoUOISZGIe1MDKyz/ohO1V6KPjNVeW1tDa8HQ="}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

st.title('Researcher Toolkit')

user_input = st.text_input("Type ONLY an individual or family name...")
button_clicked = st.button('Send')

if button_clicked and user_input:
    output = query({
        "question": user_input,
    })
    st.write(output)