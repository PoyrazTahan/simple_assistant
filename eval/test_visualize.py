#!/usr/bin/env python3
"""
HTML Test Results Visualizer
Creates a dark mode HTML report for all test results in .test_results directory
"""

import json
import os
import glob
from datetime import datetime

def load_test_results():
    """Load all test result JSON files from .test_results directory"""
    results_dir = "eval/.test_results"
    
    if not os.path.exists(results_dir):
        print(f"❌ Results directory not found: {results_dir}")
        return []
    
    test_files = glob.glob(f"{results_dir}/*.json")
    test_results = []
    
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
                result['_file_path'] = file_path
                test_results.append(result)
        except Exception as e:
            print(f"⚠️ Error loading {file_path}: {e}")
    
    return test_results

def generate_html_report(test_results):
    """Generate HTML report for test results"""
    
    # Calculate summary stats
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.get('test_evaluation', {}).get('passed', False))
    failed_tests = total_tests - passed_tests
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Assistant Test Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #1a1a1a;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #4CAF50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }}
        
        .summary {{
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .stat-card {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .stat-total {{ background: #424242; }}
        .stat-passed {{ background: #2E7D32; }}
        .stat-failed {{ background: #D32F2F; }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .test-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .test-card {{
            background: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid;
        }}
        
        .test-card.passed {{ border-left-color: #4CAF50; }}
        .test-card.failed {{ border-left-color: #F44336; }}
        
        .test-header {{
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .test-title {{
            font-size: 1.2rem;
            font-weight: bold;
            flex-grow: 1;
        }}
        
        .test-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        
        .status-passed {{
            background: #4CAF50;
            color: white;
        }}
        
        .status-failed {{
            background: #F44336;
            color: white;
        }}
        
        .test-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }}
        
        .detail-section h3 {{
            color: #81C784;
            margin-bottom: 10px;
            font-size: 1rem;
        }}
        
        .field-status {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #424242;
        }}
        
        .field-status:last-child {{
            border-bottom: none;
        }}
        
        .field-name {{
            font-weight: 500;
        }}
        
        .field-match {{ color: #4CAF50; }}
        .field-mismatch {{ color: #F44336; }}
        
        .recommendations {{
            background: #1B3A0F;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .recommendation-item {{
            background: #2E7D32;
            color: white;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 5px;
            display: inline-block;
            font-size: 0.9rem;
        }}
        
        .profile-badge {{
            background: #424242;
            color: #e0e0e0;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-left: 10px;
        }}
        
        .completion-bar {{
            background: #424242;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .completion-fill {{
            background: linear-gradient(90deg, #4CAF50, #81C784);
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.8rem;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Health Assistant Test Results</h1>
        
        <div class="summary">
            <div class="stat-card stat-total">
                <span class="stat-number">{total_tests}</span>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card stat-passed">
                <span class="stat-number">{passed_tests}</span>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card stat-failed">
                <span class="stat-number">{failed_tests}</span>
                <div class="stat-label">Failed</div>
            </div>
        </div>
        
        <div class="test-grid">
"""
    
    # Generate test cards
    for result in test_results:
        test_info = result.get('test_info', {})
        test_eval = result.get('test_evaluation', {})
        data_completion = result.get('data_completion', {})
        session_files = result.get('session_files', {})
        
        test_name = test_info.get('name', 'Unknown Test')
        profile = test_info.get('profile', 'generic')
        passed = test_eval.get('passed', False)
        mismatches = test_eval.get('mismatches', [])
        
        status_class = 'passed' if passed else 'failed'
        status_text = '✅ PASSED' if passed else '❌ FAILED'
        status_css = 'status-passed' if passed else 'status-failed'
        
        # Completion percentage
        filled_fields = data_completion.get('filled_fields', 0)
        total_fields = data_completion.get('total_fields', 1)
        completion_pct = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
        
        # Recommendations
        recommendations = session_files.get('recommendations', {})
        rec_actions = recommendations.get('top_4_actions', []) if recommendations else []
        
        html += f"""
            <div class="test-card {status_class}">
                <div class="test-header">
                    <div class="test-title">
                        {test_name}
                        <span class="profile-badge">{profile}</span>
                    </div>
                    <div class="test-status {status_css}">{status_text}</div>
                </div>
                
                <div class="completion-bar">
                    <div class="completion-fill" style="width: {completion_pct}%">
                        {completion_pct}% Complete ({filled_fields}/{total_fields} fields)
                    </div>
                </div>
                
                <div class="test-details">
                    <div class="detail-section">
                        <h3>🔍 Field Validation</h3>
"""
        
        # Show field validation results
        expected = result.get('expected_result', {})
        actual = result.get('actual_result', {})
        
        for field, expected_value in expected.items():
            actual_value = actual.get(field)
            match = str(actual_value).lower() == str(expected_value).lower()
            status_class = 'field-match' if match else 'field-mismatch'
            
            html += f"""
                        <div class="field-status">
                            <span class="field-name">{field}</span>
                            <span class="{status_class}">{'✓' if match else '✗'}</span>
                        </div>
"""
        
        html += f"""
                    </div>
                    <div class="detail-section">
                        <h3>💊 Recommendations</h3>
"""
        
        if rec_actions:
            html += '<div class="recommendations">'
            for action in rec_actions:
                # Format action names nicely
                formatted_action = action.replace('_', ' ').title()
                html += f'<span class="recommendation-item">{formatted_action}</span>'
            html += '</div>'
        else:
            html += '<p style="opacity: 0.6;">No recommendations available</p>'
        
        html += """
                    </div>
                </div>
            </div>
"""
    
    html += f"""
        </div>
        
        <div style="text-align: center; margin-top: 40px; opacity: 0.6; font-size: 0.9rem;">
            Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>
"""
    
    return html

def create_html_report():
    """Main function to create HTML report"""
    print("🎨 Creating HTML test visualization...")
    
    # Load test results
    test_results = load_test_results()
    
    if not test_results:
        print("❌ No test results found to visualize")
        return
    
    # Generate HTML
    html_content = generate_html_report(test_results)
    
    # Save HTML file
    output_file = "eval/test_results.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML report created: {output_file}")
    print(f"📊 Visualized {len(test_results)} test results")
    
    return output_file

if __name__ == "__main__":
    create_html_report()