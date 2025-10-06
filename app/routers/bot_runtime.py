# app/routers/bot_runtime.py
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import requests
from typing import Dict, Any, Optional
import datetime
from app.database import get_db
from app import models

router = APIRouter(prefix="/bot-runtime", tags=['Bot Runtime'])

class BotEngine:
    def __init__(self, bot_config: Dict, session_data: Dict):
        self.config = bot_config
        self.session = session_data
        self.collected_data = json.loads(session_data.get('collected_data', '{}'))
        
    def find_menu_by_code(self, code: str, menus: list = None) -> Optional[Dict]:
        """Recursively find menu item by code"""
        if menus is None:
            menus = self.config
            
        for menu in menus:
            if menu['code'] == code:
                return menu
            if menu.get('content'):
                found = self.find_menu_by_code(code, menu['content'])
                if found:
                    return found
        return None
    
    def get_current_menu(self) -> Dict:
        """Get current menu based on session state"""
        if not self.session.get('current_menu_code'):
            # Return root menu
            return {'content': self.config}
        
        return self.find_menu_by_code(self.session['current_menu_code'])
    
    def format_menu_text(self, menu: Dict, lang_index: str = "1") -> str:
        """Format menu description with options"""
        current_menu = menu if 'content' in menu else {'content': self.config}
        
        text = ""
        if current_menu.get('description'):
            text = current_menu['description'].get(lang_index, '')
        
        # Add numbered options from content
        if current_menu.get('content'):
            options = []
            for item in current_menu['content']:
                if item.get('active', True):
                    button_text = item['text'].get(lang_index, '')
                    options.append(f"{item['code']}. {button_text}")
            
            if options:
                text += "\n\n" + "\n".join(options)
        
        return text
    
    def process_user_input(self, user_input: str, lang_index: str = "1") -> Dict[str, Any]:
        """Process user message and determine next state"""
        current_menu = self.get_current_menu()
        
        # Check if waiting for input data
        if self.session.get('awaiting_input'):
            field_name = self.session.get('awaiting_input_field')
            data_type = self.session.get('awaiting_input_type')
            
            # Validate input based on dataType
            if not self.validate_input(user_input, data_type):
                return {
                    'response': f"Invalid {data_type}. Please try again.",
                    'next_menu': None,
                    'action': None
                }
            
            # Store collected data
            self.collected_data[field_name] = user_input
            
            # Check if this was the last input before an action
            menu_item = self.find_menu_by_code(self.session['current_menu_code'])
            if menu_item and menu_item.get('updateLink'):
                # Execute action
                action_result = self.execute_action(menu_item)
                return action_result
            
            # Move to next menu in sequence
            return self.move_to_next_menu(menu_item)
        
        # Handle menu navigation
        if user_input == "99":
            # Go back
            return self.go_back()
        
        # Find selected option
        selected = None
        if 'content' in current_menu:
            for item in current_menu['content']:
                if item['code'] == user_input and item.get('active', True):
                    selected = item
                    break
        
        if not selected:
            return {
                'response': "Invalid option. Please select a valid number.",
                'next_menu': self.session.get('current_menu_code'),
                'action': None
            }
        
        # Check if this is an input node
        if selected.get('dataType') and selected.get('payload'):
            self.session['awaiting_input'] = True
            self.session['awaiting_input_field'] = selected['payload']
            self.session['awaiting_input_type'] = selected['dataType']
            
            return {
                'response': selected['description'].get(lang_index, ''),
                'next_menu': selected['code'],
                'action': 'awaiting_input'
            }
        
        # Navigate to submenu
        response_text = self.format_menu_text(selected, lang_index)
        
        return {
            'response': response_text,
            'next_menu': selected['code'],
            'action': None
        }
    
    def execute_action(self, menu_item: Dict) -> Dict[str, Any]:
        """Execute API call with collected data"""
        update_link = menu_item.get('updateLink', '')
        
        # Replace placeholders with collected data
        for key, value in self.collected_data.items():
            update_link = update_link.replace(f"{{{{{key}}}}}", str(value))
        
        try:
            response = requests.post(update_link, json=self.collected_data, timeout=10)
            
            if response.status_code == 200:
                message = menu_item.get('finalSuccessMessage', {}).get('1', 'Success!')
            else:
                message = menu_item.get('finalFailedMessage', {}).get('1', 'Failed!')
            
            # Reset session after action
            return {
                'response': message,
                'next_menu': None,  # Return to root
                'action': 'completed',
                'clear_data': True
            }
            
        except Exception as e:
            return {
                'response': menu_item.get('finalFailedMessage', {}).get('1', 'Error occurred'),
                'next_menu': self.session.get('current_menu_code'),
                'action': 'error'
            }
    
    def validate_input(self, value: str, data_type: str) -> bool:
        """Validate user input based on dataType"""
        if data_type == "number":
            try:
                float(value)
                return True
            except:
                return False
        elif data_type == "phone":
            return len(value) >= 10 and value.replace('+', '').isdigit()
        elif data_type == "email":
            return '@' in value and '.' in value
        
        return True  # string, date, etc.
    
    def move_to_next_menu(self, current_item: Dict) -> Dict[str, Any]:
        """Move to next menu after input collection"""
        if current_item.get('content'):
            next_item = current_item['content'][0]
            return self.process_user_input(next_item['code'], "1")
        
        return {
            'response': "Process completed!",
            'next_menu': None,
            'action': 'completed'
        }
    
    def go_back(self) -> Dict[str, Any]:
        """Navigate back in menu hierarchy"""
        # Implementation depends on how you track history
        return {
            'response': self.format_menu_text({'content': self.config}),
            'next_menu': None,
            'action': None
        }


