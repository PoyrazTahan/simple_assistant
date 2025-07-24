#!/usr/bin/env python3
"""
Simple test runner - Just pipe inputs to the existing app
No code changes needed to the main system
"""

import json
import sys
import os
import subprocess
from datetime import datetime
import tempfile

def load_test_scenarios():
    """Load test scenarios from test.json"""
    test_file = "data/test.json"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return []
    
    with open(test_file, 'r') as f:
        data = json.load(f)
    return data.get("test_scenarios", [])

def setup_test_data(scenario):
    """Setup test data - reset data.json and apply existing_data"""
    existing_data = scenario.get("existing_data", {})
    
    # Load current data.json to get the field structure
    with open("data/data.json", 'r') as f:
        current_data = json.load(f)
    
    # Reset all fields to null (clean baseline)
    clean_data = {key: None for key in current_data.keys()}
    
    # Apply pre-filled fields if any
    clean_data.update(existing_data)
    
    # Save the clean starting state
    with open("data/data.json", 'w') as f:
        json.dump(clean_data, f, indent=2)
    
    if existing_data:
        print(f"    📋 Pre-filled {len(existing_data)} fields: {list(existing_data.keys())}")
    else:
        print(f"    📋 Starting with clean slate (all fields null)")
    
    return clean_data


# Test configuration constants
FALLBACK_INPUTS = {
    "GREETING": "Hello, I'm ready to start",
    "QUESTIONNAIRE": "continue",
    "RECOMMENDATIONS": "thank you"
}
INPUT_PROCESSING_DELAY = 0.5
MAX_INPUTS = 30

class InputResponder:
    """Handles input selection logic for test scenarios"""
    
    def __init__(self, scenario):
        self.inputs_provided = scenario.get("inputs", {})
        self.used_inputs = set()
        self.input_count = 0
    
    def select_input_for_field(self, stage, field):
        """Determine what input to provide based on stage and field"""
        if field != "NONE" and field in self.inputs_provided and field not in self.used_inputs:
            # We have a specific field input available
            input_value = str(self.inputs_provided[field])
            self.used_inputs.add(field)
            message = f"🎯 [{stage}] Providing '{input_value}' for field: {field}"
            return input_value, message
        
        # Use stage-appropriate fallback
        fallback = FALLBACK_INPUTS.get(stage, "yes")
        
        if field == "NONE":
            message = f"💬 [{stage}] No specific field, providing: {fallback}"
        else:
            message = f"🔄 [{stage}] Field '{field}' not available, providing: {fallback}"
        
        return fallback, message

