import os
from openai import OpenAI
from dotenv import load_dotenv
from data_manager import DataManager

# Load environment variables
load_dotenv()

class SimpleAgent:
    """Simple agent for basic LLM conversation with data tracking"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = self._load_prompt()
        self.data_manager = DataManager()
        self.conversation_history = []
        
        # Future function calling setup (commented for now)
        # self.function_choice_behavior = "auto"  # might be useful later
    
    def _load_prompt(self):
        """Load system prompt from file"""
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _format_conversation_history(self):
        """Format conversation history for prompt"""
        if not self.conversation_history:
            return "No previous conversation."
        
        lines = []
        for entry in self.conversation_history:
            lines.append(f"{entry['role'].capitalize()}: {entry['message']}")
        
        return "\n".join(lines)
    
    def _build_full_prompt(self, user_input):
        """Build full prompt with conversation history and data status"""
        conversation_history = self._format_conversation_history()
        data_status = self.data_manager.get_data_status()
        
        full_prompt = f"""{self.system_prompt}

CONVERSATION HISTORY:
{conversation_history}

CURRENT DATA STATUS:
{data_status}

User: {user_input}
Assistant: """
        
        return full_prompt
    
    def get_response(self, user_input):
        """Get response from OpenAI with conversation history and data status"""
        try:
            # Build full prompt with context
            full_prompt = self._build_full_prompt(user_input)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            assistant_response = response.choices[0].message.content
            
            # Store in conversation history
            self.conversation_history.append({"role": "user", "message": user_input})
            self.conversation_history.append({"role": "assistant", "message": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            return f"Error: {str(e)}"