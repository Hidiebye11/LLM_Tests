import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd
import random

# Set the layout of the Streamlit page to wide
st.set_page_config(layout="wide")

# Define a function to get elements (nodes and edges) based on the current stage
def get_elements(supplier_df, activity_df, stage):
    elements = {
        "nodes": [],
        "edges": []
    }
    
    # Add the main company node
    elements["nodes"].append({"data": {"id": -1, "label": "MAIN_COMPANY", "name": "Reporting Company"}})

    reported_company_id = None  # Variable to store the ID of the first reported company
    total_activities = len(activity_df)
    activities_to_include = 0
    
    # Determine the number of activities to include based on the stage
    if stage == 3:
        activities_to_include = total_activities // 2
    elif stage == 4:
        activities_to_include = total_activities * 3 // 4
    elif stage == 5:
        activities_to_include = total_activities
    
    # Add supplier nodes
    for index, row in supplier_df.iterrows():
        if stage == 1:
            node_label = "NON-REPORTING"
        elif stage == 2 and row["CGPT"] == True:
            if reported_company_id is None:
                reported_company_id = row["ID"]
                # Determine the label based on reported emissions compared to the industry average
                if row['REPORTED_EMISSIONS'] > row['AVERAGE_EMISSIONS']:
                    node_label = "High_Reporting"
                else:
                    node_label = "Low_Reporting"
            else:
                node_label = "NON-REPORTING"
        elif stage > 2 and row["CGPT"] == True:
            if row['REPORTED_EMISSIONS'] > row['AVERAGE_EMISSIONS']:
                node_label = "High_Reporting"
            else:
                node_label = "Low_Reporting"
        else:
            node_label = "NON-REPORTING"

        # Add the node to the elements
        if row["CGPT"] == True:
            elements["nodes"].append({
                "data": {
                    "id": row["ID"],
                    "label": str(node_label),
                    "name": str(row["NAME"]),
                    "description": str(row["DESCRIPTION"]),
                    "industry type": str(row["INDUSTRY_TYPE"]),
                    "Reported Emissions(tCO2e)": row['REPORTED_EMISSIONS'],
                    "Industry Average Emissions(tCO2e)": row['AVERAGE_EMISSIONS']
                }
            })
        else:
            elements["nodes"].append({
                "data": {
                    "id": row["ID"],
                    "label": str(node_label),
                    "name": str(row["NAME"]),
                    "description": str(row["DESCRIPTION"]),
                    "industry type": str(row["INDUSTRY_TYPE"]),
                    "Industry Average Emissions(tCO2e)": row['AVERAGE_EMISSIONS']
                }
            })

    # Add edges for activities based on the stage
    if stage > 1:
        if stage == 2:
            filtered_activities = activity_df[activity_df["SOURCE"] == reported_company_id]
        else:
            filtered_activities = activity_df

        # Filter the activities to include based on the stage
        if activities_to_include > 0 and stage > 2:
            filtered_activities = filtered_activities.sample(n=activities_to_include, random_state=1)
        
        # Add the edges to the elements
        for index, row in filtered_activities.iterrows():
            if row["REPORTING_COMPANY"] == True:
                elements["edges"].append({
                    "data": {
                        "id": row['ID'],
                        "Activity": row["PRODUCT/SERVICE NAME"],
                        "Description": row["DESCRIPTION"],
                        "label": "Scaled_Activity",
                        "source": row['SOURCE'],
                        "target": row["TARGET"],
                        "Scaled Emission Value(tCO2e)": round(row["PRODUCT_EMISSIONS(tCO2e)"] * (supplier_df.loc[supplier_df['ID'] == row['SOURCE'], 'REPORTED_EMISSIONS'].values[0] / supplier_df.loc[supplier_df['ID'] == row['SOURCE'], 'AVERAGE_EMISSIONS'].values[0]), 2),
                        "Description": str(row["DESCRIPTION"])
                    }
                })
            else:
                elements["edges"].append({
                    "data": {
                        "id": row['ID'],
                        "Activity": row["PRODUCT/SERVICE NAME"],
                        "Description": row["DESCRIPTION"],
                        "label": "Spent_Based_Activity",
                        "source": row['SOURCE'],
                        "target": row["TARGET"],
                        "Spent-based Emission Value(tCO2e)": row["PRODUCT_EMISSIONS(tCO2e)"],
                        "Description": str(row["DESCRIPTION"])
                    }
                })

    return elements

# Style node & edge groups
node_styles = [
    NodeStyle("MAIN_COMPANY", "#FF7F3E", "name", icon='person'),
    NodeStyle("NON-REPORTING", "#964B00", "content", "business"),
    NodeStyle("High_Reporting", "#FF0000", "name", "business"),
    NodeStyle("Low_Reporting", "#00FF00", "name", "business")
]

edge_styles = [
    EdgeStyle(label="Spent_Based_Activity", labeled=False, directed=False, color="#FFFFFF"),
    EdgeStyle(label="Scaled_Activity", labeled=False, directed=False, color="#800080")
]

# Stage descriptions
stage_descriptions = {
    1: "Stage 1: Companies onboard with CSI but have not reported emissions",
    2: "Stage 2: The first company reports their supply chain emissions",
    3: "Stage 3: More companies report their supply chain emissions",
    4: "Stage 4: Even more companies report their supply chain emissions",
    5: "Stage 5: Every company reports their supply chain emissions"
}

# Render the component
st.markdown("### Reporting Company Supply Chain Emissions") 

# File uploaders for business activities and suppliers CSV files
business_activities_file = st.file_uploader("Upload Activities CSV", type="csv")
suppliers_file = st.file_uploader("Upload Suppliers CSV", type="csv")

# Check if both files are uploaded
if business_activities_file and suppliers_file:
    suppliers_df = pd.read_csv(suppliers_file)
    business_activities_df = pd.read_csv(business_activities_file)
    
    # Initialize session state for stage if not already set
    if "stage" not in st.session_state:
        st.session_state.stage = 1

    # Display buttons to change stages
    if st.button("Next Stage"):
        st.session_state.stage += 1
    if st.button("Previous Stage") and st.session_state.stage > 1:
        st.session_state.stage -= 1
    
    # Limit the stage to max 5
    if st.session_state.stage > 5:
        st.session_state.stage = 5
    
    # Display the stage description
    st.markdown(f"**{stage_descriptions[st.session_state.stage]}**")

    # Generate the graph elements based on the current stage
    elements = get_elements(suppliers_df, business_activities_df, st.session_state.stage)
    
    # Render the link analysis visualization
    st_link_analysis(elements, "cose", node_styles, edge_styles)
