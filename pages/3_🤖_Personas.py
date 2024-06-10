import streamlit as st
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
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


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



load_dotenv()
# Set Streamlit page configuration
st.set_page_config(page_title='🤖 Chat with personas', layout='wide')
st.title("🤖 Chat with personas")

# Different personas

personas = {
   "philosopher": "You are a deep thinker who loves to ponder life's big questions and engage in intellectual discussions. You often quote famous philosophers and enjoy exploring abstract concepts.",
   
   "comedian": "You are a witty jokester who loves to make people laugh. You have a vast repertoire of jokes, puns, and humorous anecdotes that you enjoy sharing with others. Your goal is to bring a smile to everyone's face.",
   
   "motivator": "You are an enthusiastic and supportive cheerleader who loves to encourage and inspire others. You have a positive outlook on life and always find the silver lining in any situation. Your mission is to help people reach their full potential.",
   
   "artist": "You are a creative soul who sees beauty in everything. You love to discuss various forms of art, from painting and sculpture to music and poetry. You have a unique perspective on the world and enjoy sharing your artistic insights with others.",
   
   "adventurer": "You are a thrill-seeker who loves to explore new places and try new things. You have a wealth of exciting stories to share about your adventures around the globe. You inspire others to step out of their comfort zones and embrace the unknown.",
    
    "Product Guru": "Ask about the product to be launched (or for a product that the AI should do a websearch for)? Then, using that information, go step-by-step through the following: \n 1) First, list who you think the potential customers are and why they might buy the product, and the one customer group to focus on. Ask if the user has any corrections. \n 2) Next create an email marketing campaign for the product for that group. That should consist of three emails to induce demand, you should provide the entire text of the emails. Fill in all the details but bold words that you are making assumptions about (explain why they are bolded to the user). Give a schedule for when they should be sent.\n3) When done with the emails, create a website strategy for a single launch page. Ask the user for approval.\n4) Build a simple landing page for the launch. This should be a ZIP file that includes HTML, CSS, and javascript, and also at least one image you create. The material should be complete, not placeholders. Make it look nice, consider creating an image for it. You should give the entire ZIP file. Ask if the user has any suggestions or needs help hosting the content.\n5) Finally, outline a social media campaign, including posts for Twitter, Facebook, and Instagram"
}

# Sidebar info
with st.sidebar:
    st.markdown("## Inference Parameters")
    TEMPERATURE = st.slider("Temperature", min_value=0.0,
                            max_value=1.0, value=0.1, step=0.1)
    TOP_P = st.slider("Top-P", min_value=0.0,
                      max_value=1.0, value=0.9, step=0.01)
    TOP_K = st.slider("Top-K", min_value=1,
                      max_value=500, value=10, step=5)
    MAX_TOKENS = st.slider("Max Token", min_value=0,
                           max_value=2048, value=1024, step=8)
    MEMORY_WINDOW = st.slider("Memory Window", min_value=0,
                              max_value=10, value=3, step=1)
    # Add a dropdown for personas
    selected_persona = st.selectbox("Select a Persona", list(personas.keys()))

DEFAULT_CLAUDE_TEMPLATE = f"""The following is a friendly conversation between a human and an AI. The AI is {personas[selected_persona]}.

Current conversation:
{{history}}
Human: {{input}}
Assistant:"""



CLAUDE_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=DEFAULT_CLAUDE_TEMPLATE)

INIT_MESSAGE = {"role": "assistant", "content": "Hi! Select a persona on the left, at the bottom. Ask me a question"}
# Initialize the ConversationChain


def init_conversationchain():
    model_kwargs = {'temperature': TEMPERATURE,
                    'top_p': TOP_P,
                    'top_k': TOP_K,
                    'max_tokens_to_sample': MAX_TOKENS}

    llm = ChatAnthropic(model="claude-3-haiku-20240307", 
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        max_tokens_to_sample=MAX_TOKENS
        )


    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationBufferWindowMemory(
            k=MEMORY_WINDOW, ai_prefix="Assistant", chat_memory=StreamlitChatMessageHistory()),
        prompt=CLAUDE_PROMPT
    )

    # Store LLM generated responses

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [INIT_MESSAGE]

    return conversation


def generate_response(conversation, input_text):
    return conversation.run(input=input_text)


# Re-initialize the chat
def new_chat():
    st.session_state["messages"] = [INIT_MESSAGE]
    st.session_state["langchain_messages"] = []
    conv_chain = init_conversationchain()


# Add a button to start a new chat
st.sidebar.button("New Chat", on_click=new_chat, type='primary')

# Initialize the chat
conv_chain = init_conversationchain()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User-provided prompt
prompt = st.chat_input()

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        # print(st.session_state.messages)
        with st.spinner("Thinking..."):
            response = generate_response(conv_chain, prompt)
            st.markdown(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)