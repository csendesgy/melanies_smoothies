# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your smoothie""")


#option = st.selectbox(
#    "What is your favorite fruit?",
#    ("Bananas", "Strawberries", "Peaches"),
#)

#st.write("Your fav is:", option)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be: ', name_on_order)

#session = get_active_session()
cnx=st.connection('snowflake')
session=cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True) #print the list
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredience"
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    #st.write(ingredients_list) 
    #st.text(ingredients_list) 
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        #st.text(smoothiefroot_response.json())
        st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    st.write(ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, NAME_ON_ORDER)
            values ('""" + ingredients_string + """'
                   ,'""" + name_on_order + """'
                   )"""

    time_to_insert = st.button('Submit Order')
    
    #st.write(my_insert_stmt)
    #if ingredients_string:
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(name_on_order + ' Your Smoothie is ordered!', icon="✅")

