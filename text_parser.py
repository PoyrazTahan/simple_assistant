import re
import json

# Define all available actions - LLM decides which are most relevant
AVAILABLE_ACTIONS = [
    "quit_smoking", "mammography", "pap_smear", "take_vitamins", "regular_checkup",
    "drink_water", "movement_break", "mindfulness_break", "screen_curfew", 
    "journaling", "sugar_free_day", "get_sunlight", "weight_tracking", "healthy_eating"
]

def parse_language_tags(message):
    """Parse language tags and concatenate both languages for display"""
    # Check if message contains language tags
    english_pattern = r'<english>(.*?)</english>'
    turkish_pattern = r'<turkish>(.*?)</turkish>'
    
    english_match = re.search(english_pattern, message, re.DOTALL)
    turkish_match = re.search(turkish_pattern, message, re.DOTALL)
    
    if english_match and turkish_match:
        # Language mode: concatenate both languages with flag emojis
        english_text = english_match.group(1).strip()
        turkish_text = turkish_match.group(1).strip()
        return f"🇺🇸 {english_text}\n🇹🇷 {turkish_text}"
    elif english_match:
        # Only English tags found
        return f"🇺🇸 {english_match.group(1).strip()}"
    else:
        # Default mode: return message as-is (should be English)
        return message
    
    # TODO: For later reference - we're passing concatenated string to UI
    # Could separate into structured data for more advanced UI formatting
    
def parse_response(llm_response):
    """Parse LLM response into user message and system commands"""
    # Split response into user message and system message
    if "<system_message>" in llm_response:
        parts = llm_response.split("<system_message>")
        user_message = parts[0].strip()
        system_part = parts[1].replace("</system_message>", "").strip()
    else:
        user_message = llm_response.strip()
        system_part = ""
    
    # Parse language tags and get the appropriate message
    final_user_message = parse_language_tags(user_message)
    
    # Parse system commands
    system_commands = parse_system_commands(system_part)
    
    return {
        "user_message": final_user_message,
        "system_commands": system_commands,
        "raw_system": system_part
    }

def parse_system_commands(system_text):
    """Extract update, <asking> commands, and recommendations from system text"""
    commands = {
        "updates": [],
        "asking": None,
        "recommendations": []
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
    
    # Find next question: <asking>field</asking>
    asking_pattern = r'<asking>([^<]+)</asking>'
    asking_match = re.search(asking_pattern, system_text)
    
    if asking_match:
        commands["asking"] = asking_match.group(1).strip()
    
    # Find recommendations: <action>action_name</action>
    action_pattern = r'<action>([^<]+)</action>'
    action_matches = re.findall(action_pattern, system_text)
    
    for action in action_matches:
        action_name = action.strip()
        # Validate action against available actions
        validated_action = validate_any_action(action_name)
        if validated_action:
            commands["recommendations"].append(validated_action)
    
    return commands

def validate_any_action(action):
    """Validate action against available actions list (case-insensitive)"""
    action_lower = action.lower()
    
    # Check exact matches
    for available_action in AVAILABLE_ACTIONS:
        if action_lower == available_action.lower():
            return available_action  # Return the official action name
    
    # Check partial matches
    for available_action in AVAILABLE_ACTIONS:
        if action_lower in available_action.lower() or available_action.lower() in action_lower:
            print(f"[DEBUG] - Action '{action}' matched to '{available_action}'")
            return available_action
    
    print(f"[DEBUG] - Invalid action '{action}', skipping")
    return None

