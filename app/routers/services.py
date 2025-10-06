import json
from multiprocessing import AuthenticationError
from fastapi import APIRouter, HTTPException, Depends
# from fastapi import Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from openai import APIConnectionError, OpenAI, APIError, RateLimitError

import os
import re


from app import models, schema, oath2
from app.database import get_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(
        prefix="/api",
        tags=['AI Integration']
)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# @router.get("/")
# def link_home():
#     return {"Hello": "world"}


# Pydantic models
class MenuContent(BaseModel):
    code: str
    description: Dict[str, str]
    text: Dict[str, str]
    dataType: str = ""
    optionsLink: str = ""
    payload: str = ""
    input: str = ""
    required: bool = False
    updateLink: str = ""
    active: bool = True
    finalSuccessMessage: Dict[str, str] = {}
    finalFailedMessage: Dict[str, str] = {}
    content: List['MenuContent'] = []

MenuContent.update_forward_refs()

class BotConfiguration(BaseModel):
    menu_structure: List[MenuContent]
    languages: List[str]
    bot_type: Optional[str] = "custom"

class GenerateMenuRequest(BaseModel):
    description: str
    bot_type: str
    languages: List[str]

class SuggestTextRequest(BaseModel):
    menu_header: str
    payload: str
    language: str

class SuggestDescriptionRequest(BaseModel):
    menu_header: str
    button_text: str
    payload: str
    language: str

class SuggestPayloadRequest(BaseModel):
    button_text: str
    description: str

class TranslationItem(BaseModel):
    text: str
    description: str
    source_language: str
    target_language: str

class TranslateBatchRequest(BaseModel):
    translations: List[TranslationItem]

