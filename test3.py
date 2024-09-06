import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd

st.set_page_config(layout="wide")

# Define a function to get elements based on the current stage
def get_elements(supplier_df, activity_df, stage):
    elements = {
        "nodes": [],
        "edges": []
    }
    
    # Add the main company node
    elements["nodes"].append({"data": {"id": -1, "label": "MAIN_COMPANY", "name": "Reporting Company"}})

    # Add supplier nodes
    for index, row in supplier_df.iterrows():
        if stage == 1:
            node_label = "NON-REPORTING"
        elif stage == 2 and row["CGPT"] == True:
            if row['REPORTED_EMISSIONS'] > row['AVERAGE_EMISSIONS']:
                node_label = "High_Reporting"  # High emissions label
            else:
                node_label = "Low_Reporting"  # Low emissions label
        else:
            node_label = "NON-REPORTING"
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
        print(elements["nodes"][index])

    # Add edges for activities if stage is 2 or 3
    if stage > 1:
        for index, row in activity_df.iterrows():
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
    NodeStyle("NON-REPORTING", "#964B0", "content", "business"),
    NodeStyle("High_Reporting", "#FF0000", "name", "business"),
    NodeStyle("Low_Reporting", "#00FF00", "name", "business")
]

edge_styles = [
    EdgeStyle(label="Spent_Based_Activity", labeled=False, directed=False, color="#FFFFFF"),
    EdgeStyle(label="Scaled_Activity", labeled=False, directed=False, color="#800080")
]

# Render the component
st.markdown("### Reporting Company Supply Chain Emissions") 

business_activities_file = st.file_uploader("Upload Activities CSV", type="csv")
suppliers_file = st.file_uploader("Upload Suppliers CSV", type="csv")

if business_activities_file and suppliers_file:
    suppliers_df = pd.read_csv(suppliers_file)
    business_activities_df = pd.read_csv(business_activities_file)
    
    # Initialize session state for stage
    if "stage" not in st.session_state:
        st.session_state.stage = 1

    # Display buttons to change stages
    if st.button("Next Stage"):
        st.session_state.stage += 1
    if st.button("Previous Stage") and st.session_state.stage > 1:
        st.session_state.stage -= 1
    
    # Limit the stage to max 3
    if st.session_state.stage > 3:
        st.session_state.stage = 3
    
    # Generate the graph elements based on the current stage
    elements = get_elements(suppliers_df, business_activities_df, st.session_state.stage)
    
    st_link_analysis(elements, "cose", node_styles, edge_styles)
