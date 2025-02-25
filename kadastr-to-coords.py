from utils.coords import fetch_coordinates, calculate_centroid_and_coords, convert_to_dataframe, process_cadastre_numbers
import pandas as pd


# Take user input for the query (кадастровый номер)
#user_query = input("Enter the query (e.g., 77:01:0001037:2722): ")
user_query = "77:01:0001031:1014"

#user_query =  "77:01:0001026:1059"
user_query = "77:01:0001028:1039"

user_query = "77:01:0001026:2584"
df = fetch_coordinates(user_query)

#df = df["features"][0]

props = df["properties"]
geometry = df["geometry"]

# 
centroid_result = calculate_centroid_and_coords(geometry)
centroid_result =  pd.DataFrame(centroid_result)
print(centroid_result)

props = convert_to_dataframe(props)
props =  pd.DataFrame(props)
# Merge the two DataFrames
merged_df = pd.concat([props, centroid_result], axis=1)

# Read the CSV file
file_path = "../data_input/moscow-houses-extra.csv"
data = pd.read_csv(file_path, low_memory=False)

# Extract the "cadastreNumber" column
cadastreNumbers = data["cadastreNumber"]
print(cadastreNumbers)

file_path  = '../data_input/moscow-kadastr/final_results-coords-1.csv'
data2 = pd.read_csv(file_path, low_memory=False)
cadastreNumbers = data2[data2["latitude"].isna()]["cad_num"]

file_path  = '../data_input/moscow-kadastr/final_results-coords-2.csv'
data2 = pd.read_csv(file_path, low_memory=False)
cadastreNumbers = data2[data2["latitude"].isna()]["cad_num"]
cadastreNumbers


process_cadastre_numbers(cadastre_numbers = cadastreNumbers, output_file="final_results-coords.csv")
