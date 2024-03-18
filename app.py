import os
from datetime import datetime
import streamlit as st
from transfermarkt_scraper import scrape_transfermarkt_data
from transfermarkt_scraper import convert_market_value
import matplotlib.pyplot as plt


# Function to load images
def load_image(image_path):
    with open(image_path, 'rb') as f:
        image = f.read()
    return image

# Load team images
def load_team_images(df):
    team_images = {}
    for club_name in df['club'].unique():
        image_file = club_name + ".png"  #
        image_path = os.path.join("team images", image_file)
        if os.path.exists(image_path):
            team_images[club_name] = load_image(image_path)
    return team_images

@st.cache_resource()
def load_data():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
    return scrape_transfermarkt_data(), timestamp

def main():

    st.set_page_config(layout="wide")

    st.title('League of Ireland Teams App')


    st.write("\n")
    st.write("\n")

    # Load DataFrame
    df,timestamp = load_data()

    st.write("Data loaded at:", timestamp)
    st.write("\n")
    st.write("\n")
    # Load team images
    team_images = load_team_images(df)

    # Filter box based on 'club' column
    selected_club = st.sidebar.selectbox('Select Club', df['club'].unique())

    # Display team image
    if selected_club in team_images:
        with st.markdown('<div style="text-align:center">', unsafe_allow_html=True):
            st.image(team_images[selected_club], caption=selected_club, use_column_width=False, output_format="PNG",
                     width=250)
        # Center the image using CSS
        st.markdown(
            f'<style>.css-1aumxhk{{display: flex;justify-content: center;}}</style>',
            unsafe_allow_html=True
        )
    else:
        st.write("Image not found for selected club.")

    st.write("\n")
    st.write("\n")

    # Filter DataFrame based on selected club
    filtered_df = df[df['club'] == selected_club]
    # Apply market value conversion function to the 'market_value' column
    filtered_df['market_value'] = filtered_df['market_value'].apply(convert_market_value)

    # Display filtered DataFrame with widened width
    st.dataframe(filtered_df,width=40000000)

    # Count the number of positions for the selected team
    position_counts = filtered_df['position'].value_counts()

    # Count the number of footedness for the selected team
    foot_counts = filtered_df['foot'].value_counts()

    # Group by position and sum the market values
    position_market_values = filtered_df.groupby('position')['market_value'].sum()

    # Display a bar chart of market value counts for the selected team
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")

    fig, ax = plt.subplots(figsize=(8, 4))
    position_market_values.plot(kind='bar', ax=ax,color='black')
    ax.set_xlabel("Position")
    ax.set_ylabel("€ Market Values")
    ax.set_title(f"Player Market Values for {selected_club} €000's")
    plt.xticks(rotation=45)  # Rotate x-axis labels by 45 degrees
    st.pyplot(fig)


    # Display a bar chart of position counts for the selected team
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")

    fig, ax = plt.subplots(figsize=(8, 4))
    position_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel("Position")
    ax.set_ylabel("Number of Players")
    ax.set_title(f"Player Positions for {selected_club}")
    plt.xticks(rotation=45)  # Rotate x-axis labels by 45 degrees
    st.pyplot(fig)

    # Display a bar chart of foot counts for the selected team
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")

    fig, ax = plt.subplots(figsize=(8, 4))
    foot_counts.plot(kind='bar', ax=ax,color='green')
    ax.set_xlabel("Preferred Foot")
    ax.set_ylabel("Number of Players")
    ax.set_title(f"Player Preferred foot for {selected_club}")
    plt.xticks(rotation=45)  # Rotate x-axis labels by 45 degrees
    st.pyplot(fig)

# Run the app
if __name__ == '__main__':
    main()
