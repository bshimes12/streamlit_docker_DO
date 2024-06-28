import os 
from dotenv import load_dotenv, find_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.output_parsers import ReActJsonSingleInputOutputParser
from langchain.tools.render import render_text_description_and_args
from langchain_openai import ChatOpenAI
import streamlit as st 
from langchain_community.agent_toolkits.amadeus.toolkit import AmadeusToolkit
import pandas as pd
from datetime import datetime
import hmac

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





toolkit = AmadeusToolkit()
tools = toolkit.get_tools()

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

prompt = hub.pull("hwchase17/react-json")
agent = create_react_agent(
    llm,
    tools,
    prompt,
    tools_renderer=render_text_description_and_args,
    output_parser=ReActJsonSingleInputOutputParser()
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

def display_flight_results(flights):
    st.header("Flight Search Results")
    
    for flight in flights:
        if isinstance(flight, dict) and 'price' in flight:
            st.subheader(f"Flight Option")
            
            # Price information
            price = flight['price']
            st.write(f"**Price:** {price['total']} {price['currency']}")
            
            # Flight segments
            for j, segment in enumerate(flight['segments'], 1):
                st.write(f"**Segment {j}:**")
                
                # Departure
                dep = segment['departure']
                dep_time = datetime.fromisoformat(dep['at'])
                st.write(f"Departure: {dep['iataCode']} ({dep.get('terminal', 'N/A')}) at {dep_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Arrival
                arr = segment['arrival']
                arr_time = datetime.fromisoformat(arr['at'])
                st.write(f"Arrival: {arr['iataCode']} ({arr.get('terminal', 'N/A')}) at {arr_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Flight details
                st.write(f"Flight: {segment['carrier']} {segment['flightNumber']}")
            
            st.write("---")  # Separator between flight options

    # Create a summary dataframe
    summary_data = []
    for flight in flights:
        if isinstance(flight, dict) and 'price' in flight:
            summary_data.append({
                'Price': f"{flight['price']['total']} {flight['price']['currency']}",
                'Airline': flight['segments'][0]['carrier'],
                'Departure': flight['segments'][0]['departure']['at'],
                'Arrival': flight['segments'][-1]['arrival']['at'],
                'Stops': len(flight['segments']) - 1
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.subheader("Summary")
        st.dataframe(summary_df)
    else:
        st.write("No flight data available to summarize.")

st.title("Smarter way to explore flights")
st.markdown("Example: Flights from boston to paris 7/27/24 in USD   ")
st.markdown("(you have to experiment with the search parameters 😉)")
question_input = st.text_area("Enter your flight-related inquiry below.")
if st.button("Submit"):
    try:
        answer = agent_executor.invoke({"input": question_input})
        
        # Extract flight data from the intermediate steps
        flights = None
        for step in answer['intermediate_steps']:
            if isinstance(step[1], list) and len(step[1]) > 0 and isinstance(step[1][0], dict) and 'price' in step[1][0]:
                flights = step[1]
                break
        
        if flights:
            st.markdown(answer['output'])
            display_flight_results(flights)
        else:
            st.markdown("# Summary")
            st.markdown(answer['output'])
        
        st.markdown("# Full Response Details")
        st.json(answer)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Full error traceback:")
        st.exception(e)