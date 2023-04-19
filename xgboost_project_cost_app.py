"""
Author: Ensun Pak
Organization: Four Analytics, Inc
Date: April 7, 2023
Function: Deployment of XGBoost model to predict project level cost with
Streamlit, data hosted on Github.
"""

# Import libraries
import streamlit as st
import numpy as np
import pandas as pd
import pickle

def load_pickle(file_name):
    """
    Helper function to load the trained artifacts from model development
    """
    with open("./files/" + file_name + ".p", "rb") as f:
        return pickle.load(f)
    
# Load the trained XGBoost model
model = load_pickle("xgboost3_project_cost")

# Load the mappers
line_items_dict = load_pickle("prj_line_items_dict")
median_dict = load_pickle("prj_median_dict")
avg_client_rscore = load_pickle("prj_avg_client_rscore_dict")
avg_client_cost = load_pickle("prj_mean_avg_client_cost_dict")
total_client_tix_count = load_pickle("prj_total_client_tix_dict")
line_items_list = load_pickle("prj_line_items_list")
line_items_list.insert(0, "None")

# Generate options for select box
client_list_rscore = avg_client_rscore.keys()
client_list_rscore = list(client_list_rscore)
client_list_rscore = client_list_rscore[:-1]
client_list_rscore.append("No client")

client_list_cost = avg_client_cost.keys()
client_list_cost = list(client_list_cost)
client_list_cost = client_list_cost[:-1]
client_list_cost.append("No client")

client_list_tix = total_client_tix_count.keys()
client_list_tix = list(client_list_tix)
client_list_tix = client_list_tix[:-1]
client_list_tix.append("No client")

client_list = set(client_list_rscore + client_list_cost + client_list_tix)
client_list = list(client_list)
client_list = sorted(client_list)

# Constructor class for each ticket created by the user
class Ticket:
    def __init__(self, cr_max,
                 cr_min,
                 crew_best,
                 crew_worst,
                 sqft,
                 q1=None,
                 q2=None,
                 q3=None,
                 q4=None,
                 q5=None,
                 q6=None,
                 q7=None,
                 q8=None):
        self.cr_max = cr_max
        self.cr_min = cr_min
        self.crew_best = crew_best
        self.crew_worst = crew_worst
        self.sqft = sqft
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4
        self.q5 = q5
        self.q6 = q6
        self.q7 = q7
        self.q8 = q8

st.set_page_config(layout="wide")
st.header("Purple Key - Ticket SP Project Cost Model POC App")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.write(":orange[Project client]")
    client_name = st.selectbox("Client name", client_list)

    st.write(":orange[Job details]")
    cr_max = st.slider("Crew Max", 0, 15, 5)
    cr_min = st.slider("Crew Min", 0, 15, 5)
    crew_best = st.text_input("Crew best (Labor hours)", 0)
    crew_worst = st.text_input("Crew Worst (Labor hours)", 0)
    sqft = st.text_input("Job sqft", 0)

with col2:
    st.write(":orange[Quotation details (line items only)]")
    q1 = st.selectbox("Quote item #1", line_items_list)
    q2 = st.selectbox("Quote item #2", line_items_list)
    q3 = st.selectbox("Quote item #3", line_items_list)
    q4 = st.selectbox("Quote item #4", line_items_list)
    q5 = st.selectbox("Quote item #5", line_items_list)
    q6 = st.selectbox("Quote item #6", line_items_list)
    q7 = st.selectbox("Quote item #7", line_items_list)
    q8 = st.selectbox("Quote item #8", line_items_list)