@router.post("/webhook/{bot_id}")
async def handle_whatsapp_message(bot_id: int, request: Request, db: Session = Depends(get_db)):
    """Webhook endpoint for WhatsApp messages"""
    
    body = await request.json()
    
    # Extract message data (adjust based on your WhatsApp API structure)
    if "data" not in body:
        return {"status": "ignored"}
    
    data = body["data"]
    user_phone = data.get("from", "").replace("@c.us", "")
    message_text = data.get("body", "").strip()
    
    # Get bot configuration
    bot = db.query(models.Bot).filter(
        models.Bot.id == bot_id,
        models.Bot.is_active == True
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Get or create session
    session = db.query(models.BotSession).filter(
        models.BotSession.bot_id == bot_id,
        models.BotSession.user_phone == user_phone
    ).first()
    
    if not session:
        session = models.BotSession(
            bot_id=bot_id,
            user_phone=user_phone,
            current_menu_code=None,
            collected_data=json.dumps({})
        )
        db.add(session)
        db.commit()
    
    # Process message with bot engine
    bot_config = json.loads(bot.configuration)
    session_data = {
        'current_menu_code': session.current_menu_code,
        'collected_data': session.collected_data,
        'awaiting_input': getattr(session, 'awaiting_input', False)
    }
    
    engine = BotEngine(bot_config, session_data)
    result = engine.process_user_input(message_text)
    
    # Update session
    session.current_menu_code = result['next_menu']
    if result.get('clear_data'):
        session.collected_data = json.dumps({})
    else:
        session.collected_data = json.dumps(engine.collected_data)
    
    session.last_interaction = int(datetime.now().timestamp())
    db.commit()
    
    # Send response via WhatsApp API
    send_whatsapp_message(bot.phone_number, user_phone, result['response'])
    
    return {"status": "processed"}


def send_whatsapp_message(from_number: str, to_number: str, message: str):
    """Send message via WhatsApp API"""
    payload = {
        "args": {
            "to": f"{to_number}@c.us",
            "content": message
        }
    }
    
    try:
        requests.post("http://localhost:8085/sendText", json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")