import json

class DataManager:
    """Simple data manager for basic JSON operations"""
    
    def __init__(self, data_file="data/data.json"):
        self.data_file = data_file
    
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
            status_lines.append(f"• Next: Ask about {missing[0]} or related field")
        else:
            status_lines.append("• All data collected - ready for summary")
        
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
    
    def get_user_type_and_greeting_context(self):
        """Determine if user is new or returning and provide greeting context"""
        data = self.load_data()
        
        # Check if user has any data beyond name
        filled_fields = [key for key, value in data.items() if value is not None]
        
        # New user: only name or completely empty
        if len(filled_fields) == 0 or (len(filled_fields) == 1 and 'name' in filled_fields):
            user_type = "new"
        else:
            user_type = "returning"
        
        # Get first missing field for next_question
        missing_fields = [key for key, value in data.items() if value is None]
        first_missing = missing_fields[0] if missing_fields else None
        
        return {
            "user_type": user_type,
            "first_missing_field": first_missing,
            "filled_fields": filled_fields,
            "missing_fields": missing_fields
        }