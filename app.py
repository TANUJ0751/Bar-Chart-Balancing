import streamlit as st
import plotly.express as px
import pandas as pd

st.title("Bar Graph from 16 Inputs")

# Input labels
labels = [f"Label {i+1}" for i in range(16)]

# Take 16 numeric inputs
values = []
for label in labels:
    val = st.sidebar.number_input(f"Enter value for {label}", value=0)
    values.append(val)

AVG_AREA=sum(values)/16
MAX_LINE=(max(values)+AVG_AREA)/2
MIN_LINE=(min(values)+AVG_AREA)/2
st.write(AVG_AREA)
# Create dataframe
data = pd.DataFrame({
    'Label': labels,
    'Value': values
})

# Show bar graph
st.subheader("Bar Graph of Inputs")
fig = px.bar(data, x='Label', y='Value', title='Input Values Bar Chart')
st.plotly_chart(fig)
