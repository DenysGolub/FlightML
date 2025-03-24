



import json
# Data to be written
dictionary =  {
    'database': "experiments_ml",
    'user': 'postgres',
    'host': 'localhost',
    'port': 5432
}
 
# Serializing json
json_object = json.dumps(dictionary, indent=4)
 
# Writing to sample.json
with open("conn_string.json", "w") as outfile:
    outfile.write(json_object)