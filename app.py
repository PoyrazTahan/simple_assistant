import sys
from simple_agent import SimpleAgent
from stage_manager import StageManager
from data_manager import DataManager
import text_parser
from conversation_ui import print_agent_message, print_user_message, get_user_input
from widget_handler import is_widget_field, show_widget_for_field

def main():
    """Simple onboarding with flattened architecture"""
    # Check for debug mode
    debug_mode = "--debug" in sys.argv
    prompt_mode = "--full-prompt" in sys.argv
    
    if debug_mode:
        print("Simple Onboarding - DEBUG MODE")
    else:
        print("Simple Onboarding - Data Collection")
    
    print("Type 'quit' to exit")
    
    # Initialize components
    agent = SimpleAgent(debug_mode=debug_mode, prompt_mode=prompt_mode)
    stage_manager = StageManager(debug_mode=debug_mode)
    data_manager = DataManager()
    system_messages_history = []
    
    # Main conversation loop
    user_input = ""  # Initialize user_input
    
    while not stage_manager.is_complete():
        # Get current stage context
        stage_context = stage_manager.get_current_stage_context()
        profile_and_data_context = stage_manager.get_profile_and_data_context()
        
        # Get user input if needed (and not already set from widget)
        if stage_manager.needs_user_input() and not user_input:
            user_input = get_user_input()
            
            # Check for quit
            if user_input.lower() == 'quit':
                break
                
            # Display user input
            print_user_message(user_input)
        elif not stage_manager.needs_user_input():
            # Skip user input for automatic transitions (recommendations)
            user_input = ""
            if debug_mode:
                print(f"[DEBUG] - Automatic transition to recommendations stage")
        
        # Agent conversation
        response = agent.ask(user_input, stage_context, profile_and_data_context)
        
        # Execute system commands
        command_results = execute_system_commands(response["system_commands"], data_manager, debug_mode)
        
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
        
        # Display response
        print_agent_message(response["user_message"])
        
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

def execute_system_commands(system_commands, data_manager, debug_mode):
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
            
            # Show widget and get user selection
            selection = show_widget_for_field(field)
            
            if selection is not None:
                # Auto-update the field with widget selection
                result = data_manager.update_field(field, selection)
                results.append(f"WIDGET_UPDATE: {result}")
                results.append(f"WIDGET_COMPLETED: {selection}")
                
                if debug_mode:
                    print(f"[DEBUG] - Widget completed: {field} = {selection}")
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