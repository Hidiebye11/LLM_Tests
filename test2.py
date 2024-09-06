import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd

st.set_page_config(layout="wide")

def get_elements(supplier_df, activity_df):
    filter_df = supplier_df[supplier_df['CGPT']==True]
    elements = {
        "nodes": [],
        "edges": []
    }
    
    # Add the main company node
    elements["nodes"].append({"data": {"id": -1, "label": "MAIN_COMPANY", "name": "Reporting Company"}})

    # Add supplier nodes
    for index, row in supplier_df.iterrows():
        if row["CGPT"]==True:
         
            node_label = "REPORTING"
            elements["nodes"].append({
                "data": {
                    "id": row["ID"],
                    "label": str(node_label),
                    "name": str(row["NAME"]),
                    "description": str(row["DESCRIPTION"]),
                    "industry type": str(row["INDUSTRY_TYPE"]),
                    "Reported Emissions(tCO2e)":   row['REPORTED_EMISSIONS'] ,
                    "Industry Average Emissions(tCO2e)":  row['AVERAGE_EMISSIONS']
                }
                })

        else:

            node_label =  "NON-REPORTING" 
      
            elements["nodes"].append({
                "data": {
                    "id": row["ID"],
                    "label": str(node_label),
                    "name": str(row["NAME"]),
                    "description": str(row["DESCRIPTION"]),
                    "industry type": str(row["INDUSTRY_TYPE"]),
                    "Industry Average Emissions(tCO2e)":  row['AVERAGE_EMISSIONS']
                }
                })
        
       
    
    # Add edges for activities
    for index, row in activity_df.iterrows():
        if row["REPORTING_COMPANY"]==True:
            
            elements["edges"].append({
                "data": {
                    "id": row['ID'],
                    "Activity": row["PRODUCT/SERVICE NAME"],
                    "Description": row["DESCRIPTION"],
                    "label": "Scaled_Activity",
                    "source": row['SOURCE'],
                    "target": row["TARGET"],
                    "Scaled Emission Value(tCO2e)": round(row["PRODUCT_EMISSIONS(tCO2e)"] * (filter_df.loc[filter_df['ID'] == row['SOURCE'], 'REPORTED_EMISSIONS'].values[0] / filter_df.loc[filter_df['ID'] == row['SOURCE'], 'AVERAGE_EMISSIONS'].values[0]),2),
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
    print(elements["edges"][0])
    print(elements["edges"][1])
  
  
    return elements



# Style node & edge groups
node_styles = [
    NodeStyle("MAIN_COMPANY", "#FF7F3E", "name", icon='person'),
    NodeStyle("REPORTING", "#409a2a", "content", "business"),
    NodeStyle("NON-REPORTING", "#b03423", "content", "business")
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
    
    # Generate the graph elements
    elements = get_elements(suppliers_df, business_activities_df)
    

    st_link_analysis(elements, "cose", node_styles, edge_styles)
