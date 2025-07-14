# Simple Onboarding - Streamlined Health Data Collection

A simplified health data collection system that uses direct text parsing, stage-based conversation management, and integrated widget UI for enhanced user experience.

## 🏗️ Architecture Overview

**Simple Agent** → **Stage Manager** → **Text Parser** → **Widget Handler** → **Data Manager**

- **Simple Agent**: Direct LLM conversation without function calls
- **Stage Manager**: Three-stage conversation flow (GREETING → QUESTIONNAIRE → RECOMMENDATIONS)
- **Text Parser**: XML-based parsing for updates, asking fields, and recommendations
- **Widget Handler**: Self-contained UI for specific fields (gender, smoking, etc.)
- **Data Manager**: JSON-based data persistence with field validation

## 🚀 Quick Start

### Installation

#### 1. Open Terminal (macOS)

- Press `Cmd + Space`, type "Terminal", press Enter

#### 2. Create Setup Directory and Script

```bash
# Create heltia directory in your home folder
mkdir ~/heltia

# Create setup script file
touch ~/heltia/setup.sh

# Make it executable
chmod +x ~/heltia/setup.sh

# Open the heltia directory in Finder
open ~/heltia
```

#### 3. Copy Setup Script Content

1. **Open the setup.sh file** you just created (double-click it in Finder)
2. **Copy the setup script content** from: https://github.com/PoyrazTahan/simple_assistant/blob/main/setup.sh
3. **Paste the content** into your setup.sh file and save it

#### 4. Run Setup Script

```bash
# Navigate to heltia directory and run setup
cd ~/heltia
./setup.sh
```

#### 5. Add Your OpenAI API Key

**After setup completes, edit the .env file:**

```bash
# Open the environment file
open ~/heltia/simple_assistant
```

Edit .env file by right-click + Open with Text Edit

**Replace `your-openai-api-key-here` with your actual OpenAI API key from https://platform.openai.com/api-keys**

#### 6. Activate Environment and Start Using

```bash
# Activate the conda environment
conda activate planner_agent

# Navigate to project directory
cd ~/heltia/simple_assistant
```

2. **Run the Application**

```bash
# Interactive mode
python app.py

# Debug mode (shows system commands and stage transitions)
python app.py --debug

# Full prompt mode (shows complete prompts sent to LLM)
python app.py --full-prompt
```

3. **Run Tests**

```bash
# Run all test scenarios
python test.py

# List available tests
python test.py list

# Run specific test
python test.py run 1
```

## 📁 File Structure

```
simple_onboarding/
├── app.py                 # Main application entry point
├── simple_agent.py        # LLM conversation handler
├── stage_manager.py       # Conversation stage management
├── data_manager.py        # Data persistence and validation
├── text_parser.py         # XML command parsing
├── widget_handler.py      # Widget UI components
├── conversation_ui.py     # Terminal UI functions
├── test.py               # Automated testing system
├── prompts/              # LLM prompt templates
│   ├── system_prompt.txt
│   ├── greeting_prompt.txt
│   ├── questionnaire_prompt.txt
│   └── recommendation_prompt.txt
└── data/                 # Data files
    ├── data.json         # User health data (13 fields)
    ├── widget_config.json # Widget field configurations
    ├── recommendations.json # Final recommendations output
    └── test.json         # Test scenarios and expected results
```

## 🎯 Key Features

### 1. **Simplified Architecture**

- No function calls or complex tool systems
- Direct text parsing with XML tags
- Stage-based conversation flow
- Self-contained widget components

### 2. **Widget Integration**

Widget fields automatically show interactive UI:

- **Gender**: Male/Female/Other options
- **Sleep Quality**: 6-point scale
- **Stress Level**: Time-based frequency scale
- **Smoking Status**: Detailed smoking habits
- **And more...** (10 widget fields total)

### 3. **Automated Testing**

- 10+ test scenarios covering different user profiles
- Automated input provision via stdin
- Expected vs actual result validation
- Case-insensitive comparison
- Detailed test result logging

### 4. **Data Flow Protection**

- Widget fields protected from LLM updates
- Prevents duplicate data writing
- Maintains data consistency

## 🔄 Conversation Flow

```
1. GREETING
   └── Welcome user, start conversation

2. QUESTIONNAIRE
   ├── Ask for missing fields
   ├── Show widgets for configured fields
   ├── Parse and store responses
   └── Continue until all 13 fields complete

3. RECOMMENDATIONS
   ├── Generate personalized health advice
   ├── Save to recommendations.json
   └── Complete conversation
```

## 🎛️ Widget System

Widget fields are configured in `data/widget_config.json` and automatically trigger when the LLM asks for those fields:

**Example Widget Flow:**

1. LLM asks: "What is your gender?"
2. System detects `<asking>gender</asking>`
3. Shows widget with options (Erkek/Kadın/Other)
4. User selects option "2"
5. Widget returns "Female"
6. Conversation continues with "Female" as user input

## 🧪 Testing System

The testing system provides comprehensive validation:

```bash
# Run all 10+ test scenarios
python test.py

# Example test scenarios:
# - Fresh User (empty → complete profile)
# - Pregnant Woman (pre-filled data)
# - Active Young Male (high activity)
# - Senior with Health Issues
# - Stressed Professional
# - And more...
```

Test results include:

- Data completion rates
- Field-by-field validation
- Expected vs actual comparisons
- Detailed error reporting

## 📊 Data Model

**13 Health Fields:**

```json
{
  "age": 28,
  "weight": 72.0,
  "height": 175.0,
  "gender": "Female",
  "has_children": "No",
  "sleep_quality": "good",
  "stress_level": "moderate",
  "mood_level": "good",
  "activity_level": "mildly active",
  "sugar_intake": "low",
  "water_intake": "moderate",
  "smoking_status": "no",
  "supplement_usage": "yes"
}
```

## 🎨 Widget Fields

Currently configured widget fields:

- `gender` - Gender selection
- `has_children` - Children/pregnancy status
- `sleep_quality` - Sleep frequency scale
- `stress_level` - Stress frequency scale
- `mood_level` - Mood frequency scale
- `activity_level` - Physical activity levels
- `sugar_intake` - Sugar consumption frequency
- `water_intake` - Daily water intake ranges
- `smoking_status` - Detailed smoking habits
- `supplement_usage` - Supplement usage (Yes/No)

## 🔧 Development

**Debug Mode:**

```bash
python app.py --debug
```

Shows:

- Stage transitions
- System command parsing
- Widget field detection
- Data update operations

**Testing Individual Components:**

```bash
# Test widget handler
python widget_handler.py

# Test data manager
python data_manager.py

# Test text parser
python text_parser.py
```

## 🎯 Design Principles

1. **Simplicity First**: No complex function calling or tool systems
2. **Self-Contained Widgets**: Widget UI completely independent
3. **Natural Conversation**: Widget selections flow naturally into conversation
4. **Data Protection**: Prevent LLM from overwriting widget selections
5. **Testing Focus**: Comprehensive automated testing for reliability

This simplified approach maintains the essential functionality while dramatically reducing complexity compared to the full onboarding_assistant system.