class TestRunner:
    """Simplified test runner with clean separation of concerns"""
    
    def __init__(self, scenario, verbose=False, extra_flags=None):
        self.scenario = scenario
        self.verbose = verbose
        self.extra_flags = extra_flags or []
        self.responder = InputResponder(scenario)
        self.conversation_completed = False
        self.all_stdout = ""
    
    def run(self):
        """Main entry point for running a test scenario"""
        try:
            with self._create_process() as process:
                return self._communicate_with_process(process)
        except Exception as e:
            return "", f"Test failed: {e}", 1
    
    def _create_process(self):
        """Create and return the app subprocess"""
        cmd = ["python", "app.py", "--test"] + self.extra_flags
        
        return subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    
    def _communicate_with_process(self, process):
        """Handle all communication with the app process"""
        import re
        import time
        
        if self.verbose:
            print("\n" + "="*60)
            print("🔍 VERBOSE MODE - Stdout marker synchronization:")
            print("="*60)
        
        try:
            # Process stdout line by line
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                self.all_stdout += line
                self._process_output_line(line)
                
                # Look for input marker and respond
                if self._handle_input_marker(line, process):
                    if self.responder.input_count >= MAX_INPUTS:
                        break
                
                # Check if process ended
                if process.poll() is not None:
                    break
                    
        except Exception as e:
            if self.verbose and not self._is_normal_termination_error(e):
                print(f"\n[TEST] ⚠️ Communication error: {e}")
        
        return self._finalize_results(process)
    
    def _process_output_line(self, line):
        """Process a single line of stdout"""
        # Show output in verbose mode (except markers)
        if self.verbose and not line.startswith("[TEST_INPUT_NEEDED:"):
            print(line, end='')
        
        # Check for successful completion indicator
        if "📋 Recommendations:" in line:
            self.conversation_completed = True
    
    def _handle_input_marker(self, line, process):
        """Handle TEST_INPUT_NEEDED markers and send appropriate input"""
        import re
        import time
        
        marker_match = re.match(r'\[TEST_INPUT_NEEDED:([^:]+):([^\]]*)\]', line.strip())
        if not marker_match:
            return False
        
        stage, field = marker_match.groups()
        input_to_send, message = self.responder.select_input_for_field(stage, field)
        
        # Display input decision
        if self.verbose:
            print(f"\n[TEST INPUT] {message}")
            print(f"[TEST INPUT] 📤 Sending: {input_to_send}")
        else:
            print(f"    {message}")
            print(f"    📤 Input {self.responder.input_count + 1}: {input_to_send}")
        
        # Send input with proper timing
        try:
            process.stdin.write(f"{input_to_send}\n")
            process.stdin.flush()
            self.responder.input_count += 1
            time.sleep(INPUT_PROCESSING_DELAY)
            return True
        except BrokenPipeError:
            if self.verbose:
                print(f"\n[TEST] 🔚 Process ended, pipe closed")
            return False
    
    def _finalize_results(self, process):
        """Clean up and return final test results"""
        # Get any remaining output
        try:
            if not process.stdin.closed:
                process.stdin.close()
            remaining_stdout, stderr = process.communicate(timeout=10)
            self.all_stdout += remaining_stdout
            
            if self.verbose and remaining_stdout:
                print(remaining_stdout, end='')
                
        except Exception as e:
            stderr = f"Cleanup error: {e}"
        
        # Determine success
        return_code = process.returncode if process.returncode is not None else 0
        
        if self.conversation_completed and return_code != 0:
            if self.verbose:
                print(f"\n[TEST] ✅ Conversation completed successfully, ignoring exit code {return_code}")
            return_code = 0
        elif return_code != 0 and self.verbose:
            print(f"\n[TEST] ⚠️ Process ended with exit code {return_code}, inputs: {self.responder.input_count}")
        
        if self.verbose:
            if stderr:
                print(f"\n🚨 STDERR:\n{stderr}")
            print("\n" + "="*60)
        
        return self.all_stdout, stderr, return_code
    
    def _is_normal_termination_error(self, error):
        """Check if error is just normal process termination"""
        error_str = str(error).lower()
        return any(term in error_str for term in ["closed file", "broken pipe"])

def run_app_with_intelligent_inputs(scenario, verbose=False, extra_flags=None):
    """Simplified entry point that maintains backward compatibility"""
    runner = TestRunner(scenario, verbose, extra_flags)
    return runner.run()

def evaluate_test(scenario):
    """Evaluate test result - compare actual vs expected"""
    if not os.path.exists("data/data.json"):
        return False, [{"error": "No final data found"}], {}
    
    with open("data/data.json", 'r') as f:
        final_data = json.load(f)
    
    expected_data = scenario.get("expected_result", {})
    mismatches = []
    
    for field, expected_value in expected_data.items():
        actual_value = final_data.get(field)
        if str(actual_value).lower() != str(expected_value).lower():
            mismatches.append({
                "field": field,
                "expected": expected_value,
                "actual": actual_value
            })
    
    return len(mismatches) == 0, mismatches, final_data

