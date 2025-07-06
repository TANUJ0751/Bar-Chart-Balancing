import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from balance import balance_values
from pdf import generate_pdf
import pandas as pd

st.title("Bar Graph Balancing")
import io
name = st.text_input("Enter Project Name",key="project_name_input")
# Input labels
labels = ["NNW","NORTH","NNE","NE","ENE","EAST","ESE","SE","SSE","SOUTH","SSW","SW","WSW","WEST","WNW","NW"]

colors = [
    "#2986FF", '#2986FF', '#2986FF', '#2986FF', "#24FF53",
    '#24FF53', '#24FF53', "#FF3232", '#FF3232', '#FF3232',
    "#fbff1f", '#fbff1f', "#b4b4b4", "#b4b4b4", '#b4b4b4', '#b4b4b4'
]
cols = st.columns(4)
# Take 16 numeric inputs
values = []
for i, label in enumerate(labels):
    col = cols[i % 4]
    with col:
        val = st.number_input(f"{label}", min_value=0.0, value=0.0,step=0.1, key=label)
        values.append(val)

AVG_AREA=sum(values)/16
MAX_LINE=(max(values)+AVG_AREA)/2
MIN_LINE=(min(values)+AVG_AREA)/2
# Create dataframe
data = pd.DataFrame({
    'Label': labels,
    'Value': values
})

# Create bar graph
fig = go.Figure()

# Add bar chart
fig.add_trace(go.Bar(x=data['Label'], y=data['Value'],marker_color=colors, name='Input Values'))

# Add horizontal lines
fig.add_hline(y=AVG_AREA, line_dash="dash", line_color="blue", annotation_text="Avg Area", annotation_position="top left")
fig.add_hline(y=MAX_LINE, line_dash="dot", line_color="green", annotation_text="Max Line", annotation_position="top left")
fig.add_hline(y=MIN_LINE, line_dash="dot", line_color="red", annotation_text="Min Line", annotation_position="bottom left")

# Customize layout
fig.update_layout(
    title='Input Values Bar Chart with Reference Lines',
    xaxis_title='Zones',
    yaxis_title='Area',
    bargap=0.5,
    height=600
)

st.write(f"Max Line : {MAX_LINE} , Min Line : {MIN_LINE} , AVG Line : {AVG_AREA}")


# Show chart
st.plotly_chart(fig)




st.subheader("Balancing Zones")

mode = st.sidebar.radio("Balancing Mode", ["Add", "Subtract", "Both"], horizontal=True).lower()
diff=(max(values)-min(values))/32
step = st.sidebar.slider("Add/Subtract Step Size", 0.01, diff, 0.10, step=0.01)

# Balance values
balanced_values = balance_values(values,step,mode)

AVG_AREA=sum(balanced_values)/16
MAX_LINE=(max(balanced_values)+AVG_AREA)/2
MIN_LINE=(min(balanced_values)+AVG_AREA)/2

st.write(f"Max Line : {MAX_LINE} , Min Line : {MIN_LINE} , AVG Line : {AVG_AREA}")

# Plot balanced values
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=labels,
    y=balanced_values,
    marker_color=colors,
    name='Balanced Area'
))

fig2.add_hline(y=sum(balanced_values)/16, line_dash="dash", line_color="blue",
            annotation_text="Avg Area", annotation_position="top right")
fig2.add_hline(y=((sum(balanced_values)/16)+max(balanced_values))/2, line_dash="dash", line_color="red",
            annotation_text="Max Line", annotation_position="top left")
fig2.add_hline(y=((sum(balanced_values)/16)+min(balanced_values))/2, line_dash="dash", line_color="green",
            annotation_text="Min Line", annotation_position="bottom left")
fig2.update_layout(
    title="Balanced Directional Areas",
    xaxis_title="Direction",
    yaxis_title="Balanced Area (Sq.ft.)",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# Optional: Display side-by-side
balanced_data = pd.DataFrame({
    "Zone": labels,
    "Original Value": values,
    "Balanced Value": balanced_values,
    "Add/Sub": pd.Series(balanced_values) - pd.Series(values)
})

st.markdown("### Original vs Balanced Values")
st.dataframe(balanced_data,use_container_width=True)

if name and min(values)>0 :
    pdf_data = generate_pdf(balanced_data, fig, fig2,name)

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_data,
        file_name=f"{name}-report.pdf",
        mime="application/pdf"
    )