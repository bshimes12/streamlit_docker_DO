import streamlit as st
import requests
import hmac
import json

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


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

API_URL = "https://agents.ideaatoms.com/api/v1/prediction/6ad5b535-4fe0-4fba-9975-5818372c0ff2"
headers = {"Authorization": "Bearer ioOxThzoUOISZGIe1MDKyz/ohO1V6KPjNVeW1tDa8HQ="}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    print("Status code:", response.status_code)
    print("Response text:", response.text)
    return response.json()

def json_to_markdown(data, indent=0):
    markdown = ""
    indent_str = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            markdown += f"{indent_str}**{key}**:\n"
            if isinstance(value, (dict, list)):
                markdown += json_to_markdown(value, indent + 1)
            else:
                markdown += f"{indent_str}- {value}\n"
    elif isinstance(data, list):
        for i, item in enumerate(data):
            markdown += f"{indent_str}- Item {i+1}:\n"
            markdown += json_to_markdown(item, indent + 1)
    else:
        markdown += f"{indent_str}- {data}\n"

    return markdown

st.title('Researcher Toolkit')

user_input = st.text_input("Type ONLY an individual or family name...")
button_clicked = st.button('Send')

if button_clicked and user_input:
    output = query({
        "question": user_input,
    })
    markdown = json_to_markdown(output)
    st.markdown(markdown)
    st.json(output)