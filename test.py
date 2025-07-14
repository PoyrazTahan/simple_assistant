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

def create_input_sequence(scenario):
    """Create sequence of inputs to pipe to the app"""
    inputs = scenario.get("inputs", {})
    
    # Simple approach: provide all inputs in a sequence
    # The app will ask questions, we'll provide answers line by line
    input_sequence = []
    
    # Start with a greeting response
    input_sequence.append("Hello")
    
    # Add all the field responses
    for field, value in inputs.items():
        input_sequence.append(str(value))
    
    # Add many extra responses to ensure we don't run out
    input_sequence.extend(["yes", "continue", "next", "proceed", "done", "finished", "complete", "ok", "great", "perfect"])
    
    return input_sequence

def run_app_with_inputs(input_sequence):
    """Run the app and pipe in the input sequence"""
    # Join inputs with newlines
    input_text = "\n".join(input_sequence) + "\n"
    
    try:
        # Run the app with inputs piped in
        result = subprocess.run(
            ["python", "app.py"],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=60  # 60 second timeout
        )
        
        return result.stdout, result.stderr, result.returncode
        
    except subprocess.TimeoutExpired:
        return "", "Process timed out", 1
    except Exception as e:
        return "", f"Error running app: {e}", 1

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

def save_test_result(scenario, final_data, test_passed, mismatches, stdout, stderr):
    """Save test result to .test_results directory"""
    results_dir = ".test_results"
    os.makedirs(results_dir, exist_ok=True)
    
    test_name = scenario['name'].replace(' ', '_').lower()
    
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
        }
    }
    
    result_file = f"{results_dir}/{test_name}.json"
    with open(result_file, 'w') as f:
        json.dump(test_result, f, indent=2)
    
    status = "✅ PASS" if test_passed else "❌ FAIL"
    print(f"    💾 Test result saved: {result_file} ({status})")

def run_test_scenario(scenario, test_number=None):
    """Run a single test scenario"""
    print(f"\n🧪 Running: {scenario['name']}")
    
    try:
        # Setup test data
        start_data = setup_test_data(scenario)
        
        # Create input sequence
        input_sequence = create_input_sequence(scenario)
        print(f"    🎯 Will provide {len(input_sequence)} inputs to app")
        print(f"    📝 Input sequence: {input_sequence[:10]}...")
        
        # Run the app with inputs
        stdout, stderr, returncode = run_app_with_inputs(input_sequence)
        
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

def main():
    """Main test runner"""
    
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
            result, error = run_test_scenario(scenario, i)
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
        
        run_test_scenario(scenario, test_number)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'list' or 'run <test_number>'")

if __name__ == "__main__":
    main()