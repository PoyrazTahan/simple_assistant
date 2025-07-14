import json
from data_manager import DataManager

class StageManager:
    """Manages conversation stages and transitions"""
    
    def __init__(self, debug_mode=False):
        self.data_manager = DataManager()
        self.debug_mode = debug_mode
        self.current_stage = "GREETING"
        self.conversation_turn = 0
        self.recommendations_generated = False
        
        
    def get_current_stage(self):
        """Get the current conversation stage"""
        return self.current_stage
        
    def get_current_stage_context(self):
        """Get stage-specific context for prompt building"""
        if self.current_stage == "GREETING":
            return self._get_greeting_context()
        elif self.current_stage == "QUESTIONNAIRE":
            return self._get_questionnaire_context()
        elif self.current_stage == "RECOMMENDATIONS":
            return self._get_recommendations_context()
        else:
            raise ValueError(f"Unknown stage: {self.current_stage}")
    
    def _load_profile_data(self):
        """Load profile data from profile.json"""
        try:
            with open("data/profile.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"name": None, "user_type": "new"}
    
    def _get_greeting_context(self):
        """Load greeting context - single prompt handles both new and returning users"""
        with open("prompts/greeting_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _get_questionnaire_context(self):
        """Load questionnaire context"""
        with open("prompts/questionnaire_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def _get_recommendations_context(self):
        """Load recommendations context"""
        with open("prompts/recommendation_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def update_stage(self, response):
        """Update stage based on response and data status"""
        self.conversation_turn += 1
        
        if self.debug_mode:
            print(f"[DEBUG] - Stage update: Turn {self.conversation_turn}, Current stage: {self.current_stage}")
        
        # Stage transition logic
        if self.current_stage == "GREETING":
            # After greeting, always move to questionnaire
            self.current_stage = "QUESTIONNAIRE"
            if self.debug_mode:
                print(f"[DEBUG] - Stage transition: GREETING -> QUESTIONNAIRE")
                
        elif self.current_stage == "QUESTIONNAIRE":
            # Check if all fields are complete
            data = self.data_manager.load_data()
            missing_fields = [key for key, value in data.items() if value is None]
            
            if len(missing_fields) == 0:
                self.current_stage = "RECOMMENDATIONS"
                if self.debug_mode:
                    print(f"[DEBUG] - Stage transition: QUESTIONNAIRE -> RECOMMENDATIONS (all fields complete)")
            else:
                if self.debug_mode:
                    print(f"[DEBUG] - Staying in QUESTIONNAIRE stage, missing fields: {missing_fields}")
                    
        elif self.current_stage == "RECOMMENDATIONS":
            # Mark recommendations as generated
            self.recommendations_generated = True
            if self.debug_mode:
                print(f"[DEBUG] - Recommendations generated")
    
    def needs_user_input(self):
        """Determine if current stage requires user input"""
        if self.current_stage == "GREETING":
            # After greeting, need user response
            return self.conversation_turn > 0
        elif self.current_stage == "QUESTIONNAIRE":
            # Always need user input for questionnaire
            return True
        elif self.current_stage == "RECOMMENDATIONS":
            # No user input needed for recommendations
            return False
        else:
            return True
    
    def is_complete(self):
        """Check if conversation is complete"""
        # Conversation is complete only after recommendations have actually been generated
        return self.current_stage == "RECOMMENDATIONS" and self.recommendations_generated
    
    def get_profile_and_data_context(self):
        """Get combined profile and data context for prompt building"""
        profile = self._load_profile_data()
        data_status = self.data_manager.get_data_status()
        
        context_parts = []
        
        # Add profile information
        if profile.get("name"):
            context_parts.append(f"USER PROFILE:\nName: {profile['name']}")
            context_parts.append(f"User Type: {profile['user_type']}")
        
        # Add data status
        context_parts.append(f"CURRENT DATA STATUS:\n{data_status}")
        
        return "\n\n".join(context_parts)