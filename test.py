import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

st.set_page_config(layout="wide")

# Sample Data
elements = {
    "nodes": [
        {"data": {"id": "A", "label": "MAIN_COMPANY", "name": "Reporting Company"}},
        {"data": {"id": 2, "label": "SUPPLIER", "name": "Supplier A", "Description": "Supplier A is a company that provides raw materials."}},
        {"data": {"id": 3, "label": "SUPPLIER", "name": "Supplier B", "Description": "Supplier B is a company that does manufacturing."}},
        {"data": {"id": -1, "label": "SUPPLIER", "name": "Supplier C", "Description": "Supplier C is a company that provides transportation services."}},
    ],
    "edges": [
        {"data": {"id": "A1", "label": "Activity", "source": "A", "target": 2, "Emission Value(tCO2e)": 124, "Description": "Buying raw materials"}},
        {"data": {"id": "A2", "label": "Activity", "source": "A", "target": 2, "Emission Value(tCO2e)": 120, "Description": "Transporting goods"}},
        {"data": {"id": "A3", "label": "Activity", "source": "A", "target": 3, "Emission Value(tCO2e)": 2235, "Description": "Purchasing goods"}},
        {"data": {"id": "A4", "label": "Activity", "source": "A", "target": 3, "Emission Value(tCO2e)": 30, "Description": "Business travel"}},
    ],
}


# Style node & edge groups
node_styles = [
    NodeStyle("MAIN_COMPANY", "#FF7F3E", "name", icon='person'),
    NodeStyle("SUPPLIER", "#2A629A", "content", "business"),
]

edge_styles = [
    EdgeStyle("Activity", labeled=True, directed=True),
    EdgeStyle("POSTED", labeled=True, directed=True),
    EdgeStyle("QUOTES", labeled=True, directed=True),
]

# Render the component
st.markdown("### Reporting Company Supply Chain Emissions") 
print(elements)
st_link_analysis(elements, "cose", node_styles, edge_styles)