# Helper function to call OpenAI
def call_openai(prompt: str, max_tokens: int = 1000, temperature: float = 0.7,  model: str = "gpt-4-turbo-preview") -> str: # or ""gpt-4o-mini"" for faster/cheaper
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates WhatsApp bot configurations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded. Please try again later.")

    except APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    except APIConnectionError as e:
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"Auth failed: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# API Endpoints
@router.post("/ai/generate-menu")
async def generate_menu(request: GenerateMenuRequest): #, token: models.User = Depends(oath2.get_current_user)):
    """Generate complete menu structure based on description"""
    
    # Create language mapping
    # lang_map = "\n".join([f"Language {idx+1}: {lang}" for idx, lang in enumerate(request.languages)])
    # print(f"Token is : {token}")
    
    prompt = f"""You are a WhatsApp bot menu structure designer. Based on the following description, create a comprehensive bot menu structure.
You are an expert conversational system designer creating JSON-based WhatsApp chatbot menus.


## OBJECTIVE
Design a structured, stateful chatbot for WhatsApp that collects user inputs step-by-step, performs API actions, and provides feedback. 
Each menu and submenu should flow logically toward a goal.


## BOT INFORMATION
Description: {request.description}
Type: {request.bot_type}
Supported Languages: {', '.join(request.languages)}


## STRUCTURE
Generate a valid JSON array using this schema:
{{
  "code": "1",
  "nodeType": "menu" | "input" | "action",
  "text": {{"1": "English button text", "2": "Translated button text"}}, #this is the button text shown to users(e.g., "Main Menu", "Enter Amount")
  "description": {{"1": "English description", "2": "Translated description"}}, #this should be a brief description of the button's purpose
  "payload": "input_field_name (for input nodes only)",
  "dataType": "string|number|date|phone|choice|none",
  "required": true,
  "updateLink": "API endpoint for action nodes, may contain placeholders e.g. ?resource=fundraiser&title={{title}}", #(for action nodes only)
  "conditions": {{
    "field": "FIELD_NAME_TO_CHECK",
    "equals": "EXPECTED_VALUE",
    "next": "CODE_OF_NEXT_NODE"
  }}, #optional, for conditional routing based on previous inputs
  "optionsLink": "API endpoint to fetch dynamic options (for choice inputs only)",
  "active": true,
  "finalSuccessMessage": {{"1": "Success message", "2": "Language 2 success message"}},
  "finalFailedMessage": {{"1": "Failure message", "2": "Language 2 failure message"}},
  "content": []  // nested submenus or next nodes
}}


## RULES
- Always start with a main menu node at the top level. Add one “main menu” and submenus for specific flows.
- Use nested "content" arrays for submenus or next conversation states.
- Use `"nodeType": "input"` for user data collection (e.g., name, amount, phone). Every “input” node collects a single user value using `payload`.
- Use UPPER_SNAKE_CASE for payloads and API actions (e.g., CREATE_FUNDRAISER, UPDATE_PAYMENT).
- Use `"nodeType": "action"` for API trigger nodes (where `updateLink` is used). Every “action” node should have an `updateLink` where the collected data is submitted.
- Use `"nodeType": "menu"` for menu options that lead to further choices or inputs.
- Always include “99: Back” in menu descriptions to support navigation. Include "99: Back" option inside each menu description where applicable.
- Ensure every menu and input has descriptive text in all listed languages.
- Use descriptive but concise text for button labels and descriptions.
- When conditions exist, define how to route users dynamically.
- Always include translations for all provided languages.
- For {request.bot_type} bots, add realistic domain-relevant options.
- Make sure every node has a unique "code" (use nested numbering like "1.1", "1.2", etc.).
- Maintain logical progression of flow: menu → input(s) → action → success/failure.
- Ensure JSON is strictly valid — no markdown, code fences, or comments.


## EXAMPLE
Here's an example flow for a fundraiser bot with 2 languages (English, Swahili):

  {{
    "code": "1",
    "nodeType": "menu",
    "description": {{
      "1": "Changalink Main Menu:\n1. Start Fundraiser\n2. Donate to Fundraiser\n\n99: Back",
      "2": "Menyu Kuu ya Changalink:\n1. Anza Mchango\n2. Changia Mchango\n\n99: Rudi Nyuma"
    }},
    "text": {{
      "1": "Main Menu",
      "2": "Menyu Kuu"
    }},
    "dataType": "",
    "optionsLink": "",
    "payload": "",
    "input": "",
    "required": false,
    "updateLink": "",
    "active": true,
    "finalSuccessMessage": {{
      "1": "",
      "2": ""
    }},
    "finalFailedMessage": {{
      "1": "",
      "2": "",
      "3": ""
    }},
    "content": [
      {{
        "code": "1",
        "nodeType": "action",
        "description": {{
          "1": "Start a new fundraiser.\nPlease provide your fundraiser title.",
          "2": "Anza mchango mpya.\nTafadhali toa kichwa cha mchango wako."
        }},
        "text": {{
          "1": "Start Fundraiser",
          "2": "Anza Mchango"
        }},
        "payload": "",
        "dataType": "",
        "required": true,
        "updateLink": "http://api.example.com/api/?resource=fundraiser&action=create&title={{title}}&target={{target_amount}}",
        "active": true,
        "finalSuccessMessage": {{
            "1": "Fundraiser creation SUCCESS\n\n99: Back to Main Menu",
            "2": "Mchango umeundwa kwa mafanikio!\n\n99: Rudi kwenye Menyu Kuu"
          }},
        "finalFailedMessage": {{
            "1": "Fundraiser creation FAILED\n",
            "2": "Kuunda mchango kumeshindikana.\n"
        }},

        "content": [
          {{
            "code": "1.1",
            "nodeType": "input",
            "description": {{
              "1": "Enter Fundraiser Title.",
              "2": "Weka jina la mchango."
            }},
            "text": {{
              "1": "Fundraiser Title",
              "2": "Jina la mchango"
            }},
            "payload": "fundraiser_title",
            "dataType": "string",
            "required": true,
            "updateLink": "",
            "conditions": {{
              "field": "target_amount",
              "equals": "<user_input>",
              "next": "1.2"
            }},
            "active": true,
            "finalSuccessMessage": {{
              "1": "",
              "2": ""
            }},
            "finalFailedMessage": {{
              "1": "",
              "2": ""
            }},
            "content": []
          }},
          {{
            "code": "1.2",
            "nodeType": "input",
            "description": {{
              "1": "Enter target amount (KES).",
              "2": "Weka kiasi cha lengo (KES)."
            }},
            "text": {{
              "1": "Target Amount",
              "2": "Kiasi cha Lengo"
            }},
            "payload": "target_amount",
            "dataType": "number",
            "required": true,
            "updateLink": "",
            "conditions": {{
              "field": "mode_of_disbursement",
              "equals": "Mpesa",
              "next": "1.3"
            }},
            "active": true,
            "finalSuccessMessage": {{
              "1": "",
              "2": ""
            }},
            "finalFailedMessage": {{
              "1": "",
              "2": ""
            }},
            "content": []
          }},
          {{
            "code": "1.3",
            "nodeType": "input",
            "description": {{
              "1": "Enter mode of disbursement (e.g., Mpesa, Bank Transfer).",
              "2": "Weka njia ya utoaji (mfano, Mpesa, Uhamisho wa Benki)."
            }},
            "text": {{
              "1": "Mode of Disbursement",
              "2": "Njia ya Utoaji"
            }},
            "payload": "mode_of_disbursement",
            "dataType": "choice",
            "required": true,
            "updateLink": "",
            "conditions": {{
              "field": "",
              "equals": "",
              "next": ""
            }},
            "active": true,
            "finalSuccessMessage": {{
              "1": "",
              "2": ""
            }},
            "finalFailedMessage": {{
              "1": "",
              "2": ""
            }},
            "content": []
          }}
        ]
      }},
      {{
        "code": "2",
        "nodeType": "menu",
        "description": {{
          "1": "Donate to an existing fundraiser.",
          "2": "Changia mchango uliopo."
        }},
        "text": {{
          "1": "Donate",
          "2": "Changia"
        }},
        "payload": "fundraiserId",
        "dataType": "number",
        "required": true,
        "updateLink": "http://localhost/api/?resource=payment&action=generate_link&fundraiserId={{fundraiserId}}&amount={{amount}}",
        "active": true,
        "finalSuccessMessage": {{
          "1": "Payment link generated successfully!",
          "2": "Kiungo cha malipo kimeundwa kwa mafanikio!"
        }},
        "finalFailedMessage": {{
          "1": "An error occurred while generating payment link.",
          "2": "Hitilafu imetokea wakati wa kuunda kiungo cha malipo."
        }},
        "content": [
          {{
            "code": "2.1",
            "nodeType": "input",
            "description": {{
              "1": "Enter the fundraiser No. you wish to donate to.",
              "2": "Weka ID ya mchango unaotaka kuchangia."
            }},
            "text": {{
              "1": "Enter fundraiser No.",
              "2": "Weka ID ya mchango"
            }},
            "payload": "fundraiserId",
            "dataType": "number",
            "required": true,
            "updateLink": "",
            "conditions": {{
              "field": "amount",
              "equals": "",
              "next": "2.2"
            }},
            "active": true,
            "finalSuccessMessage": {{
              "1": "",
              "2": ""
            }},
            "finalFailedMessage": {{
              "1": "",
              "2": ""
            }},
            "content": []
          }},
          {{
            "code": "2.2",
            "nodeType": "input",
            "description": {{
              "1": "Enter the amount you wish to donate.",
              "2": "Weka kiasi unachotaka kuchangia."
            }},
            "text": {{
              "1": "Enter Amount",
              "2": "Weka Kiasi"
            }},
            "payload": "amount",
            "dataType": "number",
            "required": true,
            "updateLink": "",
            "conditions": {{
              "field": "",
              "equals": "",
              "next": ""
            }},
            "active": true,
            "finalSuccessMessage": {{
              "1": "",
              "2": ""
            }},
            "finalFailedMessage": {{
              "1": "",
              "2": ""
            }},
            "content": []
          }}
        ]
      }}
    ]
  }}
]

Look at the example above for guidance, but create a new menu structure tailored to the provided description and bot type.
CRITICAL: Respond ONLY with a valid JSON array. NO markdown, NO code blocks, NO explanations. Just the JSON array."""

    response_text = call_openai(prompt, max_tokens=4000, temperature=0.8)
    
    # Clean up response
    response_text = response_text.strip()
    response_text = re.sub(r'^```json\s*', '', response_text)
    response_text = re.sub(r'```\s*$', '', response_text)
    
    try:
        menu_structure = json.loads(response_text)
        return {"menu_structure": menu_structure}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
        

