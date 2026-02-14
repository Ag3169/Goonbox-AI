# AI Chatroom - Complete Documentation

**Last Updated**: February 14, 2026  
**Version**: Beta  
**Status**: Still Buggy ✅

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Main Features](#main-features)
4. [Configuration](#configuration)
5. [Chat Mode Guide](#chat-mode-guide)
6. [IDE Mode Guide](#ide-mode-guide)
7. [IDE Agent Features](#ide-agent-features)
8. [New Features (Session 1)](#new-features-session-1)
9. [New Features (Session 2)](#new-features-session-2)
10. [New Features (Session 3)](#new-features-session-3---advanced-features)
11. [Keyboard Shortcuts](#keyboard-shortcuts)
12. [Troubleshooting](#troubleshooting)
13. [API Reference](#api-reference)
14. [File Locations](#file-locations)

---

## Quick Start

### 30-Second Setup

```bash
python main.py
```

That's it! The app launches and is ready to use.

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## Main Features

✅ **Chatroom Mode** - Multi-turn conversations with AI  
✅ **IDE Mode** - Code editor with Python and Web support  
✅ **IDE Agent** - AI that can read, write, and create files  
✅ **Multi-Provider** - Groq, OpenAI, Anthropic, Google Gemini, xAI  
✅ **Chat Management** - Create, delete, rename conversations  
✅ **Package Manager** - Install Python packages from PyPI  
✅ **Export & Search** - Save conversations and find messages  
✅ **Keyboard Shortcuts** - Quick reference guide  
✅ **Chat Statistics** - Get insights into chat usage  
✅ **Message Bookmarks** - Save and organize important messages  
✅ **Chat Backup/Restore** - Backup and recover conversations  
✅ **Code Snippets** - Manage and organize code snippets  
✅ **Session Manager** - Auto-save app state and settings  
✅ **Usage Analytics** - Track and analyze application usage  
✅ **Conversation Templates** - Pre-built conversation starters  
✅ **Message Reactions** - React and rate messages  
✅ **Code Execution History** - Track executions and code diffs  
✅ **Conversation Tags** - Tag and categorize conversations  
✅ **Model Comparison** - Compare and analyze model responses  
✅ **Chat Merging** - Merge and combine conversations  
✅ **Advanced Search** - Search with multiple filters  
✅ **Conversation Forking** - Create alternate conversation paths  
✅ **Token & Cost Tracking** - Monitor API usage and costs  
✅ **Auto-complete** - Smart suggestions and auto-complete  

---

## Configuration

### Initial Setup

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Add API Keys** (Click Settings)
   - Groq, OpenAI, Anthropic, Google Gemini, or xAI
   - Keys auto-saved to `~/.ai_chatroom_settings.json`

3. **Select Provider & Model**
   - Choose your default provider
   - Select a model from the dropdown
   - Changes saved automatically

### Environment Variables (Optional)

```bash
# Set default provider
export LLM_PROVIDER="groq"  # default provider

# Add API keys
export GROQ_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export XAI_API_KEY="your-key"

# Optional settings
export IDE_RUN_TIMEOUT=""  # code execution timeout in seconds (empty means no timeout)
export AI_CHATROOM_SETTINGS_PATH="~/.ai_chatroom_settings.json"
export AI_CHATROOM_CONVERSATIONS_PATH="~/.ai_chatroom_conversations.json"
```

---

## Chat Mode Guide

### Starting a Chat

1. Click **"Chatroom Mode"** button (top left)
2. Select a chat from the sidebar or create a new one
3. Type your message in the input box
4. Press **Enter** or click **Send**

### Chat Features

- **Multiple Conversations** - Unlimited chats, each with own history
- **Provider Selection** - Switch providers anytime
- **Model Selection** - Choose from available models
- **Refresh Models** - Get latest models from provider
- **Message History** - Every message saved automatically

### Chat Management

**Create New Chat**
- Click **"+ New"** button in Chats sidebar

**Rename Chat**
- Right-click any chat
- Select **"Rename"**
- Enter new name and press Enter

**Delete Chat**
- Right-click any chat
- Select **"Delete"**
- Chat removed permanently

---

## IDE Mode Guide

### Switching to IDE Mode

1. Click **"IDE Mode"** button (top left)
2. IDE view appears with editor, console, and agent panel

### IDE Components

**Python vs Web Mode**
- **Python**: Edit `.py` files and run Python code
- **Web**: Edit HTML/CSS/JS and preview in browser

**Editor Features**
- Syntax highlighting for Python, HTML, CSS, JavaScript
- Line numbers
- Auto-save on Ctrl+S
- Tab showing current file

**Console/Terminal**
- Real-time output from code execution
- Error messages displayed
- Clear button to reset output

**Agent Panel (Right Sidebar)**
- AI coding assistant
- Chat history with agent
- Can analyze code and generate files

### IDE Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save current file |
| Ctrl+R | Run code |
| Click "Run" | Execute code |
| Click "Stop" | Stop running code |
| Right-click file | File options |

---

## IDE Agent Features

### What the Agent Can Do

The agent can automatically:
- **Read** code files for analysis
- **Create** new Python/HTML/CSS/JS files
- **Write** updates to existing files
- **Execute** code and show results

### How to Use the Agent

1. **In IDE Mode**, describe what you want:
   - "Create a Python function that..."
   - "Fix this code..."
   - "Add a button to this HTML..."

2. **Agent responds** with:
   - Explanations
   - Generated code
   - Modified files
   - Execution results

3. **Files are created** in your project folder

### Agent Capabilities

- ✅ Analyze existing code
- ✅ Generate new code files
- ✅ Modify existing files
- ✅ Run Python code
- ✅ Debug issues
- ✅ Explain code
- ✅ Suggest improvements

### File I/O Safety

- All operations sandboxed to project folder
- No access outside project directory
- Atomic writes prevent corruption
- Auto-saved to disk

---

## New Features (Session 1)

### 1. Package Installer

**Purpose**: Install Python packages from PyPI without leaving the app

**How to Use**:
1. Switch to IDE Mode
2. Click **"Packages"** button (top right toolbar)
3. Enter package names (comma or space-separated)
4. Choose installation options (upgrade, user-only, skip-deps)
5. Click **"Install Packages"**
6. Watch real-time installation output

**Features**:
- Install multiple packages at once
- Upgrade existing packages option
- User-only installation option
- Skip dependencies option
- Real-time installation feedback

**File**: `package_installer.py`

### 2. Chat Rename (Regular Chats)

**Purpose**: Organize conversations by renaming them

**How to Use**:
1. In Chatroom Mode
2. Right-click on any chat
3. Select **"Rename"**
4. Type new name
5. Press Enter to confirm (or Escape to cancel)

**Features**:
- Dialog with input field
- Text pre-selected for easy replacement
- Auto-saves to disk
- Persists across application restart

**Keyboard Shortcuts**:
- **Enter** - Confirm rename
- **Escape** - Cancel rename

### 3. Agent Chat Rename

**Purpose**: Rename IDE agent conversations

**How to Use**:
1. In IDE Mode
2. Right-click on agent chat in right panel
3. Select **"Rename"**
4. Type new name
5. Press Enter to confirm

**Features**:
- Same as regular chat rename
- For agent conversations only
- Auto-saves and persists

---

## New Features (Session 2)

### 4. Export Chat Conversations

**Purpose**: Save conversations in multiple formats for sharing and archiving

**How to Use**:
1. In Chatroom Mode, select a chat
2. Click **"Export"** button (top right toolbar)
3. Choose format: Markdown (.md) | JSON (.json) | Text (.txt)
4. Click **"Export"**
5. Choose save location
6. File is saved with all messages

**Supported Formats**:

**Markdown (.md)**
- Best for: Sharing, documentation, readability
- Format: Readable text with headers and separators
- Use: Share on platforms that support Markdown

**JSON (.json)**
- Best for: Data processing, integration
- Format: Structured JSON with all message data
- Use: Process with scripts, import to other tools

**Plain Text (.txt)**
- Best for: Universal compatibility, simplicity
- Format: Simple text format
- Use: Open anywhere, minimal formatting

**File**: `chat_exporter.py`

### 5. Search Conversations

**Purpose**: Quickly find messages across all chats

**How to Use**:
1. Click **"Search"** button (top right toolbar)
2. Type your search query
3. Press Enter or click **"Search"**
4. Results show which chats contain the query
5. Shows number of matches per chat

**Features**:
- Search across all conversations
- Case-insensitive search
- Real-time results display
- Shows match count per chat
- Context preview available

**Search Tips**:
- Leave blank to see search box
- Use exact phrases for specific matches
- Search is case-insensitive
- Works across all active chats

**File**: `chat_searcher.py`

### 6. Keyboard Shortcuts Help

**Purpose**: Quick reference for all application shortcuts

**How to Use**:
1. Click **"?"** button (top right toolbar, next to Settings)
2. Window opens showing all shortcuts
3. Organized by category (Global, Chat, IDE, Management, etc.)
4. Scroll to browse
5. Close when done

**Shortcut Categories**:

**Global**:
- **Ctrl+S** - Save current file (IDE Mode only)
- **Escape** - Cancel dialogs / Close panels

**Chat Mode**:
- **Enter** - Send message
- **Shift+Enter** - New line in message
- **Ctrl+L** - Clear chat display

**IDE Mode**:
- **Ctrl+S** - Save current file
- **Ctrl+R** - Run code
- **Ctrl+Shift+F** - Format code

**Chat Management**:
- **Right-Click** - Open chat context menu
- **Delete (menu)** - Delete chat
- **Rename (menu)** - Rename chat

**Rename Dialog**:
- **Enter** - Confirm rename
- **Escape** - Cancel rename

**File**: `shortcuts_help.py`

### 7. Chat Statistics

**Purpose**: Get insights into your chat usage and message patterns

**Statistics Available**:
- Total messages in a chat
- User vs Assistant message breakdown
- Total characters across all messages
- Average message length
- Longest message size
- Chat size in MB
- Overall aggregate statistics

**How to Access** (via Python API):

```python
from chat_stats import ChatStatistics

# Get stats for single chat
stats = ChatStatistics.get_chat_stats(chat)

# Get stats for all chats
all_stats = ChatStatistics.get_all_chats_stats(all_chats)

# Get chat size
size_mb = ChatStatistics.get_chat_size_mb(chat)

# Format for display
display = ChatStatistics.format_stats_display(stats)
```

**Use Cases**:
- Monitor chat growth
- Understand conversation patterns
- Identify most active chats
- Plan data management

**File**: `chat_stats.py`

### 8. UI Improvements

**Changes**:
- Reorganized top-right toolbar
- New buttons grouped logically
- Better spacing and organization
- Professional appearance

**New Toolbar Layout** (left to right):
```
[?] [Search] [Export] [Settings]
```

**Benefits**:
- Quick access to important features
- Consistent button placement
- Clear visual hierarchy
- Professional appearance

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save current file (IDE Mode only) |
| **Escape** | Cancel dialogs / Close panels |

### Chat Mode

| Shortcut | Action |
|----------|--------|
| **Enter** | Send message |
| **Shift+Enter** | New line in message |
| **Ctrl+L** | Clear chat display |

### IDE Mode

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save current file |
| **Ctrl+R** | Run code |
| **Ctrl+Shift+F** | Format code |

### Chat Management

| Shortcut | Action |
|----------|--------|
| **Right-Click** | Open chat context menu |
| **Delete (menu)** | Delete chat |
| **Rename (menu)** | Rename chat |

### Rename Dialog

| Shortcut | Action |
|----------|--------|
| **Enter** | Confirm rename |
| **Escape** | Cancel rename |

---

## Troubleshooting

### Application Won't Start

**Problem**: `ModuleNotFoundError: No module named 'groq'`

**Solution**:
```bash
pip install -r requirements.txt
python main.py
```

**Problem**: `AttributeError: '_tkinter.tkapp' object has no attribute...`

**Solution**: Make sure you're running the latest version. Clear `__pycache__`:
```bash
rm -rf __pycache__
python main.py
```

### No Models Appear

**Problem**: Model dropdown is empty

**Solution**:
1. Check API key is correct in Settings
2. Click "Refresh Models" in the model dropdown
3. Make sure provider is selected
4. Check internet connection

### Code Won't Run

**Problem**: IDE code execution fails

**Solution**:
1. Check syntax of code
2. Ensure all imports are available
3. Try simpler code first
4. Check IDE output for error messages

### Chats Not Saving

**Problem**: Changes don't persist

**Solution**:
1. Check file permissions for `~/.ai_chatroom_conversations.json`
2. Ensure disk has space
3. Restart application
4. Check error messages in console

### Export Not Working

**Problem**: Export button doesn't work

**Solution**:
1. Make sure you're in Chatroom Mode
2. Select a chat before exporting
3. Check file system permissions
4. Try exporting to different location

### Search Not Finding Results

**Problem**: Search returns no results

**Solution**:
1. Try different search terms
2. Check spelling
3. Make sure chats have messages
4. Search is case-insensitive (try different cases)

### Packages Won't Install

**Problem**: Package installation fails

**Solution**:
1. Check internet connection
2. Verify package name spelling
3. Check package exists on PyPI
4. Try installing with `pip` directly:
   ```bash
   pip install package_name
   ```

---

## File Locations

### Configuration Files

- **Settings**: `~/.ai_chatroom_settings.json`
  - API keys
  - Default provider
  - Default model
  - User preferences

- **Conversations**: `~/.ai_chatroom_conversations.json`
  - All chat history
  - Agent chat history
  - Message content

### Project Files

- **Main Application**: `main.py` (5600+ lines)
- **Package Manager**: `package_installer.py`
- **Chat Export**: `chat_exporter.py`
- **Chat Search**: `chat_searcher.py`
- **Shortcuts Help**: `shortcuts_help.py`
- **Chat Statistics**: `chat_stats.py`

### Environment Files

- **.env** - Local environment variables
- **.env.example** - Template for environment variables
- **requirements.txt** - Python dependencies

---

## API Reference

### ChatStatistics API

```python
from chat_stats import ChatStatistics

# Get single chat statistics
stats = ChatStatistics.get_chat_stats(chat_dict)
# Returns: {
#   'total_messages': int,
#   'user_messages': int,
#   'assistant_messages': int,
#   'total_characters': int,
#   'average_message_length': int,
#   'longest_message': int,
#   'title': str,
# }

# Get all chats statistics
all_stats = ChatStatistics.get_all_chats_stats(chats_list)
# Returns: {
#   'total_chats': int,
#   'total_messages': int,
#   'total_characters': int,
#   'average_messages_per_chat': int,
#   'average_chars_per_message': int,
# }

# Get chat size in MB
size = ChatStatistics.get_chat_size_mb(chat_dict)
# Returns: float (size in MB)

# Format statistics for display
display_text = ChatStatistics.format_stats_display(stats_dict)
# Returns: formatted string for display
```

### ChatSearcher API

```python
from chat_searcher import ChatSearcher

# Search single chat
results = ChatSearcher.search_in_chat(chat_dict, query, case_sensitive=False)
# Returns: list of matching messages with context

# Search all chats
all_results = ChatSearcher.search_in_all_chats(chats_list, query, case_sensitive=False)
# Returns: dict with chat_id as key, results as value

# Regex search
regex_results = ChatSearcher.regex_search(chat_dict, pattern)
# Returns: list of regex matches
```

### Export API

```python
from chat_exporter import export_chat_to_markdown, export_chat_to_json, export_chat_to_txt
from pathlib import Path

# Export to Markdown
success = export_chat_to_markdown(chat_dict, Path('chat.md'))

# Export to JSON
success = export_chat_to_json(chat_dict, Path('chat.json'))

# Export to Text
success = export_chat_to_txt(chat_dict, Path('chat.txt'))

# Returns: bool (True if successful)
```

---

## Multi-Provider Support

### Supported Providers

1. **Groq** - Fast, open-source models
   - Models: Llama, Mixtral
   - Get key: https://console.groq.com

2. **OpenAI** - GPT models
   - Models: GPT-4, GPT-3.5-turbo
   - Get key: https://platform.openai.com

3. **Anthropic** - Claude models
   - Models: Claude 3 family
   - Get key: https://console.anthropic.com

4. **Google Gemini** - Google's models
   - Models: Gemini Pro, Gemini Ultra
   - Get key: https://makersuite.google.com

5. **xAI** - Grok models
   - Models: Grok-1
   - Get key: https://console.x.ai

### Switching Providers

1. Click **Settings**
2. Add API key for desired provider
3. Set as default provider
4. Click **Refresh Models**
5. Select model from dropdown

---

## Features Summary

### Session 1 Features
- ✅ Package Installer - Install PyPI packages
- ✅ Chat Rename - Organize conversations
- ✅ Agent Chat Rename - Rename AI agent chats
- ✅ Bug Fixes - Critical stability fixes

### Session 2 Features
- ✅ Export Chat - Save conversations (MD/JSON/TXT)
- ✅ Search - Find messages across chats
- ✅ Help System - Keyboard shortcuts reference
- ✅ Statistics API - Get chat insights
- ✅ UI Polish - Better organized toolbar

### Session 3 Features (NEW - 15 Total)
- ✅ Message Bookmarks - Save important messages
- ✅ Chat Backup/Restore - Backup and recover chats
- ✅ Code Snippet Manager - Organize code snippets
- ✅ Session Manager - Auto-save app state
- ✅ Usage Analytics - Track and analyze usage
- ✅ Conversation Templates - Pre-built conversation starters
- ✅ Message Reactions - React and rate messages
- ✅ Code Execution History - Track execution and diffs
- ✅ Conversation Tags - Tag and categorize conversations
- ✅ Model Comparison - Compare and analyze responses
- ✅ Chat Merging - Merge and split conversations (NEW Session 3 Continued)
- ✅ Advanced Search - Search with multiple filters (NEW Session 3 Continued)
- ✅ Conversation Forking - Create alternate conversation paths (NEW Session 3 Continued)
- ✅ Token & Cost Tracking - Monitor API usage and costs (NEW Session 3 Continued)
- ✅ Auto-complete - Smart suggestions and auto-complete (NEW Session 3 Continued)

### Core Features (Existing)
- ✅ Multi-provider AI support
- ✅ Chat mode with history
- ✅ IDE mode with editor
- ✅ IDE agent for coding
- ✅ Code syntax highlighting
- ✅ Project file management
- ✅ Web preview capability

---

## Tips & Tricks

### Productivity Tips

1. **Use Keyboard Shortcuts** - Press "?" to learn them
2. **Organize Chats** - Rename chats for easy finding
3. **Search First** - Find old solutions quickly
4. **Export Important** - Archive key discussions
5. **Switch Providers** - Use best model for task

### Best Practices

1. **API Keys in Settings** - Don't put in code
2. **Archive Chats** - Export before deleting
3. **Check Syntax** - Before running code
4. **Clear Output** - Between runs for clarity
5. **Save Files** - Use Ctrl+S frequently

### Performance Tips

1. **Close Unused Chats** - Delete old conversations
2. **Export Large Chats** - Remove them when archived
3. **Clear Output** - Reduces memory usage
4. **Restart App** - Clears temporary data

---

## Getting Help

### In-App Help
- Click **"?"** button for keyboard shortcuts
- Click **"Settings"** for API key help
- Hover over buttons for tooltips

### Documentation
- All documentation in this file
- Code comments for developers
- Docstrings in Python files

### Troubleshooting
- See Troubleshooting section above
- Check console for error messages
- Verify API keys and internet connection

---

## System Requirements

### Minimum Requirements
- Python 3.10+
- 500MB free disk space
- 2GB RAM
- Internet connection (for API calls)

### Supported Operating Systems
- Windows 10+
- macOS 10.13+
- Linux (Ubuntu 18.04+)

### Dependencies
- tkinter (built-in with Python)
- groq
- python-dotenv

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Version History

### Version 2.3 (February 14, 2026 - Session 3 Extended Part 2)
- ✅ Added Chat Merging & Combining
- ✅ Added Advanced Search with Filters
- ✅ Added Conversation Forking
- ✅ Added Token & Cost Tracking
- ✅ Added Auto-complete & Smart Suggestions
- ✅ Enhanced documentation with 5 new features

### Version 2.2 (February 14, 2026 - Session 3 Extended)
- ✅ Added Conversation Templates (6 built-in templates)
- ✅ Added Message Reactions & Quality Ratings
- ✅ Added Code Execution History & Diff Tracker
- ✅ Added Conversation Tags & Auto-tagging
- ✅ Added Model Comparison & Response Analysis
- ✅ Enhanced documentation with 5 new features

### Version 2.1 (February 14, 2026 - Session 3)
- ✅ Added Message Bookmarks feature
- ✅ Added Chat Backup & Restore functionality
- ✅ Added Code Snippet Manager
- ✅ Added Session Manager (auto-save)
- ✅ Added Usage Analytics & Reporting
- ✅ Enhanced documentation for all features

### Version 2.0 (February 14, 2026 - Session 2)
- ✅ Added Export Chat feature
- ✅ Added Search functionality
- ✅ Added Help/Shortcuts system
- ✅ Added Statistics API
- ✅ UI improvements and polish
- ✅ Package Installer (Session 1)
- ✅ Chat Rename features (Session 1)
- ✅ Bug fixes and stability

### Version 1.0 (Previous)
- Core AI chat application
- IDE mode with code editor
- Multi-provider support
- File management

---

## License

Check LICENSE file for license information.

---

## Contributing

To add features or improvements:

1. Modify relevant Python files
2. Follow existing code style
3. Add docstrings and comments
4. Test thoroughly
5. Update this documentation

---

## New Features (Session 3) - Advanced Features

### 9. Message Bookmarks & Favorites

**Purpose**: Bookmark important messages in conversations for quick reference

**How to Use** (via Python API):
```python
from message_bookmarks import MessageBookmark

# Bookmark a message
MessageBookmark.bookmark_message(chat, message_index, note="Important solution")

# Check if message is bookmarked
is_bookmarked = MessageBookmark.is_bookmarked(chat, message_index)

# Get all bookmarks
bookmarks = MessageBookmark.get_bookmarks(chat)

# Export bookmarks
bookmark_text = MessageBookmark.export_bookmarks(chat)

# Remove bookmark
MessageBookmark.unbookmark_message(chat, bookmark_id)
```

**Features**:
- Bookmark any message in a chat
- Add personal notes to bookmarks
- View all bookmarks in a chat
- Export bookmarked messages
- Persistent bookmarks saved with chat

**File**: `message_bookmarks.py`

**Use Cases**:
- Save helpful solutions
- Mark important decisions
- Track key insights
- Create reference points

---

### 10. Chat Backup & Restore

**Purpose**: Create backups of conversations and restore them when needed

**How to Use** (via Python API):
```python
from chat_backup import ChatBackupManager

# Create backup
ChatBackupManager.create_backup(chats, Path('backup.gz'))

# Restore from backup
success, restored_chats, message = ChatBackupManager.restore_backup(Path('backup.gz'))

# Get backup information
info = ChatBackupManager.get_backup_info(Path('backup.gz'))

# Auto backup with rotation (keeps last 5 backups)
ChatBackupManager.auto_backup(chats, Path('backups/'), max_backups=5)
```

**Features**:
- Compressed backups (gzip format)
- Automatic backup rotation
- Restore complete chat history
- View backup metadata
- Timestamp tracking
- Size-efficient storage

**File**: `chat_backup.py`

**Use Cases**:
- Regular backups of important conversations
- Disaster recovery
- Archiving old chats
- Version history management

---

### 11. Code Snippet Manager

**Purpose**: Save, organize, and manage reusable code snippets

**How to Use** (via Python API):
```python
from code_snippets import CodeSnippetManager

# Save a snippet
snippet = CodeSnippetManager.save_snippet(
    code="def hello(): print('Hello')",
    language="python",
    description="Simple greeting function",
    tags=["greeting", "example"]
)

# Search snippets
results = CodeSnippetManager.search_snippets(snippets, "greeting")

# Get snippets by language
python_snippets = CodeSnippetManager.get_snippets_by_language(snippets, "python")

# Get snippets by tag
examples = CodeSnippetManager.get_snippets_by_tag(snippets, "example")

# Get most used snippets
popular = CodeSnippetManager.get_popular_snippets(snippets, limit=10)

# Export snippets
markdown = CodeSnippetManager.export_snippets(snippets, format="markdown")
```

**Features**:
- Save code in multiple languages (Python, HTML, CSS, JavaScript)
- Tag-based organization
- Usage tracking
- Search functionality
- Export to Markdown or JSON
- Automatic snippet ID generation

**Supported Languages**:
- Python
- HTML
- CSS
- JavaScript

**File**: `code_snippets.py`

**Use Cases**:
- Reuse common patterns
- Build personal code library
- Share code templates
- Quick reference for common tasks

---

### 12. Session Manager (Auto-save & Snapshots)

**Purpose**: Auto-save application state and create recovery snapshots

**How to Use** (via Python API):
```python
from session_manager import SessionManager

# Save session state
state = {
    "current_mode": "chat",
    "current_chat_id": "chat-1",
    "provider": "groq",
    "model": "llama-3.1-8b-instant"
}
SessionManager.save_session_state(state, Path('session.json'))

# Load previous session
restored_state = SessionManager.load_session_state(Path('session.json'))

# Create full snapshot
SessionManager.create_session_snapshot(
    chats=chats,
    agent_chats=agent_chats,
    current_chat_id="chat-1",
    current_mode="chat",
    snapshot_path=Path('snapshot.gz')
)

# Get recent sessions
history = SessionManager.get_session_history(Path('sessions/'), limit=10)
```

**Features**:
- Auto-save application state
- Restore previous session on startup
- Full state snapshots (compressed)
- Session history tracking
- Mode and chat persistence
- Provider/model memory

**File**: `session_manager.py`

**Use Cases**:
- Resume work seamlessly
- Never lose your place
- Quick application restart
- State-based workflow continuity

---

### 13. Usage Analytics & Reporting

**Purpose**: Track usage patterns and generate analytics reports

**How to Use** (via Python API):
```python
from analytics import AnalyticsTracker

# Calculate session statistics
stats = AnalyticsTracker.calculate_session_stats(chats)
# Returns: total chats, messages, characters, average message length

# Get provider usage
provider_stats = AnalyticsTracker.get_provider_stats(chats)

# Track individual messages
metric = AnalyticsTracker.track_message(message, provider="groq", model="llama")

# Generate full usage report
report = AnalyticsTracker.generate_usage_report(chats, agent_chats)

# Get most used features
features = AnalyticsTracker.get_most_used_features()
```

**Metrics Tracked**:
- Messages per chat
- Character counts
- Provider usage
- Feature usage
- Session duration
- Model preferences

**Report Contents**:
- Session statistics
- Chat breakdown
- Message volumes
- Provider distribution
- Feature utilization

**File**: `analytics.py`

**Use Cases**:
- Understand usage patterns
- Identify frequently used providers
- Monitor activity
- Optimize workflow
- Track productivity

---

### 14. Conversation Templates

**Purpose**: Pre-built conversation starters and templates for common tasks

**How to Use** (via Python API):
```python
from conversation_templates import ConversationTemplate

# Get all templates
templates = ConversationTemplate.get_all_templates()

# Get specific template
template = ConversationTemplate.get_template("code_review")

# Get templates by category
dev_templates = ConversationTemplate.get_templates_by_category("Development")

# Get all categories
categories = ConversationTemplate.get_categories()

# Apply template with custom context
message = ConversationTemplate.apply_template(
    "debugging", 
    custom_context="Python TypeError in my function"
)
```

**Available Templates**:
- **Code Review** - Get feedback on code quality
- **Debugging Session** - Help debug code issues
- **Learn New Concept** - Learn programming concepts
- **System Architecture** - Design system architecture
- **Performance Optimization** - Optimize code performance
- **Web Design Help** - Design responsive web UIs

**Features**:
- Pre-built conversation starters
- Context hints and guidelines
- Category-based organization
- Custom context support
- Structured prompts

**File**: `conversation_templates.py`

**Use Cases**:
- Jump-start conversations
- Ensure consistent prompting
- Guide users toward better questions
- Template-based workflows
- Structured problem solving

---

### 15. Message Reactions & Quality Ratings

**Purpose**: Add reactions and quality ratings to messages

**How to Use** (via Python API):
```python
from message_reactions import MessageReactions

# Add reaction to message
MessageReactions.add_reaction(chat, message_index, "helpful")

# Remove reaction
MessageReactions.remove_reaction(chat, message_index, "helpful")

# Get all reactions for message
reactions = MessageReactions.get_reactions(chat, message_index)

# Rate message quality (1-5 stars)
MessageReactions.rate_message(chat, message_index, rating=5, comment="Very helpful!")

# Get message rating
rating = MessageReactions.get_rating(chat, message_index)

# Get average chat rating
avg = MessageReactions.get_average_rating(chat)

# Get helpful messages
helpful = MessageReactions.get_helpful_messages(chat, min_reactions=2)

# Get highly rated messages
high_quality = MessageReactions.get_highly_rated_messages(chat, min_rating=4.0)
```

**Available Reactions**:
- 👍 Helpful
- ❤️ Loved
- 🤔 Thinking
- 📚 Learning
- ⭐ Important
- 💾 Saved

**Features**:
- Multiple reaction types
- Quality ratings (1-5 stars)
- Reaction counting
- Rating comments
- Filter by reactions
- Find quality content

**File**: `message_reactions.py`

**Use Cases**:
- Mark helpful responses
- Quality assurance
- Find best responses
- Community feedback
- Content ranking

---

### 16. Code Execution History & Diff Viewer

**Purpose**: Track code executions and changes with diffs

**How to Use** (via Python API):
```python
from code_history import CodeExecutionHistory, CodeDiffTracker

# Record execution
execution = CodeExecutionHistory.record_execution(
    code="print('hello')",
    output="hello",
    language="python",
    execution_time=0.023
)

# Save to chat
CodeExecutionHistory.save_to_chat(chat, execution)

# Get execution history
history = CodeExecutionHistory.get_execution_history(chat, limit=10)

# Get successful executions
successful = CodeExecutionHistory.get_successful_executions(chat)

# Get failed executions
failed = CodeExecutionHistory.get_failed_executions(chat)

# Record code change
change = CodeDiffTracker.record_code_change(
    file_path="app.py",
    old_code="def hello(): pass",
    new_code="def hello(): print('hi')",
    description="Added greeting message"
)

# Get code changes
changes = CodeDiffTracker.get_code_changes(chat, file_path="app.py")

# Generate diff summary
summary = CodeDiffTracker.generate_diff_summary(chat, "app.py")
```

**Features**:
- Execution recording
- Success/error tracking
- Execution time tracking
- Code diff generation
- Change history
- Timeline view
- Automatic unified diff

**Tracked Metrics**:
- Code content
- Output/errors
- Execution time
- Language
- Status (success/error)
- Lines added/removed
- Change descriptions

**File**: `code_history.py`

**Use Cases**:
- Debug code issues
- Track code evolution
- Compare versions
- Performance tracking
- Execution replay
- Change documentation

---

### 17. Conversation Tags & Categories

**Purpose**: Tag and categorize conversations for organization

**How to Use** (via Python API):
```python
from conversation_tags import ConversationTagger

# Add tag to chat
ConversationTagger.add_tag(chat, "urgent")

# Remove tag
ConversationTagger.remove_tag(chat, "solved")

# Get all tags
tags = ConversationTagger.get_tags(chat)

# Check if has tag
is_urgent = ConversationTagger.has_tag(chat, "urgent")

# Set category
ConversationTagger.set_category(chat, "Development")

# Get category
category = ConversationTagger.get_category(chat)

# Filter by tag
urgent_chats = ConversationTagger.filter_by_tag(chats, "urgent")

# Filter by category
dev_chats = ConversationTagger.filter_by_category(chats, "Development")

# Get tag statistics
stats = ConversationTagger.get_tag_statistics(chats)

# Auto-detect tags
suggested = ConversationTagger.auto_tag_by_content(chat)
```

**Built-in Tags**:
- 🔴 urgent - Urgent issues
- ⭐ important - Important discussions
- ✓ solved - Resolved issues
- 🚫 blocked - Blocked progress
- 👀 review - Needs review
- 📚 documentation - Documentation
- 🐛 bug - Bug report
- ✨ feature - Feature request
- ❓ question - Question
- 💬 discussion - Discussion

**Categories**:
- Development
- Learning
- Bug Fix
- Discussion
- Documentation

**Features**:
- Multi-tag support
- Primary category
- Tag statistics
- Auto-tagging
- Filtering
- Tag suggestions
- Color-coded tags

**File**: `conversation_tags.py`

**Use Cases**:
- Organize conversations
- Find related discussions
- Prioritize work
- Track issue status
- Content organization
- Quick navigation

---

### 18. Model Comparison & Response Analysis

**Purpose**: Compare models and analyze response quality

**How to Use** (via Python API):
```python
from response_analysis import ResponseAnalyzer, ResponseMetadataTracker

# Analyze response
analysis = ResponseAnalyzer.analyze_response(message, "llama-3.1-8b", "groq")

# Record analysis
ResponseAnalyzer.record_response(chat, analysis)

# Compare responses from different models
comparison = ResponseAnalyzer.compare_responses(chat, question_index=0)

# Get model performance stats
performance = ResponseAnalyzer.get_model_performance(chat)

# Find best responding model
best_model = ResponseAnalyzer.get_best_responding_model(chat, metric="length")

# Record response time
ResponseMetadataTracker.record_response_time(message, 245.5)

# Get average response time
avg_time = ResponseMetadataTracker.get_average_response_time(chat)

# Get fastest/slowest responses
fastest = ResponseMetadataTracker.get_fastest_response(chat)
slowest = ResponseMetadataTracker.get_slowest_response(chat)
```

**Analysis Metrics**:
- Response length
- Word count
- Code presence
- Links/formatting
- Token estimation
- Response time

**Performance Metrics**:
- Average response length
- Average word count
- Response count
- Response time
- Model comparison
- Quality metrics

**Files**: `response_analysis.py`

**Use Cases**:
- Compare model quality
- Track performance
- Optimize model selection
- Response time analysis
- Quality metrics
- A/B testing
- Model benchmarking

---

### 19. Chat Merging & Combining

**Purpose**: Merge multiple conversations into one or split a single conversation

**How to Use** (via Python API):
```python
from chat_merger import ChatMerger

# Merge multiple chats into a target chat
ChatMerger.merge_chats(source_chats=[chat1, chat2], target_chat=chat3)

# Split a chat at specific message
first, second = ChatMerger.split_chat(chat, split_index=10)

# Combine parallel chats (interleaved or sequential)
combined = ChatMerger.combine_parallel_chats(chats, interleave=True)

# Get merge history
history = ChatMerger.get_merge_history(chat)
```

**Features**:
- Merge multiple chats with separators
- Split conversations at any point
- Interleave messages from parallel chats
- Track merge operations
- Preserve original chat references

**File**: `chat_merger.py`

**Use Cases**:
- Combine related discussions
- Create comprehensive guides
- Consolidate chat threads
- Compare parallel conversations
- Organize fragmented discussions

---

### 20. Advanced Search with Filters

**Purpose**: Powerful search with multiple filter options

**How to Use** (via Python API):
```python
from advanced_search import AdvancedSearcher

# Search with filters
results = AdvancedSearcher.search_with_filters(
    chats,
    query="function",
    filters={
        "role": "assistant",
        "has_code": True,
        "min_length": 100,
        "tags": ["python"]
    }
)

# Search by date range
by_date = AdvancedSearcher.search_by_date_range(chats, "2026-01-01", "2026-02-14")

# Find highly rated messages
rated = AdvancedSearcher.search_by_rating(chats, min_rating=4.0)

# Find messages with reactions
helpful = AdvancedSearcher.search_by_reaction(chats, "helpful", min_count=2)

# Smart search with special syntax
results = AdvancedSearcher.smart_search(chats, "#python")  # Tag search
results = AdvancedSearcher.smart_search(chats, "@4star")   # Rating search
```

**Available Filters**:
- role - Message role (user, assistant, system)
- language - Code language (python, javascript, etc)
- has_code - Messages with/without code blocks
- has_links - Messages with/without links
- min_length/max_length - Message length range
- tags - Filter by tags
- category - Chat category

**Special Search Syntax**:
- `#tag` - Search by tag
- `@4star` - Find 4+ star rated messages
- `@helpful` - Find messages with helpful reactions

**File**: `advanced_search.py`

**Use Cases**:
- Find code examples
- Search by quality rating
- Locate high-engagement messages
- Filter by language
- Tag-based organization

---

### 21. Conversation Forking

**Purpose**: Create alternate conversation paths and explore different directions

**How to Use** (via Python API):
```python
from conversation_forker import ConversationForker

# Fork at a specific message
fork = ConversationForker.fork_at_message(chat, fork_index=5, fork_title="Alternative approach")

# Fork and replace with new message
fork = ConversationForker.fork_with_new_message(
    chat, 
    fork_index=5,
    new_message={"role": "user", "content": "Try a different approach"},
    fork_title="Different solution path"
)

# Merge fork back
ConversationForker.merge_fork_back(original_chat, forked_chat, strategy="append")

# View fork tree
tree = ConversationForker.get_fork_tree(chat)

# Get differences
diff = ConversationForker.get_fork_differences(original, fork)
```

**Merge Strategies**:
- append - Append fork messages
- replace - Replace from fork point
- interleave - Interleave both conversations

**Features**:
- Create alternate conversation paths
- Explore different solutions
- Merge forks back into original
- Track fork history
- Compare branches

**File**: `conversation_forker.py`

**Use Cases**:
- Explore alternative approaches
- Test different solutions
- Create "what-if" scenarios
- Compare problem-solving strategies
- Maintain conversation branches

---

### 22. Token & Cost Tracking

**Purpose**: Track API token usage and estimated costs

**How to Use** (via Python API):
```python
from token_tracker import TokenTracker

# Track message usage
usage = TokenTracker.track_message(message, provider="groq", model="llama-3.1-8b")

# Get chat statistics
stats = TokenTracker.get_chat_token_stats(chat)
# Returns: total tokens, costs, usage count

# Get provider breakdown
provider_stats = TokenTracker.get_provider_costs(chats)

# Get total costs
total = TokenTracker.get_total_costs(chats)

# Generate cost report
report = TokenTracker.generate_cost_report(chats)

# Calculate cost for tokens
cost = TokenTracker.calculate_cost(1000, "openai", "gpt-4", "input")
```

**Tracked Metrics**:
- Input tokens
- Output tokens
- Estimated costs
- Provider breakdown
- Cost per chat
- Token usage trends

**Supported Providers**:
- Groq (often free)
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude models)
- Google (Gemini)

**File**: `token_tracker.py`

**Use Cases**:
- Monitor API spending
- Optimize provider selection
- Budget management
- Cost-per-chat analysis
- Provider comparison
- Cost reporting

---

### 23. Auto-complete & Smart Suggestions

**Purpose**: Intelligent suggestions and auto-complete from chat history

**How to Use** (via Python API):
```python
from auto_complete import AutoCompleter

# Get word suggestions
suggestions = AutoCompleter.get_suggestions(chats, prefix="def", limit=5)

# Get phrase suggestions
phrases = AutoCompleter.get_phrase_suggestions(chats, "def function", limit=5)

# Get context-based suggestions
next_suggestions = AutoCompleter.get_context_suggestions(chat, context_type="next")
follow_up = AutoCompleter.get_context_suggestions(chat, context_type="follow_up")
related = AutoCompleter.get_context_suggestions(chat, context_type="related")

# Get code completions
code_complete = AutoCompleter.get_code_completions(chats, language="python", prefix="def")

# Get suggested next actions
actions = AutoCompleter.suggest_next_action(chat)
```

**Features**:
- Word auto-completion
- Phrase suggestions
- Context-based recommendations
- Code snippet completion
- Follow-up suggestions
- Action recommendations

**Suggestion Types**:
- Word completions from history
- Common follow-up questions
- Related topics
- Code patterns
- Next logical steps

**File**: `auto_complete.py`

**Use Cases**:
- Speed up typing
- Get context-aware suggestions
- Find code patterns
- Discover related topics
- Next action guidance
- Improve workflow efficiency

---

## Contact & Support

For issues or questions:
1. Check Troubleshooting section
2. Review in-app Help ("?" button)
3. Check code comments
4. Review configuration in Settings

---

**Happy coding with AI Chatroom! 🚀**

For the latest information, check the main application or review the source code in `main.py` and related modules.
