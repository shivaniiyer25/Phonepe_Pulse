#importing libraries
import pandas as pd
import numpy as np
import json
import requests
import subprocess
import mysql.connector as sql
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
import PIL
from PIL import Image
mydb =sql.connect(
  host = "localhost",
  user = "root",
  password = "Aishini@24",
  database ="phonepe_pulse"
)
mycursor = mydb.cursor()

st.set_page_config(layout="wide")

selected = option_menu(None,
                       options = ["Home","Analysis","Insights",],
                       icons = ["bar-chart","house","toggles","at"],
                       default_index=0,
                       orientation="vertical",
                       styles={"container": {"width": "50%", "justify-content": "flex-start"},
                               "icon": {"color": "white", "font-size": "24px"},
                               "nav-link": {"font-size": "24px", "text-align": "center", "margin": "-2px"},
                               "nav-link-selected": {"background-color": "#6F36AD"}})
if selected == "Home":
    st.title(':violet[Overview]')
    st.markdown('''The objective of this project is to create a solution capable of retrieving, modifying, and presenting data sourced from the Phonepe Pulse GitHub repository. 

    Acquiring Data:
    Retrieve data from the Phonepe Pulse GitHub repository by utilizing scripting techniques for cloning the repository and fetching data. 
    Store the acquired data in a suitable format like CSV or JSON. 

    Data Processing: 
    Leverage scripting languages like Python and libraries such as Pandas to preprocess and transform the data. 
    Tasks may involve data cleaning, managing missing values, and formatting the data to make it suitable for analysis and visualization. 

    Database Integration:
    Utilize the "mysql-connector-python" library in Python to establish a connection with a MySQL database. 
    Insert the transformed data into the database using SQL commands. 

    Dashboard Development:
    Employ Python libraries like Streamlit and Plotly to develop an interactive and visually appealing dashboard. 
    Plotly's geo map functionalities can be utilized to visually represent the data on a map. Streamlit offers tools to create a user-friendly interface with dropdown options, enabling users to select various data metrics for display. 

    Data Retrieval:
    Utilize the "mysql-connector-python" library to connect to the MySQL database and retrieve the data into a Pandas dataframe. 
    Utilize the dataframe to dynamically update the dashboard with the latest data.''')



