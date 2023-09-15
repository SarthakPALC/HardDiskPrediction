from pymongo import MongoClient
from datetime import datetime, timedelta
import re
import time

# Create a MongoClient instance and connect to the database
client = MongoClient("mongodb://mongoadmin:bdung@127.0.0.1:27017/syslog?authSource=admin")
db = client["syslog"]


# Start polling for new documents every 5 seconds
collection = db["alarms"]


# Create an index on the _id field
"""collection.create_index([("MESSAGE", 1)])

# Initialize the previous state of Ethernet
previous_state = None
"""
"""collection.create_index([("MESSAGE", 1)])

# Find the current Ethernet state document, if it exists

current_state_document = collection.find_one()
if current_state_document:
    current_state = current_state_document["MESSAGE"].split(": ")[-1]
else:
    current_state = None

# Start polling for new documents every 5 seconds
while True:
    # Get the latest document in the collection
    latest_document = collection.find_one(sort=[("_id", -1)])

    # Check if the Ethernet state has changed
    if latest_document["MESSAGE"].split(": ")[-1] != current_state:
        # Delete the previous document
        if current_state_document:
            collection.delete_one({"_id": current_state_document["_id"]})

        # Update the current Ethernet state
        current_state = latest_document["MESSAGE"].split(": ")[-1]
        current_state_document = latest_document

        # Insert the new document as the current Ethernet state
        collection.insert_one(current_state_document)

    # Wait 5 seconds before polling again
    time.sleep(5)
"""
"""current_state_document = collection.find_one()

# Get the current Ethernet state from the document, or set it to None if the document doesn't exist
current_state = current_state_document["MESSAGE"].split(": ")[-1] if current_state_document is not None else None

# Start polling for new documents every 5 seconds
while True:
    # Get the latest document in the collection
    latest_document = collection.find_one(sort=[("_id", -1)])

    # Check if the Ethernet state has changed
    if latest_document is not None and latest_document["MESSAGE"].split(": ")[-1] != current_state:
        # Update the current Ethernet state and delete the previous document
        current_state = latest_document["MESSAGE"].split(": ")[-1]
        if current_state_document is not None:
            collection.delete_one({"_id": current_state_document["_id"]})

        # Insert the new document as the current Ethernet state
        current_state_document = collection.insert_one(latest_document).inserted_id

    # Wait 5 seconds before polling again
    time.sleep(5) """

"""# Initialize the previous state of Ethernet
previous_state = None

# Start polling for new documents every 5 seconds
while True:
    # Find all documents in the collection
    documents = collection.find()

    # Loop through all documents and delete the previous state if there is a change in the Ethernet state
    for document in documents:
        # Get the Ethernet state from the document message
        ethernet_state = None
        if "Port Ethernet" in document["MESSAGE"]:
            ethernet_state = "up" if "oper state set from down to up" in document["MESSAGE"] else "down"

        # Check if the Ethernet state has changed
        if ethernet_state is not None and ethernet_state != previous_state:
            # Delete the previous document if it exists
           # if previous_state is not None:
            collection.delete_one({"MESSAGE": document["MESSAGE"], "ETHERNET_STATE": previous_state})

            # Insert the new state as a new document
            collection.insert_one({"MESSAGE": document["MESSAGE"], "ETHERNET_STATE": ethernet_state})

            # Update the previous state
            previous_state = ethernet_state

    # Wait 5 seconds before polling again
    time.sleep(5)
"""
"""latest_doc = collection.find_one(sort=[("_id", -1)])

# Check if the latest document represents an Ethernet state change
if re.search("Port [A-Za-z0-9]+ oper state set from up to down", latest_doc["MESSAGE"]):
    # Delete the previous document with the same Ethernet
    previous_doc = collection.find_one({"MESSAGE": latest_doc["MESSAGE"], "_id": {"$lt": latest_doc["_id"]}})
    if previous_doc is not None:
        collection.delete_one({"_id": previous_doc["_id"]})
elif re.search("Port [A-Za-z0-9]+ oper state set from down to up", latest_doc["MESSAGE"]):
    # Do nothing, as this represents the latest state of the Ethernet
    pass"""
