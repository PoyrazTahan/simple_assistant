import sys
from simple_agent import SimpleAgent
from stage_manager import StageManager
from data_manager import DataManager
import text_parser
from conversation_ui import print_agent_message, print_user_message, get_user_input

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
    while not stage_manager.is_complete():
        # Get current stage context
        stage_context = stage_manager.get_current_stage_context()
        profile_and_data_context = stage_manager.get_profile_and_data_context()
        
        # Get user input if needed
        if stage_manager.needs_user_input():
            user_input = get_user_input()
            
            # Check for quit
            if user_input.lower() == 'quit':
                break
                
            # Display user input
            print_user_message(user_input)
        else:
            # Skip user input for automatic transitions (recommendations)
            user_input = ""
            if debug_mode:
                print(f"[DEBUG] - Automatic transition to recommendations stage")
        
        # Agent conversation
        response = agent.ask(user_input, stage_context, profile_and_data_context)
        
        # Execute system commands
        command_results = execute_system_commands(response["system_commands"], data_manager, debug_mode)
        
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
    
    # Handle final recommendations if we're in recommendations stage
    if stage_manager.get_current_stage() == "RECOMMENDATIONS":
        handle_final_recommendations(agent, data_manager, system_messages_history, debug_mode)

def execute_system_commands(system_commands, data_manager, debug_mode):
    """Execute system commands and return results"""
    results = []
    
    # Process updates
    for update in system_commands["updates"]:
        field = update["field"]
        value = update["value"]
        result = data_manager.update_field(field, value)
        results.append(f"UPDATE: {result}")
    
    # Check if all fields are complete after updates
    data = data_manager.load_data()
    missing_fields = [key for key, value in data.items() if value is None]
    
    if len(missing_fields) == 0:
        results.append("ALL_FIELDS_COMPLETE: Transitioning to completion stage")
        return results
    
    # Process next question only if fields are still missing
    if system_commands["asking"]:
        results.append(f"ASKING: {system_commands['asking']}")
    
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