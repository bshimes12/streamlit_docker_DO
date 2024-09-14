import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
from PIL import Image
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
    st.stop()  # Do not continue if check_password is not True.


def takeInput():
    load_dotenv()
    # Title
    st.title('Make me an Image')
    st.markdown("**Example**: hyper-realistic, family beach scene with epic sandcastle dominating background.   ")
    st.markdown("**Example**: Simplified business reverse logistics diagram illustrating shipment from 3 entities labelled house 1, house 2, house 3 and receipt of goods at 2 labeled Club A, Club B.   ")
    st.markdown("**Example**: Create a fantastical yet realistic and highly intricate image of a vibrant beach party. The scene is with people enjoying various activities: some are swimming in the sparkling blue water, others are playing beach volleyball, building elaborate sandcastles, or lounging under colorful umbrellas.    ")
    st.markdown("**Example**: Style of Monet: summer afternoon on the patio next to your best dog."   )
    st.markdown("**Example**: Create a sleek, minimalist logo representing Dog Days, a backyard dog hangout.   ")
    st.markdown("**Example**: Establish a magical academy surrounded by enchanted forests, where young wizards, witches, and sorcerers learn the elements and master spells and potions.   ")
    
    
    # Ask for the API key
    #api_key = st.text_input("Enter your OpenAI API key:", type="password")
    api_key = os.getenv("OPENAI_API_KEY")

    # Ask for the model choice
    model_choice = st.selectbox(
        "Which Dall E model would you like to use? ",
        ("DALL·E 3", "DALL·E 2"),
        index=None,
        key="model_choice",
        placeholder="Select DALL·E model",
    )
    # Display user choice
    st.write('You selected:', model_choice)

    # Logic if no model is selected
    if model_choice == "DALL·E 3":
        model_choice = "dall-e-3"
    else:
        model_choice = "dall-e-2"

    # Takes the user prompt

    prompt = st.text_input("Enter a prompt:", key="user_prompt_input", placeholder="hyper-realistic, photographic yacht racing, neck and neck around the buoy")

    return model_choice, prompt, api_key

def generateImage(client, model_choice, prompt):
    if st.button("Generate Image"):
        # create the image generation request
        response = client.images.generate(
            model=model_choice,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1 #This can be modified but currently DALL.E 3 only supports 1
        )
        image_url = response.data[0].url
        print("Generated Image URL:", image_url)

        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Display the image
        st.image(img)

from openai import OpenAI



model_choice, prompt, api_key = takeInput()
# Configure the client
client = OpenAI(api_key=api_key)
# generate image and display it
generateImage(client=client, model_choice=model_choice, prompt=prompt)