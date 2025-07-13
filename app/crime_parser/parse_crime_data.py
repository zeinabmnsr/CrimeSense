import pandas as pd 
from flask import current_app 
#from tqdm import tqdm 

def parse_and_insert():

    collection = current_app.db["parsed_crimes"]

    file_path = "app/crime_parser/prc-csp-mar16-dec24-tables-240425.xlsx"
    sheets = ["2021_22", "2022_23", "2023_24", "2024_25"]
    #sheets = ["2023_24"]

    quarter_month_map = {
        "Q1" : "04-01",
        "Q2" : "07-01",
        "Q3"  :"10-01",
        "Q4" : "01-01"
        }
    
    for sheet in sheets:
        print(f"📄 Reading sheet: {sheet}")

        df = pd.read_excel(file_path, sheet_name=sheet) 

        def parse_date(row):
            try: 
                year = row["Financial Year"].split("/")[0]
                quarter = row["Financial Quarter"]
                return f"{year}-{quarter_month_map.get(quarter, '01-01')}"
            except:
                return None
        df["date_occurred"] = df.apply(parse_date, axis=1)

        #df["date_occured"] = df["Financial Year"] + " " + df["Financial Quarter"]
    
        df = df.rename(columns={
            "Offence Description": "title",
            "Offence Group" : "crime_type",
            "Offence Subgroup" : "description",
            "CSP Name": "location",
            "Offence Count": "offence_count" #how many times this crime happened
            })
        df = df.loc[:, df.columns.map(lambda x: isinstance(x, str))]
        df = df[["title", "crime_type", "description", "location", "offence_count",  "date_occurred"]]
        dict_data = df.to_dict(orient="records")

        for doc in dict_data: #tracking sheets mtl enu kl sheet ela year ka name
            doc["source_sheet"] = sheet 

        def insert_in_batches(collection, data, batch_size=1000):
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                collection.insert_many(batch)

        insert_in_batches(collection, dict_data)
        #print(df.head(10))
        #print("📌 Columns before renaming:")
        #print(df.columns.tolist())

        #break 
        print(f"✅ Inserted {len(dict_data)} rows from sheet: {sheet}")
''' 
df = df.drop(columns=["Financial Year", "Financial Quarter"])

    id : 686284d47ff0d06a19df61f0
####Financial Year : "2015/16"
####Financial Quarter :   1
####Police Force : "Avon and Somerset"
    location : "Bath and North East Somerset"
    title  : "Burglary in a building other than 
                a dwelling (outcome only)"
    crime_type : "Theft offences"
    description : "Non-domestic burglary"
####Offence Code : "30A"
    offence_count : 149
    date_occurred : "2015-01-01"
 ########## Document flagged for deletion. #########

'''