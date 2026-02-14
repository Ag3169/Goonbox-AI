# AI Chatroom (Pure Python Desktop App)

Desktop chat + Python & Web IDE built with `tkinter`.

## Quick Start

👉 **[Read documentation.md](documentation.md)** for complete feature guide, examples, and all documentation in one place.

---

## Installation

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

---

## Main Features

✅ **Chatroom Mode** - Multi-turn conversations with AI  
✅ **IDE Mode** - Code editor with Python and Web support  
✅ **IDE Agent** - AI that can read, write, and create files  
✅ **Delete Chats** - Right-click any chat to delete  
✅ **Multi-Provider** - Groq, OpenAI, Anthropic, Google Gemini, xAI  

---

## Configuration

### Settings
- Click **Settings** to add API keys for providers
- Set default provider and model
- Auto-saved to `~/.ai_chatroom_settings.json`

### Environment Variables (Optional)
```bash
export GROQ_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export LLM_PROVIDER="groq"
```

---

## Key Capabilities

### Chat with AI
- Multiple conversation threads
- Multiple AI providers (5 supported)
- Token count and response time tracking
- Auto-persisted conversations

### Code with AI
- Full Python and Web IDE
- File explorer and project management
- Code syntax highlighting
- Console output

### Agent File I/O
The IDE agent can automatically:
- **Read** code files for analysis
- **Create** new Python/HTML/CSS/JS files
- **Write** updates to existing files
- All operations safely sandboxed to project folder

### Delete Chats
- Right-click any chat to delete
- Instant removal
- Works in both Chatroom and IDE modes

---

## File Locations

- **Settings**: `~/.ai_chatroom_settings.json`
- **Conversations**: `~/.ai_chatroom_conversations.json`

---

## Optional Environment Variables

- `LLM_PROVIDER` - Default provider (default: `groq`)
- `GROQ_API_KEY`, `OPENAI_API_KEY`, etc. - API keys
- `IDE_RUN_TIMEOUT` - Code execution timeout in seconds (default: empty - no timeout)

---

## Learn More

- **documentation.md** - Complete documentation with all features, guides, and examples
- **main.py** - Main application code (5600+ lines)
- **.env.example** - Environment setup template

---

## Features Explained

### 1. Chatroom Mode
Chat with AI across multiple conversation threads. Switch between providers and models anytime.

### 2. IDE Mode  
Edit code with syntax highlighting, run Python, preview HTML/CSS/JS. Agent assists with coding.

### 3. IDE Agent
Tell the agent what you want to build. It creates files, writes code, reads and analyzes code.

### 4. Delete Chats
Keep your chat history organized by deleting old conversations. Just right-click and delete.

---

## Support

For complete feature details, usage examples, keyboard shortcuts, API reference, troubleshooting, and all other documentation, see **documentation.md** in the project root.
```
I'll create two files for you:

```agent
{
  "action": "create",
  "path": "fibonacci.py",
  "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n"
}
```

```agent
{
  "action": "create",
  "path": "test_fibonacci.py",
  "content": "from fibonacci import fibonacci\n\ndef test_fib():\n    assert fibonacci(5) == 5\n    assert fibonacci(10) == 55\n\nif __name__ == '__main__':\n    test_fib()\n    print('All tests passed!')\n"
}
```

Done! I've created both files in your project.
```

**Result:** 
- `fibonacci.py` is created in the project root
- `test_fibonacci.py` is created in the project root
- Agent output panel shows: `[action=create] written` for each file
- Project file list refreshes automatically

### Safety Features

- ✅ All paths are validated to stay within the open project folder
- ✅ File writes are **atomic** (write to temp file, then rename) to prevent corruption
- ✅ UTF-8 encoding with fallback for binary detection
- ✅ Parent directories are created automatically if needed
- ✅ Existing files require explicit `"overwrite": true` to prevent accidental overwrites
- ✅ File list refreshes automatically after writes

### Agent Output Panel

When the agent executes commands, the **OUTPUT** panel shows:
- `[Agent commands detected]` — if JSON commands were found
- `[action=read] read` — successful file read
- `[action=write] written` — successful file write  
- `[action=write] file exists and overwrite not allowed` — write prevented
- File content preview (first 2000 chars) for read operations
- Error messages for invalid paths or I/O failures

### Tips & Best Practices

1. **Include context:** Check "Current file" and "Console" in the agent sidebar to give the agent more context about what you're working on.

2. **Multi-file edits:** The agent can create or modify multiple files in one response by including multiple JSON command blocks.

3. **Iterative development:** Use the agent to suggest refactorings, create test files, and add new modules—all atomically.

4. **Check the output:** Always review the agent output panel to see which files were created/modified and any errors.

5. **Collaborate:** If the agent doesn't get it right, refine your prompt and run the agent again. It can read files it created and update them.

