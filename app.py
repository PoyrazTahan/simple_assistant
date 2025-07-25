import sys
from simple_agent import SimpleAgent
from stage_manager import StageManager
from data_manager import DataManager
from conversation_ui import print_agent_message, print_user_message, get_user_input, ThinkingAnimation
from widget_handler import is_widget_field, show_widget_for_field

def main():
    """Simple onboarding with flattened architecture"""
    # Check for modes
    debug_mode = "--debug" in sys.argv
    prompt_mode = "--full-prompt" in sys.argv
    language_mode = "--language" in sys.argv
    test_mode = "--test" in sys.argv
    
    # Check for model parameter
    model = "gpt-4.1"  # default
    for arg in sys.argv:
        if arg.startswith("--model="):
            model = arg.split("=")[1]
    
    # Display mode information
    if debug_mode:
        print(f"Simple Assistant - DEBUG MODE (Model: {model})")
    elif language_mode:
        print(f"Simple Assistant - DUAL LANGUAGE MODE (Model: {model})")
    else:
        print(f"Simple Assistant - Data Collection (Model: {model})")
    
    print("Type 'quit' to exit")
    
    # Initialize components
    agent = SimpleAgent(
        debug_mode=debug_mode, 
        prompt_mode=prompt_mode, 
        language_mode=language_mode, 
        model=model
    )
    stage_manager = StageManager(debug_mode=debug_mode)
    data_manager = DataManager()
    system_messages_history = []
    
    # Main conversation loop
    user_input = ""  # Initialize user_input
    
    while not stage_manager.is_complete():
        # Get user input if needed (and not already set from widget)
        if stage_manager.needs_user_input() and not user_input:
            # Test mode: Signal that input is needed RIGHT BEFORE asking for it
            if test_mode:
                # Use previous response's asking field, or NONE if first iteration
                asking_field = response["system_commands"]["asking"] if 'response' in locals() else None
                current_stage = stage_manager.get_current_stage()
                field_info = asking_field if asking_field is not None else "NONE"
                print(f"[TEST_INPUT_NEEDED:{current_stage}:{field_info}]", flush=True)
            
            user_input = get_user_input()
            
            # Check if user wants to quit
            if user_input is None:
                break
                
            # Display user input
            print_user_message(user_input)
        elif not stage_manager.needs_user_input():
            # Skip user input for automatic transitions (recommendations)
            user_input = ""
            if debug_mode:
                print(f"[DEBUG] - Automatic transition to recommendations stage")
        
        # Get FRESH stage context AFTER previous updates have been applied
        stage_context = stage_manager.get_current_stage_context()
        profile_and_data_context = stage_manager.get_profile_and_data_context()
        # Agent conversation with thinking animation
        thinking_animation = ThinkingAnimation()
        thinking_animation.start()
        
        response = agent.ask(user_input, stage_context, profile_and_data_context)
        
        thinking_animation.stop()
        
        # Display response FIRST (before widgets)
        print_agent_message(response["user_message"])
        
        # Execute system commands (this may show widgets)
        command_results = execute_system_commands(response["system_commands"], data_manager, debug_mode, test_mode)
        
        # Check if a widget was completed
        widget_selection = None
        for result in command_results:
            if "WIDGET_COMPLETED:" in result:
                widget_selection = result.split("WIDGET_COMPLETED: ")[1]
                break
        
        # Store system commands in history
        system_messages_history.append({
            "user_input": user_input,
            "system_commands": response["system_commands"],
            "command_results": command_results
        })
        
        # Update stage based on response
        stage_manager.update_stage(response)
        
        # Save conversation turn to history
        data_manager.save_conversation_turn(
            user_input=user_input,
            assistant_response=response["user_message"],
            system_commands=response["system_commands"],
            current_stage=stage_manager.get_current_stage()
        )
        
        # Display recommendations if any
        if response["system_commands"]["recommendations"]:
            print("    📋 Recommendations:")
            for recommendation in response["system_commands"]["recommendations"]:
                print(f"        • {recommendation}")
        
        # Debug mode: show system commands
        if debug_mode:
            print(f"\n[DEBUG] - System commands: {response['system_commands']}")
            print(f"[DEBUG] - Command results:")
            for result in command_results:
                print(f"  {result}")
        
        # Clear user_input for next iteration (unless widget sets it)
        user_input = ""
        
        # If widget was completed, set widget selection as next user input
        if widget_selection:
            if debug_mode:
                print(f"[DEBUG] - Widget completed, continuing with: {widget_selection}")
            
            # Set widget selection as next user input and continue loop
            user_input = widget_selection
            print_user_message(user_input)  # Show the widget selection as user message
    
    # Handle final recommendations if we're in recommendations stage
    if stage_manager.get_current_stage() == "RECOMMENDATIONS":
        handle_final_recommendations(agent, data_manager, system_messages_history, debug_mode)