# ANALYSIS TAB
if selected == "Analysis":
    st.title(':violet[ANALYSIS]')
    st.subheader('Analysis is of all over Indian States and union territories between 2018 and 2023')
    select = option_menu(None,
                         options=["INDIA", "STATES", "TOP CATEGORIES" ],
                         default_index=0,
                         orientation="horizontal",
                         styles={"container": {"width": "100%"},
                                   "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px"},
                                   "nav-link-selected": {"background-color": "#6F36AD"}})
    if select == "INDIA":
        tab1, tab2 = st.tabs(["TRANSACTION","USER"])

        # TRANSACTION TAB
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                in_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='in_tr_yr')
            with col2:
                in_tr_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='in_tr_qtr')
            with col3:
                in_tr_tr_typ = st.selectbox('**Select Transaction type**',
                                            ('Recharge & bill payments', 'Peer-to-peer payments',
                                             'Merchant payments', 'Financial Services', 'Others'), key='in_tr_tr_typ')
            # SQL Query
        
        # Transaction Analysis bar chart query
            mycursor.execute(
                f"SELECT State, Transaction_amount FROM agg_trans WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
            in_tr_tab_qry_rslt = mycursor.fetchall()
            df_in_tr_tab_qry_rslt = pd.DataFrame(np.array(in_tr_tab_qry_rslt), columns=['State', 'Transaction_amount'])
            df_in_tr_tab_qry_rslt1 = df_in_tr_tab_qry_rslt.set_index(pd.Index(range(1, len(df_in_tr_tab_qry_rslt) + 1)))
        
         # Transaction Analysis table query
            mycursor.execute(
                f"SELECT State, Transaction_count, Transaction_amount FROM agg_trans WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
            in_tr_anly_tab_qry_rslt = mycursor.fetchall()
            df_in_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(in_tr_anly_tab_qry_rslt),
                                                      columns=['State', 'Transaction_count', 'Transaction_amount'])
            df_in_tr_anly_tab_qry_rslt1 = df_in_tr_anly_tab_qry_rslt.set_index(
                pd.Index(range(1, len(df_in_tr_anly_tab_qry_rslt) + 1)))

            # Total Transaction Amount table query
            mycursor.execute(
                f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM agg_trans WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
            in_tr_am_qry_rslt = mycursor.fetchall()
            df_in_tr_am_qry_rslt = pd.DataFrame(np.array(in_tr_am_qry_rslt), columns=['Total', 'Average'])
            df_in_tr_am_qry_rslt1 = df_in_tr_am_qry_rslt.set_index(['Average'])

            # Total Transaction Count table query
            mycursor.execute(
                f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM agg_trans WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
            in_tr_co_qry_rslt = mycursor.fetchall()
            df_in_tr_co_qry_rslt = pd.DataFrame(np.array(in_tr_co_qry_rslt), columns=['Total', 'Average'])
            df_in_tr_co_qry_rslt1 = df_in_tr_co_qry_rslt.set_index(['Average'])


            # GEO VISUALISATION
            # Drop a State column from df_in_tr_tab_qry_rslt
            df_in_tr_tab_qry_rslt.drop(columns=['State'], inplace=True)
            # Clone the gio data
            url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            response = requests.get(url)
            data1 = json.loads(response.content)
            # Extract state names and sort them in alphabetical order
            state_names_tra = [feature['properties']['ST_NM'] for feature in data1['features']]
            state_names_tra.sort()
            # Create a DataFrame with the state names column
            df_state_names_tra = pd.DataFrame({'State': state_names_tra})
            # Combine the Geo State name with df_in_tr_tab_qry_rslt
            df_state_names_tra['Transaction_amount'] = df_in_tr_tab_qry_rslt
            # convert dataframe to csv file
            df_state_names_tra.to_csv('State_trans.csv', index=False)
            # Read csv
            df_tra = pd.read_csv('State_trans.csv')
            # Geo plot
            fig_tra = px.choropleth(
                df_tra,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM', locations='State', color='Transaction_amount',
                color_continuous_scale='magma', title='Transaction Analysis')
            fig_tra.update_geos(fitbounds="locations", visible=False)
            fig_tra.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
            st.plotly_chart(fig_tra, use_container_width=True)

            # ---------   /   All India Transaction Analysis Bar chart  /  ----- #
            df_in_tr_tab_qry_rslt1['State'] = df_in_tr_tab_qry_rslt1['State'].astype(str)
            df_in_tr_tab_qry_rslt1['Transaction_amount'] = df_in_tr_tab_qry_rslt1['Transaction_amount'].astype(float)
            df_in_tr_tab_qry_rslt1_fig = px.bar(df_in_tr_tab_qry_rslt1, x='State', y='Transaction_amount',
                                                color='Transaction_amount', color_continuous_scale='magma',
                                                title='Transaction Analysis Chart', height=700, )
            df_in_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_in_tr_tab_qry_rslt1_fig, use_container_width=True)


            # Creating the pie chart
            df_in_tr_tab_qry_rslt1_piefig = px.pie(df_in_tr_tab_qry_rslt1, 
                                                values='Transaction_amount',  
                                                names='State',  
                                                title='Transaction Analysis Pie Chart', 
                                                color='State',  
                                                height=450)

            # Customizing the layout
            df_in_tr_tab_qry_rslt1_piefig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            
            # Displaying the pie chart
            st.plotly_chart(df_in_tr_tab_qry_rslt1_piefig, use_container_width=True)

            # -------  /  All India Total Transaction calculation Table   /   ----  #
            st.header(':violet[Total calculation]')

            col4, col5 = st.columns(2)
            with col4:
                st.subheader(':violet[Transaction Analysis]')
                st.dataframe(df_in_tr_anly_tab_qry_rslt1)
            with col5:
                st.subheader(':violet[Transaction Amount]')
                st.dataframe(df_in_tr_am_qry_rslt1)
                st.subheader(':violet[Transaction Count]')
                st.dataframe(df_in_tr_co_qry_rslt1)

        # USER TAB
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                in_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='in_us_yr')
            with col2:
                in_us_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='in_us_qtr')

            # SQL Query

            # User Analysis Bar chart query
            mycursor.execute(f"SELECT State, SUM(Count) FROM agg_user WHERE Year = '{in_us_yr}' AND Quarter = '{in_us_qtr}' GROUP BY State;")
            in_us_tab_qry_rslt = mycursor.fetchall()
            df_in_us_tab_qry_rslt = pd.DataFrame(np.array(in_us_tab_qry_rslt), columns=['State', 'Count'])
            df_in_us_tab_qry_rslt1 = df_in_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_in_us_tab_qry_rslt) + 1)))

            # Total User Count table query
            mycursor.execute(f"SELECT SUM(Count), AVG(Count) FROM agg_user WHERE Year = '{in_us_yr}' AND Quarter = '{in_us_qtr}';")
            in_us_co_qry_rslt = mycursor.fetchall()
            df_in_us_co_qry_rslt = pd.DataFrame(np.array(in_us_co_qry_rslt), columns=['Total', 'Average'])
            df_in_us_co_qry_rslt1 = df_in_us_co_qry_rslt.set_index(['Average'])



            # GEO VISUALIZATION FOR USER

            # Drop a State column from df_in_us_tab_qry_rslt
            df_in_us_tab_qry_rslt.drop(columns=['State'], inplace=True)
            # Clone the gio data
            url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            response = requests.get(url)
            data2 = json.loads(response.content)
            # Extract state names and sort them in alphabetical order
            state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
            state_names_use.sort()
            # Create a DataFrame with the state names column
            df_state_names_use = pd.DataFrame({'State': state_names_use})
            # Combine the Geo State name with df_in_tr_tab_qry_rslt
            df_state_names_use['Count'] = df_in_us_tab_qry_rslt
            # convert dataframe to csv file
            df_state_names_use.to_csv('State_user.csv', index=False)
            # Read csv
            df_use = pd.read_csv('State_user.csv')
            # Geo plot
            fig_use = px.choropleth(
                df_use,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM', locations='State', color='Count',
                color_continuous_scale='magma',
                title='User Analysis')
            fig_use.update_geos(fitbounds="locations", visible=False)
            fig_use.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
            st.plotly_chart(fig_use, use_container_width=True)

            # ----   /   All India User Analysis Bar chart   /     -------- #
            
            df_in_us_tab_qry_rslt1['State'] = df_in_us_tab_qry_rslt1['State'].astype(str)
            df_in_us_tab_qry_rslt1_fig = px.bar(df_in_us_tab_qry_rslt1, 
                                                    x='State', 
                                                    y='Count', 
                                                    color='Count',
                                                    color_continuous_scale= 'magma',
                                                    title='User Analysis Bar Chart',
                                                    height=700)
            df_in_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_in_us_tab_qry_rslt1_fig, use_container_width=True)

            import plotly.express as px