with col3:
    # Initialize and increment counter if the button is clicked
    if st.button("Add ticket to project"):
        ticket = Ticket(cr_max=float(cr_max),
                        cr_min=float(cr_min),
                        crew_best=float(crew_best),
                        crew_worst=float(crew_worst),
                        sqft=float(sqft),
                        q1=q1,
                        q2=q2,
                        q3=q3,
                        q4=q4,
                        q5=q5,
                        q6=q6,
                        q7=q7,
                        q8=q8)

        if "ticket_counter" in st.session_state.keys():
            st.session_state["ticket_counter"] += 1
            st.session_state["session_tickets"].append(ticket)
        else:
            st.session_state["ticket_counter"] = 1
            st.session_state["session_tickets"] = [ticket]

    # Check if button has been clicked, return refreshed value
    total_crew_best = 0
    total_crew_worst = 0
    total_cr_min = 0
    total_cr_max = 0
    total_sqft = 0
    all_line_items = []
    line_item_count = {}
    if "ticket_counter" in st.session_state.keys():
        st.write("Number of tickets: ", f"{st.session_state.ticket_counter}")
        st.write("Project client: ", client_name)
        for obj in st.session_state.session_tickets:
            total_cr_min += obj.cr_min
            total_cr_max += obj.cr_max
            total_crew_best += obj.crew_best
            total_crew_worst += obj.crew_worst
            total_sqft += obj.sqft
            temp_list = [obj.q1, obj.q2, obj.q3, obj.q4, obj.q5, obj.q6, obj.q7, obj.q8]
            all_line_items.append([item for item in temp_list if item != "None"])
        st.write("total_cr_max: ", f"{total_cr_max}")
        st.write("total_cr_min: ", f"{total_cr_min}")
        st.write("total_crew_best: ", f"{total_crew_best}")
        st.write("total_crew_worst: ", f"{total_crew_worst}")
        st.write("total_sqft: ", f"{total_sqft}")
        st.write("line_item_count: ", all_line_items)
    else:
        # For diagnostics only - this should be transparent in the app
        st.write("Number of tickets: ", f"{0}")
        st.write("Project client: ")
        st.write("total_cr_max: ", f"{0}")
        st.write("total_cr_min: ", f"{0}")
        st.write("total_crew_best: ", f"{0}")
        st.write("total_crew_worst: ", f"{0}")
        st.write("total_sqft: ", f"{0}")
        st.write("line_item_count: ")

# Process the inputs
mean_crew = (total_cr_max + total_cr_min) / 2
mean_client_rscore_per_ticket = avg_client_rscore[client_name]
mean_client_cost_per_ticket = avg_client_cost[client_name]
total_client_tix_count = total_client_tix_count[client_name]

final_line_item = []
line_items = [item for items in all_line_items for item in items if item != "None"]

for item in line_items:
    if item in line_item_count.keys():
        line_item_count[item] += 1
    else:
        line_item_count[item] = 1

for item, count in line_item_count.items():
    final_line_item.append(str(count) + item)
final_line_item = "_".join(final_line_item)

line_item_mean_enc = line_items_dict.get(final_line_item, np.median(list(line_items_dict.values())))

# Construct array from user input, XGboost requires column names because it
# was trained with column names
new_data = [total_cr_max, mean_crew, line_item_mean_enc, total_cr_min, total_crew_best, total_crew_worst, total_sqft,
            mean_client_rscore_per_ticket, mean_client_cost_per_ticket, total_client_tix_count]

data_labels = ["total_cr_max", "mean_crew", "line_item_mean_enc", "total_cr_min", "total_crew_best", "total_crew_worst", "total_sqft", 
               "mean_client_rscore_per_ticket", "mean_client_cost_per_ticket", "total_client_tix_count"]

new_data = pd.DataFrame(new_data).T
new_data.columns = data_labels

st.write("line_item_mean_enc: ", line_item_mean_enc)
st.write("mean_crew: ", mean_crew)
st.write("mean_client_rscore_per_ticket", mean_client_rscore_per_ticket)
st.write("mean_client_cost_per_ticket", mean_client_cost_per_ticket)
st.write("total_client_tix_count", total_client_tix_count)

# Predict the input from the user
predict = model.predict(new_data)

# Display column
with col4:
    st.write("##### Predicted project cost: $", f"{predict[0]:,.2f}")
