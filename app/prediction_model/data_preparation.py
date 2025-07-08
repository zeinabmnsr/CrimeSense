import pandas as pd 
from flask import current_app 
import os 

def load_data_from_mongo(batch_size=500, max_docs=None):
    collection = current_app.db["parsed_crimes"]
    #for batch using
    all_docs = []
    last_id = None 
    while True if max_docs is None else len(all_docs) < max_docs:
        query = {}
        if last_id:
            query["_id"] = {"$gt": last_id}
        cursor = collection.find(
        query,
        {
            "_id": 1,
            "title": 1,
            "crime_type": 1,
            "location": 1,
            "date_occurred": 1,
            "offence_count": 1,
            "description": 1,
            "financial_year": 1,
            "financial_quarter": 1
    }).sort("_id").limit(batch_size)
        batch = list(cursor)
        if not batch:
            break 
        last_id = batch[-1]["_id"]
        all_docs.extend(batch)

    for doc in all_docs:
        doc.pop("_id", None)

    df = pd.DataFrame(all_docs)

    df.dropna(subset=["location", "date_occurred", "crime_type", "offence_count"], inplace=True)
    
    df = df[df["offence_count"] > 0]
    df["year"] = df["date_occurred"].str[:4]
    df["month"] = df["date_occurred"].str[5:7]

    def map_month_to_quarter(month):
        month = int(month)
        if month == 1:
            return "Q4"
        elif month in [4, 5, 6]:
            return "Q1"
        elif month in [7, 8, 9]:
            return "Q2"
        elif month in [10, 11, 12]:
            return "Q3"
        else:
            return "Unknown"
        
    df["quarter"] = df["month"].apply(map_month_to_quarter)
       # should i remove this line: ?   
    #df = df[["location", "year", "quarter", "crime_type"]]
    
    from .trend_features import add_trend_features

    df_grouped = df.groupby(
    ["location", "year", "quarter", "description", "crime_type"]
).agg({
    "offence_count": "sum"
}).reset_index().rename(columns={"offence_count": "incidents"})

    # Now that df_grouped exists, you can safely apply trend logic
    df_grouped = add_trend_features(df_grouped)

    return df_grouped