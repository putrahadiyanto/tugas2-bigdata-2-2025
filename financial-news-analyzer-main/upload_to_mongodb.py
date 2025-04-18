import json
import ssl
from pymongo import MongoClient
from pathlib import Path

# Constants for MongoDB connection
MONGO_CONNECTION_STRING = "your-connection-string-here"  # Replace with your MongoDB connection string
DATABASE_NAME = "idx_financial_news"
COLLECTION_NAME = "iqplus_processed"

def load_analysis_data(file_path):
    """Load analysis data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('results', [])
    except Exception as e:
        print(f"Error loading analysis data: {e}")
        return []

def connect_to_mongodb(connection_string):
    """Connect to MongoDB Atlas using the connection string"""
    try:
        # Connect with more permissive TLS/SSL settings
        client = MongoClient(
            connection_string,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000
        )
        
        # Test connection by listing database names
        client.list_database_names()
        print("Successfully connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {e}")
        return None

def upload_to_mongodb(client, database_name, collection_name, data):
    """Upload data to MongoDB Atlas"""
    if not client:
        return False
    
    try:
        # Get database and collection
        db = client[database_name]
        collection = db[collection_name]
        
        # Count entries for reporting
        valid_entries = 0
        invalid_entries = 0
        duplicates = 0
        
        # Process each entry
        for entry in data:
            # Check if all required fields are present
            required_fields = ["headline", "sentiment", "confidence", "tickers", "reasoning", "summary"]
            if all(field in entry for field in required_fields):
                try:
                    # Create a unique filter using headline and timestamp if available, or just headline
                    filter_criteria = {"headline": entry["headline"]}
                    if "timestamp" in entry:
                        filter_criteria["timestamp"] = entry["timestamp"]
                    
                    # Check if document already exists
                    existing_doc = collection.find_one(filter_criteria)
                    if existing_doc:
                        # Document exists, log it
                        doc_id = existing_doc.get("_id", "unknown")
                        print(f"Document already exists: ID={doc_id}, Headline=\"{entry['headline'][:50]}...\"")
                        
                        # Update the existing document
                        result = collection.update_one(
                            filter_criteria,
                            {"$set": entry}
                        )
                        duplicates += 1
                    else:
                        # Document doesn't exist, insert it
                        result = collection.insert_one(entry)
                        print(f"New document inserted: ID={result.inserted_id}, Headline=\"{entry['headline'][:50]}...\"")
                        valid_entries += 1
                except Exception as insert_error:
                    print(f"Error processing document: {insert_error}")
                    print(f"Problematic document headline: \"{entry.get('headline', 'No headline')[:50]}...\"")
                    invalid_entries += 1
            else:
                # Log missing fields
                missing = [field for field in required_fields if field not in entry]
                print(f"Skipping entry with missing fields: {missing}")
                print(f"Entry: \"{entry.get('headline', 'No headline')[:50]}...\"")
                invalid_entries += 1
        
        # Generate summary report
        print("\nUPLOAD SUMMARY:")
        print(f"✅ New entries inserted: {valid_entries}")
        print(f"🔄 Existing entries updated: {duplicates}")
        print(f"❌ Invalid entries skipped: {invalid_entries}")
        print(f"📊 Total processed: {valid_entries + duplicates + invalid_entries}")
        return True
    except Exception as e:
        print(f"Error uploading data to MongoDB: {e}")
        return False

def main():
    # Path to analysis data
    base_dir = Path(__file__).parent
    analysis_file = base_dir / "output" / "analysis.json"
    
    # Load data
    print(f"Loading analysis data from {analysis_file}...")
    data = load_analysis_data(analysis_file)
    print(f"Loaded {len(data)} analysis entries")
    
    # Connect to MongoDB
    client = connect_to_mongodb(MONGO_CONNECTION_STRING)
    if not client:
        print("Failed to connect to MongoDB. Exiting.")
        return
    
    # Upload data
    print(f"Uploading data to MongoDB Atlas ({DATABASE_NAME}.{COLLECTION_NAME})...")
    success = upload_to_mongodb(client, DATABASE_NAME, COLLECTION_NAME, data)
    if success:
        print("Data upload completed successfully")
    else:
        print("Data upload failed")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    main()
