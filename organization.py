import networkx as nx
from pyvis.network import Network
import streamlit as st
import pandas as pd
import math

# Function to create and display the network graph
def create_network_graph(facilities_df, emissions_df):
    nx_graph = nx.Graph()

    # Central node representing the main company
    nx_graph.add_node('Main Company', size=30, title='Main Company', group=1)

    # Adding secondary nodes (facilities)
    for _, row in facilities_df.iterrows():
        facility_id = row['FacilityID']
        facility_name = row['FacilityName']
        nx_graph.add_node(facility_id, size=20, title=facility_name, group=2)
        nx_graph.add_edge('Main Company', facility_id)

    # Adding tertiary nodes (emissions)
    for index, row in emissions_df.iterrows():
        
        facility_id = row['FacilityID']
        emission_value = row['Emission value(tCO2e)']
        emission_id = f'Emission_{facility_id}_{index}'  # Unique ID for each emission
        # Scale the node size based on emission value, using a logarithmic scale
        node_size = max(20, math.log(emission_value + 1) * 20)
        nx_graph.add_node(emission_id, size=node_size, title=f'Emission: {emission_value}', group=3)
        nx_graph.add_edge(facility_id, emission_id)

    nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", select_menu=True, filter_menu=True)
    nt.from_nx(nx_graph)
    nt.toggle_physics(True)
    nt.barnes_hut()
    nt.save_graph('nx.html')  # Save the graph to an HTML file
    nt.show('nx.html',notebook=False)

    
# Streamlit UI
st.title('Network Graph Visualization')

# Upload buttons for CSV files
facilities_file = st.file_uploader("Upload the 'List of Facilities' CSV", type=['csv'])
emissions_file = st.file_uploader("Upload the 'Facilities and their Emissions' CSV", type=['csv'])

# DataFrames to hold the CSV data
facilities_df = None
emissions_df = None

# Read the uploaded CSV files into DataFrames
if facilities_file:
    facilities_df = pd.read_csv(facilities_file)
    st.write("Facilities data:", facilities_df)

if emissions_file:
    emissions_df = pd.read_csv(emissions_file)
    st.write("Emissions data:", emissions_df)

# Button to generate the network graph
if st.button('Show Network Graph'):
    if facilities_df is not None and emissions_df is not None:
        st.write("Generating the network graph...")
        create_network_graph(facilities_df, emissions_df)
    else:
        st.write("Please upload both CSV files to generate the network graph.")

st.write("Press the button to generate and display the network graph.")
