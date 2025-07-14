import re
import json

class TextParser:
    """Simple text parser for extracting user messages and system commands"""
    
    def __init__(self):
        pass
    
    def parse_response(self, llm_response):
        """Parse LLM response into user message and system commands"""
        # Split response into user message and system message
        if "<system_message>" in llm_response:
            parts = llm_response.split("<system_message>")
            user_message = parts[0].strip()
            system_part = parts[1].replace("</system_message>", "").strip()
        else:
            user_message = llm_response.strip()
            system_part = ""
        
        # Parse system commands
        system_commands = self._parse_system_commands(system_part)
        
        return {
            "user_message": user_message,
            "system_commands": system_commands,
            "raw_system": system_part
        }
    
    def _parse_system_commands(self, system_text):
        """Extract update and next_question commands from system text"""
        commands = {
            "updates": [],
            "next_question": None
        }
        
        if not system_text:
            return commands
        
        # Find update commands: <update>"field":"value"</update>
        update_pattern = r'<update>"([^"]+)":"([^"]+)"</update>'
        update_matches = re.findall(update_pattern, system_text)
        
        for field, value in update_matches:
            commands["updates"].append({
                "field": field,
                "value": value
            })
        
        # Find next question: <next_question>field</next_question>
        next_question_pattern = r'<next_question>([^<]+)</next_question>'
        next_question_match = re.search(next_question_pattern, system_text)
        
        if next_question_match:
            commands["next_question"] = next_question_match.group(1).strip()
        
        return commands