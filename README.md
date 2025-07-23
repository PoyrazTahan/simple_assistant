# Simple Assistant - Streamlined Health Data Collection

A simplified health data collection system that uses direct text parsing, stage-based conversation management, and integrated widget UI for enhanced user experience.

## 🏗️ Architecture Overview

**Simple Agent** → **Stage Manager** → **Text Parser** → **Widget Handler** → **Data Manager**

- **Simple Agent**: Direct LLM conversation without function calls
- **Stage Manager**: Three-stage conversation flow (GREETING → QUESTIONNAIRE → RECOMMENDATIONS)
- **Text Parser**: XML-based parsing for updates, asking fields, and recommendations
- **Widget Handler**: Self-contained UI for specific fields (gender, smoking, etc.)
- **Data Manager**: JSON-based data persistence with field validation

## 🚀 Quick Start

### Automatic Setup (Recommended)

**One-line setup for macOS:**

```bash
# Open Terminal (Cmd+Space, type "Terminal")
# Run this single command:
curl -fsSL https://raw.githubusercontent.com/PoyrazTahan/simple_assistant/main/setup.sh | bash
```

This will:
- ✅ Install Python dependencies
- ✅ Clone the repository to `~/heltia/simple_assistant`
- ✅ Create `.env` file with placeholder
- ✅ Open the folder for you to add your API key

**After setup completes:**
1. **Add your OpenAI API key**: The setup will open the `.env` file in TextEdit
2. **Replace `OPENAI_API_KEY=put-your-key-here`** with your actual API key from [OpenAI](https://platform.openai.com/api-keys)
3. **Save and close** the .env file

### Manual Setup (If needed)

If the automatic setup doesn't work:

```bash
# 1. Create project directory
mkdir ~/heltia && cd ~/heltia

# 2. Clone repository
git clone https://github.com/PoyrazTahan/simple_assistant.git
cd simple_assistant

# 3. Install dependencies
pip install openai python-dotenv

# 4. Create environment file
echo "OPENAI_API_KEY=put-your-key-here" > .env
open .env  # Opens in TextEdit - add your actual API key
```

### Running the Application

```bash
# Navigate to the project (if not already there)
cd ~/heltia/simple_assistant

# Interactive mode
python app.py

# Debug mode (shows system commands and stage transitions)
python app.py --debug

# Full prompt mode (shows complete prompts sent to LLM)
python app.py --full-prompt

# Dual language mode (English + Turkish responses)
python app.py --language

# Use different model (default: gpt-4o-mini)
python app.py --model=gpt-4o

# Combined modes
python app.py --language --model=gpt-4o --debug
```

### Available Command Line Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--debug` | Shows system commands, data updates, and debug information | `python app.py --debug` |
| `--language` | Enable dual language mode (English 🇺🇸 + Turkish 🇹🇷) | `python app.py --language` |
| `--model=MODEL` | Specify OpenAI model (default: gpt-4o-mini) | `python app.py --model=gpt-4o` |
| `--full-prompt` | Display complete prompts sent to the AI | `python app.py --full-prompt` |

### User Interface Features

**Exiting the Application:**
- Type `quit` (case-insensitive) at any input prompt to exit
- Works in both free-form conversation and widget selection
- Examples: `quit`, `QUIT`, `Quit` all work

**AI Thinking Animation:**
- Shows "🤖 AI is thinking..." with animated dots while processing
- Automatically clears when response is ready

**Widget Interface:**
- Interactive selection menus for specific data fields  
- Shows numbered options in a bordered box
- Type `quit` during widget selection to exit

**Language Mode Features:**
- Dual language responses with flag emojis (🇺🇸/🇹🇷)
- Natural Turkish composition (not translation)
- Both languages displayed for user messages and recommendations

### Testing

Test the conversation flow:

1. Start the application: `python app.py`
2. Follow the conversation prompts
3. Use widget interfaces when they appear (numbered selections)
4. Type `quit` at any time to exit
5. The assistant will collect health data and provide recommendations

**Testing Different Modes:**
```bash
# Test with debug information
python app.py --debug

# Test dual language mode
python app.py --language

# Test with different AI model
python app.py --model=gpt-4o

# Test with full prompt visibility
python app.py --full-prompt --debug
```

**Expected UI Elements:**
- 🤖 AI thinking animation during processing
- 🎛️ Widget selection boxes for certain fields
- 📋 Recommendations display after conversation
- 🇺🇸/🇹🇷 Flag emojis in language mode

**Automated Test Suite:**
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
simple_assistant/
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
