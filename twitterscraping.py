import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
from pymongo import MongoClient 
import streamlit as st
from datetime import datetime, timedelta
import base64
st.title("Twitter scraping utility")
#Streamlit app
def TwitterScrapingUtility():
    df = pd.DataFrame()
    #Streamlit input 
    text_query = st.text_input("Enter Keyword to search:")
    since_date = st.date_input("Enter start date:")
    until_date = st.date_input("Enter end date:")
    max_tweets = st.number_input("Enter number of tweets you want : ",step=1)
    #text_query = "DasaraMovie"
    #since_date = "2023-04-01"
    #until_date = "2023-04-05"
    #max_tweets = 5
    #Creating unique name based on query 
    databasename=str(text_query)+str(since_date)+ \
                  str(until_date)+str(max_tweets)
    idx=0
    if st.button('Scrape'):
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{text_query} since:{since_date} until:{until_date}').get_items()):
            if i > max_tweets:
                break
            new_row = {'user':tweet.user.username,
                        'date':tweet.date, 
                        'id':tweet.id, 
                        'content': tweet.rawContent,
                        'url':tweet.url,
                        'likeCount':tweet.likeCount,
                        'language':tweet.lang,
                        'viewcount':tweet.viewCount}
            idx=idx+1
            df = pd.concat([df, pd.DataFrame(new_row, index=[idx])])
    df

    if not df.empty:
        if st.button('Save to Database') :
       
            data_upload = {"Scraped Word": text_query,
                            "Scraped Date" : datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                             "Scraped Data" : df.to_dict(orient='records')}
            result = upload_to_mongodb(databasename, data_upload)
        
        csvname=databasename
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        st.markdown(f'<a href="data:file/csv;base64,{b64}" download="{databasename}_data.csv">Download CSV</a>', unsafe_allow_html=True)
        
        json_str = df.to_json(orient="records",indent=3)
        b64 = base64.b64encode(json_str.encode()).decode()
        st.markdown(f'<a href="data:application/json;base64,{b64}" download="{databasename}_data.json">Download JSON</a>', unsafe_allow_html=True)

def upload_to_mongodb(databasename, data_upload):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[databasename]
    collection = db["mycollection"]
    collection.insert_one(data_upload)
    
TwitterScrapingUtility()