# ----   /   All India User Analysis Donut chart   /     -------- #
            df_in_us_tab_qry_rslt1_piefig = px.pie(df_in_us_tab_qry_rslt1, 
                                                values='Count',  
                                                names='State',   
                                                hole= 0.4,
                                                title='User Analysis Donut Chart', 
                                                height=600)

            df_in_us_tab_qry_rslt1_piefig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_in_us_tab_qry_rslt1_piefig, use_container_width=True)


            # -----   /   All India Total User calculation Table   /   ----- #
            st.header(':violet[Total calculation]')

            col3, col4 = st.columns(2)
            with col3:
                st.subheader(':violet[User Analysis]')
                st.dataframe(df_in_us_tab_qry_rslt1)
            with col4:
                st.subheader(':violet[Count]')
                st.dataframe(df_in_us_co_qry_rslt1)

        # STATE TAB
# STATE TAB
    if select == "STATES":
        tab3 ,tab4 = st.tabs(["TRANSACTION","USER"])

     #TRANSACTION TAB FOR STATE
        with tab3:
            col1, col2, col3 = st.columns(3)
            with col1:
                st_tr_st = st.selectbox('**Select State**', (
                'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
                'haryana', 'himachal-pradesh',
                'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh',
                'maharashtra', 'manipur',
                'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                'tamil-nadu', 'telangana',
                'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), key='st_tr_st')
            with col2:
                st_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='st_tr_yr')
            with col3:
                st_tr_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='st_tr_qtr')


            # SQL QUERY

            #Transaction Analysis bar chart query
            mycursor.execute(f"SELECT Transaction_type, Transaction_amount FROM agg_trans WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
            st_tr_tab_bar_qry_rslt = mycursor.fetchall()
            df_st_tr_tab_bar_qry_rslt = pd.DataFrame(np.array(st_tr_tab_bar_qry_rslt),
                                                     columns=['Transaction_type', 'Transaction_amount'])
            df_st_tr_tab_bar_qry_rslt1 = df_st_tr_tab_bar_qry_rslt.set_index(
                pd.Index(range(1, len(df_st_tr_tab_bar_qry_rslt) + 1)))

            # Transaction Analysis table query
            mycursor.execute(f"SELECT Transaction_type, Transaction_count, Transaction_amount FROM agg_trans WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
            st_tr_anly_tab_qry_rslt = mycursor.fetchall()
            df_st_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(st_tr_anly_tab_qry_rslt),
                                                      columns=['Transaction_type', 'Transaction_count',
                                                               'Transaction_amount'])
            df_st_tr_anly_tab_qry_rslt1 = df_st_tr_anly_tab_qry_rslt.set_index(
                pd.Index(range(1, len(df_st_tr_anly_tab_qry_rslt) + 1)))

            # Total Transaction Amount table query
            mycursor.execute(f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM agg_trans WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
            st_tr_am_qry_rslt = mycursor.fetchall()
            df_st_tr_am_qry_rslt = pd.DataFrame(np.array(st_tr_am_qry_rslt), columns=['Total', 'Average'])
            df_st_tr_am_qry_rslt1 = df_st_tr_am_qry_rslt.set_index(['Average'])

            # Total Transaction Count table query
            mycursor.execute(f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM agg_trans WHERE State = '{st_tr_st}' AND Year ='{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
            st_tr_co_qry_rslt = mycursor.fetchall()
            df_st_tr_co_qry_rslt = pd.DataFrame(np.array(st_tr_co_qry_rslt), columns=['Total', 'Average'])
            df_st_tr_co_qry_rslt1 = df_st_tr_co_qry_rslt.set_index(['Average'])



            # -----    /   State wise Transaction Analysis bar chart   /   ------ #

            df_st_tr_tab_bar_qry_rslt1['Transaction_type'] = df_st_tr_tab_bar_qry_rslt1['Transaction_type'].astype(str)
            df_st_tr_tab_bar_qry_rslt1['Transaction_amount'] = df_st_tr_tab_bar_qry_rslt1['Transaction_amount'].astype(
                float)
            df_st_tr_tab_bar_qry_rslt1_fig = px.bar(df_st_tr_tab_bar_qry_rslt1, x='Transaction_type',
                                                    y='Transaction_amount', color='Transaction_amount',
                                                    color_continuous_scale='magma',
                                                    title='Transaction Analysis Chart', height=500, )
            df_st_tr_tab_bar_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_st_tr_tab_bar_qry_rslt1_fig, use_container_width=True)

            # ------  /  State wise Total Transaction calculation Table  /  ---- #
            st.header(':violet[Total calculation]')

            col4, col5 = st.columns(2)
            with col4:
                st.subheader(':violet[Transaction Analysis]')
                st.dataframe(df_st_tr_anly_tab_qry_rslt1)
            with col5:
                st.subheader(':violet[Transaction Amount]')
                st.dataframe(df_st_tr_am_qry_rslt1)
                st.subheader(':violet[Transaction Count]')
                st.dataframe(df_st_tr_co_qry_rslt1)


        # USER TAB FOR STATE
        with tab4:
            col5, col6 = st.columns(2)
            with col5:
                st_us_st = st.selectbox('**Select State**', (
                'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
                'haryana', 'himachal-pradesh',
                'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh',
                'maharashtra', 'manipur',
                'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                'tamil-nadu', 'telangana',
                'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), key='st_us_st')
            with col6:
                st_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022'), key='st_us_yr')
            # SQL QUERY

            # User Analysis Bar chart query
            mycursor.execute(f"SELECT Quarter, SUM(Count) FROM agg_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}' GROUP BY Quarter;")
            st_us_tab_qry_rslt = mycursor.fetchall()
            df_st_us_tab_qry_rslt = pd.DataFrame(np.array(st_us_tab_qry_rslt), columns=['Quarter', 'Count'])
            df_st_us_tab_qry_rslt1 = df_st_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_st_us_tab_qry_rslt) + 1)))

            # Total User Count table query
            mycursor.execute(f"SELECT SUM(Count), AVG(Count) FROM agg_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}';")
            st_us_co_qry_rslt = mycursor.fetchall()
            df_st_us_co_qry_rslt = pd.DataFrame(np.array(st_us_co_qry_rslt), columns=['Total', 'Average'])
            df_st_us_co_qry_rslt1 = df_st_us_co_qry_rslt.set_index(['Average'])


            # -----   /   State User Analysis Bar chart   /   ----- #
            df_st_us_tab_qry_rslt1['Quarter'] = df_st_us_tab_qry_rslt1['Quarter'].astype(int)
    
            df_st_us_tab_qry_rslt1_fig = px.bar(df_st_us_tab_qry_rslt1, x='Quarter', y='Count', color='Count',
                                                color_continuous_scale='magma', title='User Analysis Chart',
                                                height=700 )
            df_st_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_st_us_tab_qry_rslt1_fig, use_container_width=True)

            # ------    /   State wise User Total User calculation Table   /   -----#
            st.header(':violet[Total calculation]')

            col3, col4 = st.columns(2)
            with col3:
                st.subheader(':violet[User Analysis]')
                st.dataframe(df_st_us_tab_qry_rslt1)
            with col4:
                st.subheader(':violet[User Count]')
                st.dataframe(df_st_us_co_qry_rslt1)

            
         # TOP CATEGORIES
    if select == "TOP CATEGORIES":
        tab5, tab6 = st.tabs(["TRANSACTION", "USER"])

        # Overall top transaction
        #TRANSACTION TAB
        with tab5:
            top_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_tr_yr')

            #SQL QUERY

            #Top Transaction Analysis bar chart query
            mycursor.execute(
                f"SELECT State, SUM(Transaction_amount) As Transaction_amount FROM top_trans WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
            top_tr_tab_qry_rslt = mycursor.fetchall()
            df_top_tr_tab_qry_rslt = pd.DataFrame(np.array(top_tr_tab_qry_rslt),
                                                  columns=['State', 'Top Transaction amount'])
            df_top_tr_tab_qry_rslt1 = df_top_tr_tab_qry_rslt.set_index(
                pd.Index(range(1, len(df_top_tr_tab_qry_rslt) + 1)))

            # Top Transaction Analysis table query
            mycursor.execute(
                f"SELECT State, SUM(Transaction_amount) as Transaction_amount, SUM(Transaction_count) as Transaction_count FROM top_trans WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
            top_tr_anly_tab_qry_rslt = mycursor.fetchall()
            df_top_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(top_tr_anly_tab_qry_rslt),
                                                       columns=['State', 'Top Transaction amount',
                                                                'Total Transaction count'])
            df_top_tr_anly_tab_qry_rslt1 = df_top_tr_anly_tab_qry_rslt.set_index(
                pd.Index(range(1, len(df_top_tr_anly_tab_qry_rslt) + 1)))



            # Top Transaction Analysis Bar chart
            df_top_tr_tab_qry_rslt1['State'] = df_top_tr_tab_qry_rslt1['State'].astype(str)
            #df_top_tr_tab_qry_rslt1['Top Transaction amount'] = df_top_tr_tab_qry_rslt1['Top Transaction amount'].astype(float)
            df_top_tr_tab_qry_rslt1_fig = px.bar(df_top_tr_tab_qry_rslt1, x='State', y='Top Transaction amount',
                                                 color='Top Transaction amount', color_continuous_scale='magma',
                                                 title='Top Transaction Analysis Chart', height=600, )
            df_top_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_top_tr_tab_qry_rslt1_fig, use_container_width=True)


            #Top Transaction calculation Table
            st.header(':violet[Total calculation]')
            st.subheader('Top Transaction Analysis')
            st.dataframe(df_top_tr_anly_tab_qry_rslt1)

        # OVERALL TOP USER DATA
        # USER TAB
        with tab6:
            top_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_us_yr')

            #SQL QUERY

            #Top User Analysis bar chart query
            mycursor.execute(f"SELECT State, SUM(Registered_users) AS Top_user FROM top_user WHERE Year='{top_us_yr}' GROUP BY State ORDER BY Top_user DESC LIMIT 10;")
            top_us_tab_qry_rslt = mycursor.fetchall()
            df_top_us_tab_qry_rslt = pd.DataFrame(np.array(top_us_tab_qry_rslt), columns=['State', 'Total User count'])
            df_top_us_tab_qry_rslt1 = df_top_us_tab_qry_rslt.set_index(
                pd.Index(range(1, len(df_top_us_tab_qry_rslt) + 1)))



            #Top User Analysis Bar chart
            df_top_us_tab_qry_rslt1['State'] = df_top_us_tab_qry_rslt1['State'].astype(str)
            #df_top_us_tab_qry_rslt1['Total User count'] = df_top_us_tab_qry_rslt1['Total User count'].astype(float)
            df_top_us_tab_qry_rslt1_fig = px.bar(df_top_us_tab_qry_rslt1, x='State', y='Total User count',
                                                 color='Total User count', color_continuous_scale='magma',
                                                 title='Top User Analysis Chart', height=600, )
            df_top_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_top_us_tab_qry_rslt1_fig, use_container_width=True)

            #Top User Analysis calculation Table
            st.header(':violet[Total calculation]')
            st.subheader(':violet[Total User Analysis]')
            st.dataframe(df_top_us_tab_qry_rslt1)

