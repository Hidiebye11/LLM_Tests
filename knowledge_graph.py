import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np

# Streamlit app title
st.title("Company Supplier Knowledge Graph")

# File uploaders for the CSV files
business_activities_file = st.file_uploader("Upload Business Activities CSV", type="csv")
suppliers_file = st.file_uploader("Upload Suppliers CSV", type="csv")
business_activity_suppliers_file = st.file_uploader("Upload Business Activity Suppliers CSV", type="csv")

if business_activities_file and suppliers_file and business_activity_suppliers_file:
    # Read the uploaded CSV files into DataFrames
    business_activities_df = pd.read_csv(business_activities_file)
    suppliers_df = pd.read_csv(suppliers_file)
    business_activity_suppliers_df = pd.read_csv(business_activity_suppliers_file)
    
    # Convert SupplierID to set for fast lookup
    existing_suppliers = set(suppliers_df['SupplierID'])

    # Initialize the graph
    nx_graph = nx.MultiGraph()
    
    # Add the central node for the Main Company
    main_company_node = "Main Company"
    nx_graph.add_node(main_company_node, size=50, title="Main Company", group=0)
    
    # Track created nodes
    created_nodes = {main_company_node}

    # Normalize the node sizes using logarithmic scale
    min_size = 10
    max_size = 50
    max_emissions = business_activities_df['TotalEmissions'].max()

    # Create nodes and edges based on the CSV data
    for _, activity_row in business_activities_df.iterrows():
        activity_id = activity_row['ActivityID']
        total_emissions = activity_row['TotalEmissions']

        if activity_row['HasSuppliers']:
            relevant_suppliers = business_activity_suppliers_df[business_activity_suppliers_df['ActivityID'] == activity_id]
            print(relevant_suppliers)
            
            for _, supplier_row in relevant_suppliers.iterrows():
                supplier_id = supplier_row['SupplierID']
                disclosed_suppliers = supplier_row['DisclosedSuppliers']

                # Add or update supplier node
                if supplier_id not in created_nodes:
                    if supplier_id not in existing_suppliers:
                        suppliers_df = suppliers_df._append({'SupplierID': supplier_id, 'SupplierName': f'Unknown Supplier {supplier_id}'}, ignore_index=True)
                        existing_suppliers.add(supplier_id)

                    supplier_info = suppliers_df[suppliers_df['SupplierID'] == supplier_id].iloc[0]
                    supplier_name = supplier_info['SupplierName']
                    supplier_label = f"{supplier_name} (ID: {supplier_id})"
                    nx_graph.add_node(supplier_id, size=10, title=supplier_label, group=1)
                    created_nodes.add(supplier_id)
                
                # Calculate the weight of the edge based on emissions, normalized with a logarithmic scale
                if total_emissions > 0:
                    normalized_weight = np.log1p(total_emissions) / np.log1p(max_emissions)
                else:
                    normalized_weight = 0
                nx_graph.add_edge(main_company_node, supplier_id, weight=normalized_weight, title=f"Activity_ID: {activity_id}")
                
                # Process disclosed suppliers
                if pd.notna(disclosed_suppliers):
                    disclosed_supplier_ids = disclosed_suppliers.split(',')
                    for disclosed_id in disclosed_supplier_ids:
                        if disclosed_id not in created_nodes:
                            if disclosed_id not in existing_suppliers:
                                suppliers_df = suppliers_df._append({'SupplierID': disclosed_id, 'SupplierName': f'Unknown Supplier {disclosed_id}'}, ignore_index=True)
                                existing_suppliers.add(disclosed_id)

                            nx_graph.add_node(disclosed_id, size=10, title=f"Supplier {disclosed_id}", group=2)
                            created_nodes.add(disclosed_id)

                        nx_graph.add_edge(supplier_id, disclosed_id, title=f"Activity_ID: {activity_id}")


    # Visualize the graph using PyVis
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", select_menu=True, filter_menu=True)
    net.from_nx(nx_graph)
    net.toggle_physics(True)
    net.set_edge_smooth('dynamic')
    path = "knowledge_graph.html"
    net.save_graph(path)
    
    net.show(path, notebook=False)
