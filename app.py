import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
st.title("Bar Graph Balancing")

# Input labels
labels = ["NNW","NORTH","NNE","NE","ENE","EAST","ESE","SE","SSE","SOUTH","SSW","SW","WSW","WEST","WNW","NW"]

colors = [
    "#2986FF", '#2986FF', '#2986FF', '#2986FF', "#24FF53",
    '#24FF53', '#24FF53', "#FF3232", '#FF3232', '#FF3232',
    "#fbff1f", '#fbff1f', '#ffffff', "#ffffff", '#ffffff', '#ffffff'
]
# Take 16 numeric inputs
values = []
for label in labels:
    val = st.sidebar.number_input(f"Enter area of {label} in Sq.ft.",min_value=0, value=0)
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
    xaxis_title='Labels',
    yaxis_title='Values',
    height=600
)

# Show chart
st.plotly_chart(fig)

st.write(f"Max Line : {MAX_LINE}")
st.write(f"Min Line : {MIN_LINE}")
st.write(f"Average Line : {AVG_AREA}")


def balance_values(values, step, mode, max_iterations=100):
    """
    Recursively balance values between dynamic min and max line using given mode.
    Modes: 'add', 'subtract', 'both'
    """
    values = values[:]  # clone input list

    for _ in range(max_iterations):
        avg = sum(values) / len(values)
        max_line = (max(values) + avg) / 2
        min_line = (min(values) + avg) / 2

        updated = False
        for i, val in enumerate(values):
            if mode == 'add' and val < avg:
                values[i] = min(val + step, max_line)
                updated = True
            elif mode == 'subtract' and val > avg:
                values[i] = max(val - step, min_line)
                updated = True
            elif mode == 'both':
                if val < avg:
                    values[i] = min(val + step, max_line)
                    updated = True
                elif val > avg:
                    values[i] = max(val - step, min_line)
                    updated = True

        if not updated:
            break

    return [round(v, 2) for v in values]

mode = st.radio("Balancing Mode", ["Add", "Subtract", "Both"], horizontal=True).lower()
step = st.slider("Add/Subtract Step Size", 0.1, 1.0, 0.10, step=0.1)

# Balance values
balanced_values = balance_values(values,step,mode)


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
    "Label": labels,
    "Original Value": values,
    "Balanced Value": balanced_values,
    "Add/Sub": pd.Series(balanced_values) - pd.Series(values)
})

st.markdown("### Original vs Balanced Values")
st.dataframe(balanced_data)