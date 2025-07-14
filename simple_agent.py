import os
import textwrap
from openai import OpenAI
from dotenv import load_dotenv
import text_parser

# Load environment variables
load_dotenv()

class SimpleAgent:
    """Simple agent for basic LLM conversation - pure conversation handler"""
    
    def __init__(self, debug_mode=False, prompt_mode=False):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = self._load_system_prompt()
        self.conversation_history = []
        self.debug_mode = debug_mode
        self.prompt_mode = prompt_mode
    
    def _load_system_prompt(self):
        """Load system prompt from file"""
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _format_conversation_history(self):
        """Format conversation history for prompt"""
        if not self.conversation_history:
            return "The conversation hasn't started yet."
        
        lines = []
        for entry in self.conversation_history:
            lines.append(f"{entry['role'].capitalize()}: {entry['message']}")
        
        return "\n".join(lines)
    
    def _build_full_prompt(self, user_input, stage_context, profile_and_data_context):
        """Build full prompt with stage context, profile, and data"""
        conversation_history = self._format_conversation_history()
        
        full_prompt = textwrap.dedent(f"""
        {self.system_prompt}

        {stage_context}
        
        {profile_and_data_context}

        CONVERSATION HISTORY:
        {conversation_history}
        
        User: {user_input}
        Assistant: """).strip()
        
        # DEBUG: Print the full prompt being sent to the model
        if self.prompt_mode:
            print(f"[PROMPT] - Full prompt being sent to model:")
            print("=" * 50)
            print(full_prompt)
            print("=" * 50)
        
        return full_prompt
    
    def ask(self, user_input, stage_context, profile_and_data_context):
        """Ask the agent with user input and stage context"""
        full_prompt = self._build_full_prompt(user_input, stage_context, profile_and_data_context)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        raw_response = response.choices[0].message.content
        parsed = text_parser.parse_response(raw_response)
        
        # Store in conversation history
        self.conversation_history.append({"role": "user", "message": user_input})
        self.conversation_history.append({"role": "assistant", "message": parsed["user_message"]})
        
        return {
            "user_message": parsed["user_message"],
            "system_commands": parsed["system_commands"],
            "raw_response": raw_response
        }