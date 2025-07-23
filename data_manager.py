import json

class DataManager:
    """Simple data manager for basic JSON operations"""
    
    def __init__(self, data_file="data/data.json"):
        self.data_file = data_file
        self.session_initialized = False  # Track if this session has been initialized
    
    def load_data(self):
        """Load data from JSON file"""
        with open(self.data_file, 'r') as f:
            return json.load(f)
    
    def save_data(self, data):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_field(self, field, value):
        """Update a single field in data.json"""
        data = self.load_data()
        
        # Convert field to lowercase for matching
        field = field.lower()
        
        # Simple field validation
        if field not in data:
            return f"Error: Field '{field}' not found"
        
        # Type conversion for numeric fields - simple, no error handling
        if field == "age":
            data[field] = int(value)
        elif field == "weight":
            data[field] = float(value)
        elif field == "height":
            data[field] = float(value)
        else:
            # All other fields as strings
            data[field] = value
        
        self.save_data(data)
        return f"Updated {field} to {data[field]}"
    
    def get_data_status(self):
        """Get current data status formatted for LLM"""
        data = self.load_data()
        
        # Separate filled and missing data
        filled = {key: value for key, value in data.items() if value is not None}
        missing = [key for key, value in data.items() if value is None]
        
        # Build simple status
        status_lines = []
        status_lines.append("=== RECORDED USER DATA ===")
        
        if not filled:
            status_lines.append("• No data recorded yet")
        else:
            for field, value in filled.items():
                status_lines.append(f"• {field.capitalize()}: {value}")
        
        status_lines.append("\n=== MISSING FIELDS ===")
        if not missing:
            status_lines.append("• All fields complete!")
        else:
            for field in missing:
                status_lines.append(f"• {field.capitalize()}: null")
        
        # Add BMI section if weight and height are available
        bmi = self._calculate_bmi(data)
        if bmi:
            bmi_category = self._get_bmi_category(bmi)
            status_lines.append(f"\n=== HEALTH INSIGHTS ===")
            status_lines.append(f"• BMI: {bmi} ({bmi_category})")
        
        status_lines.append(f"\n=== GUIDANCE ===")
        if missing:
            if len(missing) == 1:
                status_lines.append(f"• FINAL QUESTION: Ask about {missing[0]} only - this will complete the assessment")
            else:
                status_lines.append(f"• Next: Ask about {missing[0]} or related field")
        else:
            status_lines.append("• We have all the information we need - DO NOT ASK ANY ADDITIONAL INFORMATION")
        
        return "\n".join(status_lines)
    
    def _calculate_bmi(self, data):
        """Calculate BMI if weight and height available - simple, no error handling"""
        weight = data.get("weight")
        height = data.get("height")
        
        if weight is None or height is None:
            return None
            
        # Direct validation - fail fast if invalid data
        if weight <= 0 or height <= 0:
            return None
            
        # Convert height to meters and calculate BMI
        height_m = height / 100
        return round(weight / (height_m * height_m), 1)
    
    def _get_bmi_category(self, bmi):
        """Get BMI category - simple conditions"""
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"
    
    
    def save_recommendations(self, actions_list, user_message):
        """Save simplified recommendations to JSON file with top 4 actions"""
        from datetime import datetime
        
        data = self.load_data()
        
        # Create simple recommendation record
        recommendation_record = {
            "timestamp": datetime.now().isoformat(),
            "user_data": data,
            "recommendation_message": user_message,
            "top_4_actions": actions_list
        }
        
        # Save to recommendations.json
        with open("data/recommendations.json", 'w') as f:
            json.dump(recommendation_record, f, indent=2)
        
        return recommendation_record
    
    def save_conversation_turn(self, user_input, assistant_response, system_commands, current_stage):
        """Save a conversation turn to conversation_history.json"""
        from datetime import datetime
        import os
        
        history_file = "data/conversation_history.json"
        
        # Check if this is the first turn of a new session
        if not self.session_initialized:
            # Start fresh conversation history for new session
            history = {
                "session_start": datetime.now().isoformat(),
                "turns": []
            }
            self.session_initialized = True
        else:
            # Load existing history from current session
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                # Fallback if file doesn't exist
                history = {
                    "session_start": datetime.now().isoformat(),
                    "turns": []
                }
        
        # Create new turn
        turn = {
            "turn_number": len(history["turns"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "assistant_response": assistant_response,
            "system_commands": system_commands,
            "stage": current_stage
        }
        
        # Add turn to history
        history["turns"].append(turn)
        
        # Save updated history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return turn