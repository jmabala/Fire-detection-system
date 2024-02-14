from supabase import create_client
import pandas as pd 
import streamlit as st 
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots  # Import make_subplots from plotly.subplots
import time

# Initialize Supabase client
API_URL = 'https://bpqfldreekysyesnmbdj.supabase.co'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwcWZsZHJlZWt5c3llc25tYmRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDczMDMzMjUsImV4cCI6MjAyMjg3OTMyNX0.Em3Rj74RHxRRVvK6UTF4s_61_6rPR301nRNXqDD2bi0'
supabase = create_client(API_URL, API_KEY)

# Streamlit app configuration
st.set_page_config(page_title="Dashboard", layout='wide', initial_sidebar_state='collapsed')

def main():
    # Retrieve coordinates from the Supabase table
    coordinates = get_coordinates()

    # Default map location: Kampala
    kampala_latitude = 0.347596
    kampala_longitude = 32.582520
    kampala_df = pd.DataFrame({'latitude': [kampala_latitude], 'longitude': [kampala_longitude]})
    map_container = st.empty()

    if coordinates:
        # Display coordinates from the Supabase table
        name, latitude, longitude = coordinates
        new_data = pd.DataFrame({'latitude': [float(latitude)], 'longitude': [float(longitude)]})
        map_data = map_container.map(new_data)
        st.write(coordinates)
    else:
        latitude, longitude = kampala_latitude, kampala_longitude
        map_data = map_container.map(kampala_df)


    # name, latitude, longitude = coordinates


    # Text box for entering coordinates
    st.sidebar.header("Enter Coordinates")
    name = st.sidebar.text_input("Name", '')
    latitude = st.sidebar.text_input("Latitude", '')
    longitude = st.sidebar.text_input("Longitude", '')


    # Button to display coordinates on the map
    if st.sidebar.button("Enter"):
        if name and latitude and longitude:
            # Clear the existing map
            map_container.empty()
            # Update the existing map with new coordinates
            new_data = pd.DataFrame({'latitude': [float(latitude)], 'longitude': [float(longitude)]})
            map_data = map_container.map(new_data)
            log_coordinates(name, float(latitude), float(longitude))
            st.sidebar.success("Coordinates logged successfully.")


    while True:
        # Retrieve data from Supabase table
        supabaseList = supabase.table('maintable').select('*').order('created_at').execute().data

        # Reverse the order of the list to achieve descending order
        supabaseList.reverse()

        # Process data into a DataFrame
        df = pd.DataFrame()
        data = []

        for index, row in enumerate(supabaseList):
            row["created_at"] = row["created_at"].split(".")[0]
            row["time"] = row["created_at"].split("T")[1]
            row["date"] = row["created_at"].split("T")[0]
            row["DateTime"] = row["created_at"]
            data.append(row)

        df = pd.DataFrame(data)

        # Filter out rows where temperature exceeds -1
        df = df[df['temperature'] >= -1]

        # Display the latest readings
        display_latest_readings(df)

        # Sleep for 10 seconds before reloading
        time.sleep(15)

        # Reload the page every 60 seconds
        st.rerun()

# df = df[df['temperature'] >= -1]

