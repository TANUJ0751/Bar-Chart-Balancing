import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from balance import balance_values
from pdf import generate_pdf
import pandas as pd

# Hardcoded credentials (in production, use hashed passwords + database)
USER_CREDENTIALS = {
    "tanuj": "ZKd8iEyp7945K5u",
    "admin": "ZKd8iEyp7945K5u"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.success("Login successful! 🎉")
            st.rerun()  # ✅ use this instead of st.experimental_rerun()
        else:
            st.error("Invalid username or password ❌")


# Show login page if not authenticated

if not st.session_state.authenticated:
    login()
    st.stop()


st.set_page_config(
    page_title="Bar Chart Balancer",
    page_icon="🧭",  # Emoji or path to image file
    layout="wide"
)

st.title("Bar Graph Balancing")
st.write("#### Specially for Acharya Pankit Sir")
st.write("This app is made by - **Tanuj Jain**, this app is used in vastu for balancing each and every zone in the resedential/commercial premises")
import io
st.write("------")
st.write("Enter Project Name for Exporting/Downloading full report")
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

# Divide the labels into chunks for each column
rows_per_col = (len(labels) + 3) // 4  # Divide evenly across 4 columns
for col_index in range(4):
    with cols[col_index]:
        for i in range(rows_per_col):
            idx = i + col_index * rows_per_col
            if idx < len(labels):
                label = labels[idx]
                val = st.number_input(f"{label} zone area", min_value=0.0, value=0.0, step=0.1, key=label)
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
fig.add_hline(y=AVG_AREA, line_dash="dash", line_color="blue", annotation_text="Avg Area", annotation_position="top right")
fig.add_hline(y=MAX_LINE, line_dash="dot", line_color="green", annotation_text="Max Line", annotation_position="top left")
fig.add_hline(y=MIN_LINE, line_dash="dot", line_color="red", annotation_text="Min Line", annotation_position="bottom left")

# Customize layout
fig.update_layout(
    title='Input Values Bar Chart with Reference Lines',
    xaxis_title='Zones',
    yaxis_title='Area',
    bargap=0.5,
    dragmode=False,
    height=600
)

total_original=f"Max Line : {MAX_LINE} , Min Line : {MIN_LINE} , AVG Line : {AVG_AREA}, Total Area : {sum(values)}"
st.write(total_original)


# Show chart
st.plotly_chart(fig)




st.subheader("Balancing Zones")

mode = st.sidebar.radio("Balancing Mode", ["Add", "Subtract", "Both"], horizontal=True).lower()
diff=(max(values)-min(values))/32
step = st.sidebar.slider("Threshold Value", 0.01, diff, 0.10, step=0.01)

# Balance values
balanced_values = balance_values(values,step,mode)

AVG_AREA=sum(balanced_values)/16
MAX_LINE=(max(balanced_values)+AVG_AREA)/2
MIN_LINE=(min(balanced_values)+AVG_AREA)/2
total_balance=f"Max Line : {MAX_LINE} , Min Line : {MIN_LINE} , AVG Line : {AVG_AREA},Total Area : {sum(values)}"
st.write(total_balance)

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
    height=500,
    dragmode=False
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
function_detail=f"Function Mode : {mode} , Step Size : {step}"
if name and min(values)>0 :
    pdf_data = generate_pdf(balanced_data, fig, fig2,name,total_original,total_balance,function_detail)

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_data,
        file_name=f"{name}-report.pdf",
        mime="application/pdf"
    )