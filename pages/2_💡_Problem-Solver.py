import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.chains.llm import LLMChain
from langchain_anthropic import ChatAnthropic
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





st.title("💡 Problem Solver")


def main():
    
# Sidebar input for API key
    #api_key = st.sidebar.text_input("Enter your Anthropic API key:", type="password", value="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")

 
        # Dropdown to select the model
    model_options = {
        "Claude 3.5 Sonnet - Latest and Greatest": "claude-3-5-sonnet-20240620",
        "Claude 3 Opus - Advanced/Slower/Expensive": "claude-3-opus-20240229",
        "Claude 3 Haiku - Good/Fast/Affordable": "claude-3-haiku-20240307",
        "Claude 3 Sonnet - Basic/Cheap/Affordable": "claude-3-sonnet-20240229",
        "Claude 2.1 - Legacy/Basic/Cheap": "claude-2.1"
    }
    model_name = st.sidebar.selectbox("Select your model:", list(model_options.keys()))
    myModel = model_options[model_name]

    try:
        llm = ChatAnthropic(model=myModel)
    except TypeError as e:
        st.error(f"Error initializing ChatAnthropic: {e}")
        st.stop()

    solutions_template = """
    You are a careful, analytical thinker with experience in solving problems. You offer advice that is creative and achievable. Think step by step and make helpful solutions.
    Generate {num_solutions} distinct solutions for <problem>{problem}</problem>. 
    Consider factors like {factors}. 
    Solutions:
    """
    solutions_prompt = PromptTemplate(
        template=solutions_template,
        input_variables=["problem", "factors", "num_solutions"]
    )
    evaluation_template = """
    Evaluate each solution in {solutions} by analyzing pros, cons, feasibility, and probability of success.

    Evaluations:
    """
    evaluation_prompt = PromptTemplate(
        template=evaluation_template,
        input_variables=["solutions"]
    )
    reasoning_template = """
    For the most promising solutions in {evaluations}, explain scenarios, implementation strategies, partnerships needed, and handling potential obstacles. 
    Enhanced Reasoning: 
    """
    reasoning_prompt = PromptTemplate(
        template=reasoning_template,
        input_variables=["evaluations"]
    )
    ranking_template = """
    Based on the evaluations and reasoning, rank the solutions in {enhanced_reasoning} from most to least promising.
    If you doubt anything about the solutions, write questions that are needed to address those doubts.
    Ranked Solutions:
    """
    ranking_prompt = PromptTemplate(
        template=ranking_template,
        input_variables=["enhanced_reasoning"]
    )

    

    solutions_chain = LLMChain(
        llm=llm,
        prompt=solutions_prompt,
        output_key="solutions",
        #verbose=True,
    )
    evaluation_chain = LLMChain(
        llm=llm,
        prompt=evaluation_prompt,
        output_key="evaluations",
        #verbose=True,
    )
    reasoning_chain = LLMChain(
        llm=llm,
        prompt=reasoning_prompt,
        output_key="enhanced_reasoning",
        #verbose=True,
    )
    ranking_chain = LLMChain(
        llm=llm,
        prompt=ranking_prompt,
        output_key="ranked_solutions",
        #verbose=True,
    )
    tot_chain = SequentialChain(
        chains=[solutions_chain, evaluation_chain, reasoning_chain, ranking_chain],
        input_variables=["problem", "factors", "num_solutions"],
        output_variables=["ranked_solutions","enhanced_reasoning","evaluations","solutions"],
        #verbose=True,
        #return_all=True
    )
    # Streamlit input for problem details
    st.title("Advanced Tree of Thought Solver")
    problem = st.text_area("Enter the problem description:", "")
    factors = st.text_area("Enter the factors to consider:", "")
    num_solutions = st.number_input("Enter the number of solutions to generate:", min_value=1, value=2)
    
    if st.button("Solve"):
        if problem and factors:
            # Run the SequentialChain
            result = tot_chain.invoke(
                {
                    "problem": problem,
                    "factors": factors,
                    "num_solutions": num_solutions
                }
            )
            # Display the ranked solutions
            st.subheader("Solutions")
            st.write(result["solutions"])
            st.subheader("Evaluations")
            st.write(result["evaluations"])
            st.subheader("Enhanced Reasoning")
            st.write(result["enhanced_reasoning"])
            st.subheader("Ranked Solutions")
            st.write(result["ranked_solutions"])
# Display the ranked solutions
            
            

        else:
            st.error("Please provide both problem description and factors.")

if __name__ == "__main__":
    main()