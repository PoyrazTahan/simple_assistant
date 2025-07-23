#!/usr/bin/env python3
"""
Simplified widget handler for simple_onboarding
"""

import json
from conversation_ui import get_user_input
import textwrap

def wrap_text_with_prefix(text, max_width, continuation_prefix):
    """Wrap text with proper alignment for continuation lines"""
    if len(text) <= max_width:
        return [text]
    
    lines = []
    remaining = text
    first_line = True
    
    while remaining:
        if first_line:
            # First line uses full width
            if len(remaining) <= max_width:
                lines.append(remaining)
                break
            else:
                # Find last space before max_width
                cut_pos = max_width
                while cut_pos > 0 and remaining[cut_pos] != ' ':
                    cut_pos -= 1
                
                if cut_pos == 0:  # No space found, cut at max_width
                    cut_pos = max_width
                
                lines.append(remaining[:cut_pos])
                remaining = continuation_prefix + remaining[cut_pos:].lstrip()
                first_line = False
        else:
            # Continuation lines
            if len(remaining) <= max_width:
                lines.append(remaining)
                break
            else:
                # Find last space before max_width
                cut_pos = max_width
                while cut_pos > len(continuation_prefix) and remaining[cut_pos] != ' ':
                    cut_pos -= 1
                
                if cut_pos <= len(continuation_prefix):  # No space found
                    cut_pos = max_width
                
                lines.append(remaining[:cut_pos])
                remaining = continuation_prefix + remaining[cut_pos:].lstrip()
    
    return lines

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
    """Print entire widget content in a nice box with text wrapping"""
    BOX_WIDTH = 41  # Total inner width
    
    print()
    print("    ┌─────────────────────────────────────────┐")
    print("    │              🎛️  WIDGET UI               │")
    print("    ├─────────────────────────────────────────┤")
    
    # Wrap question text with proper alignment (reserve 2 spaces for padding)
    question_lines = wrap_text_with_prefix(f"📝 {question_text}", BOX_WIDTH - 2, "   ")
    for line in question_lines:
        print(f"    │ {line:<{BOX_WIDTH - 2}} │")
    
    print("    │                                         │")
    print("    │ Seçenekler:                             │")
    
    # Wrap option text with proper alignment
    for i, option in enumerate(options, 1):
        prefix = f"{i:2}) "
        if selected_option and option == selected_option:
            # For selected option, reserve space for checkmark (✅ = 3 chars including space)
            option_lines = wrap_text_with_prefix(f"{prefix}{option}", BOX_WIDTH - 5, "     ")
            for j, line in enumerate(option_lines):
                if j == 0:
                    # First line gets the checkmark
                    print(f"    │ {line:<{BOX_WIDTH - 5}} ✅ │")
                else:
                    # Continuation lines get normal spacing
                    print(f"    │ {line:<{BOX_WIDTH - 2}} │")
        else:
            option_lines = wrap_text_with_prefix(f"{prefix}{option}", BOX_WIDTH - 2, "     ")
            for line in option_lines:
                print(f"    │ {line:<{BOX_WIDTH - 2}} │")
    
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
    
    # Use Turkish question text
    question_text = widget_config.get("question_text_tr", f"Select {field_name}")
    
    # Get options
    if "options" in widget_config:
        option_objects = widget_config["options"]
        display_options = [opt["display_tr"] for opt in option_objects]
    else:
        print(f"❌ No options available for field: {field_name}")
        return None
    
    # Show widget box with all options
    print_widget_box(question_text, display_options)
    
    # Get user input with unified quit check
    while True:
        try:
            user_input = get_user_input("    Seçiminizi yapın (sadece rakam): ")
            
            # Check if user wants to quit
            if user_input is None:
                print("    ❌ Çıkış yapılıyor...")
                return "QUIT"  # Special return value to signal quit
                
            choice_num = int(user_input)
            
            if 1 <= choice_num <= len(display_options):
                choice_index = choice_num - 1
                selected_display = display_options[choice_index]  # Turkish display
                selected_value = option_objects[choice_index]["value"]  # English value
                
                print_widget_box(question_text, display_options, selected_display)
                return selected_value, selected_display  # Return English for backend, Turkish for display
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
                return selected_value, selected_display
            return None