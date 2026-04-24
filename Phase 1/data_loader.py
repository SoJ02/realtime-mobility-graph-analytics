import pyarrow.parquet as pq
import pandas as pd
from neo4j import GraphDatabase
import time

class DataLoader:
    def __init__(self, uri, user, password):
        """
        Connect to the Neo4j database and other init steps
        Args:
            uri (str): URI of the Neo4j database
            user (str): Username of the Neo4j database
            password (str): Password of the Neo4j database
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.driver.verify_connectivity()
        
    def close(self):
        """
        Close the connection to the Neo4j database
        """
        self.driver.close()
        
    # Define a function to create nodes and relationships in the graph
    def load_transform_file(self, file_path):
        """
        Load the parquet file and transform it into a csv file
        Then load the csv file into neo4j
        Args:
            file_path (str): Path to the parquet file to be loaded
        """
        # Read the parquet file
        trips = pq.read_table(file_path)
        trips = trips.to_pandas()
        
        # Some data cleaning and filtering
        trips = trips[['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'trip_distance', 'fare_amount']]
        
        # Filter out trips that are not in bronx
        bronx = [3, 18, 20, 31, 32, 46, 47, 51, 58, 59, 60, 69, 78, 81, 94, 119, 126, 136, 147, 159, 167, 168, 169, 174, 182, 183, 184, 185, 199, 200, 208, 212, 213, 220, 235, 240, 241, 242, 247, 248, 250, 254, 259]
        trips = trips[trips.iloc[:, 2].isin(bronx) & trips.iloc[:, 3].isin(bronx)]
        trips = trips[trips['trip_distance'] > 0.1]
        trips = trips[trips['fare_amount'] > 2.5]
        
        # Convert date-time columns to supported format
        trips['tpep_pickup_datetime'] = pd.to_datetime(trips['tpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
        trips['tpep_dropoff_datetime'] = pd.to_datetime(trips['tpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')
        
        # Convert to csv and store in the current directory
        save_loc = "/var/lib/neo4j/import/" + file_path.split(".")[0] + '.csv'
        trips.to_csv(save_loc, index=False)
        
        # Import data into Neo4j graph database
        # First, collect all unique location IDs
        all_locations = set()
        for pu_id in trips['PULocationID'].unique():
            all_locations.add(int(pu_id))
        for do_id in trips['DOLocationID'].unique():
            all_locations.add(int(do_id))
        
        # Create a constraint to ensure uniqueness
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT location_name_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE")
            except:
                # If the constraint already exists or can't be created, continue
                pass
        
        # Create all location nodes
        with self.driver.session() as session:
            for loc_id in all_locations:
                session.run(
                    "MERGE (l:Location {name: $location_id})",
                    location_id=loc_id
                )
        
        # Process trips in smaller chunks to avoid memory issues
        chunk_size = 500
        total_trips = len(trips)
        
        for start_idx in range(0, total_trips, chunk_size):
            end_idx = min(start_idx + chunk_size, total_trips)
            chunk = trips.iloc[start_idx:end_idx]
            
            with self.driver.session() as session:
                for _, row in chunk.iterrows():
                    # Create relationship between pickup and dropoff locations
                    session.run("""
                    MATCH (pickup:Location {name: $pickup_id})
                    MATCH (dropoff:Location {name: $dropoff_id})
                    CREATE (pickup)-[t:TRIP {
                        distance: $distance,
                        fare: $fare,
                        pickup_dt: datetime($pickup_dt),
                        dropoff_dt: datetime($dropoff_dt)
                    }]->(dropoff)
                    """,
                    pickup_id=int(row['PULocationID']),
                    dropoff_id=int(row['DOLocationID']),
                    distance=float(row['trip_distance']),
                    fare=float(row['fare_amount']),
                    pickup_dt=row['tpep_pickup_datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
                    dropoff_dt=row['tpep_dropoff_datetime'].strftime('%Y-%m-%dT%H:%M:%S'))

def main():
    total_attempts = 10
    attempt = 0
    # The database takes some time to starup!
    # Try to connect to the database 10 times
    while attempt < total_attempts:
        try:
            data_loader = DataLoader("neo4j://localhost:7687", "neo4j", "project1phase1")
            data_loader.load_transform_file("yellow_tripdata_2022-03.parquet")
            data_loader.close()
            attempt = total_attempts
        except Exception as e:
            print(f"(Attempt {attempt+1}/{total_attempts}) Error: ", e)
            attempt += 1
            time.sleep(10)

if __name__ == "__main__":
    main()