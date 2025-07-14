def print_agent_message(message):
    """Print agent message aligned to the left"""
    print()
    print("🤖 Assistant:")
    print(f"   {message}")

def print_user_message(message):
    """Print user message aligned to the right"""
    terminal_width = 80
    print()
    print(f"You: {message:>{terminal_width-5}}")

def get_user_input():
    """Get user input with simple prompt"""
    print()
    user_input = input("💬 Your message: ").strip()
    return user_input

def show_conversation_history(history):
    """Simple conversation display"""
    print("\n=== CONVERSATION HISTORY ===")
    for entry in history:
        if entry['role'] == 'user':
            print_user_message(entry['message'])
        else:
            print_agent_message(entry['message'])
    print("=" * 30)