"""collection.create_index([("DATE", -1)])

# Start polling for new documents every 5 seconds
while True:
    # Get the latest Ethernet state document in the collection
    #latest_document = collection.find_one({"MESSAGE": re.compile("Port [A-Za-z0-9]+ oper state set from"), "DATE": {"$exists": True}}, sort=[("DATE", -1)])
    latest_document = collection.find_one({"MESSAGE": re.compile("Port [A-Za-z0-9]+ oper state set from (up to down|down to up)"), "DATE": {"$exists": True}}, sort=[("DATE", -1)])


    # Get the latest Ethernet state from the latest document
    latest_state = latest_document["MESSAGE"] if latest_document else None
    count = collection.count_documents({"MESSAGE": latest_state})
    # Delete all previous Ethernet state documents
    
   
    if latest_state:
       #collection.delete_many({"MESSAGE": latest_state})
       latest_id = latest_document["_id"]
       #print(latest_id)
       #count_without_latest = collection.count_documents({"MESSAGE": latest_state, "_id": {"$ne": latest_id}})
       #if count_without_latest > 0:
       collection.delete_many({"MESSAGE": latest_state, "_id": {"$ne": latest_id}})
       #cursor = collection.find({"MESSAGE": latest_state, "_id": {"$ne": latest_id}})
       #for doc in cursor:
       #    collection.delete_one({"_id": doc["_id"]})
    # Wait 5 seconds before polling again
    time.sleep(5)"""

"""while True:
    # Get the latest Ethernet state document in the collection
    latest_document = collection.find_one({"MESSAGE": re.compile("Port [A-Za-z0-9]+ oper state set from"), "DATE": {"$exists": True}}, sort=[("DATE", -1)])

    # Get the latest Ethernet state from the latest document
    latest_state = latest_document["MESSAGE"] if latest_document else None

    # Delete all previous Ethernet state documents, except the latest one if there is only one document
    if latest_state:
        count = collection.count_documents({"MESSAGE": latest_state})
        if count > 1:
            collection.delete_many({"MESSAGE": latest_state, "DATE": {"$lt": latest_document["DATE"]}})

    # Wait 5 seconds before polling again
    time.sleep(5)"""
# Initialize the previous latest document ID
previous_latest_id = None
if "alarm_summary" not in db.list_collection_names():
    db.create_collection("alarm_summary")
    print("db is created")
alarm_summary_collection = db["alarm_summary"]
while True:
    # Get the latest Ethernet state document in the collection
    latest_document = collection.find_one({"MESSAGE": re.compile("Port [A-Za-z0-9]+ oper state set from (up to down|down to up)"), "DATE": {"$exists": True}}, sort=[("DATE", -1)])

    # Get the latest document ID
    #latest_id = latest_document["_id"] 
    if latest_document:
        # Get the latest document ID
        latest_id = latest_document["_id"]
        
    else:
        # No matching document found
        latest_id = None
    # Compare with the previous latest document ID
    if latest_id != previous_latest_id:
        # Document ID has changed, perform necessary actions
        if previous_latest_id is not None:
            # Perform actions for document change
            #print("Document ID has not changesd changed.")
            log_message = latest_document["MESSAGE"]
            # Check if the log message matches the desired condition
            ethernet_match_for_down = re.search(r"Port ([A-Za-z0-9]+) oper state set from up to down", log_message)
            ethernet_match_for_up = re.search(r"Port ([A-Za-z0-9]+) oper state set from down to up", log_message)

            #if "Port Ethernet48 oper state set from up to down" in log_message:
            if ethernet_match_for_down:
                # Extract the necessary data from row 2 (modify as per your data structure)
                """    time_value = "10.0.3PM"
                node_value = "192.168.1.1"
                severity_value = "Medium"
                alarm_type_value = "Link Down"
                description_value = "Ethernet1 down"
                # Insert a new row in the alarm_summary table
                insert_alarm_summary(node_value, severity_value, alarm_type_value, description_value)"""
                ethernet_name_down = ethernet_match_for_down.group(1)
                Time = datetime.now().strftime("%I:%M %p")
                node = latest_document["SOURCEIP"]
                severity = "Medium"
                alarm_type = "Link Down"
                #description = "Ethernet1 down"
                description = f"{ethernet_name_down} down" 

                # Create a new document in the "alarm_summary" table
                #alarm_summary_collection = db["alarm_summary"]
                new_alarm_document = {
                       "Time": Time,
                       "Node": node,
                       "Severity": severity,
                       "Alarm-Type": alarm_type,
                       "Description": description
                }
                alarm_summary_collection.insert_one(new_alarm_document)
                print("db is populated")
            if ethernet_match_for_up:
                ethernet_name_up =ethernet_match_for_up.group(1)
                alarm_summary_collection.delete_one({"Description": f"{ethernet_name_up} down"})
                print("this entry deleted")
        # Update the previous latest document ID
        previous_latest_id = latest_id
  
    #print(latest_id)
    # Wait 5 seconds before polling again
    time.sleep(5)

