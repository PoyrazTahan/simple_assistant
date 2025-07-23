def print_agent_message(message):
    """Print agent message aligned to the left with proper indentation"""
    print()
    print("🤖 Assistant:")
    # Add tab indentation to each line for hierarchy
    indented_lines = []
    for line in message.split('\n'):
        indented_lines.append(f"    {line}")
    print('\n'.join(indented_lines))

def print_user_message(message):
    """Print user message aligned to the right"""
    terminal_width = 80
    print()
    print(f"You: {message:>{terminal_width-5}}")

def get_user_input(prompt="💬 Your message: "):
    """Get user input with universal quit check - returns None if user wants to quit"""
    print()
    user_input = input(prompt).strip()
    
    # Universal quit check
    if user_input.lower() == 'quit':
        return None  # Signal to quit
    
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

class ThinkingAnimation:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the thinking animation"""
        import sys
        import time
        import threading
        
        if self.running:
            return
            
        self.running = True
        
        def animate():
            dots = 0
            while self.running:
                dots = (dots + 1) % 4
                dot_string = "." * dots
                padding = " " * (3 - dots)
                sys.stdout.write(f"\r🤖 AI is thinking{dot_string}{padding}")
                sys.stdout.flush()
                time.sleep(0.5)
        
        self.thread = threading.Thread(target=animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the thinking animation and clear the line"""
        import sys
        import time
        
        if not self.running:
            return
            
        self.running = False
        
        # Give thread time to stop
        time.sleep(0.1)
        
        # Clear the animation line
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()