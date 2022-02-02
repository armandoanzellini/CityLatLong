# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 13:51:50 2022

@author: Armando Anzellini

Create a CSV spreadsheet which converts City, State, and Country data into 
Latitude and Longitude coordinates based on OpenStreetMap (https://www.openstreetmap.org/)
"""
import base64
import pandas as pd
import streamlit as st
from OSMPythonTools.nominatim import Nominatim

st.title('City and State Lat Long Finder')
st.markdown('Ensure the file has column names titled City, State, and Country \
            to be used in finding the latitude and longitude (case sensitive)')

# Ask user to upload a file
uploaded_file = st.file_uploader("Upload single XLSX or CSV file...", 
                                                  type=["xlsx", "csv"])

class CityLatLong():
    def __init__(self, file):
        self.file = file
        # check filetype and read using that                                                   
        filename = file.name
        
        if filename.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            filename = filename.strip('.xlsx')
        elif filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)  
            filename = filename.strip('.csv')
        
        # df = pd.read_excel("D:\\Users\\Armando\\OneDrive\\Documents\\Academic\\Dissertation\\Bass Collection\\DonorResidenceCityTime.xlsx")
        
        df['location'] = df['City'] + ', ' + df['State'] + ', ' + df['Country']
        
        self.data     = df
        self.filename = filename
    #-----------------------------------------------------------------------------        
    def latlongquery(self):
        data = self.data
        
        nominatim = Nominatim()
        loclist = data['location'].unique()
        locdict = {}

        # iterate over cities in set to get their lat and long and add to dict
        for city in loclist:
            try:
                city_json = nominatim.query(city).toJSON()[0]
            except IndexError:
                city_json = {"lat" : None, "lon" : None}
                
            locdict[city] = [city_json["lat"], city_json["lon"]]
                
        return locdict
    #-----------------------------------------------------------------------------  
    def run(self):
        data = self.data
        locdict = self.latlongquery()
        
        # take returned dictionary and add lat and long to dataframe
        data[['Lat','Long']] = data['location'].map(locdict).to_list()
        
        data.drop('location', axis=1, inplace=True)
        
        return self.filename, data
#-----------------------------------------------------------------------------    
def download_csv(dataframe, filename, display_text, index=False):
    '''
    
    Parameters
    ----------
    dataframe : TYPE
        DESCRIPTION.
    filename  : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    csv = dataframe.to_csv(index=index)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings
    linko= f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">{display_text}</a>'
    st.markdown(linko, unsafe_allow_html=True)
#-----------------------------------------------------------------------------    
if uploaded_file:
    run    = st.button('Run', help='hover_text')
    if run:
        fname, new = CityLatLong(uploaded_file).run()
        st.title('Download CSV output file')
        download_csv(new, fname +'_LatLong', 
                             'Download new CSV with Coordinates')

