import sys
from conversation_ui import print_agent_message, print_user_message, get_user_input, show_conversation_history
from simple_agent import SimpleAgent

def main():
    """Simple onboarding with dual-response system and debug mode"""
    # Check for debug mode
    debug_mode = "--debug" in sys.argv
    
    if debug_mode:
        print("Simple Onboarding - DEBUG MODE")
    else:
        print("Simple Onboarding - Data Collection")
    
    print("Type 'quit' to exit")
    
    # Initialize agent with debug mode (auto-generates greeting)
    agent = SimpleAgent(debug_mode=debug_mode)
    
    # Get and display initial greeting
    greeting_response = agent.get_initial_greeting()
    print_agent_message(greeting_response["user_message"])
    
    # Debug mode: show greeting system commands
    if debug_mode:
        print(f"\n[DEBUG] - Initial greeting system commands:")
        print(f"  System commands: {greeting_response['system_commands']}")
        
        print(f"[DEBUG] - Greeting command results:")
        for result in greeting_response["command_results"]:
            print(f"  {result}")
    
    while True:
        user_input = get_user_input()
        
        if user_input.lower() == 'quit':
            break
            
        # Ask agent with user input
        response = agent.ask(user_input)
        
        # Display user message
        print_user_message(user_input)
        
        # Display assistant message (only user-facing part)
        print_agent_message(response["user_message"])
        
        # Debug mode: show system commands
        if debug_mode:
            print(f"\n[DEBUG] - System commands: {response['system_commands']}")
            
            print(f"[DEBUG] - Command results:")
            for result in response["command_results"]:
                print(f"  {result}")

if __name__ == "__main__":
    main()