def execute_system_commands(system_commands, data_manager, debug_mode, test_mode=False):
    """Execute system commands and return results"""
    results = []
    
    # Process updates - but skip widget fields to prevent LLM overwriting widget selections
    for update in system_commands["updates"]:
        field = update["field"]
        value = update["value"]
        
        # Protection: Skip updates for widget fields
        if is_widget_field(field):
            if debug_mode:
                print(f"[DEBUG] - Skipping update for widget field: {field}")
            results.append(f"SKIP_UPDATE: {field} is widget field")
            continue
            
        result = data_manager.update_field(field, value)
        results.append(f"UPDATE: {result}")
    
    # Check if asking field is a widget field
    if system_commands["asking"]:
        field = system_commands["asking"]
        
        if is_widget_field(field):
            if debug_mode:
                print(f"[DEBUG] - Showing widget for field: {field}")
            
            # Test mode: Print marker before widget is shown so test can provide input
            if test_mode:
                print(f"[TEST_INPUT_NEEDED:QUESTIONNAIRE:{field}]", flush=True)
            
            # Show widget and get user selection
            widget_result = show_widget_for_field(field)
            
            if widget_result == "QUIT":
                # User wants to quit during widget selection - exit main loop
                import sys
                print("    ❌ Uygulamadan çıkılıyor...")
                sys.exit(0)
            elif widget_result is not None:
                # Widget returns (english_value, turkish_display)
                english_value, turkish_display = widget_result
                
                # Use English value for backend storage
                result = data_manager.update_field(field, english_value)
                results.append(f"WIDGET_UPDATE: {result}")
                # Store Turkish display for user display
                results.append(f"WIDGET_COMPLETED: {turkish_display}")
                
                if debug_mode:
                    print(f"[DEBUG] - Widget completed: {field} = {english_value} (display: {turkish_display})")
            else:
                results.append(f"WIDGET_CANCELLED: {field}")
        else:
            results.append(f"ASKING: {field}")
    
    # Check if all fields are complete after updates
    data = data_manager.load_data()
    missing_fields = [key for key, value in data.items() if value is None]
    
    if len(missing_fields) == 0:
        results.append("ALL_FIELDS_COMPLETE: Transitioning to completion stage")
    
    return results

def handle_final_recommendations(agent, data_manager, system_messages_history, debug_mode):
    """Handle final recommendations parsing and saving"""
    # Find the last system message with recommendations
    for entry in reversed(agent.conversation_history):
        if entry["role"] == "assistant":
            # Check if this response has recommendations in system commands
            for system_entry in reversed(system_messages_history):
                if "recommendations" in system_entry["system_commands"] and len(system_entry["system_commands"]["recommendations"]) > 0:
                    try:
                        actions_list = system_entry["system_commands"]["recommendations"]
                        user_message = entry["message"]
                        
                        # Save recommendations
                        data_manager.save_recommendations(actions_list, user_message)
                        
                        if debug_mode:
                            print(f"[DEBUG] - Recommendations saved: {actions_list}")
                        
                        return
                        
                    except Exception as e:
                        if debug_mode:
                            print(f"[DEBUG] - Error saving recommendations: {e}")
                        return
            break
    
    if debug_mode:
        print(f"[DEBUG] - No recommendations found to save")

if __name__ == "__main__":
    main()