def print_test_summary(test_num, scenario, test_passed, mismatches, final_data, start_data):
    """Print concise test summary"""
    status = "✅ PASS" if test_passed else "❌ FAIL"
    profile = scenario.get("profile", "generic")
    
    print(f"{test_num:2d}. {status} {scenario['name']} ({profile})")
    
    if not test_passed:
        print(f"    Mismatches: {len(mismatches)}")
        for mismatch in mismatches[:3]:  # Show first 3 mismatches
            field = mismatch['field']
            expected = mismatch['expected']
            actual = mismatch['actual']
            print(f"    • {field}: expected '{expected}', got '{actual}'")
        if len(mismatches) > 3:
            print(f"    • ... and {len(mismatches) - 3} more")
    
    # Show data completion stats
    filled_fields = sum(1 for v in final_data.values() if v is not None)
    total_fields = len(final_data)
    pre_filled = sum(1 for v in start_data.values() if v is not None)
    
    print(f"    Data: {pre_filled}→{filled_fields}/{total_fields} fields")

def _load_session_files():
    """Load recommendations and simplified conversation history from session files"""
    # Load recommendations if available
    recommendations = None
    if os.path.exists("data/recommendations.json"):
        try:
            with open("data/recommendations.json", 'r', encoding='utf-8') as f:
                recommendations = json.load(f)
        except Exception:
            recommendations = None
    
    # Load and simplify conversation history if available
    simplified_conversation = []
    if os.path.exists("data/conversation_history.json"):
        try:
            with open("data/conversation_history.json", 'r', encoding='utf-8') as f:
                full_history = json.load(f)
                turns = full_history.get('turns', [])
                
                # Extract just user_input and assistant_response pairs
                for turn in turns:
                    if turn.get('user_input') and turn.get('assistant_response'):
                        simplified_conversation.append({
                            "user_input": turn['user_input'],
                            "assistant_response": turn['assistant_response']
                        })
        except Exception:
            simplified_conversation = []
    
    return recommendations, simplified_conversation

def save_test_result(scenario, final_data, test_passed, mismatches, stdout, stderr):
    """Save test result to .test_results directory"""
    results_dir = "eval/.test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    test_name = scenario['name'].replace(' ', '_').lower()
    
    # Load session files
    recommendations, simplified_conversation = _load_session_files()
    
    test_result = {
        "test_info": {
            "name": scenario['name'],
            "profile": scenario.get('profile', 'generic'),
            "description": scenario.get('description', ''),
            "timestamp": datetime.now().isoformat()
        },
        "inputs_provided": scenario.get('inputs', {}),
        "expected_result": scenario.get('expected_result', {}),
        "actual_result": final_data,
        "test_evaluation": {
            "passed": test_passed,
            "total_fields": len(scenario.get('expected_result', {})),
            "matched_fields": len(scenario.get('expected_result', {})) - len(mismatches),
            "mismatches": mismatches
        },
        "data_completion": {
            "filled_fields": sum(1 for v in final_data.values() if v is not None),
            "total_fields": len(final_data),
            "completion_rate": sum(1 for v in final_data.values() if v is not None) / len(final_data) if final_data else 0
        },
        "app_output": {
            "stdout": stdout,
            "stderr": stderr
        },
        "session_files": {
            "recommendations": recommendations,
            "conversation_history": simplified_conversation
        }
    }
    
    result_file = f"{results_dir}/{test_name}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(test_result, f, indent=2, ensure_ascii=False)
    
    status = "✅ PASS" if test_passed else "❌ FAIL"
    print(f"    💾 Test result saved: {result_file} ({status})")

