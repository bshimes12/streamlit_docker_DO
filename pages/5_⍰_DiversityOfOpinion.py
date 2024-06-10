

## python3 Diversity_of_tree_of_thought_Solver.py > the_statments.txt

from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import streamlit as st
import hmac
load_dotenv()




#llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
#llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo-0125")
#llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-0613")
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")


## Anthropic
#myModel="claude-3-opus-20240229"
#myModel="claude-3-haiku-20240307"
#myModel="claude-3-sonnet-20240229"
#myModel="claude-2.1"
#llm = ChatAnthropic(model=myModel)

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

def main():
    statement_template = """
    When I give you a {the_statement}, follow the <instruction> and output this <output> format as an example.
    <instruction>
    Tell me diverse opinions about the statement. Use “Agree” or “Disagree” then one-word or one-phrase criteria that describes their opinions. Provide a variety but very diverse viewpoints.
    </instruction>
    <output>
    1:“Stance”: “Agree”,
    “Criteria”: [“personal boundaries”, “autonomy”]
    2:“Stance”: “Disagree”,
    “Criteria”: [“transparency”, “trust”]
    </output>
    Viewpoints:
    """
    statement_prompt = PromptTemplate(
    template=statement_template,
    input_variables=["the_statement"]
    )
    Evaluate_template = """
    Evaluate each Stance in {the_viewpoints} and write a well thought out reason for this perspective as seen from the opinion holder based on the Criteria listed for each statement.
    Reasons:
    """
    evaluation_prompt = PromptTemplate(
    template=Evaluate_template,
    input_variables=["the_viewpoints"]
    )
    reasoning_template = """
    For each {reasons}, provide balanced and pursuasive counterpoint thoughts to be used to engage with this viewpoint. 
    counter-reasons: 
    """
    reasoning_prompt = PromptTemplate(
    template=reasoning_template,
    input_variables=["reasons"]
    )

    solutions_chain = LLMChain(
    llm=llm,
    prompt=statement_prompt,
    output_key="the_viewpoints",
    verbose=True
    )
    evalutation_chain = LLMChain(
    llm=llm,
    prompt=evaluation_prompt,
    output_key="reasons",
    verbose=True
    )
    reasoning_chain = LLMChain(
    llm=llm,
    prompt=reasoning_prompt,
    output_key="counter_reasons",
    verbose=True
    )
    tot_chain = SequentialChain(
    chains=[solutions_chain, evalutation_chain, reasoning_chain],
    input_variables=["the_statement"],
    output_variables=["the_viewpoints", "reasons", "counter_reasons"],
    verbose=True,
    return_all=True
    )


    # Streamlit input for problem details
    st.title("Diversity of Opinions")
    the_statement = st.text_area("Enter your opinion and discover a diversity of other opinions:", "")
    if st.button("Get Opinions"):
        if the_statement:
            # Run the SequentialChain
            result = tot_chain.invoke({
                "the_statement": the_statement,
            })
            # Display the ranked solutions
            st.subheader("Your Opinion")
            st.write(result["the_statement"])
            st.subheader("The Other Opinions")
            st.write(result["the_viewpoints"])
            st.subheader("Their Reasons")
            st.write(result["reasons"])
            st.subheader("Your Counter Reasons (Prepare to defend your opinion!)")
            st.write(result["counter_reasons"])
        else:
            st.error("Please provide an opinion of your own.")

if __name__ == "__main__":
    main()