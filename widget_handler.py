#!/usr/bin/env python3
"""
Simplified widget handler for simple_onboarding
"""

import json

def load_widget_config():
    """Load widget configuration"""
    try:
        with open("data/widget_config.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading widget config: {e}")
        return {}

def is_widget_field(field_name):
    """Check if a field is configured as a widget field"""
    config = load_widget_config()
    widget_fields = config.get("widget_fields", {})
    return field_name in widget_fields and widget_fields[field_name].get("enabled", False)

def print_widget_box(question_text, options, selected_option=None):
    """Print entire widget content in a nice box"""
    print()
    print("    ┌─────────────────────────────────────────┐")
    print("    │              🎛️  WIDGET UI               │")
    print("    ├─────────────────────────────────────────┤")
    print(f"    │ 📝 {question_text[:34]:<34}   │")
    print("    │                                         │")
    print("    │ Seçenekler:                             │")
    
    for i, option in enumerate(options, 1):
        if selected_option and option == selected_option:
            print(f"    │ {i:2}) {option:<32} ✅ │")
        else:
            print(f"    │ {i:2}) {option:<34}  │")
    
    print("    │                                         │")
    print("    └─────────────────────────────────────────┘")
    
    if selected_option:
        print(f"    ✅ Seçiminiz: {selected_option}")
        print()

def show_widget_for_field(field_name):
    """Show widget interface for a specific field and get user selection"""
    config = load_widget_config()
    widget_fields = config.get("widget_fields", {})
    
    if field_name not in widget_fields:
        print(f"❌ No widget configuration found for field: {field_name}")
        return None
    
    widget_config = widget_fields[field_name]
    
    # Use English question text
    question_text = widget_config.get("question_text", f"Select {field_name}")
    
    # Get options
    if "options" in widget_config:
        option_objects = widget_config["options"]
        display_options = [opt["display_tr"] for opt in option_objects]
    else:
        print(f"❌ No options available for field: {field_name}")
        return None
    
    # Show widget box with all options
    print_widget_box(question_text, display_options)
    
    # Get user input (stdin will be handled by test.py automatically)
    while True:
        try:
            user_input = input("    Seçiminizi yapın (sadece rakam): ").strip()
            choice_num = int(user_input)
            
            if 1 <= choice_num <= len(display_options):
                choice_index = choice_num - 1
                selected_display = display_options[choice_index]  # Turkish display
                selected_value = option_objects[choice_index]["value"]  # English value
                
                print_widget_box(question_text, display_options, selected_display)
                return selected_value  # Return English value for data consistency
            else:
                print(f"    ❌ Lütfen 1-{len(display_options)} arasında bir rakam girin")
                
        except ValueError:
            print("    ❌ Lütfen sadece rakam girin")
        except (KeyboardInterrupt, EOFError):
            print("\n    ❌ Widget iptal edildi")
            # Default to first option on cancel
            if display_options:
                choice_index = 0
                selected_display = display_options[choice_index]
                selected_value = option_objects[choice_index]["value"]
                print_widget_box(question_text, display_options, selected_display)
                return selected_value
            return None