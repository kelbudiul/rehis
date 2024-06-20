import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Define the function to fetch air quality data
def get_air_quality_data(location):
    try:
        url = f"https://api.openaq.org/v1/latest?city={location}"
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        if not data['results']:
            return None
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching air quality data: {e}")
        return None

# Define the function to fetch water quality data
def get_water_quality_data(site_code):
    try:
        url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={site_code}&parameterCd=00010,00095,00400,00300&siteType=ST"
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        if not data['value']['timeSeries']:
            return None
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching water quality data: {e}")
        return None

# Mock function to convert location to site code
def get_site_code(location):
    # In a real application, you would implement logic to map the location to the appropriate site code
    # Here we use a mock site code for demonstration purposes
    site_codes = {
        "Los Angeles": "1106170",  # Example site code
        "New York": "01333000",  # Example site code
        "Washington": "01646500"  # Example site code
    }
    return site_codes.get(location, None)

# Map parameter codes to descriptive names
parameter_descriptions = {
    'pm25': 'PM2.5 (Fine particulate matter)',
    'pm10': 'PM10 (Respirable particulate matter)',
    'co': 'CO (Carbon monoxide)',
    'no2': 'NO2 (Nitrogen dioxide)',
    'so2': 'SO2 (Sulfur dioxide)',
    'o3': 'O3 (Ozone)'
}

# Streamlit App
st.title("Real-Time Environmental Health Information Service (REHIS)")

# User input for location
location = st.text_input("Enter your location (city):", "Los Angeles")

if location:
    st.subheader("Air Quality Data")
    air_quality_data = get_air_quality_data(location)
    if air_quality_data:
        locations = []
        parameters = []
        values = []
        units = []
        for result in air_quality_data['results']:
            for measurement in result['measurements']:
                locations.append(result['location'])
                parameters.append(parameter_descriptions.get(measurement['parameter'], measurement['parameter']))
                values.append(measurement['value'])
                units.append(measurement['unit'])
        
        df_air_quality = pd.DataFrame({
            'Location': locations,
            'Parameter': parameters,
            'Value': values,
            'Unit': units
        })
        
        st.write(df_air_quality)
        
        # Plot air quality data
        fig = px.line(df_air_quality, x='Location', y='Value', color='Parameter', title='Air Quality Measurements', labels={
            'Value': 'Measurement Value',
            'Location': 'Measurement Location',
            'Parameter': 'Pollutant'
        })
        st.plotly_chart(fig)
        
    else:
        st.write("No air quality data available for the specified location.")
    
    st.subheader("Water Quality Data")
    site_code = get_site_code(location)
    if site_code:
        water_quality_data = get_water_quality_data(site_code)
        if water_quality_data:
            timestamps = []
            variable_names = []
            values = []
            for result in water_quality_data['value']['timeSeries']:
                for value in result['values'][0]['value']:
                    timestamps.append(value['dateTime'])
                    variable_names.append(result['variable']['variableName'])
                    values.append(value['value'])
            
            df_water_quality = pd.DataFrame({
                'Timestamp': timestamps,
                'Variable': variable_names,
                'Value': values
            })
            
            st.write(df_water_quality)
            
            # Plot water quality data
            fig = px.line(df_water_quality, x='Timestamp', y='Value', color='Variable', title='Water Quality Measurements', labels={
                'Value': 'Measurement Value',
                'Timestamp': 'Measurement Time',
                'Variable': 'Water Quality Parameter'
            })
            st.plotly_chart(fig)
            
        else:
            st.write("No water quality data available for the specified location.")
    else:
        st.write("No site code available for the specified location.")
