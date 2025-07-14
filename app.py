from conversation_ui import print_agent_message, print_user_message, get_user_input, show_conversation_history

def main():
    """Simple echo app for testing UI"""
    print("Simple Onboarding - Echo Test")
    print("Type 'quit' to exit")
    
    conversation_history = []
    
    while True:
        user_input = get_user_input()
        
        if user_input.lower() == 'quit':
            break
            
        # Echo back what user said
        response = f"You said: {user_input}"
        print_user_message(user_input)
        print_agent_message(response)
        
        # Store in history
        conversation_history.append({"role": "user", "message": user_input})
        conversation_history.append({"role": "assistant", "message": response})
        
        # Show history every 3 exchanges
        if len(conversation_history) >= 6:
            show_conversation_history(conversation_history)
            conversation_history = []  # Reset for testing

if __name__ == "__main__":
    main()