from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
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

app = FastAPI(title="TSA Item Checker API")

class Item(BaseModel):
    name: str
    description: str = ""

class ItemResponse(BaseModel):
    item_name: str
    carry_on: str  # "yes", "no", or "restrictions"
    check_in: str  # "yes", "no", or "restrictions"
    explanation: str

SYSTEM_PROMPT = """You are a TSA security expert. Analyze the given item and determine:
1. If it can be taken in carry-on luggage (yes/no/restrictions)
2. If it can be checked in luggage (yes/no/restrictions)
3. Provide a brief explanation for your decisions

Format your response exactly as follows:
Carry-on: [yes/no/restrictions]
Check-in: [yes/no/restrictions]
Explanation: [your explanation]"""

@app.post("/check-item", response_model=ItemResponse)
async def check_item(item: Item):
    try:
        # Check Supabase first
        result = supabase.table('tsa_items').select('*').eq('item_name', item.name).execute()
        
        if result.data and len(result.data) > 0:
            db_item = result.data[0]
            return ItemResponse(
                item_name=db_item['item_name'],
                carry_on=db_item['carry_on'],
                check_in=db_item['check_in'],
                explanation=db_item['explanation']
            )

        # If not found, call OpenRouter API
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://brutalist-checkpoint-guide.lovable.app",
            "X-Title": "TSA Item Checker",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Item: {item.name}\n" + (f"Description: {item.description}\n" if item.description else "") + "\nPlease analyze this item for air travel safety and restrictions."}
        ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": messages
                }
            )
            response.raise_for_status()
            result = response.json()
            
            llm_response = result["choices"][0]["message"]["content"]
            
            # Parse the response
            lines = llm_response.split("\n")
            carry_on = "unknown"
            check_in = "unknown"
            explanation = ""
            
            for line in lines:
                if line.startswith("Carry-on:"):
                    carry_on = line.split(":")[1].strip().lower()
                elif line.startswith("Check-in:"):
                    check_in = line.split(":")[1].strip().lower()
                elif line.startswith("Explanation:"):
                    explanation = line.split(":")[1].strip()

            # Store in Supabase
            new_item = {
                "item_name": item.name,
                "description": item.description,
                "carry_on": carry_on,
                "check_in": check_in,
                "explanation": explanation
            }
            supabase.table('tsa_items').insert(new_item).execute()
            
            return ItemResponse(
                item_name=item.name,
                carry_on=carry_on,
                check_in=check_in,
                explanation=explanation
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to TSA Item Checker API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 