import httpx
import asyncio

async def test_api():
    # Test item
    test_item = {
        "name": "almonds",
        "description": "raw almonds in sealed package"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/check-item",
                json=test_item
            )
            
            print("\nRequest sent with status code:", response.status_code)
            if response.status_code == 200:
                print("\nSuccessfully added item!")
                print("Response:", response.json())
            else:
                print("\nError:", response.status_code)
                print("Response:", response.text)
    except Exception as e:
        print(f"\nError: {str(e)}")

# Run the test
asyncio.run(test_api()) 