#INSIGHTS TAB
if selected == "Insights":
    st.title(':violet[BASIC INSIGHTS]')
    st.subheader("Conclusions of Analysis and to answer the below questions.")
    options = ["--select--",
               "Top 10 states based on year and amount of transaction",
               "Least 10 states based on year and amount of transaction",
               "Top 10 States and Districts based on Registered Users",
               "Least 10 States and Districts based on Registered Users",
               "Top 10 Districts based on the Transaction Amount",
               "Least 10 Districts based on the Transaction Amount",
               "Top 10 Districts based on the Transaction count",
               "Least 10 Districts based on the Transaction count",
               "Top Transaction types based on the Transaction Amount",
               "Top 10 Mobile Brands based on the User count of transaction"]
    selectquery = st.selectbox(":violet[Select the option]",options)

    #1
    if selectquery == "Top 10 states based on year and amount of transaction":
        mycursor.execute(
            "SELECT DISTINCT State,Year, SUM(Transaction_amount) AS Total_Transaction_Amount FROM top_trans GROUP BY State,Year ORDER BY Total_Transaction_Amount DESC LIMIT 10");

        data = mycursor.fetchall()
        columns = ['States', 'Year', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 states based on amount of transaction")
            fig = px.bar(df, x="States", y="Transaction_amount", color="Year", barmode="stack")
            st.plotly_chart(fig, use_container_width=True)

    #2
    elif selectquery == "Least 10 states based on year and amount of transaction":
        mycursor.execute(
            "SELECT DISTINCT State,Year, SUM(Transaction_amount) as Total FROM top_trans GROUP BY State, Year ORDER BY Total ASC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['States', 'Year', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1,len(data)+1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 states based on amount of transaction")
            fig = px.bar(df, x="States", y="Transaction_amount", color="Year", barmode="stack")
            st.plotly_chart(fig, use_container_width=True)
    #3
    elif selectquery == "Top 10 States and Districts based on Registered Users":
        mycursor.execute("SELECT DISTINCT State, Pincode, SUM(Registered_users) AS Users FROM top_user GROUP BY State, Pincode ORDER BY Users DESC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['State', 'District_Pincode', 'Registered_User']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 States and Districts based on Registered Users")
            
            fig = px.pie(df, values='Registered_User', names='State')
            st.plotly_chart(fig, use_container_width=True)

    #4
    elif selectquery == "Least 10 States and Districts based on Registered Users":
        mycursor.execute("SELECT DISTINCT State,Pincode, SUM(Registered_users) AS Users FROM top_user GROUP BY State,Pincode ORDER BY Users ASC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['State', 'District_Pincode', 'Registered_User']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 States and Districts based on Registered Users")
            fig = px.pie(df, values='Registered_User', names='State')
            st.plotly_chart(fig, use_container_width=True)
            
            
    #5
    elif selectquery == "Top 10 Districts based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT State ,District,SUM(Amount) AS Total FROM map_trans GROUP BY State ,District ORDER BY Total DESC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_Amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on Transaction Amount")
            st.bar_chart(data=df, x="District", y="Transaction_Amount")

    #6
    elif selectquery == "Least 10 Districts based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT State,District,SUM(Amount) AS Total FROM map_trans GROUP BY State, District ORDER BY Total ASC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 Districts based on Transaction Amount")
            st.bar_chart(data=df, x="District", y="Transaction_amount")

    #7
    elif selectquery == "Top 10 Districts based on the Transaction count":
        mycursor.execute(
            "SELECT DISTINCT State,District,SUM(Count) AS Counts FROM map_trans GROUP BY State ,District ORDER BY Counts DESC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on Transaction Count")
            #st.bar_chart(data=df, x="Transaction_Count", y="District")
            fig = px.pie(df, values='Transaction_Count', names='District', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)


    #8
    elif selectquery== "Least 10 Districts based on the Transaction count":
        mycursor.execute(
            "SELECT DISTINCT State ,District,SUM(Count) AS Counts FROM map_trans GROUP BY State ,District ORDER BY Counts ASC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 Districts based on the Transaction Count")
            fig = px.pie(df, values='Transaction_Count', names='District', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    #9
    elif selectquery == "Top Transaction types based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT Transaction_type, SUM(Transaction_amount) AS Amount FROM agg_trans GROUP BY Transaction_type ORDER BY Amount DESC LIMIT 5");
        data = mycursor.fetchall()
        columns = ['Transaction_type', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top Transaction Types based on the Transaction Amount")
            fig = px.pie(df, values='Transaction_amount', names='Transaction_type', hole=0.2)
            st.plotly_chart(fig, use_container_width=True)

    #10
    elif selectquery == "Top 10 Mobile Brands based on the User count of transaction":
        mycursor.execute(
            "SELECT DISTINCT Brands,SUM(Count) as Total FROM agg_user GROUP BY Brands ORDER BY Total DESC LIMIT 10");
        data = mycursor.fetchall()
        columns = ['Brands', 'User_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Mobile Brands based on User count of transaction")
            st.plotly_chart(px.pie(df, values='User_Count', names='Brands').update_traces(textinfo='percent+label').update_layout(showlegend=False), use_container_width=True)


