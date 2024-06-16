import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
import hmac
from dotenv import load_dotenv
load_dotenv()


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





st.title("🧨 Problem Maker")
#api_key = st.sidebar.text_input("Enter your Anthropic API key:", type="password", value="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")
    # Define the prompt template
prompt_template = "Complete the problem statement elements below based on this {problem}. The detailed problem: \n###Introduction: Briefly describes the problem, setting the context for a deeper understanding of the issue at hand.\n###Background: Provides the historical context, the circumstances that have led to the problem, and any previous attempts to solve the issue. This section may include data, research findings, or a summary of relevant events.\n###Problem Description: Clearly and specifically describes the problem, including who it affects and in what ways. It should detail the symptoms of the problem and its impact on stakeholder\n###Scope: Outlines the boundaries of the problem, including what is and isn't included within the scope of the issue. This helps to focus the problem statement on a specific area of concern.\n\n ###Factors Involed: Factors Influencing the Problem: Identifies the internal and external factors contributing to the problem. This can include organizational, environmental, societal, technological, or individual factors that affect the issue."
multi_markdown = """      
        :blue-background[The better you articulate your problem, the better the problem solver will do. Edit this freely after you get a boilerplate response.]    
        **Introduction:** Briefly describes the problem, setting the context for a deeper understanding of the issue at hand.  
        **Background:** Provides the historical context, the circumstances that have led to the problem, and any previous attempts to solve the issue. This section may include data, research findings, or a summary of relevant events.  
        **Problem Description:** Clearly and specifically describes the problem, including who it affects and in what ways. It should detail the symptoms of the problem and its impact on stakeholder.  
        **Scope:** Outlines the boundaries of the problem, including what is and isn't included within the scope of the issue. This helps to focus the problem statement on a specific area of concern.   
        **Factors Involed:** Factors Influencing the Problem: Identifies the internal and external factors contributing to the problem. This can include organizational, environmental, societal, technological, or individual factors that affect the issue.
        """
st.markdown(multi_markdown)
def generate_response(problem):
    prompt = PromptTemplate.from_template(prompt_template)
    model = ChatAnthropic(model="claude-3-sonnet-20240229")
    chain = prompt | model
    response= chain.invoke({"problem": problem})
    return response.content

def main():
    st.title("Problem Maker")
    st.write("Enter a simple problem statement.")
    st.write("The return will be a proper problem definition. Edit from there.")

    
    problem = st.text_area("Enter your problem:")
    
    if st.button("Define Problem"):
        if problem.strip():
            response = generate_response(problem)
            st.write("Problem Statement:")
            st.write(response)
        else:
            st.warning("Please enter a problem.")

if __name__ == "__main__":
    main()
