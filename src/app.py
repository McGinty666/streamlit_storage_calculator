import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp1d
from utils.synthetic_flow import generate_synthetic_flow

def main():
    st.title("Synthetic Flow, Storage, and PFF Simulator")

    # Create columns for layout
    col1, col2 = st.columns(2)

    with col1:
        # User inputs for rainfall
        rainfall = st.text_area("Enter rainfall intensity (mm/h) at 5-minute intervals, separated by commas or spaces:")
        rainfall = np.array([float(x) for x in rainfall.replace(',', ' ').split()]) if rainfall else np.array([])

    with col2:
        # User inputs for R, T, K values
        R1 = st.number_input("Enter R value for set 1:", value=4.4)
        T1 = st.number_input("Enter T value for set 1:", value=1)
        K1 = st.number_input("Enter K value for set 1:", value=16.43)

        R2 = st.number_input("Enter R value for set 2:", value=2.19)
        T2 = st.number_input("Enter T value for set 2:", value=9.5)
        K2 = st.number_input("Enter K value for set 2:", value=8)

        PFF = st.number_input("Enter the user-defined PFF (l/s):", value=0.0)

    # Button to generate synthetic flow
    if st.button("Generate Synthetic Flow"):
        synthetic_flow1 = generate_synthetic_flow(rainfall, R1, T1, K1)
        synthetic_flow2 = generate_synthetic_flow(rainfall, R2, T2, K2)
        overall_synthetic_flow = synthetic_flow1 + synthetic_flow2

        # Interpolate synthetic flow values for better granularity
        x = np.arange(len(overall_synthetic_flow))
        x_interp = np.linspace(0, len(overall_synthetic_flow) - 1, len(overall_synthetic_flow) * 10)
        interp_func = interp1d(x, overall_synthetic_flow, kind='cubic')
        overall_synthetic_flow_interp = interp_func(x_interp)

        # Create plotly figure
        fig = go.Figure()

        # Add synthetic flows to the figure
        fig.add_trace(go.Scatter(x=x_interp, y=overall_synthetic_flow_interp, mode='lines', name='Overall Synthetic Flow', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=x_interp, y=interp_func(x_interp), mode='lines', name='Synthetic Flow 1', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=x_interp, y=interp_func(x_interp), mode='lines', name='Synthetic Flow 2', line=dict(color='lime')))
        fig.add_trace(go.Scatter(x=x_interp, y=[PFF]*len(x_interp), mode='lines', name='PFF', line=dict(color='red', dash='dash')))

        # Add shaded area between PFF and synthetic flow where storage is positive
        positive_storage_mask = overall_synthetic_flow_interp > PFF
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_interp[positive_storage_mask], x_interp[positive_storage_mask][::-1]]),
            y=np.concatenate([overall_synthetic_flow_interp[positive_storage_mask], np.full_like(x_interp[positive_storage_mask], PFF)]),
            fill='toself',
            fillcolor='orange',
            opacity=0.5,
            line=dict(color='orange'),
            hoverinfo="skip",
            showlegend=False
        ))

        # Add rainfall to the figure
        fig.add_trace(go.Bar(x=np.arange(len(rainfall)), y=rainfall, name='Rainfall', marker=dict(color='blue', opacity=0.6), yaxis='y2'))

        # Update layout for dual y-axes
        fig.update_layout(
            yaxis=dict(title='Synthetic Flow (l/s)', titlefont=dict(color='green'), tickfont=dict(color='green')),
            yaxis2=dict(title='Rainfall (mm/h)', titlefont=dict(color='blue'), tickfont=dict(color='blue'), overlaying='y', side='right', range=[120, 0]),
            xaxis=dict(title='Time', tickmode='linear'),
            legend=dict(x=0, y=1.1, orientation='h'),
            hovermode='x unified'
        )

        # Enable zooming and panning
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(autosize=True)

        st.plotly_chart(fig)

        # Storage calculation in cubic meters
        x_interp_seconds = x_interp * 300  # Convert 5-minute intervals to seconds
        storage_required_liters = np.trapz(overall_synthetic_flow_interp[positive_storage_mask] - PFF, x_interp_seconds[positive_storage_mask])
        storage_required_m3 = storage_required_liters / 1000  # Convert liters to cubic meters
        storage_required_m3 = max(storage_required_m3, 0)

        st.write(f"Storage required: {storage_required_m3:.2f} m³")

if __name__ == "__main__":
    main()