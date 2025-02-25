import http.client
import ssl
import json
import pandas as pd
import os

from shapely.geometry import shape, MultiPolygon, Polygon
from pyproj import Transformer


def fetch_coordinates(query):
    conn = http.client.HTTPSConnection('nspd.gov.ru', context=ssl._create_unverified_context())
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=1, i',
        'referer': 'https://nspd.gov.ru/map?thematic=PKK&zoom=18.995658374628206&coordinate_x=4189211.38550531&coordinate_y=7511046.631810119&theme_id=1&is_copy_url=true',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    # Update the query parameter
    endpoint = f'/api/geoportal/v2/search/geoportal?query={query}&thematicSearchId=1'
    conn.request('GET', endpoint, headers=headers)

    response = conn.getresponse()
    data = response.read()

    try:
        # Parse the response as JSON
        json_data = json.loads(data)
        
        # Assuming the response contains a list of coordinates in a key like 'results'
        results = json_data.get('data', [])
        
        # Convert to a DataFrame
        #df = pd.DataFrame(results)

        # Display the DataFrame
        df = results['features'][0]
        return df

        # Optionally, save the DataFrame to a CSV file
        #df.to_csv('coordinates_table.csv', index=False)
    
    except json.JSONDecodeError:
        print("Failed to parse the response as JSON.")
        print(data)


def calculate_centroid_and_coords(geometry):
    """
    Calculate the centroid and transformed coordinates of the given geometry.

    Parameters:
        geometry (dict): The geometry data.

    Returns:
        pd.DataFrame: A DataFrame containing the centroid and transformed coordinates.
    """
    try:
        # Convert geometry to Shapely object
        shapely_geometry = shape(geometry)

        # Check if the geometry is a MultiPolygon or Polygon
        if isinstance(shapely_geometry, MultiPolygon):
            polygons = shapely_geometry.geoms
        elif isinstance(shapely_geometry, Polygon):
            polygons = [shapely_geometry]
        else:
            raise ValueError("Unsupported geometry type")

        # Transform coordinates
        transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
        transformed_polygons = []

        for polygon in polygons:
            transformed_polygon = []
            # Iterate through the exterior coordinates of the polygon
            for x, y in polygon.exterior.coords:
                lon, lat = transformer.transform(x, y)
                transformed_polygon.append((lon, lat))
            transformed_polygons.append(transformed_polygon)

        # Create Shapely Polygon or MultiPolygon
        if len(transformed_polygons) == 1:
            polygon = Polygon(transformed_polygons[0])
        else:
            polygon = MultiPolygon([Polygon(coords) for coords in transformed_polygons])

        # Validate and fix invalid geometries
        if not polygon.is_valid:
            polygon = polygon.buffer(0)  # Attempt to fix invalid geometry

        if not polygon.is_valid:
            raise ValueError("Invalid geometry after fix attempt")

        # Calculate the centroid
        if not polygon.is_empty:
            centroid = polygon.centroid
            if centroid.is_empty or not centroid.is_valid:
                return pd.DataFrame(columns=["latitude", "longitude", "coordinates"])

            # Create DataFrame
            data = {
                "latitude": [centroid.y],
                "longitude": [centroid.x],
                "coordinates": [transformed_polygons]
            }
            df = pd.DataFrame(data)
            return df
        else:
            return pd.DataFrame(columns=["latitude", "longitude", "coordinates"])

    except Exception as e:
        print(f"Error processing geometry: {e}")
        return pd.DataFrame(columns=["latitude", "longitude", "coordinates"])


def convert_to_dataframe(data):
    """
    Convert the provided nested data into a pandas DataFrame.

    Parameters:
        data (dict): The nested dictionary containing property information.

    Returns:
        pd.DataFrame: A DataFrame containing extracted property details.
    """
    # Extract relevant fields from the data
    options = data.get('options', {})
    system_info = data.get('systemInfo', {})

    # Define the fields to extract
    property_details = {
        "cad_num": options.get("cad_num"),
        "readable_address": options.get("readable_address"),
        "build_record_type_value": options.get("build_record_type_value"),
        "year_built": options.get("year_built"),
        "floors": options.get("floors"),
        "underground_floors": options.get("underground_floors"),
        "build_record_area": options.get("build_record_area"),
        "purpose": options.get("purpose"),
        "materials": options.get("materials"),
        "cost_value": options.get("cost_value"),
        "cost_index": options.get("cost_index"),
        "cost_determination_date": options.get("cost_determination_date"),
        "cultural_heritage_val": options.get("cultural_heritage_val"),
        "status": options.get("status"),
        "updated": system_info.get("updated"),
    }

    # Convert to DataFrame
    df = pd.DataFrame([property_details])
    return df 

def process_cadastre_numbers(cadastre_numbers, output_file="final_results-coords.csv"):
    """
    Processes a CSV file of cadastral numbers, fetches related data,
    and saves intermediate and final results to a CSV file.

    Args:
        file_path (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file (default: "final_results.csv").
    """
    # Read the CSV file
    #data = pd.read_csv(file_path, low_memory= False )
    #cadastre_numbers = data["cadastreNumber"]
    

    results = []

    # Create or clear the output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    for i, user_query in enumerate(cadastre_numbers, start=1):
        try:
            print(f"Processing {i}/{len(cadastre_numbers)}: {user_query}")
            df = fetch_coordinates(user_query)
            if df is None:
                continue

            props = df["properties"]
            geometry = df["geometry"]

            # Calculate centroid and coordinates
            centroid_result = calculate_centroid_and_coords(geometry)
            centroid_result =  pd.DataFrame(centroid_result)

            # Convert properties to DataFrame
            props_df = convert_to_dataframe(props)
            props_df =  pd.DataFrame(props_df)

            # Merge the two DataFrames
            merged_df = pd.concat([props_df, centroid_result], axis=1)
            results.append(merged_df)

            # Save intermediate results every 100 records
            if i % 100 == 0:
                print(f"Saving intermediate results at record {i}...")
                intermediate_df = pd.concat(results, ignore_index=True)
                intermediate_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
                results = []  # Clear results to free up memory

        except Exception as e:
            print(f"Error processing {user_query}: {e}")
            continue

    # Save any remaining results
    if results:
        print("Saving final results...")
        final_df = pd.concat(results, ignore_index=True)
        final_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

    print(f"Processing complete. Results saved to {output_file}.")