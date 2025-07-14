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
        
        status_lines.append(f"\n=== GUIDANCE ===")
        if missing:
            status_lines.append(f"• Next: Ask about {missing[0]} or related field")
        else:
            status_lines.append("• All data collected - ready for summary")
        
        return "\n".join(status_lines)