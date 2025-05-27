from dotenv import load_dotenv
import os
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise Exception("Missing Supabase credentials")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Fetch all items from the table
try:
    result = supabase.table('tsa_items').select('*').execute()
    
    if result.data:
        print("\nFound items in database:")
        print("-" * 50)
        for item in result.data:
            print(f"\nItem: {item['item_name']}")
            print(f"Description: {item.get('description', 'N/A')}")
            print(f"Carry-on: {item['carry_on']}")
            print(f"Check-in: {item['check_in']}")
            print(f"Explanation: {item['explanation']}")
            print("-" * 50)
        print(f"\nTotal items found: {len(result.data)}")
    else:
        print("\nNo items found in the database.")
except Exception as e:
    print(f"Error accessing database: {str(e)}") 