def display_latest_readings(df):
    # Sort the DataFrame by 'DateTime'
    df = df.sort_values(by='DateTime')

    temp = df['temperature'].iloc[-1]
    Humidity = df['humidity'].iloc[-1]
    smoke = df['smoke'].iloc[-1]
    CO = df['carbon monoxide'].iloc[-1]
    LPG = df['LPG'].iloc[-1]
    flame = df['flame'].iloc[-1]

    # Display metrics on the same line with increased font size and spacing
    st.write(
        f"<span style='font-size: 20px;'>Temperature:   <span style='font-size: 30px;'> <span style='color: red;'>{temp}</span> "
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='font-size: 30px;'>|</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        f"<span style='font-size: 20px;'>Humidity:   <span style='font-size: 30px;'> <span style='color: green;'>{Humidity}</span> "
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='font-size: 30px;'>|</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        f"<span style='font-size: 20px;'>Smoke:   <span style='font-size: 30px;'> <span style='color: blue;'>{smoke}</span> "
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='font-size: 30px;'>|</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        f"<span style='font-size: 20px;'>CO:   <span style='font-size: 30px;'> <span style='color: yellow;'>{CO}</span> "
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='font-size: 30px;'>|</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        f"<span style='font-size: 20px;'>LPG: <span style='font-size: 30px;'> <span style='color:   purple;'>{LPG}</span> "
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='font-size: 30px;'>|</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        f"<span style='font-size: 20px;'>Flame: <span style='font-size: 30px;'> <span style='color:   orange;'>{flame}</span>"
        , unsafe_allow_html=True
    )

    df = df.iloc[-50:]
    
    # Create Plotly Express figures
    fig1 = px.line(x=df["DateTime"], y=df["temperature"], labels={'x': 'X', 'y': 'Y'}, title='Temperature', color_discrete_sequence=['red'])
    fig2 = px.line(x=df["DateTime"], y=df["humidity"], labels={'x': 'X', 'y': 'Y'}, title='Humidity', color_discrete_sequence=['green'])
    fig3 = px.line(x=df["DateTime"], y=df["smoke"], labels={'x': 'X', 'y': 'Y'}, title='Smoke', color_discrete_sequence=['blue'])
    fig4 = px.line(x=df["DateTime"], y=df["carbon monoxide"], labels={'x': 'X', 'y': 'Y'}, title='Carbon Monoxide', color_discrete_sequence=['yellow'])
    fig5 = px.line(x=df["DateTime"], y=df["LPG"], labels={'x': 'X', 'y': 'Y'}, title='LPG', color_discrete_sequence=['purple'])
    
    # Display the figures side by side
    # st.plotly_chart(fig1, use_container_width=True)
    # st.plotly_chart(fig2, use_container_width=True)
    
    # Create subplots
    # fig = make_subplots(rows=3, cols=2, subplot_titles=('Temperature', 'Humidity', 'Smoke', 'CO', 'LPG'))
    fig = make_subplots(rows=3, cols=2, subplot_titles=('Temperature & Humidity', 'Smoke', 'Carbon Monoxide', 'LPG'), horizontal_spacing=0.1, vertical_spacing=0.15, row_heights=[0.3, 0.3, 0.3], column_widths=[0.4, 0.4])
    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=1)
    fig.add_trace(fig3.data[0], row=1, col=2)
    fig.add_trace(fig4.data[0], row=2, col=1)
    fig.add_trace(fig5.data[0], row=2, col=2)
    
    # Update layout
    fig.update_layout(showlegend=False, width=800, height=800, margin=dict(t=100))
    
    # Display the figures side by side
    st.plotly_chart(fig, use_container_width=True)

def log_coordinates(name, latitude, longitude):
    # Insert coordinates into the Supabase table
    supabase.table('locations').insert({'name': name, 'latitude': latitude, 'longitude': longitude}).execute()
    # response = supabase.table('locations').insert({'latitude': latitude, 'longitude': longitude}).execute()
    # if response['status'] == 201:
        # st.sidebar.success("Coordinates logged successfully.")
    # else:
        # st.sidebar.error("Failed to log coordinates. Error: {}".format(response['error']))
    
 # Function to retrieve coordinates from the Supabase table
def get_coordinates():
    supabase_data = supabase.table('locations').select('*').order('created_at').execute().data
    
    # Reverse the order of the list to achieve descending order
    supabase_data.reverse()

    # Process data into a DataFrame
    lf = pd.DataFrame()
    data = []

    for index, row in enumerate(supabase_data):
        row["created_at"] = row["created_at"].split(".")[0]
        row["time"] = row["created_at"].split("T")[1]
        row["date"] = row["created_at"].split("T")[0]
        row["DateTime"] = row["created_at"]
        data.append(row)

    lf = pd.DataFrame(data)
    lf = lf.sort_values(by='DateTime')

    clatitude = lf['latitude'].iloc[-1]
    clongitude = lf['longitude'].iloc[-1]
    name = lf['name'].iloc[-1]

    return name, clatitude, clongitude
    
# Call the main function
if __name__ == "__main__":
    main()