def run_test_scenario(scenario, test_number=None, verbose=False, extra_flags=None):
    """Run a single test scenario"""
    print(f"\n🧪 Running: {scenario['name']}")
    
    try:
        # Setup test data
        start_data = setup_test_data(scenario)
        
        # Show available inputs for this scenario
        inputs_provided = scenario.get("inputs", {})
        if not verbose:
            print(f"    📝 Available inputs: {list(inputs_provided.keys())}")
        
        # Show extra flags if any
        if extra_flags and not verbose:
            print(f"    🚩 Extra flags: {' '.join(extra_flags)}")
        
        # Run the app with intelligent input selection
        stdout, stderr, returncode = run_app_with_intelligent_inputs(scenario, verbose, extra_flags)
        
        if returncode != 0:
            print(f"    ❌ App failed with return code {returncode}")
            if stderr:
                print(f"    Error: {stderr}")
            # Show partial output for debugging
            if stdout:
                print(f"    📄 Partial output: {stdout[:500]}...")
            return False, f"App crashed: {stderr}"
        
        # Evaluate results
        test_passed, mismatches, final_data = evaluate_test(scenario)
        
        # Save test result
        save_test_result(scenario, final_data, test_passed, mismatches, stdout, stderr)
        
        # Print summary
        if test_number:
            print_test_summary(test_number, scenario, test_passed, mismatches, final_data, start_data)
        
        return test_passed, None
        
    except Exception as e:
        error_msg = f"❌ CRASH {scenario['name']} - {str(e)}"
        print(error_msg)
        return None, error_msg

def list_tests():
    """List available test scenarios"""
    scenarios = load_test_scenarios()
    print("📋 Available test scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        name = scenario["name"]
        profile = scenario.get("profile", "generic")
        existing = scenario.get("existing_data", {})
        
        filled_count = sum(1 for v in existing.values() if v is not None) if existing else 0
        
        print(f"  {i:2d}. {name} ({profile}) - {filled_count} pre-filled")
    print()

def _parse_command_line_flags():
    """Parse and extract command-line flags, returning processed flags and verbose setting"""
    # Check for verbose flag
    verbose = "--verbose" in sys.argv
    if verbose:
        sys.argv.remove("--verbose")  # Remove it so other parsing works
    
    # Extract extra flags to pass to app.py
    extra_flags = []
    app_flags = ["--full-prompt", "--language", "--debug"]
    for flag in app_flags:
        if flag in sys.argv:
            extra_flags.append(flag)
            sys.argv.remove(flag)
    
    # Extract model parameter
    model_flag = None
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--model="):
            model_flag = arg
            sys.argv.remove(arg)
            break
    if model_flag:
        extra_flags.append(model_flag)
    
    return verbose, extra_flags

def main():
    """Main test runner"""
    
    # Parse command-line flags
    verbose, extra_flags = _parse_command_line_flags()
    
    # No arguments = run all tests
    if len(sys.argv) < 2:
        scenarios = load_test_scenarios()
        if not scenarios:
            print("❌ No test scenarios found. Create data/test.json first.")
            return
            
        print(f"🧪 Simple Onboarding Test Suite - {len(scenarios)} scenarios")
        print("=" * 60)
        
        passed_tests = 0
        failed_tests = 0
        
        for i, scenario in enumerate(scenarios, 1):
            result, error = run_test_scenario(scenario, i, verbose, extra_flags)
            if result is None:  # Crashed
                failed_tests += 1
            elif result:  # Passed
                passed_tests += 1
            else:  # Failed
                failed_tests += 1
        
        print("=" * 60)
        print(f"📊 Results: {passed_tests} passed, {failed_tests} failed")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_tests()
        return
    
    if command == "run":
        if len(sys.argv) < 3:
            print("❌ Please specify test number")
            list_tests()
            return
        
        try:
            test_number = int(sys.argv[2])
        except ValueError:
            print("❌ Test number must be an integer")
            return
        
        # Get specific test scenario
        scenarios = load_test_scenarios()
        if test_number < 1 or test_number > len(scenarios):
            print(f"❌ Invalid test number. Available: 1-{len(scenarios)}")
            return
        
        scenario = scenarios[test_number - 1]
        print(f"🧪 Running: {scenario['name']} ({scenario.get('profile', 'generic')})")
        
        run_test_scenario(scenario, test_number, verbose, extra_flags)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'list' or 'run <test_number>'")

if __name__ == "__main__":
    main()