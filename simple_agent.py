import os
import textwrap
import asyncio
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions.kernel_arguments import KernelArguments
from dotenv import load_dotenv
import text_parser

# Load environment variables
load_dotenv()

class SimpleAgent:
    """Simple agent for basic LLM conversation using Semantic Kernel"""
    
    def __init__(self, debug_mode=False, prompt_mode=False, language_mode=False, model="gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.language_prompt = self._load_language_prompt() if language_mode else ""
        self.conversation_history = []
        self.debug_mode = debug_mode
        self.prompt_mode = prompt_mode
        self.language_mode = language_mode
        
        # Initialize semantic kernel
        self.kernel = self._setup_kernel()
        self.execution_settings = self._setup_execution_settings()
        
        if self.debug_mode:
            print(f"[DEBUG] - Using Semantic Kernel with model: {self.model}")
    
    def _load_system_prompt(self):
        """Load system prompt from file"""
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _load_language_prompt(self):
        """Load language prompt instructions for dual language mode"""
        with open("prompts/language_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _setup_kernel(self):
        """Setup semantic kernel with OpenAI service"""
        kernel = sk.Kernel()
        
        # Add OpenAI chat completion service
        chat_service = OpenAIChatCompletion(
            ai_model_id=self.model,
            api_key=self.api_key,
            service_id="openai"
        )
        kernel.add_service(chat_service)
        
        return kernel
    
    def _setup_execution_settings(self):
        """Setup execution settings for semantic kernel"""
        return OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )
    
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

        {self.language_prompt if self.language_mode else ""}

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
        
        # Use semantic kernel with async-to-sync wrapper
        raw_response = self._ask_with_semantic_kernel(full_prompt)
        
        parsed = text_parser.parse_response(raw_response)
        
        # Store in conversation history
        self.conversation_history.append({"role": "user", "message": user_input})
        self.conversation_history.append({"role": "assistant", "message": parsed["user_message"]})
        
        return {
            "user_message": parsed["user_message"],
            "system_commands": parsed["system_commands"],
            "raw_response": raw_response
        }
    
    def _ask_with_semantic_kernel(self, prompt):
        """Use semantic kernel to get response (async wrapped in sync)"""
        async def _async_ask():
            # Create kernel arguments
            arguments = KernelArguments()
            
            # Invoke the kernel with the prompt directly
            result = await self.kernel.invoke_prompt(
                prompt=prompt,
                arguments=arguments
            )
            
            return str(result).strip()
        
        # Run async function synchronously
        return asyncio.run(_async_ask())