@router.post("/ai/suggest-text")
async def suggest_text(request: SuggestTextRequest): #, token: models.User = Depends(oath2.get_current_user)):
    """Generate button text suggestion"""
    
    prompt = f"""Generate a concise button text in {request.language} for a WhatsApp bot menu option.

Menu: {request.menu_header}
Payload: {request.payload}
Language: {request.language}

Return ONLY the concise button text, no explanations, no quotes, no markdown, no code blocks."""
    
    response_text = call_openai(prompt, max_tokens=300, temperature=0.7)
    
    # Clean up response
    response_text = response_text.strip()
    response_text = re.sub(r'^```json\s*', '', response_text)
    response_text = re.sub(r'```\s*$', '', response_text)

    suggestion = call_openai(prompt, max_tokens=50, temperature=0.7)
    suggestion = suggestion.strip().strip('"').strip("'")
    
    return {"suggestion": suggestion}

@router.post("/ai/suggest-description")
async def suggest_description(request: SuggestDescriptionRequest): #, token: models.User = Depends(oath2.get_current_user)):
    """Generate description text suggestion"""
    
    prompt = f"""Generate a clear description in {request.language} for a WhatsApp bot menu option.

Menu: {request.menu_header}
Button Text: {request.button_text}
Payload: {request.payload}
Language: {request.language}

Return ONLY the description text (1-2 sentences), no explanations, no quotes."""

    suggestion = call_openai(prompt, max_tokens=150, temperature=0.7)
    suggestion = suggestion.strip().strip('"').strip("'")
    
    return {"suggestion": suggestion}

