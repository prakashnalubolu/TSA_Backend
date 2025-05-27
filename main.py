from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    # OpenRouter API configuration
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://brutalist-checkpoint-guide.lovable.app/",  # Your site URL
        "X-Title": "TSA Item Checker",  # Your app name
        "Content-Type": "application/json"
    }

    # Prepare the message for the LLM
    prompt = f"Item: {item.name}\n"
    if item.description:
        prompt += f"Description: {item.description}\n"
    prompt += "\nPlease analyze this item for air travel safety and restrictions."

    # Make API call to OpenRouter
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "openai/gpt-3.5-turbo",  # Using OpenRouter's format for OpenAI model
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 150  # Reasonable limit for our response
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract the response content
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
            
            return ItemResponse(
                item_name=item.name,
                carry_on=carry_on,
                check_in=check_in,
                explanation=explanation
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calling LLM API: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to TSA Item Checker API"} 