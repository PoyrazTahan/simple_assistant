import os
from openai import OpenAI
from dotenv import load_dotenv
from data_manager import DataManager
from text_parser import TextParser

# Load environment variables
load_dotenv()

class SimpleAgent:
    """Simple agent for basic LLM conversation with data tracking"""
    
    def __init__(self, debug_mode=False):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = self._load_prompt()
        self.data_manager = DataManager()
        self.text_parser = TextParser()
        self.conversation_history = []
        self.system_messages_history = []
        self.debug_mode = debug_mode
        
        # Auto-generate initial greeting (not stored in conversation history)
        self.initial_greeting = self._generate_initial_greeting()
        
        # Future function calling setup (commented for now)
        # self.function_choice_behavior = "auto"  # might be useful later
    
    def _load_prompt(self):
        """Load system prompt from file"""
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _load_greeting_prompt(self, user_type):
        """Load greeting prompt based on user type"""
        if user_type == "new":
            filename = "prompts/greeting_new_user.txt"
        else:
            filename = "prompts/greeting_returning_user.txt"
        
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _format_conversation_history(self):
        """Format conversation history for prompt"""
        if not self.conversation_history:
            return "The conversation hasn't started yet."
        
        lines = []
        for entry in self.conversation_history:
            lines.append(f"{entry['role'].capitalize()}: {entry['message']}")
        
        return "\n".join(lines)
    
    def _build_full_prompt(self, user_input):
        """Build full prompt with conversation history, data status, and stage context"""
        conversation_history = self._format_conversation_history()
        data_status = self.data_manager.get_data_status()
        stage_context = self._get_conversation_stage_context(user_input)
        
        full_prompt = f"""{self.system_prompt}

{stage_context}

CONVERSATION HISTORY:
{conversation_history}

CURRENT DATA STATUS:
{data_status}

User: {user_input}
Assistant: """
        
        return full_prompt
    
    def _generate_initial_greeting(self):
        """Generate initial greeting based on user type (not stored in conversation history)"""
        user_context = self.data_manager.get_user_type_and_greeting_context()
        greeting_instruction = self._load_greeting_prompt(user_context['user_type'])
        
        greeting_prompt = f"""{self.system_prompt}

CONVERSATION STAGE: Initial greeting for {user_context['user_type']} user

STAGE INSTRUCTIONS:
{greeting_instruction}

This is ONLY a greeting - DON'T ask any questions yet. Just welcome and introduce what we do.
CRITICAL: You MUST include <system_message></system_message> tags at the end, even if empty.

CONVERSATION HISTORY:
The conversation hasn't started yet.

User: 
Assistant: """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": greeting_prompt}
            ]
        )
        
        raw_response = response.choices[0].message.content
        parsed = self.text_parser.parse_response(raw_response)
        
        return {
            "user_message": parsed["user_message"],
            "system_commands": parsed["system_commands"],
            "command_results": []
        }
    
    def _get_conversation_stage_context(self, user_input=None, next_question=None):
        """Get additional context based on conversation stage"""
        user_context = self.data_manager.get_user_type_and_greeting_context()
        
        # DEBUG: Print stage detection info
        print(f"[DEBUG] - Stage detection:")
        print(f"  Missing fields: {user_context['missing_fields']}")
        print(f"  Missing count: {len(user_context['missing_fields'])}")
        print(f"  User input: '{user_input}'")
        print(f"  Next question: '{next_question}'")
        
        # Check if we should load recommendation prompt
        # Either: next_question is DONE/NONE with ≤1 missing fields OR all fields complete
        should_recommend = (
            (next_question in ["DONE", "NONE", None] and len(user_context['missing_fields']) <= 1) or
            len(user_context['missing_fields']) == 0 or
            (len(user_context['missing_fields']) == 1 and user_input and user_input.strip())
        )
        
        if should_recommend:
            print(f"[DEBUG] - Loading RECOMMENDATION PROMPT (completion triggered)")
            # Load recommendation prompt for completion stage
            with open("prompts/recommendation_prompt.txt", "r") as f:
                recommendation_prompt = f.read()
            return recommendation_prompt
        else:
            print(f"[DEBUG] - Loading DATA COLLECTION PROMPT")
            # Data collection stage
            return """CONVERSATION STAGE: Data collection in progress

STAGE INSTRUCTIONS:
Continue collecting missing health information. Ask one question at a time and acknowledge responses warmly."""
    
    
    def _execute_system_commands(self, system_commands):
        """Execute system commands and return results"""
        results = []
        
        # Process updates
        for update in system_commands["updates"]:
            field = update["field"]
            value = update["value"]
            result = self.data_manager.update_field(field, value)
            results.append(f"UPDATE: {result}")
        
        # Check if all fields are complete after updates
        user_context = self.data_manager.get_user_type_and_greeting_context()
        if len(user_context['missing_fields']) == 0:
            results.append("ALL_FIELDS_COMPLETE: Transitioning to completion stage")
            return results
        
        # Process next question only if fields are still missing
        if system_commands["next_question"]:
            results.append(f"NEXT_QUESTION: {system_commands['next_question']}")
        
        return results
    
    
    def get_initial_greeting(self):
        """Get the initial greeting generated during initialization"""
        return self.initial_greeting
    
    def ask(self, user_input):
        """Ask the agent with user input and get response"""
        full_prompt = self._build_full_prompt(user_input)
        
        # DEBUG: Print the full prompt being sent to the model
        print(f"[DEBUG] - Full prompt being sent to model:")
        print("=" * 50)
        # print(full_prompt)
        print("=" * 50)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        raw_response = response.choices[0].message.content
        parsed = self.text_parser.parse_response(raw_response)
        command_results = self._execute_system_commands(parsed["system_commands"])
        
        # Store in conversation history
        self.conversation_history.append({"role": "user", "message": user_input})
        self.conversation_history.append({"role": "assistant", "message": parsed["user_message"]})
        
        # Store system commands in separate history (only meaningful data)
        self.system_messages_history.append({
            "user_input": user_input,
            "system_commands": parsed["system_commands"],
            "command_results": command_results
        })
        
        return {
            "user_message": parsed["user_message"],
            "system_commands": parsed["system_commands"],
            "command_results": command_results
        }