@router.post("/ai/suggest-payload")
async def suggest_payload(request: SuggestPayloadRequest): #, token: models.User = Depends(oath2.get_current_user)):
    """Generate payload name suggestion"""
    
    prompt = f"""Generate a technical payload name for a WhatsApp bot menu option.

Button Text: {request.button_text}
Description: {request.description}

Return ONLY the payload in UPPER_SNAKE_CASE format (e.g., CREATE_FUNDRAISER, MAKE_PAYMENT).
No explanations, no examples, just the payload name."""

    suggestion = call_openai(prompt, max_tokens=50, temperature=0.5)
    # Clean up and ensure uppercase snake case
    suggestion = suggestion.strip().strip('"').strip("'")
    suggestion = re.sub(r'[^A-Z_]', '', suggestion.upper())
    
    return {"suggestion": suggestion}

@router.post("/ai/translate-batch")
async def translate_batch(request: TranslateBatchRequest): #, token: models.User = Depends(oath2.get_current_user)):
    """Translate multiple menu items in batch"""
    
    translations = []
    
    for item in request.translations:
        prompt = f"""Translate the following WhatsApp bot menu text from {item.source_language} to {item.target_language}.

Button Text: {item.text}
Description: {item.description}

Return ONLY a JSON object with this exact format:
{{"text": "translated button text", "description": "translated description"}}

No markdown, no code blocks, just the JSON object."""

        response_text = call_openai(prompt, max_tokens=300, temperature=0.7)

        try:
            translation = json.loads(response_text)
            translations.append(translation)
        except json.JSONDecodeError:
            # If parsing fails, return original text
            translations.append({"text": item.text, "description": item.description})
    
    return {"translations": translations}