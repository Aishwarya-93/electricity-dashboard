import streamlit as st
import pandas as pd
import plotly.express as px
import sys

st.set_page_config(
    page_title="Electricity Dashboard",
    page_icon="⚡",
    layout="wide"
)

# --- BACKGROUND + TEXT ---
st.markdown("""
<style>

/* --- BACKGROUND --- */
.stApp {
    background: linear-gradient(90deg,rgba(232, 84, 84, 1) 0%, rgba(252, 104, 104, 1) 42%, rgba(194, 109, 237, 1) 100%);
}

/* --- TEXT --- */
h1, h2, h3 {
    color: white !important;
}

/* --- DOWNLOAD BUTTON --- */
.stDownloadButton > button {
    background-color: black !important;
    color: white !important;
    border-radius: 8px;
    border: 1px solid white;
    font-weight: bold;
}

/* --- SUCCESS MESSAGE --- */
div[data-testid="stAlert"] {
    background-color: #1e1e1e !important;
}

div[data-testid="stAlert"] p {
    color: #00ffcc !important;
    font-weight: bold;
}

/* --- TABS --- */
button[role="tab"] {
    color: white !important;
    font-weight: bold;
}


[data-testid="stFileUploader"] > label {
    color: white !important;
    font-weight: bold !important;
}

/* Box text */
[data-testid="stFileUploader"] section {
    opacity: 1 !important;
}

/* Drag text */
[data-testid="stFileUploader"] section div {
    color: black !important;
    font-weight: bold !important;
}

/* Small text */
[data-testid="stFileUploader"] small {
    color: black !important;
    font-weight: bold !important;
}

/* Uploaded filename */
[data-testid="stFileUploaderFileName"] {
    color: white !important;
    font-weight: bold !important;
}



section[data-testid="stSidebar"] {
    background-color: rgba(0,0,0,0.2);
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Labels */
section[data-testid="stSidebar"] label {
    font-weight: bold !important;
}

/* Input boxes */
section[data-testid="stSidebar"] input {
    color: black !important;
    font-weight: bold !important;
}


[data-testid="stMarkdownContainer"] p {
    color: white !important;
    opacity: 1 !important;
    font-weight: 500;
}

/* General text blocks */
[data-testid="stText"] {
    color: white !important;
    opacity: 1 !important;
}

/* Stronger visibility */
strong {
    color: #ffffff !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* 🔥 FIX UPLOADER BOX (THIS IS THE MISSING PART) */
[data-testid="stFileUploader"] section {
    background-color: #f1f3f6 !important;   /* light box */
    border-radius: 12px !important;
    padding: 20px !important;
    border: none !important;
}

/* Make icon + text aligned nicely */
[data-testid="stFileUploader"] section div {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Fix button */
[data-testid="stFileUploader"] button {
    background-color: #e6e6e6 !important;
    color: black !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>⚡ Electricity Consumption Dashboard</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your electricity dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    with st.spinner("Processing data..."):
        df = pd.read_csv(uploaded_file)
    df.columns = ['Date', 'Consumption']

    st.success("File uploaded successfully!")
    
    st.sidebar.header("⚙️ Controls")

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    
    start_date = st.sidebar.date_input("Start Date", df['Date'].min().date())
    end_date = st.sidebar.date_input("End Date", df['Date'].max().date())
    
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
            (df['Date'] <= pd.to_datetime(end_date))]

    col1, col2, col3 = st.columns(3)
    
    col1.metric("🔋 Total Consumption", round(df['Consumption'].sum(), 2))
    col2.metric("📈 Average Consumption", round(df['Consumption'].mean(), 2))
    col3.metric("⚡ Max Consumption", df['Consumption'].max())
    
    tab1, tab2, tab3, tab4, tab5, tab7 = st.tabs([
        "📄 Data",
        "📊 Graph",
        "🔥 Peak",
        "⚠️ Anomaly",
        "📈 Prediction",
        "🗺️ India Map"
    ])

    # -------- DATA --------
    with tab1:
        st.subheader("📄 Data Preview")
        st.dataframe(df)

        st.subheader("📊 Summary Statistics")
        st.write(df['Consumption'].describe())

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Data", csv, "electricity_data.csv", "text/csv")

    # -------- GRAPH --------
    with tab2:
        st.subheader("📊 Electricity Consumption Over Time")

        fig = px.line(df, x='Date', y='Consumption', title="Consumption Trend")

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white")
        )
        fig.update_layout(
            title_font=dict(size=20, color="white")
        )

        fig.update_xaxes(showgrid=True, gridcolor="gray", color="white")
        fig.update_yaxes(showgrid=True, gridcolor="gray", color="white")

        fig.update_traces(line=dict(color="#00FFFF", width=3))

        st.plotly_chart(fig, use_container_width=True)

    # -------- PEAK --------
    with tab3:
        st.subheader("🔥 Peak Usage Analysis")
        max_value = df['Consumption'].max()
        max_date = df.loc[df['Consumption'].idxmax(), 'Date']

        st.write(f"Highest Consumption: {max_value}")
        st.write(f"Occurred on: {max_date.date()}")

    # -------- ANOMALY --------
    with tab4:
        st.subheader("⚠️ Anomaly Detection")
    
        mean = df['Consumption'].mean()
        std = df['Consumption'].std()
    
        df['Z_score'] = (df['Consumption'] - mean) / std
        threshold = 2
    
        anomalies = df[df['Z_score'].abs() > threshold]
    
        st.write(f"Number of anomalies detected: {len(anomalies)}")
        st.dataframe(anomalies)
    
        fig2 = px.line(df, x='Date', y='Consumption', title="Anomaly Detection")
    
        fig2.update_layout(
            template="plotly_dark",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white")
        )
    
        fig2.update_layout(
            title_font=dict(size=20, color="white"),
    
            legend=dict(
                font=dict(color="white", size=14),
                bgcolor="rgba(0,0,0,0.5)"   
            )
        )
    
        fig2.update_xaxes(showgrid=True, gridcolor="gray", color="white")
        fig2.update_yaxes(showgrid=True, gridcolor="gray", color="white")
    
        fig2.update_traces(line=dict(color="#00FFFF", width=3))
    
        fig2.add_scatter(
            x=anomalies['Date'],
            y=anomalies['Consumption'],
            mode='markers',
            name='Anomalies',
            marker=dict(
                color='red',       
                size=10,
                line=dict(color='white', width=1)
            )
        )
    
        st.plotly_chart(fig2, use_container_width=True)
    
        anomaly_csv = anomalies.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Anomaly Data", anomaly_csv, "anomalies.csv", "text/csv")
        
    # -------- PREDICTION --------
    with tab5:
        st.subheader("📈 Electricity Consumption Prediction")

        from sklearn.linear_model import LinearRegression
        import numpy as np

        df = df.sort_values('Date')
        df['Days'] = (df['Date'] - df['Date'].min()).dt.days

        X = df[['Days']]
        y = df['Consumption']

        model = LinearRegression()
        model.fit(X, y)

        future_days = np.arange(df['Days'].max() + 1, df['Days'].max() + 8)
        future_dates = pd.date_range(df['Date'].max() + pd.Timedelta(days=1), periods=7)

        future_pred = model.predict(future_days.reshape(-1, 1))

        future_df = pd.DataFrame({
            'Date': future_dates,
            'Consumption': future_pred
        })

        st.write("📅 Predicted Data (Next 7 Days)")
        st.dataframe(future_df)

        combined_df = pd.concat([df[['Date', 'Consumption']], future_df])

        fig3 = px.line(combined_df, x='Date', y='Consumption', title="Actual + Predicted")

        fig3.update_layout(
            template="plotly_dark",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white")
        )
        fig3.update_layout(
            title_font=dict(size=20, color="white")
        )
        fig3.update_xaxes(showgrid=True, gridcolor="gray", color="white")
        fig3.update_yaxes(showgrid=True, gridcolor="gray", color="white")

        fig3.update_traces(line=dict(color="#00FFFF", width=3))

        st.plotly_chart(fig3, use_container_width=True)

        pred_csv = future_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Prediction Data", pred_csv, "predictions.csv", "text/csv")
  
    import json
    
    # -------- INDIA MAP --------
    with tab7:
        st.subheader("🗺️ India Electricity Consumption Map")
    
        # Load dataset
        df_std = pd.read_csv("Indias_Electricity_Consumption_Dataset.csv")
        df_std.rename(columns={"Dates": "Date"}, inplace=True)
    
        # Convert wide → long
        df_long = df_std.melt(
            id_vars=["Date"],
            var_name="State",
            value_name="Consumption"
        )
    

        df_long = df_long[df_long["State"] != "Total Consumption"]
    
        # Clean names
        df_long["State"] = df_long["State"].str.strip()
    
        # STATE MAPPING
        mapping = {
            "J&K": "Jammu and Kashmir",
            "HP": "Himachal Pradesh",
            "MP": "Madhya Pradesh",
            "UP": "Uttar Pradesh",
            "Pondy": "Puducherry",
            "DNH": "Dadra and Nagar Haveli and Daman and Diu",
            "DD": "Dadra and Nagar Haveli and Daman and Diu",
            "Andaman and Nicobar Islands": "Andaman and Nicobar"
        }
    
        df_long["State"] = df_long["State"].replace(mapping)
    
        # Remove non-state data
        df_long = df_long[~df_long["State"].isin(["DVC", "Essar steel"])]
    
        # Normalize case (
        df_long["State"] = df_long["State"].str.title()
    
        # Group data
        state_data = df_long.groupby("State")["Consumption"].sum().reset_index()
    
        # -------- LOAD GEOJSON --------
        with open("india_state.geojson") as f:
            geojson_data = json.load(f)
    
        # -------- FILTER VALID STATES --------
        valid_states = [f["properties"]["NAME_1"] for f in geojson_data["features"]]
        state_data = state_data[state_data["State"].isin(valid_states)]
    
        # -------- MAP --------
        fig_map = px.choropleth(
            state_data,
            geojson=geojson_data,
            featureidkey="properties.NAME_1",
            locations="State",
            color="Consumption",
            color_continuous_scale="Reds",
            title="Electricity Consumption by State"
        )
    
        fig_map.update_geos(fitbounds="locations", visible=False)
    
        fig_map.update_layout(
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white")
        )
        fig_map.update_layout(
            title_font=dict(size=22, color="white"),
            font=dict(color="white")
        )
        fig_map.update_coloraxes(
            colorbar=dict(
                title=dict(
                    text="Consumption",
                    font=dict(color="white")  
                ),
                tickfont=dict(color="white")
            )
        )  

        st.plotly_chart(fig_map, use_container_width=True)
