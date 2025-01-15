import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

# App title and description
st.title('NBA Player Stats Explorer')
st.markdown("""
This app performs simple web scraping of NBA player stats data!
* **Python Libraries:** base64, pandas, streamlit, matplotlib, seaborn, numpy
* **Data Source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

# Sidebar for user input features
st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950, 2020))))

# Function to load data from the website
def load_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    # Remove repeated headers
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats

# Load data
playerstats = load_data(selected_year)

# Debugging: Display the dataset structure
st.write("Data Preview:")
st.write(playerstats.head())

# Check if expected columns exist
if 'Tm' in playerstats.columns and 'Pos' in playerstats.columns:
    # Sidebar filters for teams and positions
    sorted_unique_team = sorted(playerstats['Tm'].unique())
    selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

    unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
    selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

    # Filter the data based on user selections
    df_selected_team = playerstats[
        (playerstats['Tm'].isin(selected_team)) & (playerstats['Pos'].isin(selected_pos))
    ]

    # Display filtered data
    st.header('Display Player Stats of the Selected Team(s)')
    st.write(f"Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns.")
    st.dataframe(df_selected_team)

    # Function to download filtered data
    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # Encode CSV file to base64
        href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

    # Intercorrelation heatmap
    if st.button('Intercorrelation Heatmap'):
        st.header('Intercorrelation Matrix Heatmap')
        if not df_selected_team.empty:
            corr = df_selected_team.select_dtypes(include=['float', 'int']).corr()  # Numeric columns only
            mask = np.zeros_like(corr)
            mask[np.triu_indices_from(mask)] = True
            with sns.axes_style("white"):
                f, ax = plt.subplots(figsize=(7, 5))
                sns.heatmap(corr, mask=mask, vmax=1, square=True, annot=True, fmt='.2f')
                st.pyplot(f)
        else:
            st.error("No data available for the selected filters to create a heatmap.")
else:
    st.error("The dataset does not contain the required columns ('Tm' or 'Pos'). Please check the data source.")
