import builtins
import html
import io
import json
import keyword
import os
import queue
import re
import subprocess
import sys
import tempfile
import time
import threading
import tkinter as tk
import tokenize
import webbrowser
from pathlib import Path
from tkinter import filedialog
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import ttk
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

from dotenv import load_dotenv
from groq import Groq
from package_installer import PackageInstallerWindow
from chat_exporter import export_chat_to_markdown, export_chat_to_json, export_chat_to_txt
from chat_searcher import ChatSearcher
from shortcuts_help import KeyboardShortcutsWindow
from chat_stats import ChatStatistics
from local_models import LocalModelManager, LMStudioClient, OllamaClient, LocalModelConfig

try:
    from tkinterweb import HtmlFrame
except ImportError:
    HtmlFrame = None

from advanced_search import AdvancedSearcher
from analytics import AnalyticsTracker
from auto_complete import AutoCompleter
from chat_backup import ChatBackupManager
from chat_merger import ChatMerger
from code_history import CodeExecutionHistory, CodeDiffTracker
from code_snippets import CodeSnippetManager
from conversation_forker import ConversationForker
from conversation_tags import ConversationTagger
from conversation_templates import ConversationTemplate
from message_bookmarks import MessageBookmark
from message_reactions import MessageReactions
from response_analysis import ResponseAnalyzer, ResponseMetadataTracker
from session_manager import SessionManager
from token_tracker import TokenTracker

load_dotenv()

GROQ_FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]
DEFAULT_PROVIDER = "groq"
MODEL_PLACEHOLDER = "(no models loaded)"
PROVIDERS = {
    "groq": {"label": "Groq", "env_key": "GROQ_API_KEY"},
    "openai": {"label": "OpenAI", "env_key": "OPENAI_API_KEY"},
    "anthropic": {"label": "Anthropic", "env_key": "ANTHROPIC_API_KEY"},
    "gemini": {"label": "Google Gemini", "env_key": "GEMINI_API_KEY"},
    "xai": {"label": "xAI", "env_key": "XAI_API_KEY"},
}
OPENAI_COMPATIBLE_BASE_URL = {
    "openai": "https://api.openai.com/v1",
    "xai": "https://api.x.ai/v1",
}

SETTINGS_PATH = Path(
    os.getenv(
        "AI_CHATROOM_SETTINGS_PATH",
        str(Path.home() / ".ai_goonbox_settings.json"),
    )
)
CONVERSATIONS_PATH = Path(
    os.getenv(
        "AI_CHATROOM_CONVERSATIONS_PATH",
        str(Path.home() / ".ai_goonbox_conversations.json"),
    )
)

IGNORED_DIRS = {".venv", ".git", "__pycache__", ".idea", ".pytest_cache"}

# ===== THEME DEFINITIONS =====
THEMES = {
    "Dark Mode": {
        "bg": "#1e1e1e",
        "panel": "#252526",
        "sidebar": "#2d2d30",
        "border": "#3e3e42",
        "text": "#d4d4d4",
        "muted": "#858585",
        "assistant_bubble": "#2d2d30",
        "user_bubble": "#3a3d41",
        "system_bubble": "#2a2d2e",
        "button": "#0e7490",
        "button_hover": "#0891b2",
        "entry_bg": "#1e1e1e",
        "list_bg": "#252526",
        "syntax_keyword": "#569cd6",
        "syntax_builtin": "#4ec9b0",
        "syntax_string": "#ce9178",
        "syntax_comment": "#6a9955",
        "syntax_number": "#b5cea8",
        "syntax_function": "#dcdcaa",
        "syntax_class": "#4ec9b0",
        "syntax_decorator": "#c586c0",
    },
    "Dark Blue": {
        "bg": "#090d14",
        "panel": "#0f1623",
        "sidebar": "#111b2b",
        "border": "#263245",
        "text": "#e8edf5",
        "muted": "#9aa9be",
        "assistant_bubble": "#131d2c",
        "user_bubble": "#18354a",
        "system_bubble": "#162334",
        "button": "#22b3a5",
        "button_hover": "#178779",
        "entry_bg": "#0f1726",
        "list_bg": "#0f1726",
        "syntax_keyword": "#78a9ff",
        "syntax_builtin": "#6cc8ff",
        "syntax_string": "#8ed68f",
        "syntax_comment": "#6c7787",
        "syntax_number": "#f5be7a",
        "syntax_function": "#ffd479",
        "syntax_class": "#c9a6ff",
        "syntax_decorator": "#ff8ab5",
    },
    "GitHub Dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "sidebar": "#21262d",
        "border": "#30363d",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "assistant_bubble": "#161b22",
        "user_bubble": "#21262d",
        "system_bubble": "#1c2128",
        "button": "#238636",
        "button_hover": "#2ea043",
        "entry_bg": "#0d1117",
        "list_bg": "#161b22",
        "syntax_keyword": "#ff7b72",
        "syntax_builtin": "#79c0ff",
        "syntax_string": "#a5d6ff",
        "syntax_comment": "#8b949e",
        "syntax_number": "#79c0ff",
        "syntax_function": "#d2a8ff",
        "syntax_class": "#7ee787",
        "syntax_decorator": "#ffa657",
    },
    "Dracula": {
        "bg": "#282a36",
        "panel": "#343746",
        "sidebar": "#44475a",
        "border": "#6272a4",
        "text": "#f8f8f2",
        "muted": "#6272a4",
        "assistant_bubble": "#343746",
        "user_bubble": "#44475a",
        "system_bubble": "#383a59",
        "button": "#50fa7b",
        "button_hover": "#5af78e",
        "entry_bg": "#282a36",
        "list_bg": "#343746",
        "syntax_keyword": "#ff79c6",
        "syntax_builtin": "#8be9fd",
        "syntax_string": "#f1fa8c",
        "syntax_comment": "#6272a4",
        "syntax_number": "#bd93f9",
        "syntax_function": "#50fa7b",
        "syntax_class": "#8be9fd",
        "syntax_decorator": "#ffb86c",
    },
    "Monokai": {
        "bg": "#272822",
        "panel": "#3e3d32",
        "sidebar": "#49483e",
        "border": "#75715e",
        "text": "#f8f8f2",
        "muted": "#75715e",
        "assistant_bubble": "#3e3d32",
        "user_bubble": "#49483e",
        "system_bubble": "#3c3b2f",
        "button": "#a6e22e",
        "button_hover": "#b8ef41",
        "entry_bg": "#272822",
        "list_bg": "#3e3d32",
        "syntax_keyword": "#f92672",
        "syntax_builtin": "#66d9ef",
        "syntax_string": "#e6db74",
        "syntax_comment": "#75715e",
        "syntax_number": "#ae81ff",
        "syntax_function": "#a6e22e",
        "syntax_class": "#66d9ef",
        "syntax_decorator": "#fd971f",
    },
}

# Current active theme (defaults to Dark Mode)
CURRENT_THEME = "Dark Mode"

# Active color scheme (loaded from THEMES based on CURRENT_THEME)
COLORS = THEMES.get(CURRENT_THEME, THEMES["Dark Mode"]).copy()

WELCOME_MESSAGE = "Welcome to AI-goonbox. Ask anything to get started."
AGENT_WELCOME_MESSAGE = "AI coding agent ready. Describe what you want to build."

IDE_PYTHON_TEMPLATE = """"""

IDE_WEB_TEMPLATE = """"""

PYTHON_AGENT_PROMPT = """You are an expert coding and debugging assistant specializing in Python and web development. Your role:

CAPABILITIES - PYTHON:
• Write clean, efficient, production-ready Python code
• Debug Python code and fix errors
• Explain code functionality and best practices
• Refactor code for better performance and readability
• Create unit tests and test cases
• Suggest improvements and optimizations

CAPABILITIES - WEB DEVELOPMENT:
• Write clean, responsive HTML/CSS/JavaScript code
• Debug web code and fix errors
• Explain DOM manipulation and events
• Optimize CSS for performance and accessibility
• Create interactive web components
• Debug CSS layout and styling issues

ACTIONS TO TAKE:
• WRITE code directly into the editor using fenced code blocks (```python, ```html, ```css, ```javascript)
• READ existing code to analyze and improve it
• CREATE new functions, classes, modules, or web components as needed
• FIX bugs by analyzing error messages and logic

OUTPUT FORMAT:
• Return code in appropriate fenced blocks - it will be loaded into the editor
• Include brief explanations before code blocks
• Show only the code to generate, not the entire file
• Keep code concise and focused on the task
• Use ```python for Python code, ```html for HTML, ```css for CSS, ```javascript for JS

DEBUGGING HELP:
• Ask for error messages or unexpected behavior
• Analyze stack traces and suggest fixes
• Add print statements, logging, or console statements for debugging
• Identify CSS layout issues and suggest fixes
• Check browser compatibility and accessibility
• Optimize performance and loading times

BEST PRACTICES:
• Follow PEP 8 for Python code
• Use semantic HTML for web development
• Write accessible code (a11y)
• Use modern ES6+ JavaScript
• Create responsive designs that work on all devices
• Keep security in mind (no inline scripts, proper escaping)

Example Python: User says "Create a function to sort a list"
You respond: "Here's an optimized sorting function using quicksort:"
Then: ```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

Example Web: User says "Create a dark mode toggle"
You respond: "Here's a working dark mode toggle with HTML, CSS, and JavaScript:"
Then: ```html
<button id="themeToggle">🌙 Dark Mode</button>
```
```css
body.dark-mode { background: #1a1a1a; color: #fff; }
```
```javascript
const toggle = document.getElementById('themeToggle');
toggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
});
```"""

WEB_AGENT_PROMPT = """You are an expert web development coding and debugging assistant. Your role:

CAPABILITIES:
• Write clean, responsive HTML/CSS/JavaScript code
• Debug web code and fix errors
• Explain DOM manipulation and events
• Optimize CSS for performance and accessibility
• Create interactive web components
• Debug CSS layout and styling issues

ACTIONS TO TAKE:
• WRITE code directly into the editor using fenced code blocks
• READ existing HTML/CSS/JS to analyze and improve
• CREATE responsive layouts and components
• FIX bugs in styling, logic, or interactions

OUTPUT FORMAT:
• Return code in appropriate fenced blocks (```html, ```css, ```javascript)
• Include brief explanations before code blocks
• Show complete, working code snippets
• Keep code modern and use ES6+ where appropriate

DEBUGGING HELP:
• Identify CSS layout issues and suggest fixes
• Debug JavaScript errors and logic problems
• Check browser compatibility
• Optimize performance and loading times
• Improve accessibility (a11y)

Example: User says "Create a dark mode toggle button"
You respond: "Here's a working dark mode toggle with CSS and JavaScript:"
Then: ```html
<button id="themeToggle">🌙 Dark Mode</button>
```
```css
body.dark-mode { background: #1a1a1a; color: #fff; }
```
```javascript
const toggle = document.getElementById('themeToggle');
toggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
});
```"""

WEB_JS_KEYWORDS = {
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "debugger",
    "default",
    "delete",
    "do",
    "else",
    "export",
    "extends",
    "false",
    "finally",
    "for",
    "function",
    "if",
    "import",
    "in",
    "instanceof",
    "let",
    "new",
    "null",
    "return",
    "super",
    "switch",
    "this",
    "throw",
    "true",
    "try",
    "typeof",
    "var",
    "void",
    "while",
    "with",
    "yield",
    "await",
    "async",
}

WEB_HTML_TAGS = {
    "a",
    "article",
    "aside",
    "body",
    "button",
    "canvas",
    "code",
    "div",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "html",
    "img",
    "input",
    "label",
    "li",
    "link",
    "main",
    "meta",
    "nav",
    "ol",
    "option",
    "p",
    "script",
    "section",
    "select",
    "span",
    "style",
    "table",
    "tbody",
    "td",
    "textarea",
    "th",
    "thead",
    "title",
    "tr",
    "ul",
}

WEB_HTML_ATTRIBUTES = {
    "alt",
    "aria-label",
    "class",
    "content",
    "data-",
    "href",
    "id",
    "lang",
    "name",
    "placeholder",
    "rel",
    "src",
    "style",
    "title",
    "type",
    "value",
}

WEB_CSS_PROPERTIES = {
    "align-items",
    "background",
    "background-color",
    "border",
    "border-radius",
    "box-shadow",
    "color",
    "display",
    "font-family",
    "font-size",
    "font-weight",
    "gap",
    "grid-template-columns",
    "height",
    "justify-content",
    "line-height",
    "margin",
    "max-width",
    "min-height",
    "opacity",
    "padding",
    "position",
    "transition",
    "transform",
    "width",
}

WEB_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
WEB_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
WEB_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
WEB_STRING_RE = re.compile(r"(\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*')")
WEB_NUMBER_RE = re.compile(r"\b(?:\d+(?:\.\d+)?|\.\d+)\b")
WEB_HTML_TAG_RE = re.compile(r"</?\s*([A-Za-z][\w:-]*)")
WEB_HTML_ATTR_RE = re.compile(r"\s([A-Za-z_:][\w:.-]*)\s*=")
WEB_CSS_PROP_RE = re.compile(r"\b([-\w]+)\s*:")
WEB_CSS_SELECTOR_RE = re.compile(r"(^|[}\n])\s*([^\n{}][^{]*)\{")
WEB_JS_KEYWORD_RE = re.compile(r"\b([A-Za-z_]\w*)\b")
WEB_JS_FUNCTION_RE = re.compile(r"\bfunction\s+([A-Za-z_]\w*)")
WEB_JS_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_]\w*)")

WEB_FILE_EXTENSIONS = {".html", ".htm", ".css", ".js", ".mjs", ".jsx", ".ts", ".tsx"}


class GroqChatroomApp(tk.Tk):
    def __init__(self) -> None:
        """Initialize app state, restore persisted data, and build the UI."""
        super().__init__()
        self.title("AI-goonbox")
        self.geometry("1300x820")
        self.minsize(980, 700)
        self.configure(bg=COLORS["bg"])

        self.project_root: Path | None = None
        self.settings_path = SETTINGS_PATH
        self.conversations_path = CONVERSATIONS_PATH
        self.settings = self._load_settings()

        # Feature modules initialization
        self.advanced_searcher = AdvancedSearcher()
        self.analytics_tracker = AnalyticsTracker()
        self.auto_completer = AutoCompleter()
        self.backup_manager = ChatBackupManager()
        self.chat_merger = ChatMerger()
        self.code_history = CodeExecutionHistory()
        self.code_diff_tracker = CodeDiffTracker()
        self.snippet_manager = CodeSnippetManager()
        self.conversation_forker = ConversationForker()
        self.conversation_tagger = ConversationTagger()
        self.conversation_template = ConversationTemplate()
        self.message_bookmark = MessageBookmark()
        self.message_reactions = MessageReactions()
        self.response_analyzer = ResponseAnalyzer()
        self.response_metadata_tracker = ResponseMetadataTracker()
        self.session_manager = SessionManager()
        self.token_tracker = TokenTracker()

        # Background threads post structured UI events here; only the Tk thread reads it.
        self.event_queue: queue.Queue[dict[str, object]] = queue.Queue()
        self.model_cache: dict[str, list[str]] = {
            "groq": list(GROQ_FALLBACK_MODELS),
        }
        # Provider/model comboboxes are initialized inside _build_chat_sidebar.
        self.chat_provider_combo: ttk.Combobox | None = None
        self.chat_model_combo: ttk.Combobox | None = None
        self.chat_provider_label_var: tk.StringVar | None = None

        # Chat send lock so users cannot queue overlapping requests into one thread.
        self.pending = False
        self.pending_chat_id: str | None = None

        # Lazily created "Thinking..." row and hover tooltip widgets.
        self.typing_row: tk.Frame | None = None
        self.typing_label: tk.Label | None = None
        self.typing_animation_id: str | None = None
        self.typing_tick = 1
        self.message_hover_tip: tk.Toplevel | None = None
        self.message_hover_label: tk.Label | None = None

        self.settings_window: tk.Toplevel | None = None

        # Normal chat threads shown in Chatroom mode.
        self.chat_counter = 0
        self.chats: list[dict[str, object]] = []
        self.current_chat_id: str | None = None
        self._suppress_chat_select = False

        # IDE agent threads shown in IDE mode.
        self.agent_chat_counter = 0
        self.agent_chats: list[dict[str, object]] = []
        self.current_agent_chat_id: str | None = None
        self._suppress_agent_select = False

        # IDE run state and editor file bookkeeping.
        self.ide_running = False
        self.ide_process: subprocess.Popen[str] | None = None
        self.ide_process_lock = threading.Lock()
        self.ide_current_file: Path | None = None
        self.ide_files: list[Path] = []
        self.ide_dirty = False
        self.ide_line_count = 0
        self.ide_syntax_job_id: str | None = None
        self.ide_autosave_job_id: str | None = None
        self.ide_preview_temp_path: Path | None = None
        self.ide_python_keywords = set(keyword.kwlist)
        self.ide_python_builtins = set(dir(builtins))
        self._ide_loading = False
        self.agent_running = False
        
        # Browser state for web IDE mode
        self.ide_browser: HtmlFrame | None = None
        self.ide_browser_panel: tk.Frame | None = None
        self.ide_browser_update_job_id: str | None = None

        default_provider = self._default_provider_from_settings()
        default_model = self._default_model_from_settings(default_provider)
        self.provider_var = tk.StringVar(value=default_provider)
        self.model_var = tk.StringVar(value=default_model)
        self.mode_var = tk.StringVar(value="chat")
        # Reasoning effort level (0-2, where 0 is minimal, 1 is standard, 2 is high effort)
        self.reasoning_effort_var = tk.IntVar(value=1)
        self.agent_reasoning_effort_var = tk.IntVar(value=1)
        self.ide_kind_var = tk.StringVar(value="python")
        self.status_var = tk.StringVar(value="Ready")
        self.ide_status_var = tk.StringVar(value="Idle")
        self.ide_file_var = tk.StringVar(value="No file selected")
        self.ide_tab_title_var = tk.StringVar(value="scratch.py")
        self.ide_cursor_var = tk.StringVar(value="Ln 1, Col 1")
        self.ide_runtime_var = tk.StringVar(
            value=f"Python {sys.version_info.major}.{sys.version_info.minor}"
        )
        self.project_label_var = tk.StringVar(value="")
        self.agent_status_var = tk.StringVar(value="Idle")
        self.agent_include_file_var = tk.BooleanVar(value=True)
        self.agent_include_console_var = tk.BooleanVar(value=True)
        self._update_project_label()

        self._load_conversations()
        self._build_ui()
        self._update_ide_panel_for_kind()
        self.provider_var.trace_add("write", self._on_provider_change)
        self.ide_kind_var.trace_add("write", self._on_ide_kind_change)
        self._apply_model_menu(default_provider, preferred_model=default_model)

        if not self.chats:
            self._create_chat(switch_to_chat=False)
        else:
            self._refresh_chat_list()
            self._render_current_chat()

        if not self.agent_chats:
            self._create_agent_chat()
        else:
            self._refresh_agent_chat_list()
            self._render_current_agent_chat()

        self._refresh_project_file_list()
        self.switch_mode("chat")
        self._refresh_models_async(
            default_provider,
            preferred_model=default_model,
            show_status=False,
        )
        self.after(120, self._process_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        """Handle app shutdown by stopping processes and persisting conversations."""
        if self.ide_syntax_job_id is not None:
            try:
                self.after_cancel(self.ide_syntax_job_id)
            except tk.TclError:
                pass
            self.ide_syntax_job_id = None
        if self.ide_autosave_job_id is not None:
            try:
                self.after_cancel(self.ide_autosave_job_id)
            except tk.TclError:
                pass
            self.ide_autosave_job_id = None
        if self.ide_browser_update_job_id is not None:
            try:
                self.after_cancel(self.ide_browser_update_job_id)
            except tk.TclError:
                pass
            self.ide_browser_update_job_id = None
        self._hide_message_hover()
        self.stop_ide_code()
        self._save_conversations()
        self.destroy()

    def _build_ui(self) -> None:
        """Build the main application layout and compose all mode panes."""
        app_font = tkfont.nametofont("TkDefaultFont")
        app_font.configure(size=11)
        self._configure_ttk_styles()

        shell = tk.Frame(
            self,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        shell.pack(fill="both", expand=True, padx=14, pady=14)

        top_bar = tk.Frame(
            shell,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        top_bar.pack(fill="x")

        top_left = tk.Frame(top_bar, bg=COLORS["panel"])
        top_left.pack(side="left", padx=14, pady=10)
        tk.Label(
            top_left,
            text="●",
            fg=COLORS["button"],
            bg=COLORS["panel"],
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")
        tk.Label(
            top_left,
            text=" AI-goonbox",
            fg=COLORS["text"],
            bg=COLORS["panel"],
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        top_center = tk.Frame(top_bar, bg=COLORS["panel"])
        top_center.pack(side="left", padx=10, pady=10)

        self.chat_mode_button = tk.Button(
            top_center,
            text="Chatroom Mode",
            command=lambda: self.switch_mode("chat"),
            bd=0,
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.chat_mode_button.pack(side="left", padx=(0, 8))

        self.ide_mode_button = tk.Button(
            top_center,
            text="IDE Mode",
            command=lambda: self.switch_mode("ide"),
            bd=0,
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.ide_mode_button.pack(side="left")

        top_right = tk.Frame(top_bar, bg=COLORS["panel"])
        top_right.pack(side="right", padx=14, pady=10)
        
        tk.Button(
            top_right,
            text="?",
            command=self.open_keyboard_shortcuts,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=8,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="right", padx=(0, 8))
        
        self.search_button = tk.Button(
            top_right,
            text="Search",
            command=self.open_search_dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.search_button.pack(side="right", padx=(0, 8))
        
        self.export_button = tk.Button(
            top_right,
            text="Export",
            command=self.open_export_dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.export_button.pack(side="right", padx=(0, 8))
        
        self.settings_button = tk.Button(
            top_right,
            text="Settings",
            command=self.open_settings_dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=12,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.settings_button.pack(side="right")

        body = tk.Frame(shell, bg=COLORS["panel"])
        body.pack(fill="both", expand=True)

        self.left_sidebar_stack = tk.Frame(
            body,
            width=300,
            bg=COLORS["sidebar"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.left_sidebar_stack.pack(side="left", fill="y")
        self.left_sidebar_stack.pack_propagate(False)

        self.right_view_stack = tk.Frame(body, bg=COLORS["panel"])
        self.right_view_stack.pack(side="left", fill="both", expand=True)

        self.chat_sidebar = tk.Frame(self.left_sidebar_stack, bg=COLORS["sidebar"])
        self.file_sidebar = tk.Frame(self.left_sidebar_stack, bg=COLORS["sidebar"])
        self.chat_sidebar.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.file_sidebar.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.chat_view = tk.Frame(self.right_view_stack, bg=COLORS["panel"])
        self.ide_view = tk.Frame(self.right_view_stack, bg=COLORS["panel"])
        self.chat_view.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.ide_view.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_chat_sidebar(self.chat_sidebar)
        self._build_file_sidebar(self.file_sidebar)
        self._build_chat_view(self.chat_view)
        self._build_ide_view(self.ide_view)
        self.bind_all("<Control-s>", self._handle_ctrl_s)

    def _configure_ttk_styles(self) -> None:
        """Configure ttk combobox styling so selectors remain stable in fullscreen."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Dark.TCombobox",
            fieldbackground=COLORS["entry_bg"],
            background=COLORS["entry_bg"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            padding=5,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", COLORS["entry_bg"])],
            selectbackground=[("readonly", COLORS["entry_bg"])],
            selectforeground=[("readonly", COLORS["text"])],
            foreground=[("readonly", COLORS["text"])],
            background=[("readonly", COLORS["entry_bg"])],
        )

    def _build_chat_sidebar(self, parent: tk.Frame) -> None:
        """Build the chat sidebar UI section."""
        header = tk.Frame(parent, bg=COLORS["sidebar"])
        header.pack(fill="x", padx=14, pady=(14, 10))
        tk.Label(
            header,
            text="Chats",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self.new_chat_button = tk.Button(
            header,
            text="+ New",
            command=self._create_chat,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.new_chat_button.pack(side="right")

        list_wrap = tk.Frame(parent, bg=COLORS["sidebar"])
        list_wrap.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        self.chat_listbox = tk.Listbox(
            list_wrap,
            bg=COLORS["list_bg"],
            fg=COLORS["text"],
            selectbackground=COLORS["button"],
            selectforeground="#03100f",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            borderwidth=0,
            activestyle="none",
            font=("Segoe UI", 10),
        )
        self.chat_listbox.pack(side="left", fill="both", expand=True)
        self.chat_listbox.bind("<<ListboxSelect>>", self._on_chat_selected)
        self.chat_listbox.bind("<Button-3>", self._on_chat_right_click)

        chat_scroll = tk.Scrollbar(
            list_wrap,
            orient="vertical",
            command=self.chat_listbox.yview,
            troughcolor=COLORS["sidebar"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        chat_scroll.pack(side="right", fill="y")
        self.chat_listbox.configure(yscrollcommand=chat_scroll.set)

        tip = tk.Label(
            parent,
            text="Each chat keeps its own history.",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            justify="left",
            wraplength=250,
            font=("Segoe UI", 9),
        )
        tip.pack(anchor="w", padx=14, pady=(0, 14))

    def _build_file_sidebar(self, parent: tk.Frame) -> None:
        """Build the file sidebar UI section."""
        shell = tk.Frame(parent, bg=COLORS["sidebar"])
        shell.pack(fill="both", expand=True)

        activity_bar = tk.Frame(shell, width=44, bg="#0c1422")
        activity_bar.pack(side="left", fill="y")
        activity_bar.pack_propagate(False)
        for idx, label in enumerate(("EX", "SR", "SCM", "RUN", "EXT")):
            tk.Button(
                activity_bar,
                text=label,
                bg="#0c1422",
                fg=COLORS["muted"] if idx else COLORS["text"],
                activebackground="#131f33",
                activeforeground=COLORS["text"],
                bd=0,
                padx=2,
                pady=8,
                highlightthickness=0,
                font=("Consolas", 8, "bold"),
                cursor="hand2",
            ).pack(fill="x", padx=4, pady=(8 if idx == 0 else 2, 0))

        explorer = tk.Frame(
            shell,
            bg=COLORS["sidebar"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        explorer.pack(side="left", fill="both", expand=True)

        header = tk.Frame(explorer, bg=COLORS["sidebar"])
        header.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(
            header,
            text="EXPLORER",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        tk.Label(
            explorer,
            text="WORKSPACE",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        tk.Label(
            explorer,
            textvariable=self.project_label_var,
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            justify="left",
            wraplength=220,
            font=("Consolas", 8),
        ).pack(anchor="w", padx=12, pady=(0, 8))

        actions = tk.Frame(explorer, bg=COLORS["sidebar"])
        actions.pack(fill="x", padx=12, pady=(0, 8))

        open_folder_btn = tk.Button(
            actions,
            text="Open",
            command=self._choose_project_folder,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=8,
            pady=4,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        open_folder_btn.pack(side="left")

        open_file_btn = tk.Button(
            actions,
            text="File",
            command=self._choose_file_from_disk,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=8,
            pady=4,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        open_file_btn.pack(side="left", padx=(6, 0))

        save_btn = tk.Button(
            actions,
            text="Save",
            command=self.save_current_file,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=8,
            pady=4,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        save_btn.pack(side="left", padx=(6, 0))

        refresh_btn = tk.Button(
            actions,
            text="Refresh",
            command=self._refresh_project_file_list,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=8,
            pady=4,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        refresh_btn.pack(side="left", padx=(6, 0))

        tk.Label(
            explorer,
            text="FILES",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        list_wrap = tk.Frame(explorer, bg=COLORS["sidebar"])
        list_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.file_listbox = tk.Listbox(
            list_wrap,
            bg=COLORS["list_bg"],
            fg=COLORS["text"],
            selectbackground=COLORS["button"],
            selectforeground="#03100f",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            borderwidth=0,
            activestyle="none",
            font=("Consolas", 9),
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self._on_file_selected)

        file_scroll = tk.Scrollbar(
            list_wrap,
            orient="vertical",
            command=self.file_listbox.yview,
            troughcolor=COLORS["sidebar"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        file_scroll.pack(side="right", fill="y")
        self.file_listbox.configure(yscrollcommand=file_scroll.set)

        tip = tk.Label(
            explorer,
            text="Open any file to start editing.",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            justify="left",
            wraplength=220,
            font=("Segoe UI", 8),
        )
        tip.pack(anchor="w", padx=12, pady=(0, 10))

    def _build_chat_view(self, parent: tk.Frame) -> None:
        """Build the chat view UI section."""
        header = tk.Frame(
            parent,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        header.pack(fill="x")

        left = tk.Frame(header, bg=COLORS["panel"])
        left.pack(side="left", padx=16, pady=12)
        tk.Label(
            left,
            text="Assistant Chatroom",
            fg=COLORS["text"],
            bg=COLORS["panel"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            textvariable=self.status_var,
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        model_wrap = tk.Frame(header, bg=COLORS["panel"])
        model_wrap.pack(side="right", padx=16, pady=12)
        tk.Label(
            model_wrap,
            text="Provider",
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            font=("Segoe UI", 9),
        ).pack(anchor="e")
        provider_choices = [PROVIDERS[key]["label"] for key in PROVIDERS]
        self.chat_provider_label_var = tk.StringVar(value=PROVIDERS[self.provider_var.get()]["label"])
        provider_combo = ttk.Combobox(
            model_wrap,
            textvariable=self.chat_provider_label_var,
            values=provider_choices,
            state="readonly",
            width=22,
            style="Dark.TCombobox",
        )
        provider_combo.pack(anchor="e", pady=(2, 8))
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_label_selected)
        self.chat_provider_combo = provider_combo

        tk.Label(
            model_wrap,
            text="Model",
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            font=("Segoe UI", 9),
        ).pack(anchor="e")
        model_combo = ttk.Combobox(
            model_wrap,
            textvariable=self.model_var,
            values=(MODEL_PLACEHOLDER,),
            state="readonly",
            width=34,
            style="Dark.TCombobox",
        )
        model_combo.pack(anchor="e", pady=(2, 8))
        self.chat_model_combo = model_combo

        refresh_models_btn = tk.Button(
            model_wrap,
            text="Refresh Models",
            command=self._refresh_models_for_selected_provider,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        refresh_models_btn.pack(anchor="e")

        # Add reasoning effort control
        tk.Label(
            model_wrap,
            text="Reasoning Effort",
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            font=("Segoe UI", 9),
        ).pack(anchor="e", pady=(8, 0))
        
        reasoning_frame = tk.Frame(model_wrap, bg=COLORS["panel"])
        reasoning_frame.pack(anchor="e", pady=(2, 0))
        
        tk.Radiobutton(
            reasoning_frame,
            text="Low",
            variable=self.reasoning_effort_var,
            value=0,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["text"],
        ).pack(side="left")
        
        tk.Radiobutton(
            reasoning_frame,
            text="Standard",
            variable=self.reasoning_effort_var,
            value=1,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["text"],
        ).pack(side="left", padx=(8, 0))
        
        tk.Radiobutton(
            reasoning_frame,
            text="High",
            variable=self.reasoning_effort_var,
            value=2,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["text"],
        ).pack(side="left", padx=(8, 0))

        message_container = tk.Frame(parent, bg=COLORS["panel"])
        message_container.pack(fill="both", expand=True)

        self.messages_canvas = tk.Canvas(
            message_container,
            bg=COLORS["panel"],
            highlightthickness=0,
            bd=0,
        )
        self.messages_canvas.pack(side="left", fill="both", expand=True)

        scroll = tk.Scrollbar(
            message_container,
            orient="vertical",
            command=self.messages_canvas.yview,
            troughcolor=COLORS["panel"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        scroll.pack(side="right", fill="y")
        self.messages_canvas.configure(yscrollcommand=scroll.set)

        self.message_frame = tk.Frame(self.messages_canvas, bg=COLORS["panel"])
        self.canvas_window = self.messages_canvas.create_window(
            (0, 0), window=self.message_frame, anchor="nw"
        )
        self.message_frame.bind("<Configure>", self._refresh_scroll_region)
        self.messages_canvas.bind("<Configure>", self._resize_canvas_window)
        self.messages_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        composer = tk.Frame(
            parent,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        composer.pack(fill="x")

        self.input_box = tk.Text(
            composer,
            wrap="word",
            height=2,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Segoe UI", 11),
            padx=10,
            pady=8,
        )
        self.input_box.pack(side="left", fill="both", expand=True, padx=(12, 10), pady=12)
        self.input_box.bind("<Return>", self._on_enter_press)
        self.input_box.bind("<KeyRelease>", self._adjust_input_height)

        self.send_button = tk.Button(
            composer,
            text="Send",
            command=self.send_message,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=16,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.send_button.pack(side="right", padx=(0, 12), pady=12)

    def _build_ide_view(self, parent: tk.Frame) -> None:
        """Build the IDE workspace, editor, console, and right agent panel."""
        header = tk.Frame(
            parent,
            bg="#0b1322",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        header.pack(fill="x")

        ide_kind_toggle = tk.Frame(header, bg="#0b1322")
        ide_kind_toggle.pack(side="left", padx=(10, 4), pady=8)
        self.ide_python_kind_button = tk.Button(
            ide_kind_toggle,
            text="Python",
            command=lambda: self.switch_ide_kind("python"),
            bd=0,
            padx=10,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.ide_python_kind_button.pack(side="left", padx=(0, 4))
        self.ide_web_kind_button = tk.Button(
            ide_kind_toggle,
            text="Web",
            command=lambda: self.switch_ide_kind("web"),
            bd=0,
            padx=10,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.ide_web_kind_button.pack(side="left")

        tab_strip = tk.Frame(header, bg="#0b1322")
        tab_strip.pack(side="left", fill="x", expand=True, padx=(4, 8), pady=8)
        tab = tk.Frame(
            tab_strip,
            bg=COLORS["entry_bg"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        tab.pack(side="left")
        tk.Label(
            tab,
            textvariable=self.ide_tab_title_var,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            font=("Consolas", 9, "bold"),
            padx=10,
            pady=6,
        ).pack(side="left")
        tk.Label(
            tab_strip,
            textvariable=self.ide_status_var,
            bg="#0b1322",
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(10, 0))

        controls = tk.Frame(header, bg="#0b1322")
        controls.pack(side="right", padx=10, pady=8)

        self.save_button = tk.Button(
            controls,
            text="Save",
            command=self.save_current_file,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.save_button.pack(side="left", padx=(0, 6))

        self.run_button = tk.Button(
            controls,
            text="Run",
            command=self.run_ide_code,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=12,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.run_button.pack(side="left", padx=(0, 6))

        self.stop_button = tk.Button(
            controls,
            text="Stop",
            command=self.stop_ide_code,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=(0, 6))

        self.ask_ai_button = tk.Button(
            controls,
            text="Agent",
            command=self.ask_ai_about_code,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.ask_ai_button.pack(side="left")

        self.package_manager_button = tk.Button(
            controls,
            text="Packages",
            command=self.open_package_installer,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=5,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.package_manager_button.pack(side="left", padx=(6, 0))

        ide_body = tk.Frame(parent, bg=COLORS["panel"])
        ide_body.pack(fill="both", expand=True)

        workspace = tk.Frame(ide_body, bg=COLORS["panel"])
        workspace.pack(side="left", fill="both", expand=True, pady=(6, 0))

        agent_sidebar = tk.Frame(
            ide_body,
            width=360,
            bg=COLORS["sidebar"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        agent_sidebar.pack(side="right", fill="y", pady=(6, 0))
        agent_sidebar.pack_propagate(False)

        split = tk.PanedWindow(
            workspace,
            orient="vertical",
            bg=COLORS["panel"],
            sashwidth=7,
            sashpad=2,
            bd=0,
            relief="flat",
        )
        split.pack(fill="both", expand=True)

        editor_panel = tk.Frame(
            split,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        terminal_panel = tk.Frame(
            split,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        split.add(editor_panel, minsize=280)
        split.add(terminal_panel, minsize=160)

        editor_header = tk.Frame(editor_panel, bg=COLORS["panel"])
        editor_header.pack(fill="x", padx=10, pady=(8, 6))
        tk.Label(
            editor_header,
            text="EDITOR",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Consolas", 9, "bold"),
        ).pack(side="left")
        
        header_right = tk.Frame(editor_header, bg=COLORS["panel"])
        header_right.pack(side="right")
        
        tk.Button(
            header_right,
            text="Save As",
            command=self._ide_save_as,
            bg=COLORS["button"],
            fg=COLORS["text"],
            activebackground=COLORS["button_hover"],
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=0,
            padx=8,
            pady=2,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 6))
        
        tk.Label(
            header_right,
            textvariable=self.ide_file_var,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Consolas", 8),
        ).pack(side="left")

        editor_wrap = tk.Frame(editor_panel, bg=COLORS["panel"])
        editor_wrap.pack(fill="both", expand=True, padx=10)

        self.ide_line_numbers = tk.Text(
            editor_wrap,
            width=5,
            wrap="none",
            bg="#0a111f",
            fg="#6b7f9a",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            bd=0,
            padx=6,
            pady=10,
            font=("Consolas", 10),
            state="disabled",
        )
        self.ide_line_numbers.pack(side="left", fill="y")
        self.ide_line_numbers.bind("<MouseWheel>", lambda _e: "break")

        self.ide_editor = tk.Text(
            editor_wrap,
            wrap="none",
            undo=True,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Consolas", 11),
            padx=10,
            pady=10,
        )
        self.ide_editor.pack(side="left", fill="both", expand=True)
        self._configure_ide_syntax_tags()
        self.ide_editor.bind("<KeyRelease>", self._on_ide_editor_change)
        self.ide_editor.bind("<ButtonRelease-1>", self._update_ide_cursor_position)

        self.ide_editor_scroll = tk.Scrollbar(
            editor_wrap,
            orient="vertical",
            command=self._on_ide_editor_scrollbar,
            troughcolor=COLORS["panel"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        self.ide_editor_scroll.pack(side="right", fill="y")
        self.ide_editor.configure(yscrollcommand=self._on_ide_editor_yscroll)

        xscroll_editor = tk.Scrollbar(
            editor_panel,
            orient="horizontal",
            command=self.ide_editor.xview,
            troughcolor=COLORS["panel"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        xscroll_editor.pack(fill="x", padx=10, pady=(0, 8))
        self.ide_editor.configure(xscrollcommand=xscroll_editor.set)

        # Save reference to terminal panel for later modification
        self.ide_terminal_panel = terminal_panel
        self.ide_split = split

        terminal_header = tk.Frame(terminal_panel, bg=COLORS["panel"])
        terminal_header.pack(fill="x", padx=10, pady=(8, 6))
        
        self.ide_panel_label = tk.Label(
            terminal_header,
            text="TERMINAL",
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            font=("Consolas", 8, "bold"),
            padx=8,
            pady=4,
        )
        self.ide_panel_label.pack(side="left")

        clear_output_btn = tk.Button(
            terminal_header,
            text="Clear",
            command=self.clear_ide_output,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=4,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        clear_output_btn.pack(side="right")

        output_wrap = tk.Frame(terminal_panel, bg=COLORS["panel"])
        output_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.ide_output_container = output_wrap
        
        self.ide_output = tk.Text(
            output_wrap,
            wrap="word",
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            state="disabled",
        )
        self.ide_output.pack(side="left", fill="both", expand=True)

        yscroll_output = tk.Scrollbar(
            output_wrap,
            orient="vertical",
            command=self.ide_output.yview,
            troughcolor=COLORS["panel"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        yscroll_output.pack(side="right", fill="y")
        self.ide_output.configure(yscrollcommand=yscroll_output.set)

        status_bar = tk.Frame(
            parent,
            bg="#0b1322",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        status_bar.pack(fill="x")
        tk.Label(
            status_bar,
            textvariable=self.ide_runtime_var,
            bg="#0b1322",
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(side="left", padx=10, pady=5)
        tk.Label(
            status_bar,
            textvariable=self.ide_cursor_var,
            bg="#0b1322",
            fg=COLORS["muted"],
            font=("Consolas", 8),
        ).pack(side="right", padx=10)

        self._refresh_ide_line_numbers()
        self._update_ide_cursor_position()
        self._schedule_ide_syntax_highlight(delay_ms=10)
        self._build_ide_agent_sidebar(agent_sidebar)
        self._refresh_ide_kind_ui()
        self._sync_agent_prompt_with_ide_kind(force=True)

    def _build_ide_agent_sidebar(self, parent: tk.Frame) -> None:
        """Build the IDE agent sidebar with controls, history, and output."""
        top = tk.Frame(parent, bg=COLORS["sidebar"])
        top.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(
            top,
            text="Agent",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("Consolas", 10, "bold"),
        ).pack(side="left")
        self.new_agent_chat_button = tk.Button(
            top,
            text="+ New",
            command=self._create_agent_chat,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=8,
            pady=4,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        self.new_agent_chat_button.pack(side="right")

        tk.Label(
            parent,
            textvariable=self.agent_status_var,
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
        ).pack(anchor="w", padx=12, pady=(0, 6))

        tk.Label(
            parent,
            text="THREADS",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        chats_wrap = tk.Frame(parent, bg=COLORS["sidebar"])
        chats_wrap.pack(fill="x", padx=12, pady=(0, 8))
        self.agent_chat_listbox = tk.Listbox(
            chats_wrap,
            height=4,
            bg=COLORS["list_bg"],
            fg=COLORS["text"],
            selectbackground=COLORS["button"],
            selectforeground="#03100f",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            borderwidth=0,
            activestyle="none",
            font=("Segoe UI", 9),
        )
        self.agent_chat_listbox.pack(side="left", fill="x", expand=True)
        self.agent_chat_listbox.bind("<<ListboxSelect>>", self._on_agent_chat_selected)
        self.agent_chat_listbox.bind("<Button-3>", self._on_agent_chat_right_click)

        chats_scroll = tk.Scrollbar(
            chats_wrap,
            orient="vertical",
            command=self.agent_chat_listbox.yview,
            troughcolor=COLORS["sidebar"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        chats_scroll.pack(side="right", fill="y")
        self.agent_chat_listbox.configure(yscrollcommand=chats_scroll.set)

        tk.Label(
            parent,
            text="SYSTEM PROMPT",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        self.agent_prompt_input = tk.Text(
            parent,
            wrap="word",
            height=6,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Segoe UI", 10),
            padx=10,
            pady=8,
        )
        self.agent_prompt_input.pack(fill="x", padx=12, pady=(0, 8))
        self.agent_prompt_input.insert(
            "1.0",
            PYTHON_AGENT_PROMPT,
        )
        options = tk.Frame(parent, bg=COLORS["sidebar"])
        options.pack(fill="x", padx=10, pady=(0, 8))
        
        tk.Label(
            options,
            text="GOAL / REQUEST",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.agent_goal_input = tk.Text(
            options,
            wrap="word",
            height=3,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Segoe UI", 9),
            padx=10,
            pady=6,
        )
        self.agent_goal_input.pack(fill="x", padx=0, pady=(0, 8))

        context_options = tk.Frame(parent, bg=COLORS["sidebar"])
        context_options.pack(fill="x", padx=10, pady=(0, 8))
        tk.Checkbutton(
            context_options,
            text="Current file",
            variable=self.agent_include_file_var,
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            activebackground=COLORS["sidebar"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            highlightthickness=0,
            font=("Segoe UI", 8),
        ).pack(side="left")
        tk.Checkbutton(
            context_options,
            text="Console output",
            variable=self.agent_include_console_var,
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            activebackground=COLORS["sidebar"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            highlightthickness=0,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=(12, 0))

        # Add provider/model selection controls for the agent
        agent_model_frame = tk.Frame(parent, bg=COLORS["sidebar"])
        agent_model_frame.pack(fill="x", padx=10, pady=(8, 8))

        # Provider selection
        tk.Label(
            agent_model_frame,
            text="Provider",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        provider_choices = [PROVIDERS[key]["label"] for key in PROVIDERS]
        self.agent_provider_label_var = tk.StringVar(value=PROVIDERS[self.provider_var.get()]["label"])
        agent_provider_combo = ttk.Combobox(
            agent_model_frame,
            textvariable=self.agent_provider_label_var,
            values=provider_choices,
            state="readonly",
            width=18,
            style="Dark.TCombobox",
        )
        agent_provider_combo.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        agent_provider_combo.bind("<<ComboboxSelected>>", self._on_agent_provider_label_selected)
        self.agent_provider_combo = agent_provider_combo

        # Model selection
        tk.Label(
            agent_model_frame,
            text="Model",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 2))
        
        self.agent_model_var = tk.StringVar(value=self.model_var.get())  # Initialize with current model
        agent_model_combo = ttk.Combobox(
            agent_model_frame,
            textvariable=self.agent_model_var,
            values=(MODEL_PLACEHOLDER,),
            state="readonly",
            width=22,
            style="Dark.TCombobox",
        )
        agent_model_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        self.agent_model_combo = agent_model_combo
        
        # Refresh models button
        refresh_agent_models_btn = tk.Button(
            agent_model_frame,
            text="Refresh",
            command=self._refresh_agent_models,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=6,
            pady=2,
            font=("Segoe UI", 7, "bold"),
            cursor="hand2",
        )
        refresh_agent_models_btn.grid(row=1, column=2, padx=(6, 0), sticky="ew")

        agent_model_frame.columnconfigure(0, weight=1)
        agent_model_frame.columnconfigure(1, weight=1)
        agent_model_frame.columnconfigure(2, weight=0)

        # Add reasoning effort control below the model selection
        reasoning_frame = tk.Frame(parent, bg=COLORS["sidebar"])
        reasoning_frame.pack(fill="x", padx=10, pady=(8, 8))
        
        tk.Label(
            reasoning_frame,
            text="Agent Reasoning Effort",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        
        effort_radio_frame = tk.Frame(reasoning_frame, bg=COLORS["sidebar"])
        effort_radio_frame.pack(anchor="w")
        
        # Create the reasoning effort variable if it doesn't exist
        if not hasattr(self, 'agent_reasoning_effort_var'):
            self.agent_reasoning_effort_var = tk.IntVar(value=1)  # Default to standard effort
        
        tk.Radiobutton(
            effort_radio_frame,
            text="Low",
            variable=self.agent_reasoning_effort_var,
            value=0,
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            activebackground=COLORS["sidebar"],
            activeforeground=COLORS["text"],
        ).pack(side="left")
        
        tk.Radiobutton(
            effort_radio_frame,
            text="Standard",
            variable=self.agent_reasoning_effort_var,
            value=1,
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            activebackground=COLORS["sidebar"],
            activeforeground=COLORS["text"],
        ).pack(side="left", padx=(8, 0))
        
        tk.Radiobutton(
            effort_radio_frame,
            text="High",
            variable=self.agent_reasoning_effort_var,
            value=2,
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            activebackground=COLORS["sidebar"],
            activeforeground=COLORS["text"],
        ).pack(side="left", padx=(8, 0))

        # Initialize agent model menu with the current provider
        current_provider = self._provider_from_label(self.agent_provider_label_var.get())
        self._apply_agent_model_menu(current_provider)

        button_row = tk.Frame(parent, bg=COLORS["sidebar"])
        button_row.pack(fill="x", padx=12, pady=(0, 10))
        self.agent_run_button = tk.Button(
            button_row,
            text="Run Agent",
            command=self.run_ide_agent,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=10,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.agent_run_button.pack(side="left")
        clear_btn = tk.Button(
            button_row,
            text="Clear",
            command=self.clear_agent_output,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=10,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        clear_btn.pack(side="left", padx=(8, 0))

        tk.Label(
            parent,
            text="OUTPUT",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 4))

        output_wrap = tk.Frame(parent, bg=COLORS["sidebar"])
        output_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.agent_output = tk.Text(
            output_wrap,
            wrap="word",
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Consolas", 9),
            padx=10,
            pady=8,
            state="disabled",
        )
        self.agent_output.pack(side="left", fill="both", expand=True)
        agent_scroll = tk.Scrollbar(
            output_wrap,
            orient="vertical",
            command=self.agent_output.yview,
            troughcolor=COLORS["sidebar"],
            bg=COLORS["entry_bg"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        agent_scroll.pack(side="right", fill="y")
        self.agent_output.configure(yscrollcommand=agent_scroll.set)

    def switch_mode(self, mode: str) -> None:
        """Switch between chatroom and IDE modes and update visible panels."""
        if mode not in {"chat", "ide"}:
            return

        self._hide_message_hover()
        self.mode_var.set(mode)
        if mode == "chat":
            self.chat_sidebar.tkraise()
            self.chat_view.tkraise()
            self.input_box.focus_set()
        else:
            self.file_sidebar.tkraise()
            self.ide_view.tkraise()
            self.ide_editor.focus_set()
            self._refresh_project_file_list(select_current=True)

        self._refresh_mode_buttons()

    def _refresh_mode_buttons(self) -> None:
        """Refresh mode buttons to match current state."""
        active_bg = COLORS["button"]
        active_fg = "#04100f"
        inactive_bg = COLORS["entry_bg"]
        inactive_fg = COLORS["text"]

        if self.mode_var.get() == "chat":
            self.chat_mode_button.configure(
                bg=active_bg,
                fg=active_fg,
                activebackground=COLORS["button_hover"],
                activeforeground=active_fg,
                highlightthickness=0,
            )
            self.ide_mode_button.configure(
                bg=inactive_bg,
                fg=inactive_fg,
                activebackground="#172135",
                activeforeground=inactive_fg,
                highlightthickness=1,
                highlightbackground=COLORS["border"],
            )
        else:
            self.ide_mode_button.configure(
                bg=active_bg,
                fg=active_fg,
                activebackground=COLORS["button_hover"],
                activeforeground=active_fg,
                highlightthickness=0,
            )
            self.chat_mode_button.configure(
                bg=inactive_bg,
                fg=inactive_fg,
                activebackground="#172135",
                activeforeground=inactive_fg,
                highlightthickness=1,
                highlightbackground=COLORS["border"],
            )

    def _default_scratch_filename_for_kind(self, kind: str | None = None) -> str:
        """Return the default unsaved filename label for the active IDE kind."""
        ide_kind = kind if kind in {"python", "web"} else self.ide_kind_var.get()
        return "index.html" if ide_kind == "web" else "scratch.py"

    def _ide_template_for_kind(self, kind: str | None = None) -> str:
        """Return the editor template text for a given IDE kind."""
        ide_kind = kind if kind in {"python", "web"} else self.ide_kind_var.get()
        return IDE_WEB_TEMPLATE if ide_kind == "web" else IDE_PYTHON_TEMPLATE

    def _agent_prompt_for_kind(self, kind: str | None = None) -> str:
        """Return the default agent prompt for the active IDE kind."""
        ide_kind = kind if kind in {"python", "web"} else self.ide_kind_var.get()
        return WEB_AGENT_PROMPT if ide_kind == "web" else PYTHON_AGENT_PROMPT

    def _sync_agent_prompt_with_ide_kind(self, force: bool = False) -> None:
        """Update the agent prompt text when switching IDE kinds, preserving user edits."""
        if not hasattr(self, "agent_prompt_input"):
            return
        current_prompt = self.agent_prompt_input.get("1.0", "end-1c").strip()
        known_defaults = {PYTHON_AGENT_PROMPT, WEB_AGENT_PROMPT}
        if force or not current_prompt or current_prompt in known_defaults:
            self.agent_prompt_input.delete("1.0", "end")
            self.agent_prompt_input.insert("1.0", self._agent_prompt_for_kind())

    def _can_replace_scratch_buffer(self) -> bool:
        """Return whether mode switching can safely replace unsaved scratch content."""
        if self.ide_current_file is not None:
            return False
        if not hasattr(self, "ide_editor"):
            return True
        content = self.ide_editor.get("1.0", "end-1c").strip()
        if not content:
            return True
        template_text = {
            IDE_PYTHON_TEMPLATE.strip(),
            IDE_WEB_TEMPLATE.strip(),
        }
        if content in template_text:
            return True
        return not self.ide_dirty

    def _apply_scratch_template_for_kind(self, kind: str, force: bool = False) -> None:
        """Load the default scratch template for a kind when no file is open."""
        if kind not in {"python", "web"}:
            return
        if not force and not self._can_replace_scratch_buffer():
            return
        if not hasattr(self, "ide_editor"):
            return

        self._ide_loading = True
        self.ide_editor.delete("1.0", "end")
        self.ide_editor.insert("1.0", self._ide_template_for_kind(kind))
        self._ide_loading = False

        self.ide_current_file = None
        self.ide_dirty = False
        scratch_name = self._default_scratch_filename_for_kind(kind)
        self.ide_file_var.set(scratch_name)
        self.ide_tab_title_var.set(scratch_name)
        self._refresh_ide_line_numbers()
        self._update_ide_cursor_position()
        self._schedule_ide_syntax_highlight(delay_ms=10)

    def _ide_kind_for_path(self, path: Path) -> str | None:
        """Infer which IDE kind should handle a file extension."""
        suffix = path.suffix.lower()
        if suffix == ".py":
            return "python"
        if suffix in WEB_FILE_EXTENSIONS:
            return "web"
        return None

    def _ide_language_for_path(self, path: Path | None = None) -> str:
        """Resolve editor language for syntax highlighting and fenced prompts."""
        target = path if path is not None else self.ide_current_file
        suffix = target.suffix.lower() if target is not None else ""
        if suffix == ".py":
            return "python"
        if suffix in {".html", ".htm"}:
            return "html"
        if suffix == ".css":
            return "css"
        if suffix in {".js", ".mjs", ".jsx", ".ts", ".tsx"}:
            return "javascript"
        return "python" if self.ide_kind_var.get() == "python" else "html"

    def _refresh_ide_kind_ui(self) -> None:
        """Refresh IDE-kind toggle buttons, runtime label, and run/stop labels."""
        if not hasattr(self, "ide_python_kind_button"):
            return

        kind = self.ide_kind_var.get()
        active_bg = COLORS["button"]
        active_fg = "#04100f"
        inactive_bg = COLORS["entry_bg"]
        inactive_fg = COLORS["text"]

        def style_toggle(button: tk.Button, active: bool) -> None:
            if active:
                button.configure(
                    bg=active_bg,
                    fg=active_fg,
                    activebackground=COLORS["button_hover"],
                    activeforeground=active_fg,
                    highlightthickness=0,
                )
            else:
                button.configure(
                    bg=inactive_bg,
                    fg=inactive_fg,
                    activebackground="#172135",
                    activeforeground=inactive_fg,
                    highlightthickness=1,
                    highlightbackground=COLORS["border"],
                )

        style_toggle(self.ide_python_kind_button, kind == "python")
        style_toggle(self.ide_web_kind_button, kind == "web")

        if kind == "web":
            self.ide_runtime_var.set("Web IDE · HTML/CSS/JS")
            self.run_button.configure(text="Preview")
        else:
            self.ide_runtime_var.set(f"Python {sys.version_info.major}.{sys.version_info.minor}")
            self.run_button.configure(text="Run")

        # Reuse one path to keep stop-button behavior in sync with active IDE kind.
        self._set_ide_running(self.ide_running)

    def switch_ide_kind(self, kind: str) -> None:
        """Switch IDE kind between Python and Web while preserving current workflow."""
        if kind not in {"python", "web"}:
            return
        if self.ide_running:
            self.ide_status_var.set("Stop the current run before switching IDE modes.")
            return
        if self.ide_kind_var.get() == kind:
            return

        self.ide_kind_var.set(kind)
        if self.ide_current_file is None:
            self._apply_scratch_template_for_kind(kind, force=False)
        self._sync_agent_prompt_with_ide_kind(force=False)
        self._refresh_ide_kind_ui()
        self._schedule_ide_syntax_highlight(delay_ms=10)
        self.ide_status_var.set(f"{kind.title()} IDE ready")

    def _provider_label(self, provider: str) -> str:
        """Compute label for provider-specific behavior."""
        info = PROVIDERS.get(provider)
        if info is None:
            return provider
        return str(info["label"])

    def _provider_from_label(self, label: str) -> str:
        """Convert a provider display label back to its internal provider key."""
        wanted = label.strip().lower()
        for provider, info in PROVIDERS.items():
            if str(info["label"]).strip().lower() == wanted:
                return provider
        return DEFAULT_PROVIDER

    def _default_provider_from_settings(self) -> str:
        """Resolve the default provider from saved settings or environment variables."""
        value = str(self.settings.get("default_provider", "")).strip().lower()
        if value in PROVIDERS:
            return value
        env_value = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()
        if env_value in PROVIDERS:
            return env_value
        return DEFAULT_PROVIDER

    def _fallback_models_for_provider(self, provider: str) -> list[str]:
        """Return local fallback models for providers that support built-in defaults."""
        if provider == "groq":
            return list(GROQ_FALLBACK_MODELS)
        return []

    def _default_model_from_settings(self, provider: str) -> str:
        """Resolve the default model for a provider from settings or environment variables."""
        settings_model = str(self.settings.get("default_model", "")).strip()
        if settings_model:
            return settings_model

        if provider == "groq":
            env_model = os.getenv("GROQ_MODEL", "").strip()
            if env_model:
                return env_model
            return GROQ_FALLBACK_MODELS[0]


    def _load_settings(self) -> dict[str, object]:
        """Load settings from persisted or remote sources."""
        defaults: dict[str, object] = {
            "api_keys": {},
            "default_provider": DEFAULT_PROVIDER,
            "default_model": "",
        }
        if not self.settings_path.exists():
            return defaults

        try:
            payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return defaults

        if not isinstance(payload, dict):
            return defaults

        api_keys: dict[str, str] = {}
        raw_api_keys = payload.get("api_keys")
        if isinstance(raw_api_keys, dict):
            for provider in PROVIDERS:
                value = str(raw_api_keys.get(provider, "")).strip()
                if value:
                    api_keys[provider] = value

        # Backward compatibility with prior settings format.
        for provider in PROVIDERS:
            legacy_field = f"{provider}_api_key"
            value = str(payload.get(legacy_field, "")).strip()
            if value and provider not in api_keys:
                api_keys[provider] = value

        default_provider = str(payload.get("default_provider", "")).strip().lower()
        if default_provider not in PROVIDERS:
            default_provider = DEFAULT_PROVIDER

        default_model = str(payload.get("default_model", "")).strip()
        return {
            "api_keys": api_keys,
            "default_provider": default_provider,
            "default_model": default_model,
        }

    def _save_settings(
        self,
        api_keys: dict[str, str],
        default_provider: str,
        default_model: str,
        theme: str = None,
        font_family: str = None,
        font_size: int = None,
        editor_font_family: str = None,
        editor_font_size: int = None,
    ) -> None:
        """Save settings to persistent storage including visual preferences."""
        clean_keys = {
            provider: value.strip()
            for provider, value in api_keys.items()
            if provider in PROVIDERS and value.strip()
        }
        provider = default_provider if default_provider in PROVIDERS else DEFAULT_PROVIDER

        payload = {
            "api_keys": clean_keys,
            "default_provider": provider,
            "default_model": default_model.strip(),
        }

        # Add visual settings if provided
        if theme is not None:
            payload["theme"] = theme
        if font_family is not None:
            payload["font_family"] = font_family
        if font_size is not None:
            payload["font_size"] = font_size
        if editor_font_family is not None:
            payload["editor_font_family"] = editor_font_family
        if editor_font_size is not None:
            payload["editor_font_size"] = editor_font_size

        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        try:
            os.chmod(self.settings_path, 0o600)
        except OSError:
            pass

        self.settings = self._load_settings()

    def _get_api_key(self, provider: str) -> str:
        """Get api key with configured fallbacks."""
        if provider not in PROVIDERS:
            return ""
        settings_keys = self.settings.get("api_keys", {})
        if isinstance(settings_keys, dict):
            key = str(settings_keys.get(provider, "")).strip()
            if key:
                return key
        env_key_name = str(PROVIDERS[provider]["env_key"])
        return os.getenv(env_key_name, "").strip()

    def _has_key(self, provider: str | None = None) -> bool:
        """Check whether the selected provider currently has an API key."""
        wanted = provider or self.provider_var.get().strip().lower()
        return bool(self._get_api_key(wanted))

    def _missing_key_message(self, provider: str | None = None) -> str:
        """Build a provider-specific message shown when an API key is missing."""
        wanted = provider or self.provider_var.get().strip().lower()
        label = self._provider_label(wanted)
        return f"No {label} key is saved. Click Settings to add your API key."

    def _set_combobox_values(
        self,
        combo: ttk.Combobox,
        variable: tk.StringVar,
        values: list[str],
        preferred_value: str = "",
    ) -> None:
        """Populate a readonly combobox with values and keep its selection valid."""
        choices = [item.strip() for item in values if item and item.strip()]
        if not choices:
            choices = [MODEL_PLACEHOLDER]
        combo.configure(values=choices)

        wanted = preferred_value.strip() or variable.get().strip()
        if wanted and wanted in choices:
            variable.set(wanted)
        else:
            variable.set(choices[0])

    def _on_provider_label_selected(self, event_or_label: object | None = None) -> None:
        """Handle the provider label selected event."""
        if isinstance(event_or_label, str):
            label = event_or_label
        elif self.chat_provider_label_var is not None:
            label = self.chat_provider_label_var.get()
        else:
            return
        provider = self._provider_from_label(label)
        if provider != self.provider_var.get():
            self.provider_var.set(provider)

    def _on_agent_provider_label_selected(self, event_or_label: object | None = None) -> None:
        """Handle the agent provider label selected event."""
        if isinstance(event_or_label, str):
            label = event_or_label
        elif self.agent_provider_label_var is not None:
            label = self.agent_provider_label_var.get()
        else:
            return
        provider = self._provider_from_label(label)
        if provider:
            # Update agent model menu to match new provider
            self._apply_agent_model_menu(provider)

    def _refresh_agent_models(self) -> None:
        """Refresh the models for the selected agent provider."""
        provider = self._provider_from_label(self.agent_provider_label_var.get())
        if provider:
            self._apply_agent_model_menu(provider)

    def _apply_agent_model_menu(self, provider: str, preferred_model: str = "") -> None:
        """Apply cached/fallback models to the agent model selector for the given provider."""
        if provider not in PROVIDERS:
            return

        # Use cached models if available, otherwise fall back to provider defaults
        models = list(self.model_cache.get(provider, []))
        if not models:
            models = self._fallback_models_for_provider(provider)

        # Apply models to the agent combobox
        if hasattr(self, 'agent_model_var') and hasattr(self, 'agent_model_combo'):
            self.agent_model_combo['values'] = models if models else [MODEL_PLACEHOLDER]
            
            # Set to preferred model if provided and available, otherwise use first model
            if preferred_model and preferred_model in models:
                self.agent_model_var.set(preferred_model)
            elif models:
                self.agent_model_var.set(models[0])
            else:
                self.agent_model_var.set(MODEL_PLACEHOLDER)
        elif hasattr(self, 'agent_model_var'):  # Fallback if combo box isn't accessible directly
            # Update the variable with the first available model
            if models:
                self.agent_model_var.set(models[0])
            else:
                self.agent_model_var.set(MODEL_PLACEHOLDER)

    def _apply_model_menu(self, provider: str, preferred_model: str = "") -> None:
        """Apply cached/fallback models to the model selector for the given provider."""
        if provider not in PROVIDERS:
            return
        models = list(self.model_cache.get(provider, []))
        if not models:
            models = self._fallback_models_for_provider(provider)
        if preferred_model.strip() and preferred_model.strip() not in models:
            models.insert(0, preferred_model.strip())

        if self.chat_model_combo is not None:
            self._set_combobox_values(
                self.chat_model_combo,
                self.model_var,
                models,
                preferred_value=preferred_model,
            )
        elif models:
            self.model_var.set(models[0])

    def _on_provider_change(self, *_args: object) -> None:
        """Handle the provider change event."""
        provider = self.provider_var.get().strip().lower()
        if provider not in PROVIDERS:
            self.provider_var.set(DEFAULT_PROVIDER)
            return
        if self.chat_provider_label_var is not None:
            self.chat_provider_label_var.set(self._provider_label(provider))

        self._apply_model_menu(provider)
        self._refresh_models_async(
            provider,
            preferred_model=self.model_var.get(),
            show_status=False,
        )
        self._render_current_chat()

    def _refresh_models_for_selected_provider(self) -> None:
        """Refresh models for selected provider to match current state."""
        self._refresh_models_async(
            self.provider_var.get(),
            preferred_model=self.model_var.get(),
            show_status=True,
        )

    def _refresh_models_async(
        self,
        provider: str,
        preferred_model: str = "",
        show_status: bool = True,
    ) -> None:
        """Fetch provider models on a background thread and report results through the queue."""
        wanted = provider.strip().lower()
        if wanted not in PROVIDERS:
            wanted = DEFAULT_PROVIDER

        api_key = self._get_api_key(wanted)
        # Do not launch worker threads when we already know auth is unavailable.
        if not api_key:
            if show_status:
                self.status_var.set(f"{self._provider_label(wanted)} key missing")
            return

        if show_status:
            self.status_var.set(f"Loading {self._provider_label(wanted)} models...")

        thread = threading.Thread(
            target=self._list_models_worker,
            args=(wanted, api_key, preferred_model.strip()),
            daemon=True,
        )
        # Network calls stay off the UI thread; results are marshaled back via event_queue.
        thread.start()

    def _list_models_worker(self, provider: str, api_key: str, preferred_model: str) -> None:
        """Background worker that retrieves models for a provider and emits queue events."""
        try:
            models = self._list_models_for_provider(provider, api_key)
            # Keep payload primitives/dicts only so queue events remain serialization-friendly.
            self.event_queue.put(
                {
                    "type": "models_loaded",
                    "provider": provider,
                    "models": models,
                    "preferred_model": preferred_model,
                }
            )
        except Exception as exc:  # noqa: BLE001
            self.event_queue.put(
                {
                    "type": "models_error",
                    "provider": provider,
                    "message": str(exc),
                }
            )

    def _list_models_for_provider(self, provider: str, api_key: str) -> list[str]:
        """Dispatch model-list retrieval to the provider-specific implementation."""
        if provider == "groq":
            return self._list_groq_models(api_key)
        if provider in OPENAI_COMPATIBLE_BASE_URL:
            return self._list_openai_compatible_models(provider, api_key)
        if provider == "anthropic":
            return self._list_anthropic_models(api_key)
        if provider == "gemini":
            return self._list_gemini_models(api_key)
        raise RuntimeError(f"Unsupported provider: {provider}")

    def _list_groq_models(self, api_key: str) -> list[str]:
        """List groq models from the selected provider."""
        try:
            client = Groq(api_key=api_key)
        except TypeError as e:
            if "proxies" in str(e):
                # Handle the case where proxy settings cause issues with Groq client
                # Create the client without passing proxy-related arguments
                import os
                # Temporarily unset proxy environment variables if present
                original_http_proxy = os.environ.pop('HTTP_PROXY', None)
                original_https_proxy = os.environ.pop('HTTPS_PROXY', None)
                
                try:
                    client = Groq(api_key=api_key)
                finally:
                    # Restore original proxy settings
                    if original_http_proxy:
                        os.environ['HTTP_PROXY'] = original_http_proxy
                    if original_https_proxy:
                        os.environ['HTTPS_PROXY'] = original_https_proxy
            else:
                raise
        response = client.models.list()
        raw_models = getattr(response, "data", [])
        models = sorted(
            {
                str(getattr(item, "id", "")).strip()
                for item in raw_models
                if str(getattr(item, "id", "")).strip()
            }
        )
        if not models:
            raise RuntimeError("No models returned by Groq.")
        return models

    def _list_openai_compatible_models(self, provider: str, api_key: str) -> list[str]:
        """List openai compatible models from the selected provider."""
        base_url = OPENAI_COMPATIBLE_BASE_URL.get(provider, "")
        if not base_url:
            raise RuntimeError(f"Unsupported OpenAI-compatible provider: {provider}")
        payload = self._http_json(
            method="GET",
            url=f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        raw_models = payload.get("data", [])
        models = sorted(
            {
                str(item.get("id", "")).strip()
                for item in raw_models
                if isinstance(item, dict) and str(item.get("id", "")).strip()
            }
        )
        if not models:
            raise RuntimeError(f"No models returned by {self._provider_label(provider)}.")
        return models

    def _list_anthropic_models(self, api_key: str) -> list[str]:
        """List anthropic models from the selected provider."""
        payload = self._http_json(
            method="GET",
            url="https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            },
        )
        raw_models = payload.get("data", [])
        models = sorted(
            {
                str(item.get("id", "")).strip()
                for item in raw_models
                if isinstance(item, dict) and str(item.get("id", "")).strip()
            }
        )
        if not models:
            raise RuntimeError("No models returned by Anthropic.")
        return models

    def _list_gemini_models(self, api_key: str) -> list[str]:
        """List gemini models from the selected provider."""
        payload = self._http_json(
            method="GET",
            url="https://generativelanguage.googleapis.com/v1beta/models",
            headers={"x-goog-api-key": api_key},
        )
        raw_models = payload.get("models", [])
        models: set[str] = set()
        for item in raw_models:
            if not isinstance(item, dict):
                continue
            methods = item.get("supportedGenerationMethods")
            if isinstance(methods, list) and "generateContent" not in methods:
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            if name.startswith("models/"):
                name = name[len("models/") :]
            if name:
                models.add(name)

        ordered = sorted(models)
        if not ordered:
            raise RuntimeError("No Gemini chat models returned.")
        return ordered

    def _http_json(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: dict[str, object] | None = None,
        timeout: int = 45,
    ) -> dict[str, object]:
        """Execute an HTTP request and return parsed JSON with normalized errors."""
        request_headers = dict(headers)
        payload_data: bytes | None = None
        if body is not None:
            payload_data = json.dumps(body).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        req = urlrequest.Request(
            url=url,
            data=payload_data,
            headers=request_headers,
            method=method.upper(),
        )

        try:
            with urlrequest.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
        except urlerror.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            message = body_text.strip() or exc.reason
            try:
                parsed = json.loads(body_text)
                if isinstance(parsed, dict):
                    if isinstance(parsed.get("error"), dict):
                        msg = str(parsed["error"].get("message", "")).strip()
                        if msg:
                            message = msg
                    elif isinstance(parsed.get("error"), str):
                        msg = str(parsed["error"]).strip()
                        if msg:
                            message = msg
            except json.JSONDecodeError:
                pass
            raise RuntimeError(f"{exc.code} {message}") from exc
        except urlerror.URLError as exc:
            reason = str(getattr(exc, "reason", exc))
            raise RuntimeError(f"Network error: {reason}") from exc

        if not raw:
            return {}

        try:
            parsed_payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Provider returned invalid JSON.") from exc
        if isinstance(parsed_payload, dict):
            return parsed_payload
        raise RuntimeError("Provider returned an unexpected JSON payload.")

    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count when provider usage stats are unavailable."""
        stripped = text.strip()
        if not stripped:
            return 0
        # Rough heuristic: most LLM tokenizers average around 3-4 chars per token.
        return max(1, int(round(len(stripped) / 4)))

    def _normalize_message_meta(self, raw_meta: object, role: str, content: str) -> dict[str, object]:
        """Normalize message metadata and ensure token count is always available."""
        meta: dict[str, object] = {}
        if isinstance(raw_meta, dict):
            token_count = raw_meta.get("token_count")
            if isinstance(token_count, int) and token_count >= 0:
                meta["token_count"] = token_count
            elif isinstance(token_count, float) and token_count >= 0:
                meta["token_count"] = int(round(token_count))

            response_seconds = raw_meta.get("response_seconds")
            if isinstance(response_seconds, (int, float)) and float(response_seconds) >= 0:
                meta["response_seconds"] = round(float(response_seconds), 3)

            for key in ("provider", "model", "token_source"):
                value = raw_meta.get(key)
                if isinstance(value, str):
                    cleaned = value.strip()
                    if cleaned:
                        meta[key] = cleaned

            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                value = raw_meta.get(key)
                if isinstance(value, int) and value >= 0:
                    meta[key] = value
                elif isinstance(value, float) and value >= 0:
                    meta[key] = int(round(value))

        if "token_count" not in meta and role in {"assistant", "user", "system"}:
            meta["token_count"] = self._estimate_token_count(content)
            meta["token_source"] = "estimated"

        return meta

    def _format_seconds(self, seconds: float) -> str:
        """Format a duration in seconds for compact UI display."""
        if seconds < 1:
            return f"{seconds:.2f}s"
        if seconds < 10:
            return f"{seconds:.2f}s"
        return f"{seconds:.1f}s"

    def _build_message_hover_text(self, role: str, text: str, meta: dict[str, object]) -> str:
        """Build the hover tooltip content for a chat message."""
        normalized = self._normalize_message_meta(meta, role, text)
        token_count = int(normalized.get("token_count", 0))
        token_source = str(normalized.get("token_source", "")).strip().lower()
        token_suffix = " (est.)" if token_source == "estimated" else ""
        lines = [f"Tokens: {token_count}{token_suffix}"]

        response_seconds = normalized.get("response_seconds")
        if isinstance(response_seconds, (int, float)) and float(response_seconds) >= 0:
            lines.append(f"Response time: {self._format_seconds(float(response_seconds))}")
        else:
            lines.append("Response time: n/a")

        return "\n".join(lines)

    def _show_message_hover(self, event: tk.Event, hover_text: str) -> None:
        """Show hover tooltip near the cursor for a chat bubble."""
        if self.message_hover_tip is None or not self.message_hover_tip.winfo_exists():
            self.message_hover_tip = tk.Toplevel(self)
            self.message_hover_tip.withdraw()
            self.message_hover_tip.overrideredirect(True)
            try:
                self.message_hover_tip.attributes("-topmost", True)
            except tk.TclError:
                pass
            label = tk.Label(
                self.message_hover_tip,
                text=hover_text,
                justify="left",
                bg=COLORS["entry_bg"],
                fg=COLORS["text"],
                font=("Consolas", 9),
                padx=10,
                pady=7,
                bd=1,
                relief="solid",
                highlightthickness=1,
                highlightbackground=COLORS["border"],
            )
            label.pack()
            self.message_hover_label = label
        elif self.message_hover_label is not None:
            self.message_hover_label.configure(text=hover_text)

        x = int(getattr(event, "x_root", self.winfo_pointerx())) + 14
        y = int(getattr(event, "y_root", self.winfo_pointery())) + 14
        self.message_hover_tip.geometry(f"+{x}+{y}")
        self.message_hover_tip.deiconify()

    def _move_message_hover(self, event: tk.Event) -> None:
        """Reposition the hover tooltip while the cursor moves."""
        if self.message_hover_tip is None or not self.message_hover_tip.winfo_exists():
            return
        x = int(getattr(event, "x_root", self.winfo_pointerx())) + 14
        y = int(getattr(event, "y_root", self.winfo_pointery())) + 14
        self.message_hover_tip.geometry(f"+{x}+{y}")

    def _hide_message_hover(self, _event: tk.Event | None = None) -> None:
        """Hide the hover tooltip if it is currently visible."""
        if self.message_hover_tip is not None and self.message_hover_tip.winfo_exists():
            self.message_hover_tip.withdraw()

    def _sanitize_messages(self, raw_messages: object, fallback_message: str) -> list[dict[str, object]]:
        """Validate and normalize persisted message objects before rendering or sending."""
        cleaned: list[dict[str, object]] = []
        if isinstance(raw_messages, list):
            for item in raw_messages:
                if not isinstance(item, dict):
                    continue
                role = str(item.get("role", "")).strip()
                content = str(item.get("content", "")).strip()
                if role not in {"assistant", "user", "system"}:
                    continue
                if not content:
                    continue
                
                # Filter out temporary attachment paths from the content
                filtered_content = self._filter_attachment_paths_from_text(content)
                
                # Extract thought process from the content
                visible_text, thought_process = self._extract_thought_process(filtered_content)
                
                # Add thought process to meta if found
                if thought_process:
                    # Get existing meta or create new one
                    existing_meta = item.get("meta", {})
                    if not isinstance(existing_meta, dict):
                        existing_meta = {}
                    if 'thought_process' not in existing_meta:
                        existing_meta['thought_process'] = thought_process
                    meta_dict = existing_meta
                else:
                    meta_dict = item.get("meta", {})
                    if not isinstance(meta_dict, dict):
                        meta_dict = {}
                
                # Only add if there's content after filtering
                if visible_text.strip():
                    message: dict[str, object] = {"role": role, "content": visible_text}
                    if meta_dict:
                        message["meta"] = meta_dict
                    cleaned.append(message)
                else:
                    # Skip messages that only contain attachment paths
                    continue

        if not cleaned:
            cleaned.append(
                {
                    "role": "assistant",
                    "content": fallback_message,
                    "meta": self._normalize_message_meta({}, "assistant", fallback_message),
                }
            )
        return cleaned

    def _load_conversations(self) -> None:
        """Load conversations from persisted or remote sources."""
        if not self.conversations_path.exists():
            return

        try:
            payload = json.loads(self.conversations_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(payload, dict):
            return

        loaded_chats: list[dict[str, object]] = []
        for idx, item in enumerate(payload.get("chats", [])):
            if not isinstance(item, dict):
                continue
            thread_id = str(item.get("id", "")).strip()
            if not thread_id:
                continue
            title = str(item.get("title", "")).strip() or f"Chat {idx + 1}"
            # Sanitize old/invalid records so a bad disk payload cannot break rendering.
            messages = self._sanitize_messages(item.get("messages"), WELCOME_MESSAGE)
            loaded_chats.append({"id": thread_id, "title": title, "messages": messages})

        self.chats = loaded_chats
        saved_chat_counter = payload.get("chat_counter")
        # Counter never goes backward; keeps generated IDs unique across restarts.
        if isinstance(saved_chat_counter, int):
            self.chat_counter = max(saved_chat_counter, len(self.chats))
        else:
            self.chat_counter = len(self.chats)

        requested_chat_id = str(payload.get("current_chat_id", "")).strip()
        valid_chat_ids = {str(c["id"]) for c in self.chats}
        if requested_chat_id and requested_chat_id in valid_chat_ids:
            self.current_chat_id = requested_chat_id
        elif self.chats:
            self.current_chat_id = str(self.chats[0]["id"])
        else:
            self.current_chat_id = None

        loaded_agent_chats: list[dict[str, object]] = []
        for idx, item in enumerate(payload.get("agent_chats", [])):
            if not isinstance(item, dict):
                continue
            thread_id = str(item.get("id", "")).strip()
            if not thread_id:
                continue
            title = str(item.get("title", "")).strip() or f"Agent Chat {idx + 1}"
            # Agent history uses the same message schema but a different empty-state welcome.
            messages = self._sanitize_messages(item.get("messages"), AGENT_WELCOME_MESSAGE)
            loaded_agent_chats.append({"id": thread_id, "title": title, "messages": messages})

        self.agent_chats = loaded_agent_chats
        saved_agent_counter = payload.get("agent_chat_counter")
        if isinstance(saved_agent_counter, int):
            self.agent_chat_counter = max(saved_agent_counter, len(self.agent_chats))
        else:
            self.agent_chat_counter = len(self.agent_chats)

        requested_agent_id = str(payload.get("current_agent_chat_id", "")).strip()
        valid_agent_ids = {str(c["id"]) for c in self.agent_chats}
        if requested_agent_id and requested_agent_id in valid_agent_ids:
            self.current_agent_chat_id = requested_agent_id
        elif self.agent_chats:
            self.current_agent_chat_id = str(self.agent_chats[0]["id"])
        else:
            self.current_agent_chat_id = None

    def _save_conversations(self) -> None:
        """Save conversations to persistent storage."""
        payload = {
            "chat_counter": self.chat_counter,
            "current_chat_id": self.current_chat_id,
            "chats": self.chats,
            "agent_chat_counter": self.agent_chat_counter,
            "current_agent_chat_id": self.current_agent_chat_id,
            "agent_chats": self.agent_chats,
        }
        try:
            self.conversations_path.parent.mkdir(parents=True, exist_ok=True)
            self.conversations_path.write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8",
            )
            os.chmod(self.conversations_path, 0o600)
        except OSError:
            pass

    def open_settings_dialog(self) -> None:
        """Open the settings dialog with tabs for API Keys, Defaults, and Visuals."""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_set()
            return

        window = tk.Toplevel(self)
        window.title("Settings")
        window.configure(bg=COLORS["panel"])
        window.geometry("800x650")
        window.resizable(False, False)
        window.transient(self)
        window.grab_set()
        self.settings_window = window

        # ===== Create Notebook (Tabs) =====
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Settings.TNotebook', background=COLORS["panel"], borderwidth=0)
        style.configure('Settings.TNotebook.Tab',
                       background=COLORS["entry_bg"],
                       foreground=COLORS["text"],
                       padding=[20, 10],
                       font=("Segoe UI", 10))
        style.map('Settings.TNotebook.Tab',
                 background=[('selected', COLORS["panel"])],
                 foreground=[('selected', COLORS["button"])])

        notebook = ttk.Notebook(window, style='Settings.TNotebook')
        notebook.pack(fill="both", expand=True, padx=16, pady=16)

        # ===== Tab 1: API Keys =====
        api_tab = tk.Frame(notebook, bg=COLORS["panel"])
        notebook.add(api_tab, text="API Keys")

        settings_keys_raw = self.settings.get("api_keys", {})
        settings_keys = settings_keys_raw if isinstance(settings_keys_raw, dict) else {}

        key_vars: dict[str, tk.StringVar] = {}
        key_entries: list[tk.Entry] = []
        for provider, info in PROVIDERS.items():
            from_settings = str(settings_keys.get(provider, "")).strip()
            if from_settings:
                value = from_settings
            else:
                value = os.getenv(str(info["env_key"]), "").strip()
            key_vars[provider] = tk.StringVar(value=value)

        show_var = tk.BooleanVar(value=False)

        # API Keys Content
        api_content = tk.Frame(api_tab, bg=COLORS["panel"])
        api_content.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            api_content,
            text="API Keys (major providers)",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        for provider, info in PROVIDERS.items():
            row = tk.Frame(api_content, bg=COLORS["panel"])
            row.pack(fill="x", pady=(0, 10))

            tk.Label(
                row,
                text=f"{info['label']} API Key",
                bg=COLORS["panel"],
                fg=COLORS["text"],
                width=20,
                anchor="w",
                font=("Segoe UI", 10, "bold"),
            ).pack(side="left")

            entry = tk.Entry(
                row,
                textvariable=key_vars[provider],
                show="*",
                bg=COLORS["entry_bg"],
                fg=COLORS["text"],
                insertbackground=COLORS["text"],
                highlightthickness=1,
                highlightbackground=COLORS["border"],
                relief="flat",
                font=("Consolas", 10),
            )
            entry.pack(side="left", fill="x", expand=True)
            key_entries.append(entry)

        def toggle_key_visibility() -> None:
            """Toggle API key entry fields between masked and visible text."""
            reveal = "" if show_var.get() else "*"
            for entry in key_entries:
                entry.configure(show=reveal)

        tk.Checkbutton(
            api_content,
            text="Show API keys",
            variable=show_var,
            command=toggle_key_visibility,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            activebackground=COLORS["panel"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["entry_bg"],
            highlightthickness=0,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(10, 0))

        # ===== Tab 2: Defaults =====
        defaults_tab = tk.Frame(notebook, bg=COLORS["panel"])
        notebook.add(defaults_tab, text="Defaults")

        default_provider_var = tk.StringVar(value=self.provider_var.get())
        default_provider_label_var = tk.StringVar(value=self._provider_label(default_provider_var.get()))
        default_model_var = tk.StringVar(value=self.model_var.get())

        # Defaults Content
        defaults_content = tk.Frame(defaults_tab, bg=COLORS["panel"])
        defaults_content.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            defaults_content,
            text="Default Provider and Model",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        defaults_row = tk.Frame(defaults_content, bg=COLORS["panel"])
        defaults_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            defaults_row,
            text="Provider:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            width=10,
            anchor="w",
        ).pack(side="left")

        provider_menu = tk.OptionMenu(
            defaults_row,
            default_provider_label_var,
            *[self._provider_label(provider) for provider in PROVIDERS],
            command=lambda label: default_provider_var.set(self._provider_from_label(label)),
        )
        provider_menu.config(
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            bd=0,
            width=18,
            cursor="hand2",
        )
        provider_menu["menu"].config(
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
        )
        provider_menu.pack(side="left", padx=(0, 10))

        tk.Label(
            defaults_row,
            text="Model:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            width=8,
            anchor="w",
        ).pack(side="left")

        model_entry = tk.Entry(
            defaults_row,
            textvariable=default_model_var,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Consolas", 10),
        )
        model_entry.pack(side="left", fill="x", expand=True)

        tk.Label(
            defaults_content,
            text="Use 'Refresh Models' in chat header to fetch all models your selected API key can access.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
            justify="left",
            wraplength=700,
        ).pack(anchor="w", pady=(10, 0))

        # ===== Tab 3: Visuals =====
        visuals_tab = tk.Frame(notebook, bg=COLORS["panel"])
        notebook.add(visuals_tab, text="Visuals")

        # Get saved visual settings
        saved_theme = self.settings.get("theme", CURRENT_THEME)
        saved_font = self.settings.get("font_family", "Segoe UI")
        saved_font_size = self.settings.get("font_size", 10)
        saved_editor_font = self.settings.get("editor_font_family", "Consolas")
        saved_editor_font_size = self.settings.get("editor_font_size", 10)

        theme_var = tk.StringVar(value=saved_theme)
        font_var = tk.StringVar(value=saved_font)
        font_size_var = tk.IntVar(value=saved_font_size)
        editor_font_var = tk.StringVar(value=saved_editor_font)
        editor_font_size_var = tk.IntVar(value=saved_editor_font_size)

        # Visuals Content
        visuals_content = tk.Frame(visuals_tab, bg=COLORS["panel"])
        visuals_content.pack(fill="both", expand=True, padx=16, pady=16)

        # Theme Selection
        tk.Label(
            visuals_content,
            text="Color Theme",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        theme_frame = tk.Frame(visuals_content, bg=COLORS["panel"])
        theme_frame.pack(fill="x", pady=(0, 20))

        for theme_name in THEMES.keys():
            tk.Radiobutton(
                theme_frame,
                text=theme_name,
                variable=theme_var,
                value=theme_name,
                bg=COLORS["panel"],
                fg=COLORS["text"],
                selectcolor=COLORS["entry_bg"],
                activebackground=COLORS["panel"],
                activeforeground=COLORS["button"],
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=4)

        # Font Settings
        tk.Label(
            visuals_content,
            text="Interface Font",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(10, 12))

        font_row = tk.Frame(visuals_content, bg=COLORS["panel"])
        font_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            font_row,
            text="Font Family:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            width=15,
            anchor="w",
        ).pack(side="left")

        available_fonts = ["Segoe UI", "Arial", "Helvetica", "Verdana", "Tahoma", "Calibri"]
        font_menu = tk.OptionMenu(font_row, font_var, *available_fonts)
        font_menu.config(
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            bd=0,
            width=15,
        )
        font_menu["menu"].config(bg=COLORS["entry_bg"], fg=COLORS["text"])
        font_menu.pack(side="left", padx=(0, 20))

        tk.Label(
            font_row,
            text="Size:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(side="left")

        font_size_spin = tk.Spinbox(
            font_row,
            from_=8,
            to=16,
            textvariable=font_size_var,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            width=5,
        )
        font_size_spin.pack(side="left", padx=(5, 0))

        # Editor Font Settings
        tk.Label(
            visuals_content,
            text="Editor/Code Font",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(20, 12))

        editor_font_row = tk.Frame(visuals_content, bg=COLORS["panel"])
        editor_font_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            editor_font_row,
            text="Font Family:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            width=15,
            anchor="w",
        ).pack(side="left")

        mono_fonts = ["Consolas", "Courier New", "Monaco", "Menlo", "Source Code Pro", "Fira Code"]
        editor_font_menu = tk.OptionMenu(editor_font_row, editor_font_var, *mono_fonts)
        editor_font_menu.config(
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            bd=0,
            width=15,
        )
        editor_font_menu["menu"].config(bg=COLORS["entry_bg"], fg=COLORS["text"])
        editor_font_menu.pack(side="left", padx=(0, 20))

        tk.Label(
            editor_font_row,
            text="Size:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(side="left")

        editor_font_size_spin = tk.Spinbox(
            editor_font_row,
            from_=8,
            to=18,
            textvariable=editor_font_size_var,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            width=5,
        )
        editor_font_size_spin.pack(side="left", padx=(5, 0))

        tk.Label(
            visuals_content,
            text="Note: Restart the application for all visual changes to take full effect.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "italic"),
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(20, 0))

        # ===== Info and Buttons =====
        info_var = tk.StringVar(value="")

        info_frame = tk.Frame(window, bg=COLORS["panel"])
        info_frame.pack(fill="x", padx=16, pady=(0, 10))

        tk.Label(
            info_frame,
            text=f"Saved to: {self.settings_path}",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            textvariable=info_var,
            bg=COLORS["panel"],
            fg="#f2aa7b",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 0))

        button_row = tk.Frame(window, bg=COLORS["panel"])
        button_row.pack(fill="x", padx=16, pady=(0, 16))

        def close_dialog() -> None:
            """Close the settings dialog and clear its window reference."""
            if window.winfo_exists():
                window.destroy()
            self.settings_window = None

        def save_settings() -> None:
            """Persist all settings including API keys, defaults, and visuals."""
            default_provider = default_provider_var.get().strip().lower()
            if default_provider not in PROVIDERS:
                info_var.set("Choose a valid default provider.")
                return

            try:
                self._save_settings(
                    api_keys={k: v.get().strip() for k, v in key_vars.items()},
                    default_provider=default_provider,
                    default_model=default_model_var.get().strip(),
                    theme=theme_var.get(),
                    font_family=font_var.get(),
                    font_size=font_size_var.get(),
                    editor_font_family=editor_font_var.get(),
                    editor_font_size=editor_font_size_var.get(),
                )
            except OSError as exc:
                info_var.set(f"Could not save settings: {exc}")
                return

            # Apply theme immediately
            global CURRENT_THEME, COLORS
            CURRENT_THEME = theme_var.get()
            COLORS = THEMES.get(CURRENT_THEME, THEMES["Dark Mode"]).copy()

            # Update provider/model
            self.provider_var.set(default_provider)
            wanted_model = default_model_var.get().strip()
            if wanted_model:
                self.model_var.set(wanted_model)
            self._apply_model_menu(default_provider, preferred_model=wanted_model)
            self._refresh_models_async(
                default_provider,
                preferred_model=self.model_var.get(),
                show_status=False,
            )

            self.status_var.set("Settings saved - Restart recommended for full effect")
            self._render_current_chat()
            close_dialog()

        tk.Button(
            button_row,
            text="Cancel",
            command=close_dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=20,
            pady=8,
            font=("Segoe UI", 10),
            cursor="hand2",
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            button_row,
            text="Save Settings",
            command=save_settings,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=24,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="right")

        # Center window
        window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (window.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{int(x)}+{int(y)}")

    def open_package_installer(self) -> None:
        """Open the package installer window for installing PyPI packages."""
        installer = PackageInstallerWindow(parent=self, colors=COLORS)
        installer.root.mainloop()

    def open_keyboard_shortcuts(self) -> None:
        """Open keyboard shortcuts help window."""
        KeyboardShortcutsWindow(self, COLORS)

    def open_export_dialog(self) -> None:
        """Open export dialog for current chat."""
        current_chat = self._current_chat()
        if not current_chat:
            messagebox.showwarning("No Chat", "Please select a chat to export.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Export Chat")
        dialog.configure(bg=COLORS["panel"])
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Title
        tk.Label(
            dialog,
            text="Export Chat",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 12))

        tk.Label(
            dialog,
            text=f"Chat: {current_chat.get('title', 'Unknown')}",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Format selection
        tk.Label(
            dialog,
            text="Select Format:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=16, pady=(0, 6))

        format_var = tk.StringVar(value="markdown")

        formats = [("Markdown (.md)", "markdown"), ("JSON (.json)", "json"), ("Text (.txt)", "txt")]
        for label, value in formats:
            tk.Radiobutton(
                dialog,
                text=label,
                variable=format_var,
                value=value,
                bg=COLORS["panel"],
                fg=COLORS["text"],
                selectcolor=COLORS["entry_bg"],
                activebackground=COLORS["panel"],
                activeforeground=COLORS["text"],
                font=("Segoe UI", 9),
            ).pack(anchor="w", padx=32, pady=2)

        # Buttons
        button_frame = tk.Frame(dialog, bg=COLORS["panel"])
        button_frame.pack(fill="x", padx=16, pady=(16, 16))

        def on_export():
            """Handle export."""
            file_ext = format_var.get()
            ext_map = {"markdown": ".md", "json": ".json", "txt": ".txt"}

            filepath = filedialog.asksaveasfilename(
                defaultextension=ext_map.get(file_ext, ".txt"),
                filetypes=[(f"{file_ext.upper()} files", f"*{ext_map.get(file_ext)}")],
                parent=dialog,
            )

            if filepath:
                success = False
                if file_ext == "markdown":
                    success = export_chat_to_markdown(current_chat, Path(filepath))
                elif file_ext == "json":
                    success = export_chat_to_json(current_chat, Path(filepath))
                elif file_ext == "txt":
                    success = export_chat_to_txt(current_chat, Path(filepath))

                if success:
                    messagebox.showinfo("Export Successful", f"Chat exported to:\n{filepath}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Export Failed", "Failed to export chat.")

        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            button_frame,
            text="Export",
            command=on_export,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right")

    def open_search_dialog(self) -> None:
        """Open search dialog for conversations."""
        dialog = tk.Toplevel(self)
        dialog.title("Search Conversations")
        dialog.configure(bg=COLORS["panel"])
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        dialog.transient(self)
        dialog.grab_set()

        # Title
        tk.Label(
            dialog,
            text="🔍 Search Conversations",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 12))

        # Search input
        tk.Label(
            dialog,
            text="Search Query:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=16, pady=(0, 4))

        search_entry = tk.Entry(
            dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Segoe UI", 10),
        )
        search_entry.pack(fill="x", padx=16, pady=(0, 12))
        search_entry.focus_set()

        # Results display
        tk.Label(
            dialog,
            text="Results:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=16, pady=(0, 4))

        results_frame = tk.Frame(dialog, bg=COLORS["panel"])
        results_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        results_text = tk.Text(
            results_frame,
            height=12,
            wrap="word",
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Consolas", 9),
            padx=10,
            pady=10,
            state="disabled",
        )
        results_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            results_frame,
            orient="vertical",
            command=results_text.yview,
            bg=COLORS["entry_bg"],
            troughcolor=COLORS["panel"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        scrollbar.pack(side="right", fill="y")
        results_text.configure(yscrollcommand=scrollbar.set)

        def perform_search():
            """Perform search."""
            query = search_entry.get().strip()
            if not query:
                results_text.configure(state="normal")
                results_text.delete("1.0", "end")
                results_text.insert("end", "Enter a search query to find messages.")
                results_text.configure(state="disabled")
                return

            results_text.configure(state="normal")
            results_text.delete("1.0", "end")

            # Search in regular chats
            search_results = ChatSearcher.search_in_all_chats(self.chats, query, case_sensitive=False)

            if search_results:
                results_text.insert("end", f"Found in {len(search_results)} chat(s):\n\n")
                for chat_id, data in search_results.items():
                    results_text.insert("end", f"💬 {data['title']}\n")
                    results_text.insert("end", f"   Matches: {data['matches']}\n\n")
            else:
                results_text.insert("end", "No results found.")

            results_text.configure(state="disabled")

        # Search button
        button_frame = tk.Frame(dialog, bg=COLORS["panel"])
        button_frame.pack(fill="x", padx=16, pady=(0, 16))

        tk.Button(
            button_frame,
            text="Search",
            command=perform_search,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right")

        # Allow Enter to search
        search_entry.bind("<Return>", lambda _: perform_search())

    def _create_chat(self, switch_to_chat: bool = True) -> None:
        """Create a new chat."""
        self.chat_counter += 1
        chat_id = f"chat-{self.chat_counter}"
        chat = {
            "id": chat_id,
            "title": f"Chat {self.chat_counter}",
            "messages": [
                {
                    "role": "assistant",
                    "content": WELCOME_MESSAGE,
                    "meta": self._normalize_message_meta({}, "assistant", WELCOME_MESSAGE),
                }
            ],
        }
        self.chats.append(chat)
        self.current_chat_id = chat_id
        self._refresh_chat_list()
        self._render_current_chat()
        self._save_conversations()
        if switch_to_chat:
            self.switch_mode("chat")

    def _current_chat(self) -> dict[str, object] | None:
        """Return the currently selected chat."""
        if self.current_chat_id is None:
            return None
        for chat in self.chats:
            if chat.get("id") == self.current_chat_id:
                return chat
        return None

    def _create_agent_chat(self) -> None:
        """Create a new agent chat."""
        self.agent_chat_counter += 1
        chat_id = f"agent-{self.agent_chat_counter}"
        chat = {
            "id": chat_id,
            "title": f"Agent Chat {self.agent_chat_counter}",
            "messages": [{"role": "assistant", "content": AGENT_WELCOME_MESSAGE}],
        }
        self.agent_chats.append(chat)
        self.current_agent_chat_id = chat_id
        self._refresh_agent_chat_list()
        self._render_current_agent_chat()
        self._save_conversations()

    def _current_agent_chat(self) -> dict[str, object] | None:
        """Return the currently selected agent chat."""
        if self.current_agent_chat_id is None:
            return None
        for chat in self.agent_chats:
            if chat.get("id") == self.current_agent_chat_id:
                return chat
        return None

    def _chat_title_from_text(self, text: str) -> str:
        """Create a short chat title from the user's first message."""
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            return "New Chat"
        return cleaned[:36] + ("..." if len(cleaned) > 36 else "")

    def _agent_chat_title_from_text(self, text: str) -> str:
        """Create a short IDE-agent chat title from the first goal."""
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            return "Agent Chat"
        return cleaned[:36] + ("..." if len(cleaned) > 36 else "")

    def _refresh_chat_list(self) -> None:
        """Refresh chat list to match current state."""
        self._suppress_chat_select = True
        self.chat_listbox.delete(0, "end")
        selected_index = None
        for idx, chat in enumerate(self.chats):
            title = str(chat.get("title", f"Chat {idx + 1}"))
            self.chat_listbox.insert("end", title)
            if chat.get("id") == self.current_chat_id:
                selected_index = idx

        if selected_index is not None:
            self.chat_listbox.selection_clear(0, "end")
            self.chat_listbox.selection_set(selected_index)
            self.chat_listbox.activate(selected_index)
        self._suppress_chat_select = False

    def _on_chat_selected(self, _event: tk.Event) -> None:
        """Handle the chat selected event."""
        if self._suppress_chat_select or self.pending:
            return
        selection = self.chat_listbox.curselection()
        if not selection:
            return
        index = int(selection[0])
        if index < 0 or index >= len(self.chats):
            return
        chat_id = str(self.chats[index]["id"])
        if chat_id == self.current_chat_id:
            return
        self.current_chat_id = chat_id
        self._render_current_chat()
        self._save_conversations()

    def _refresh_agent_chat_list(self) -> None:
        """Refresh agent chat list to match current state."""
        self._suppress_agent_select = True
        self.agent_chat_listbox.delete(0, "end")
        selected_index = None
        for idx, chat in enumerate(self.agent_chats):
            title = str(chat.get("title", f"Agent Chat {idx + 1}"))
            self.agent_chat_listbox.insert("end", title)
            if chat.get("id") == self.current_agent_chat_id:
                selected_index = idx

        if selected_index is not None:
            self.agent_chat_listbox.selection_clear(0, "end")
            self.agent_chat_listbox.selection_set(selected_index)
            self.agent_chat_listbox.activate(selected_index)
        self._suppress_agent_select = False

    def _on_agent_chat_selected(self, _event: tk.Event) -> None:
        """Handle the agent chat selected event."""
        if self._suppress_agent_select or self.agent_running:
            return
        selection = self.agent_chat_listbox.curselection()
        if not selection:
            return
        index = int(selection[0])
        if index < 0 or index >= len(self.agent_chats):
            return
        chat_id = str(self.agent_chats[index]["id"])
        if chat_id == self.current_agent_chat_id:
            return
        self.current_agent_chat_id = chat_id
        self._render_current_agent_chat()
        self._save_conversations()

    def _on_chat_right_click(self, event: tk.Event) -> None:
        """Handle right-click on chat listbox to show context menu."""
        index = self.chat_listbox.nearest(event.y)
        if index < 0 or index >= len(self.chats):
            return

        # Select the item under cursor
        self.chat_listbox.selection_clear(0, "end")
        self.chat_listbox.selection_set(index)
        self.chat_listbox.activate(index)

        # Create context menu
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(
            label="Rename",
            command=lambda: self._rename_chat(index)
        )
        menu.add_command(
            label="Delete",
            command=lambda: self._delete_chat(index)
        )

        # Display menu at cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_agent_chat_right_click(self, event: tk.Event) -> None:
        """Handle right-click on agent chat listbox to show context menu."""
        index = self.agent_chat_listbox.nearest(event.y)
        if index < 0 or index >= len(self.agent_chats):
            return

        # Select the item under cursor
        self.agent_chat_listbox.selection_clear(0, "end")
        self.agent_chat_listbox.selection_set(index)
        self.agent_chat_listbox.activate(index)

        # Create context menu
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(
            label="Rename",
            command=lambda: self._rename_agent_chat(index)
        )
        menu.add_command(
            label="Delete",
            command=lambda: self._delete_agent_chat(index)
        )

        # Display menu at cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _delete_chat(self, index: int) -> None:
        """Delete a chat at the given index."""
        if index < 0 or index >= len(self.chats):
            return

        chat_id = str(self.chats[index]["id"])

        # Remove from list
        self.chats.pop(index)

        # If it was the current chat, switch to another one
        if chat_id == self.current_chat_id:
            if self.chats:
                # Switch to the previous chat or first if at end
                new_index = max(0, index - 1)
                self.current_chat_id = str(self.chats[new_index]["id"])
            else:
                self.current_chat_id = None

        # Refresh the UI
        self._refresh_chat_list()
        if self.current_chat_id is not None:
            self._render_current_chat()
        else:
            # Create a new empty chat if none left
            self._create_chat()

        # Save to disk
        self._save_conversations()

    def _delete_agent_chat(self, index: int) -> None:
        """Delete an agent chat at the given index."""
        if index < 0 or index >= len(self.agent_chats):
            return

        chat_id = str(self.agent_chat_chats[index]["id"]) if hasattr(self, "agent_chat_chats") else str(self.agent_chat_listbox.get(index)) if hasattr(self, "agent_chat_listbox") else str(self.agent_chats[index]["id"])
        chat_id = str(self.agent_chats[index]["id"])

        # Remove from list
        self.agent_chats.pop(index)

        # If it was the current chat, switch to another one
        if chat_id == self.current_agent_chat_id:
            if self.agent_chats:
                # Switch to the previous chat or first if at end
                new_index = max(0, index - 1)
                self.current_agent_chat_id = str(self.agent_chats[new_index]["id"])
            else:
                self.current_agent_chat_id = None

        # Refresh the UI
        self._refresh_agent_chat_list()
        if self.current_agent_chat_id is not None:
            self._render_current_agent_chat()
        else:
            # Create a new empty agent chat if none left
            self._create_agent_chat()

        # Save to disk
        self._save_conversations()

    def _rename_chat(self, index: int) -> None:
        """Open a dialog to rename a chat."""
        if index < 0 or index >= len(self.chats):
            return

        chat = self.chats[index]
        current_title = str(chat.get("title", "Chat"))

        # Create a simple rename dialog
        dialog = tk.Toplevel(self)
        dialog.title("Rename Chat")
        dialog.configure(bg=COLORS["panel"])
        dialog.geometry("400x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Label
        tk.Label(
            dialog,
            text="New chat name:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Input field
        entry = tk.Entry(
            dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Segoe UI", 10),
        )
        entry.pack(fill="x", padx=16, pady=(0, 16))
        entry.insert(0, current_title)
        entry.select_range(0, "end")
        entry.focus_set()

        def on_ok() -> None:
            """Handle OK button."""
            new_title = entry.get().strip()
            if new_title:
                chat["title"] = new_title
                self._refresh_chat_list()
                self._save_conversations()
            dialog.destroy()

        def on_cancel() -> None:
            """Handle Cancel button."""
            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(dialog, bg=COLORS["panel"])
        button_frame.pack(fill="x", padx=16, pady=(0, 16))

        tk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right")

        # Handle Enter key
        entry.bind("<Return>", lambda _: on_ok())
        entry.bind("<Escape>", lambda _: on_cancel())

    def _rename_agent_chat(self, index: int) -> None:
        """Open a dialog to rename an agent chat."""
        if index < 0 or index >= len(self.agent_chats):
            return

        chat = self.agent_chats[index]
        current_title = str(chat.get("title", "Agent Chat"))

        # Create a simple rename dialog
        dialog = tk.Toplevel(self)
        dialog.title("Rename Agent Chat")
        dialog.configure(bg=COLORS["panel"])
        dialog.geometry("400x120")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Label
        tk.Label(
            dialog,
            text="New agent chat name:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Input field
        entry = tk.Entry(
            dialog,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            relief="flat",
            font=("Segoe UI", 10),
        )
        entry.pack(fill="x", padx=16, pady=(0, 16))
        entry.insert(0, current_title)
        entry.select_range(0, "end")
        entry.focus_set()

        def on_ok() -> None:
            """Handle OK button."""
            new_title = entry.get().strip()
            if new_title:
                chat["title"] = new_title
                self._refresh_agent_chat_list()
                self._save_conversations()
            dialog.destroy()

        def on_cancel() -> None:
            """Handle Cancel button."""
            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(dialog, bg=COLORS["panel"])
        button_frame.pack(fill="x", padx=16, pady=(0, 16))

        tk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            activebackground="#172135",
            activeforeground=COLORS["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            bg=COLORS["button"],
            fg="#04100f",
            activebackground=COLORS["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=16,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="right")

        # Handle Enter key
        entry.bind("<Return>", lambda _: on_ok())
        entry.bind("<Escape>", lambda _: on_cancel())

    def _render_current_agent_chat(self) -> None:
        """Render current agent chat in the active panel."""
        self.clear_agent_output()
        chat = self._current_agent_chat()
        if chat is None:
            self.agent_status_var.set("Idle")
            return

        messages = chat.get("messages", [])
        if isinstance(messages, list):
            for item in messages:
                if not isinstance(item, dict):
                    continue
                role = str(item.get("role", "assistant"))
                content = str(item.get("content", "")).strip()
                if not content:
                    continue
                if role == "assistant":
                    title = "Agent"
                elif role == "user":
                    title = "You"
                else:
                    title = "System"
                self._append_agent_output(f"{title}:\n{content}\n\n")

        if not self.agent_running:
            self.agent_status_var.set("Idle")

    def _render_current_chat(self) -> None:
        """Render current chat in the active panel."""
        for child in self.message_frame.winfo_children():
            child.destroy()
        self._hide_typing()

        chat = self._current_chat()
        if chat is None:
            self.status_var.set("Ready")
            return

        messages = chat.get("messages", [])
        if isinstance(messages, list):
            for item in messages:
                if not isinstance(item, dict):
                    continue
                role = str(item.get("role", "assistant"))
                content = str(item.get("content", "")).strip()
                if not content:
                    continue
                meta = item.get("meta", {})
                if not isinstance(meta, dict):
                    meta = {}
                self._add_message(role=role, text=content, auto_scroll=False, meta=meta)

        user_count = 0
        if isinstance(messages, list):
            user_count = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == "user")
        selected_provider = self.provider_var.get().strip().lower()
        if user_count == 0 and not self._has_key(selected_provider):
            self._add_message(
                role="system",
                text=self._missing_key_message(selected_provider),
                auto_scroll=False,
            )

        self.messages_canvas.yview_moveto(1.0)
        self.status_var.set("Ready")

    def _set_chat_controls_enabled(self, enabled: bool) -> None:
        """Set chat controls enabled state and related controls."""
        state = "normal" if enabled else "disabled"
        self.send_button.configure(state=state)
        self.new_chat_button.configure(state=state)
        self.chat_listbox.configure(state=state)

    def _set_agent_controls_enabled(self, enabled: bool) -> None:
        """Set agent controls enabled state and related controls."""
        state = "normal" if enabled else "disabled"
        self.agent_run_button.configure(state=state)
        self.new_agent_chat_button.configure(state=state)
        self.agent_chat_listbox.configure(state=state)

    def _refresh_scroll_region(self, _event: tk.Event) -> None:
        """Refresh scroll region to match current state."""
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))

    def _resize_canvas_window(self, event: tk.Event) -> None:
        """Resize the chat canvas window item when the canvas width changes."""
        self.messages_canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Handle the mousewheel event."""
        if self.messages_canvas.winfo_exists():
            self.messages_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_enter_press(self, event: tk.Event) -> str | None:
        """Handle the enter press event."""
        if event.state & 0x0001:
            return None
        self.send_message()
        return "break"

    def _adjust_input_height(self, _event: tk.Event | None = None) -> None:
        """Auto-resize the chat input box based on line count."""
        lines = int(self.input_box.index("end-1c").split(".")[0])
        target = max(2, min(8, lines))
        self.input_box.configure(height=target)

    def _extract_thought_process(self, text: str) -> tuple[str, str | None]:
        """Extract thought process from text and return (visible_text, thought_process).
        
        Identifies common patterns used by AI models to denote their thinking process.
        """
        import re
        
        # Common patterns for AI thought processes
        patterns = [
            # XML-style tags
            (r'<thinking>(.*?)</thinking>', re.DOTALL | re.IGNORECASE),
            (r'<think>(.*?)</think>', re.DOTALL | re.IGNORECASE),
            (r'<scratchpad>(.*?)</scratchpad>', re.DOTALL | re.IGNORECASE),
            (r'<inner_thoughts>(.*?)</inner_thoughts>', re.DOTALL | re.IGNORECASE),
            # Markdown-style
            (r'\[THOUGHT\](.*?)\[/THOUGHT\]', re.DOTALL | re.IGNORECASE),
            (r'\[THINKING\](.*?)\[/THINKING\]', re.DOTALL | re.IGNORECASE),
            (r'\[REASONING\](.*?)\[/REASONING\]', re.DOTALL | re.IGNORECASE),
            # Parentheses or brackets
            (r'\(let me think.*?\)', re.IGNORECASE),
            (r'\(reasoning:.*?\)', re.IGNORECASE),
            (r'\(thinking.*?\)', re.IGNORECASE),
        ]
        
        thought_process = None
        
        for pattern, flags in patterns:
            matches = re.findall(pattern, text, flags)
            if matches:
                # Extract the longest thought process found
                for match in matches:
                    if thought_process is None or len(match) > len(thought_process):
                        thought_process = match.strip()
        
        if thought_process:
            # Remove the thought process from the visible text
            for pattern, flags in patterns:
                text = re.sub(pattern, '', text, flags=flags).strip()
            # Clean up extra whitespace that might remain
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple newlines with double newline
            text = text.strip()
        
        return text, thought_process

    def _add_message(
        self,
        role: str,
        text: str,
        auto_scroll: bool = True,
        meta: dict[str, object] | None = None,
    ) -> tuple[tk.Frame, tk.Label]:
        """Render one chat bubble row for assistant/user/system messages."""
        row = tk.Frame(self.message_frame, bg=COLORS["panel"])
        row.pack(fill="x", padx=12, pady=6)

        bubble_bg = COLORS["assistant_bubble"]
        fg = COLORS["text"]
        anchor = "w"
        padding = (0, 220)
        bubble_font = ("Segoe UI", 11)
        justify = "left"

        if role == "user":
            bubble_bg = COLORS["user_bubble"]
            anchor = "e"
            padding = (220, 0)
        elif role == "system":
            bubble_bg = COLORS["system_bubble"]
            fg = COLORS["muted"]
            anchor = "center"
            padding = (140, 140)
            bubble_font = ("Segoe UI", 10)
            justify = "center"

        bubble = tk.Label(
            row,
            text=text,
            wraplength=720,
            justify=justify,
            bg=bubble_bg,
            fg=fg,
            font=bubble_font,
            padx=14,
            pady=10,
        )
        bubble.pack(anchor=anchor, padx=padding)

        # Extract thought process from the message text
        visible_text, thought_process = self._extract_thought_process(text)
        
        # If there's a thought process, update the bubble text to show only the visible part
        if thought_process:
            bubble.config(text=visible_text)
            # Store the thought process in the meta for later retrieval
            if meta is None:
                meta = {}
            meta['thought_process'] = thought_process
            # Store the original visible text for toggling
            meta['original_content'] = visible_text
        
        hover_text = self._build_message_hover_text(role, text, meta or {})
        for widget in (row, bubble):
            widget.bind("<Enter>", lambda event, txt=hover_text: self._show_message_hover(event, txt))
            widget.bind("<Motion>", self._move_message_hover)
            widget.bind("<Leave>", self._hide_message_hover)
            
            # Add right-click context menu for showing thought process
            if role == "assistant" and meta and meta.get('thought_process'):
                original_content = meta.get('original_content', visible_text)
                widget.bind("<Button-3>", lambda event, b=bubble, tp=meta['thought_process'], oc=original_content: 
                           self._show_thought_process_context_menu(event, b, tp, oc))

        if auto_scroll:
            self.after(30, lambda: self.messages_canvas.yview_moveto(1.0))
        return row, bubble

    def _get_reasoning_effort(self, is_agent: bool = False) -> int:
        """Get the appropriate reasoning effort level based on context.
        
        Args:
            is_agent: Whether this is for an agent request (True) or regular chat (False)
        """
        if is_agent:
            return self.agent_reasoning_effort_var.get()
        else:
            return self.reasoning_effort_var.get()

    def _show_thought_process_context_menu(self, event, bubble_widget, thought_process, original_content=None):
        """Show context menu with option to toggle thought process visibility."""
        # Create a context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Check if thought process is currently visible by looking for the marker
        current_text = bubble_widget.cget('text')
        is_visible = f"<thinking>" in current_text and f"{thought_process}" in current_text
        
        if is_visible:
            # Add option to hide the thought process
            context_menu.add_command(
                label="Hide Thought Process",
                command=lambda: self._hide_thought_process(bubble_widget, original_content)
            )
        else:
            # Add option to show the thought process
            context_menu.add_command(
                label="Show Thought Process",
                command=lambda: self._display_thought_process(bubble_widget, thought_process, original_content)
            )
        
        # Show the context menu at the mouse position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _display_thought_process(self, bubble_widget, thought_process, original_content=None):
        """Display the thought process in the bubble."""
        # Use the original content if provided, otherwise get current text
        if original_content:
            current_text = original_content
        else:
            current_text = bubble_widget.cget('text')
            # Remove any existing thought process markers to avoid duplication
            if "<thinking>" in current_text and "</thinking>" in current_text:
                # Extract the original content without thought process
                import re
                original_parts = re.split(r'<thinking>.*?</thinking>', current_text, flags=re.DOTALL)
                current_text = ''.join(original_parts).strip()
        
        full_text = f"{current_text}\n\n<thinking>\n{thought_process}\n</thinking>"
        bubble_widget.config(text=full_text)

    def _hide_thought_process(self, bubble_widget, original_content):
        """Hide the thought process in the bubble."""
        # Use the original content to restore the bubble text
        if original_content:
            bubble_widget.config(text=original_content)

    def _show_typing(self) -> None:
        """Insert the typing indicator row for in-flight chat requests."""
        if self.typing_row is not None:
            return
        row, label = self._add_message("assistant", "Thinking.")
        self.typing_row = row
        self.typing_label = label
        self.typing_tick = 1
        self._animate_typing()

    def _animate_typing(self) -> None:
        """Animate typing indicator dots while a reply is pending."""
        if self.typing_label is None:
            return
        self.typing_tick = 1 if self.typing_tick >= 3 else self.typing_tick + 1
        self.typing_label.configure(text=f"Thinking{'.' * self.typing_tick}")
        self.typing_animation_id = self.after(420, self._animate_typing)

    def _hide_typing(self) -> None:
        """Remove the typing indicator row and stop its animation timer."""
        if self.typing_animation_id is not None:
            self.after_cancel(self.typing_animation_id)
            self.typing_animation_id = None
        if self.typing_row is not None:
            self.typing_row.destroy()
            self.typing_row = None
            self.typing_label = None

    def _prepare_messages(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        """Prepare messages before sending requests."""
        cleaned: list[dict[str, str]] = []
        for message in history:
            role = message.get("role")
            content = message.get("content", "").strip()
            # Keep only roles accepted by every provider adapter.
            if role not in {"system", "user", "assistant"}:
                continue
            if not content:
                continue
            cleaned.append({"role": role, "content": content})

        # Ensure conversations always have a leading system instruction for stable behavior.
        if not cleaned or cleaned[0]["role"] != "system":
            system_prompt = os.getenv(
                "SYSTEM_PROMPT",
                "You are a helpful AI assistant inside a desktop chatroom app.",
            )
            cleaned.insert(0, {"role": "system", "content": system_prompt})

        return cleaned

    def _prepare_agent_messages(
        self,
        history: list[dict[str, str]],
        ide_kind: str,
    ) -> list[dict[str, str]]:
        """Prepare agent messages before sending requests.

        This function ensures that:
        1. Only valid message roles (system/user/assistant) are included
        2. The agent ALWAYS receives its system prompt (critical for consistent behavior)
        3. Empty messages are filtered out
        4. The system prompt is always at position 0 in the message list

        Args:
            history: List of message dicts from conversation history
            ide_kind: Type of IDE mode ("python" or "web")

        Returns:
            Cleaned list of messages with system prompt guaranteed at position 0
        """
        # Step 1: Clean and validate all messages from history
        cleaned: list[dict[str, str]] = []
        for message in history:
            role = message.get("role")
            content = message.get("content", "").strip()

            # Keep only roles accepted by every provider adapter
            # This ensures compatibility across Groq, OpenAI, Claude, etc.
            if role not in {"system", "user", "assistant"}:
                continue

            # Skip empty messages - they provide no value
            if not content:
                continue

            # Filter out temporary attachment paths from the content
            filtered_content = self._filter_attachment_paths_from_text(content)
            
            # Only add if there's content after filtering
            if filtered_content.strip():
                cleaned.append({"role": role, "content": filtered_content})

        # Step 2: ALWAYS ensure we have the agent system prompt
        # This is CRITICAL - without it, the agent won't know to write code in fenced blocks
        # and will just respond conversationally instead of updating the editor

        # Try to get the user-editable agent prompt from the UI first
        if hasattr(self, "agent_prompt_input"):
            system_prompt = self.agent_prompt_input.get("1.0", "end-1c").strip()
        else:
            # Fallback to defaults if UI not available (shouldn't happen in normal usage)
            if ide_kind == "web":
                system_prompt = WEB_AGENT_PROMPT
            else:
                system_prompt = PYTHON_AGENT_PROMPT

        # Step 3: If system prompt is still empty, use environment variables or hardcoded defaults
        # This provides multiple layers of fallback to ensure we always have a prompt
        if not system_prompt:
            if ide_kind == "web":
                system_prompt = os.getenv(
                    "AGENT_SYSTEM_PROMPT_WEB",
                    WEB_AGENT_PROMPT,
                )
            else:
                system_prompt = os.getenv(
                    "AGENT_SYSTEM_PROMPT",
                    PYTHON_AGENT_PROMPT,
                )

        # Step 4: Remove any existing system messages and add fresh one at the start
        # This ensures the agent ALWAYS gets its instructions, even on 2nd, 3rd, Nth prompts
        # Previously this was conditional which caused the "only works on first prompt" bug
        cleaned = [msg for msg in cleaned if msg["role"] != "system"]
        cleaned.insert(0, {"role": "system", "content": system_prompt})

        return cleaned


    def _provider_temperature(self, provider: str) -> float:
        """Compute temperature for provider-specific behavior."""
        value = os.getenv(
            f"{provider.upper()}_TEMPERATURE",
            os.getenv("LLM_TEMPERATURE", os.getenv("GROQ_TEMPERATURE", "0.7")),
        )
        try:
            return float(value)
        except ValueError:
            return 0.7

    def _provider_max_tokens(self, provider: str) -> int:
        """Compute max tokens for provider-specific behavior."""
        value = os.getenv(
            f"{provider.upper()}_MAX_TOKENS",
            os.getenv("LLM_MAX_TOKENS", os.getenv("GROQ_MAX_TOKENS", "1024")),
        )
        try:
            return max(1, int(value))
        except ValueError:
            return 1024

    def _provider_model_text(self, provider: str, model: str) -> str:
        """Compute model text for provider-specific behavior."""
        return f"{self._provider_label(provider)} · {model}"

    def _extract_openai_compatible_text(self, payload: dict[str, object]) -> str:
        """Extract assistant text from an OpenAI-compatible completion payload."""
        choices = payload.get("choices", [])
        if not isinstance(choices, list) or not choices:
            return ""

        first = choices[0]
        if not isinstance(first, dict):
            return ""

        message = first.get("message")
        if not isinstance(message, dict):
            return ""

        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                text = str(item.get("text", "")).strip()
                if text:
                    parts.append(text)
            return "\n".join(parts).strip()
        return ""

    def _extract_openai_compatible_usage(self, payload: dict[str, object]) -> dict[str, int]:
        """Extract usage token fields from an OpenAI-compatible response payload."""
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            return {}

        result: dict[str, int] = {}
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        if isinstance(prompt_tokens, (int, float)) and prompt_tokens >= 0:
            result["prompt_tokens"] = int(round(prompt_tokens))
        if isinstance(completion_tokens, (int, float)) and completion_tokens >= 0:
            result["completion_tokens"] = int(round(completion_tokens))
        if isinstance(total_tokens, (int, float)) and total_tokens >= 0:
            result["total_tokens"] = int(round(total_tokens))
        return result

    def _extract_anthropic_usage(self, payload: dict[str, object]) -> dict[str, int]:
        """Extract usage token fields from an Anthropic response payload."""
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            return {}

        result: dict[str, int] = {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if isinstance(input_tokens, (int, float)) and input_tokens >= 0:
            result["prompt_tokens"] = int(round(input_tokens))
        if isinstance(output_tokens, (int, float)) and output_tokens >= 0:
            result["completion_tokens"] = int(round(output_tokens))
        if "prompt_tokens" in result and "completion_tokens" in result:
            result["total_tokens"] = result["prompt_tokens"] + result["completion_tokens"]
        return result

    def _extract_gemini_usage(self, payload: dict[str, object]) -> dict[str, int]:
        """Extract usage token fields from a Gemini response payload."""
        usage = payload.get("usageMetadata")
        if not isinstance(usage, dict):
            return {}

        result: dict[str, int] = {}
        prompt_tokens = usage.get("promptTokenCount")
        completion_tokens = usage.get("candidatesTokenCount")
        total_tokens = usage.get("totalTokenCount")

        if isinstance(prompt_tokens, (int, float)) and prompt_tokens >= 0:
            result["prompt_tokens"] = int(round(prompt_tokens))
        if isinstance(completion_tokens, (int, float)) and completion_tokens >= 0:
            result["completion_tokens"] = int(round(completion_tokens))
        if isinstance(total_tokens, (int, float)) and total_tokens >= 0:
            result["total_tokens"] = int(round(total_tokens))
        return result

    def _build_assistant_meta(
        self,
        provider: str,
        model: str,
        reply_text: str,
        usage: dict[str, int],
        response_seconds: float,
    ) -> dict[str, object]:
        """Build metadata used for hover details on assistant replies."""
        meta: dict[str, object] = {
            "provider": provider,
            "model": model,
            "response_seconds": round(max(0.0, response_seconds), 3),
        }
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = usage.get(key)
            if isinstance(value, int) and value >= 0:
                meta[key] = value
        if "completion_tokens" in usage:
            meta["token_count"] = usage["completion_tokens"]
            meta["token_source"] = "provider"
        elif "total_tokens" in usage:
            meta["token_count"] = usage["total_tokens"]
            meta["token_source"] = "provider"
        else:
            meta["token_count"] = self._estimate_token_count(reply_text)
            meta["token_source"] = "estimated"
        return meta

    def _chat_with_openai_compatible(
        self,
        provider: str,
        model: str,
        messages: list[dict[str, str]],
        is_agent: bool = False,
    ) -> tuple[str, dict[str, int]]:
        """Send a chat request using the openai compatible adapter."""
        base_url = OPENAI_COMPATIBLE_BASE_URL.get(provider, "")
        if not base_url:
            raise RuntimeError(f"Unsupported provider: {provider}")
        api_key = self._get_api_key(provider)
        if not api_key:
            raise RuntimeError(self._missing_key_message(provider))

        # Adjust temperature based on reasoning effort
        base_temp = self._provider_temperature(provider)
        reasoning_effort = self._get_reasoning_effort(is_agent=is_agent)
        
        if reasoning_effort == 0:  # Low effort
            adjusted_temp = min(base_temp, 0.3)  # More deterministic
        elif reasoning_effort == 2:  # High effort
            adjusted_temp = max(base_temp, 0.8)  # More creative exploration
        else:  # Standard effort
            adjusted_temp = base_temp
        
        payload = self._http_json(
            method="POST",
            url=f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            body={
                "model": model,
                "messages": messages,
                "temperature": adjusted_temp,
                "max_tokens": self._provider_max_tokens(provider),
            },
        )
        text = self._extract_openai_compatible_text(payload)
        if text:
            return text, self._extract_openai_compatible_usage(payload)
        raise RuntimeError("No content returned.")

    def _chat_with_groq(self, model: str, messages: list[dict[str, str]], is_agent: bool = False) -> tuple[str, dict[str, int]]:
        """Send a chat request using the groq adapter."""
        api_key = self._get_api_key("groq")
        if not api_key:
            raise RuntimeError(self._missing_key_message("groq"))

        try:
            client = Groq(api_key=api_key)
        except TypeError as e:
            if "proxies" in str(e):
                # Handle the case where proxy settings cause issues with Groq client
                # Create the client without passing proxy-related arguments
                import os
                # Temporarily unset proxy environment variables if present
                original_http_proxy = os.environ.pop('HTTP_PROXY', None)
                original_https_proxy = os.environ.pop('HTTPS_PROXY', None)
                
                try:
                    client = Groq(api_key=api_key)
                finally:
                    # Restore original proxy settings
                    if original_http_proxy:
                        os.environ['HTTP_PROXY'] = original_http_proxy
                    if original_https_proxy:
                        os.environ['HTTPS_PROXY'] = original_https_proxy
            else:
                raise
        
        # Adjust temperature based on reasoning effort
        base_temp = self._provider_temperature("groq")
        reasoning_effort = self._get_reasoning_effort(is_agent=is_agent)
        
        if reasoning_effort == 0:  # Low effort
            adjusted_temp = min(base_temp, 0.3)  # More deterministic
        elif reasoning_effort == 2:  # High effort
            adjusted_temp = max(base_temp, 0.8)  # More creative exploration
        else:  # Standard effort
            adjusted_temp = base_temp
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=adjusted_temp,
            max_completion_tokens=self._provider_max_tokens("groq"),
        )
        text = (completion.choices[0].message.content or "").strip()
        if text:
            usage_raw = getattr(completion, "usage", None)
            usage: dict[str, int] = {}
            if usage_raw is not None:
                prompt_tokens = getattr(usage_raw, "prompt_tokens", None)
                completion_tokens = getattr(usage_raw, "completion_tokens", None)
                total_tokens = getattr(usage_raw, "total_tokens", None)
                if isinstance(prompt_tokens, int) and prompt_tokens >= 0:
                    usage["prompt_tokens"] = prompt_tokens
                if isinstance(completion_tokens, int) and completion_tokens >= 0:
                    usage["completion_tokens"] = completion_tokens
                if isinstance(total_tokens, int) and total_tokens >= 0:
                    usage["total_tokens"] = total_tokens
            return text, usage
        raise RuntimeError("No content returned.")

    def _chat_with_anthropic(self, model: str, messages: list[dict[str, str]], is_agent: bool = False) -> tuple[str, dict[str, int]]:
        """Send a chat request using the anthropic adapter."""
        api_key = self._get_api_key("anthropic")
        if not api_key:
            raise RuntimeError(self._missing_key_message("anthropic"))

        system_blocks = [m["content"] for m in messages if m.get("role") == "system"]
        chat_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m.get("role") in {"user", "assistant"}
        ]
        if not chat_messages:
            chat_messages = [{"role": "user", "content": "Hello"}]

        body: dict[str, object] = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": self._provider_max_tokens("anthropic"),
            "temperature": self._provider_temperature("anthropic"),
        }
        
        # Add reasoning effort settings based on user selection
        reasoning_effort = self._get_reasoning_effort(is_agent=is_agent)
        if reasoning_effort == 0:  # Low effort
            body["temperature"] = min(body["temperature"], 0.3)  # Lower temperature for more focused responses
        elif reasoning_effort == 2:  # High effort
            # For Claude models, we can enable advanced reasoning features
            body["extra_body"] = {
                "beta": ["reasoning"]  # Enable reasoning beta feature if available
            }
            # Higher temperature for more creative, thorough responses
            body["temperature"] = max(body["temperature"], 0.8)
        
        if system_blocks:
            body["system"] = "\n\n".join(system_blocks)

        payload = self._http_json(
            method="POST",
            url="https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            },
            body=body,
        )
        content = payload.get("content", [])
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                if str(item.get("type", "")).strip() != "text":
                    continue
                text = str(item.get("text", "")).strip()
                if text:
                    text_parts.append(text)
            if text_parts:
                return "\n".join(text_parts).strip(), self._extract_anthropic_usage(payload)
        raise RuntimeError("No content returned.")

    def _chat_with_gemini(self, model: str, messages: list[dict[str, str]], is_agent: bool = False) -> tuple[str, dict[str, int]]:
        """Send a chat request using the gemini adapter."""
        api_key = self._get_api_key("gemini")
        if not api_key:
            raise RuntimeError(self._missing_key_message("gemini"))

        system_blocks: list[str] = []
        contents: list[dict[str, object]] = []
        for item in messages:
            role = item.get("role")
            text = item.get("content", "").strip()
            if not text:
                continue
            if role == "system":
                system_blocks.append(text)
                continue
            if role == "assistant":
                gem_role = "model"
            elif role == "user":
                gem_role = "user"
            else:
                continue
            contents.append({"role": gem_role, "parts": [{"text": text}]})

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        # Adjust temperature based on reasoning effort
        base_temp = self._provider_temperature("gemini")
        reasoning_effort = self._get_reasoning_effort(is_agent=is_agent)
        
        if reasoning_effort == 0:  # Low effort
            adjusted_temp = min(base_temp, 0.3)  # More deterministic
        elif reasoning_effort == 2:  # High effort
            adjusted_temp = max(base_temp, 0.8)  # More creative exploration
        else:  # Standard effort
            adjusted_temp = base_temp

        body: dict[str, object] = {
            "contents": contents,
            "generationConfig": {
                "temperature": adjusted_temp,
                "maxOutputTokens": self._provider_max_tokens("gemini"),
            },
        }
        if system_blocks:
            body["systemInstruction"] = {
                "parts": [{"text": "\n\n".join(system_blocks)}],
            }

        model_path = urlparse.quote(model, safe="")
        payload = self._http_json(
            method="POST",
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{model_path}:generateContent",
            headers={"x-goog-api-key": api_key},
            body=body,
        )
        candidates = payload.get("candidates", [])
        if isinstance(candidates, list) and candidates:
            first = candidates[0]
            if isinstance(first, dict):
                content = first.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    if isinstance(parts, list):
                        text_parts: list[str] = []
                        for part in parts:
                            if not isinstance(part, dict):
                                continue
                            text = str(part.get("text", "")).strip()
                            if text:
                                text_parts.append(text)
                        if text_parts:
                            return "\n".join(text_parts).strip(), self._extract_gemini_usage(payload)
        raise RuntimeError("No content returned.")

    def _chat_with_provider(
        self,
        provider: str,
        model: str,
        messages: list[dict[str, str]],
        is_agent: bool = False,
    ) -> tuple[str, dict[str, int]]:
        """Send a chat request using the provider adapter."""
        wanted = provider.strip().lower()
        if wanted == "groq":
            return self._chat_with_groq(model, messages, is_agent)
        if wanted in OPENAI_COMPATIBLE_BASE_URL:
            return self._chat_with_openai_compatible(wanted, model, messages, is_agent)
        if wanted == "anthropic":
            return self._chat_with_anthropic(model, messages, is_agent)
        if wanted == "gemini":
            return self._chat_with_gemini(model, messages, is_agent)
        raise RuntimeError(f"Unsupported provider: {provider}")

    def send_message(self, preset_text: str | None = None) -> None:
        """Queue a user message and dispatch the async chat completion request."""
        if self.pending:
            return

        chat = self._current_chat()
        if chat is None:
            self._create_chat()
            chat = self._current_chat()
        if chat is None:
            return

        if preset_text is None:
            user_text = self.input_box.get("1.0", "end-1c").strip()
        else:
            user_text = preset_text.strip()
        if not user_text:
            return

        messages = chat.get("messages")
        if not isinstance(messages, list):
            messages = []
            chat["messages"] = messages
        # Persist the user message immediately so UI and disk stay in sync even on request failure.
        user_meta = self._normalize_message_meta({}, role="user", content=user_text)
        messages.append({"role": "user", "content": user_text, "meta": user_meta})
        self._add_message("user", user_text, meta=user_meta)

        user_count = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == "user")
        if user_count == 1:
            chat["title"] = self._chat_title_from_text(user_text)
            self._refresh_chat_list()
        self._save_conversations()

        if preset_text is None:
            self.input_box.delete("1.0", "end")
            self._adjust_input_height()

        chat_id = str(chat["id"])
        self.pending = True
        self.pending_chat_id = chat_id
        self._set_chat_controls_enabled(False)
        self.status_var.set("Thinking...")
        self._show_typing()

        # Copy current history for the worker thread so later UI mutations do not race.
        payload = [dict(item) for item in messages if isinstance(item, dict)]
        provider = self.provider_var.get().strip().lower()
        model = self.model_var.get().strip()
        thread = threading.Thread(
            target=self._request_completion,
            args=(payload, provider, model, chat_id),
            daemon=True,
        )
        thread.start()

    def _request_completion(
        self,
        history: list[dict[str, str]],
        provider: str,
        model: str,
        chat_id: str,
    ) -> None:
        """Run one provider chat completion request and push the result to the UI queue."""
        # Validate fast-fail conditions before incurring provider latency.
        if provider not in PROVIDERS:
            self.event_queue.put(
                {
                    "type": "chat_error",
                    "chat_id": chat_id,
                    "message": f"Unknown provider: {provider}",
                }
            )
            return

        if not model or model == MODEL_PLACEHOLDER:
            self.event_queue.put(
                {
                    "type": "chat_error",
                    "chat_id": chat_id,
                    "message": "Select a model first.",
                }
            )
            return

        if not self._has_key(provider):
            self.event_queue.put(
                {
                    "type": "chat_error",
                    "chat_id": chat_id,
                    "message": self._missing_key_message(provider),
                }
            )
            return

        messages = self._prepare_messages(history)
        try:
            # Monotonic clock avoids wall-clock jumps in latency stats.
            started = time.monotonic()
            reply_text, usage = self._chat_with_provider(provider, model, messages, is_agent=False)
            elapsed = max(0.0, time.monotonic() - started)
            meta = self._build_assistant_meta(
                provider=provider,
                model=model,
                reply_text=reply_text,
                usage=usage,
                response_seconds=elapsed,
            )
            self.event_queue.put(
                {
                    "type": "chat_reply",
                    "chat_id": chat_id,
                    "message": reply_text,
                    "provider": provider,
                    "model": model,
                    "meta": meta,
                }
            )
        except Exception as exc:  # noqa: BLE001
            # Workers never touch widgets directly; all failures become queue events.
            self.event_queue.put(
                {
                    "type": "chat_error",
                    "chat_id": chat_id,
                    "message": f"{self._provider_label(provider)} request failed: {exc}",
                }
            )

    def _path_relative_to_project(self, path: Path) -> Path | None:
        """Return the path relative to current project root when possible."""
        if self.project_root is None:
            return None
        try:
            return path.resolve().relative_to(self.project_root.resolve())
        except ValueError:
            return None
        except OSError:
            return None

    def _display_path(self, path: Path) -> str:
        """Return a user-facing path string relative to project root when possible."""
        rel = self._path_relative_to_project(path)
        if rel is not None:
            return str(rel)
        return str(path)

    def _is_code_file(self, path: Path) -> bool:
        """Check if a file is a code file based on its extension."""
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.htm', '.css', '.json', 
            '.xml', '.yaml', '.yml', '.md', '.txt', '.sql', '.sh', '.bash', 
            '.cpp', '.c', '.h', '.hpp', '.java', '.go', '.rs', '.rb', '.php'
        }
        return path.suffix.lower() in code_extensions

    def _is_temp_attachment_path(self, text: str) -> bool:
        """Check if text contains temporary attachment paths that should be filtered out."""
        # Check if the text looks like a temporary file path containing attachment indicators
        text_lower = text.strip().lower()
        # Remove @ prefix if present
        if text_lower.startswith('@'):
            text_lower = text_lower[1:]
        if '/tmp/' in text_lower and 'ai-chat-attachment' in text_lower:
            return True
        if '/tmp/' in text_lower and 'attachment' in text_lower and len(text_lower) < 100:
            return True
        return False

    def _filter_attachment_paths_from_text(self, text: str) -> str:
        """Remove temporary attachment paths from text to prevent agent from echoing them."""
        import re
        
        # Remove lines that look like temporary attachment paths
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Skip lines that look like temporary attachment paths (with or without @ prefix)
            if ('/tmp/' in line_lower and 'ai-chat-attachment' in line_lower) or \
               ('/tmp/' in line_lower and 'attachment' in line_lower and len(line_stripped) < 100):
                continue
            # Also check for paths that start with @ followed by the attachment pattern
            if line_stripped.startswith('@') and '/tmp/' in line_lower and 'ai-chat-attachment' in line_lower:
                continue
            # Skip lines that look like content markers for empty files
            if '--- Content from referenced files ---' in line or \
               '--- End of content ---' in line:
                continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def _looks_like_code(self, text: str) -> bool:
        """Heuristic to determine if text looks like code."""
        # Count lines that look like code vs prose
        lines = text.split('\n')
        code_lines = 0
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines == 0:
            return False
        
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('def ') or 
                stripped.startswith('class ') or 
                stripped.startswith('import ') or 
                stripped.startswith('from ') or 
                stripped.startswith('function ') or 
                stripped.startswith('<') or  # HTML
                ':' in stripped and '{' in stripped or  # CSS
                '=' in stripped or  # Assignment
                stripped.endswith(':') or  # Function/class definitions
                stripped.startswith('return ') or  # Return statements
                stripped.startswith('if ') or  # Conditional statements
                stripped.startswith('for ') or  # Loop statements
                stripped.startswith('while ') or  # Loop statements
                stripped.startswith('try:') or  # Try statements
                stripped.startswith('except ') or  # Except statements
                stripped.startswith('with ') or  # With statements
                line.startswith('    ') or  # Indented code
                line.startswith('\t') or  # Tab-indented code
                stripped.count('(') > 0 and stripped.count(')') > 0):  # Function calls
                code_lines += 1
        
        # If more than half the lines look like code, treat as code
        return (code_lines / total_lines) > 0.5

    def _update_project_label(self) -> None:
        """Update the sidebar label showing the current project folder."""
        root = self.project_root
        if root is None:
            self.project_label_var.set("Folder: (none opened)")
            return
        try:
            home = Path.home().resolve()
            rel = root.resolve().relative_to(home)
            text = "~" if str(rel) == "." else f"~/{rel}"
        except (ValueError, OSError):
            text = str(root)
        self.project_label_var.set(f"Folder: {text}")

    def _choose_project_folder(self) -> None:
        """Open a picker and choose project folder."""
        initial_dir = self.project_root if self.project_root is not None else Path.cwd()
        selected = filedialog.askdirectory(
            parent=self,
            title="Open Folder",
            initialdir=str(initial_dir),
        )
        if not selected:
            return

        self.project_root = Path(selected).resolve()
        self._update_project_label()
        self._refresh_project_file_list(select_current=True)
        self.ide_status_var.set(f"Opened folder {self.project_root}")

    def _choose_file_from_disk(self) -> None:
        """Open a picker and choose file from disk."""
        initial_dir = self.project_root if self.project_root is not None else Path.cwd()
        selected = filedialog.askopenfilename(
            parent=self,
            title="Open File",
            initialdir=str(initial_dir),
        )
        if not selected:
            return

        path = Path(selected).resolve()
        if self._path_relative_to_project(path) is None:
            self.project_root = path.parent
            self._update_project_label()

        self.open_file_in_editor(path)
        self._refresh_project_file_list(select_current=True)

    def _iter_project_files(self) -> list[Path]:
        """Collect visible project files while skipping ignored directories."""
        files: list[Path] = []
        if self.project_root is None:
            return files
        if not self.project_root.exists() or not self.project_root.is_dir():
            return files
        for path in self.project_root.rglob("*"):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(self.project_root).parts
            if any(part in IGNORED_DIRS for part in rel_parts):
                continue
            files.append(path)
        files.sort(key=lambda p: str(p.relative_to(self.project_root)).lower())
        return files

    def _refresh_project_file_list(self, select_current: bool = False) -> None:
        """Refresh project file list to match current state."""
        self.ide_files = self._iter_project_files()
        self.file_listbox.delete(0, "end")
        selected_idx = None

        for idx, path in enumerate(self.ide_files):
            self.file_listbox.insert("end", self._display_path(path))
            if select_current and self.ide_current_file is not None and path == self.ide_current_file:
                selected_idx = idx

        if selected_idx is not None:
            self.file_listbox.selection_clear(0, "end")
            self.file_listbox.selection_set(selected_idx)
            self.file_listbox.activate(selected_idx)

    def _on_file_selected(self, _event: tk.Event) -> None:
        """Handle the file selected event."""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        index = int(selection[0])
        if index < 0 or index >= len(self.ide_files):
            return
        self.open_file_in_editor(self.ide_files[index])

    def open_file_in_editor(self, path: Path) -> None:
        """Load a file into the IDE editor and update file status indicators."""
        try:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self.ide_status_var.set(f"Open failed: {exc}")
            return

        self._ide_loading = True
        self.ide_editor.delete("1.0", "end")
        self.ide_editor.insert("1.0", content)
        self._ide_loading = False

        self.ide_current_file = path
        self.ide_dirty = False
        shown = self._display_path(path)
        self.ide_file_var.set(shown)
        self.ide_tab_title_var.set(shown)
        self.ide_status_var.set(f"Loaded {shown}")
        self._refresh_ide_line_numbers()
        self._update_ide_cursor_position()
        self._schedule_ide_syntax_highlight(delay_ms=10)

    def _on_ide_editor_scrollbar(self, *args: str) -> None:
        """Scroll editor and line-number gutter together from scrollbar input."""
        self.ide_editor.yview(*args)
        self.ide_line_numbers.yview(*args)

    def _on_ide_editor_yscroll(self, first: str, last: str) -> None:
        """Synchronize line-number gutter and scrollbar with editor scroll."""
        self.ide_editor_scroll.set(first, last)
        self.ide_line_numbers.yview_moveto(float(first))

    def _refresh_ide_line_numbers(self) -> None:
        """Refresh visible line numbers in the editor gutter."""
        if not hasattr(self, "ide_line_numbers"):
            return
        line_count = int(self.ide_editor.index("end-1c").split(".")[0])
        if line_count == self.ide_line_count:
            return
        first_view = self.ide_editor.yview()[0]
        self.ide_line_count = line_count

        lines = "\n".join(str(num) for num in range(1, line_count + 1))
        self.ide_line_numbers.configure(state="normal")
        self.ide_line_numbers.delete("1.0", "end")
        self.ide_line_numbers.insert("1.0", lines)
        self.ide_line_numbers.configure(state="disabled")
        self.ide_line_numbers.yview_moveto(first_view)

    def _update_ide_cursor_position(self, _event: tk.Event | None = None) -> None:
        """Update status bar cursor position (`Ln`, `Col`) for the active editor."""
        index = self.ide_editor.index("insert")
        line_str, col_str = index.split(".")
        line = int(line_str)
        col = int(col_str) + 1
        self.ide_cursor_var.set(f"Ln {line}, Col {col}")

    def _configure_ide_syntax_tags(self) -> None:
        """Configure editor tags used for Python syntax highlighting."""
        self.ide_editor.tag_configure("syn_keyword", foreground=COLORS["syntax_keyword"])
        self.ide_editor.tag_configure("syn_builtin", foreground=COLORS["syntax_builtin"])
        self.ide_editor.tag_configure("syn_string", foreground=COLORS["syntax_string"])
        self.ide_editor.tag_configure("syn_comment", foreground=COLORS["syntax_comment"])
        self.ide_editor.tag_configure("syn_number", foreground=COLORS["syntax_number"])
        self.ide_editor.tag_configure("syn_function", foreground=COLORS["syntax_function"])
        self.ide_editor.tag_configure("syn_class", foreground=COLORS["syntax_class"])
        self.ide_editor.tag_configure("syn_decorator", foreground=COLORS["syntax_decorator"])

    def _schedule_ide_syntax_highlight(self, delay_ms: int = 80) -> None:
        """Debounce syntax highlighting so rapid typing stays responsive."""
        if self.ide_syntax_job_id is not None:
            try:
                self.after_cancel(self.ide_syntax_job_id)
            except tk.TclError:
                pass
        self.ide_syntax_job_id = self.after(delay_ms, self._apply_ide_syntax_highlight)

    def _schedule_autosave(self, delay_ms: int = 3000) -> None:
        """Schedule autosave 3 seconds after user stops typing."""
        if self.ide_autosave_job_id is not None:
            try:
                self.after_cancel(self.ide_autosave_job_id)
            except tk.TclError:
                pass
        self.ide_autosave_job_id = self.after(delay_ms, self._autosave_current_file)

    def _autosave_current_file(self) -> None:
        """Automatically save the current file if it's been modified."""
        self.ide_autosave_job_id = None

        # Only autosave if file is dirty and user has a file open
        if not self.ide_dirty or self.ide_current_file is None:
            return

        try:
            content = self.ide_editor.get("1.0", "end-1c")
            self.ide_current_file.write_text(content, encoding="utf-8")

            # Update UI to show file is saved
            self.ide_dirty = False
            shown = self._display_path(self.ide_current_file)
            self.ide_file_var.set(shown)
            self.ide_tab_title_var.set(shown)
            self.ide_status_var.set(f"Autosaved {shown}")
        except OSError:
            # Silently fail on autosave errors - don't interrupt user
            pass

    def _ide_save_as(self) -> None:
        """Open a 'Save As' dialog to save the current editor content to a new file."""
        content = self.ide_editor.get("1.0", "end-1c")

        if not content.strip():
            self.ide_status_var.set("Nothing to save")
            return

        # Determine default filename and extension based on IDE kind
        ide_kind = self.ide_kind_var.get()
        if ide_kind == "web":
            filetypes = [("HTML files", "*.html"), ("All files", "*.*")]
            default_name = "index.html"
        else:
            filetypes = [("Python files", "*.py"), ("All files", "*.*")]
            default_name = "script.py"

        # Determine initial directory
        initial_dir = str(self.project_root) if self.project_root else str(Path.home())

        filepath = filedialog.asksaveasfilename(
            initialfile=default_name,
            initialdir=initial_dir,
            filetypes=filetypes,
            defaultextension=".py" if ide_kind == "python" else ".html",
            title="Save File As"
        )

        if not filepath:
            return

        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

            # Update IDE state to reflect the new file
            self.ide_current_file = path
            self.ide_dirty = False

            shown = self._display_path(path)
            self.ide_file_var.set(shown)
            self.ide_tab_title_var.set(shown)
            self.ide_status_var.set(f"Saved to {shown}")

            # Refresh project file list if applicable
            self._refresh_project_file_list()
        except OSError as e:
            self.ide_status_var.set(f"Save failed: {e}")

    def _tag_ide_token(self, tag: str, start: tuple[int, int], end: tuple[int, int]) -> None:
        """Apply a syntax tag to a token range inside the editor."""
        start_line, start_col = start
        end_line, end_col = end
        if start_line <= 0 or end_line <= 0:
            return
        if (start_line, start_col) >= (end_line, end_col):
            return
        self.ide_editor.tag_add(tag, f"{start_line}.{start_col}", f"{end_line}.{end_col}")

    def _apply_ide_syntax_highlight(self) -> None:
        """Apply Python syntax highlighting to the current editor buffer."""
        self.ide_syntax_job_id = None
        if not hasattr(self, "ide_editor"):
            return

        text = self.ide_editor.get("1.0", "end-1c")
        syntax_tags = (
            "syn_keyword",
            "syn_builtin",
            "syn_string",
            "syn_comment",
            "syn_number",
            "syn_function",
            "syn_class",
            "syn_decorator",
        )
        for tag in syntax_tags:
            self.ide_editor.tag_remove(tag, "1.0", "end")

        if not text:
            return

        # Avoid UI stalls on extremely large files in the Tk text widget.
        if len(text) > 350_000:
            return

        ignore_types = {
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.ENDMARKER,
            tokenize.ENCODING,
        }
        reader = io.StringIO(text).readline
        previous_significant: tokenize.TokenInfo | None = None

        try:
            for tok in tokenize.generate_tokens(reader):
                ttype = tok.type
                tstring = tok.string

                if ttype == tokenize.NAME:
                    if (
                        previous_significant is not None
                        and previous_significant.type == tokenize.OP
                        and previous_significant.string == "@"
                    ):
                        self._tag_ide_token("syn_decorator", tok.start, tok.end)
                    elif (
                        previous_significant is not None
                        and previous_significant.type == tokenize.NAME
                        and previous_significant.string == "def"
                    ):
                        self._tag_ide_token("syn_function", tok.start, tok.end)
                    elif (
                        previous_significant is not None
                        and previous_significant.type == tokenize.NAME
                        and previous_significant.string == "class"
                    ):
                        self._tag_ide_token("syn_class", tok.start, tok.end)
                    elif tstring in self.ide_python_keywords:
                        self._tag_ide_token("syn_keyword", tok.start, tok.end)
                    elif tstring in self.ide_python_builtins:
                        self._tag_ide_token("syn_builtin", tok.start, tok.end)
                elif ttype == tokenize.STRING:
                    self._tag_ide_token("syn_string", tok.start, tok.end)
                elif ttype == tokenize.COMMENT:
                    self._tag_ide_token("syn_comment", tok.start, tok.end)
                elif ttype == tokenize.NUMBER:
                    self._tag_ide_token("syn_number", tok.start, tok.end)

                if ttype not in ignore_types and ttype != tokenize.COMMENT:
                    previous_significant = tok
        except tokenize.TokenError:
            # Keep any partial highlighting we already applied.
            pass

    def _on_ide_kind_change(self, *_args: object) -> None:
        """Handle IDE kind change (Python to Web or vice versa)."""
        self._update_ide_panel_for_kind()

    def _update_ide_panel_for_kind(self) -> None:
        """Update the bottom panel to show browser or terminal based on IDE kind."""
        ide_kind = self.ide_kind_var.get()

        # Clear the output container
        for widget in self.ide_output_container.winfo_children():
            widget.destroy()

        if ide_kind == "web" and HtmlFrame is not None:
            # Show browser preview
            self.ide_panel_label.config(text="PREVIEW")
            self.ide_browser = HtmlFrame(self.ide_output_container, bg=COLORS["entry_bg"])
            self.ide_browser.pack(fill="both", expand=True)
            self._update_browser_preview()
        else:
            # Show terminal output
            self.ide_panel_label.config(text="TERMINAL")
            self.ide_output = tk.Text(
                self.ide_output_container,
                wrap="word",
                bg=COLORS["entry_bg"],
                fg=COLORS["text"],
                insertbackground=COLORS["text"],
                highlightthickness=1,
                highlightbackground=COLORS["border"],
                relief="flat",
                font=("Consolas", 10),
                padx=10,
                pady=10,
                state="disabled",
            )
            self.ide_output.pack(side="left", fill="both", expand=True)

            yscroll_output = tk.Scrollbar(
                self.ide_output_container,
                orient="vertical",
                command=self.ide_output.yview,
                troughcolor=COLORS["panel"],
                bg=COLORS["entry_bg"],
                activebackground="#1c2740",
                bd=0,
                highlightthickness=0,
            )
            yscroll_output.pack(side="right", fill="y")
            self.ide_output.configure(yscrollcommand=yscroll_output.set)

    def _schedule_browser_update(self, delay_ms: int = 500) -> None:
        """Schedule browser preview update after a delay."""
        if self.ide_browser_update_job_id is not None:
            try:
                self.after_cancel(self.ide_browser_update_job_id)
            except tk.TclError:
                pass
        self.ide_browser_update_job_id = self.after(delay_ms, self._update_browser_preview)

    def _update_browser_preview(self) -> None:
        """Update the browser preview with current HTML content."""
        self.ide_browser_update_job_id = None

        if self.ide_browser is None or HtmlFrame is None:
            return

        try:
            content = self.ide_editor.get("1.0", "end-1c")
            if not content.strip():
                content = "<html><body><p>Start typing HTML...</p></body></html>"

            # Create a temporary HTML file for the browser to load
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name

            # Store the temp path so we can clean it up later
            self.ide_preview_temp_path = Path(temp_path)

            # Load the HTML into the browser
            self.ide_browser.load_file(temp_path)
        except Exception as e:
            pass  # Silently fail on preview errors

    def _on_ide_editor_change(self, _event: tk.Event) -> None:
        """Handle the ide editor change event."""
        self._refresh_ide_line_numbers()
        self._update_ide_cursor_position()
        self._schedule_ide_syntax_highlight()
        self._schedule_autosave()

        # Update browser preview if in web mode
        if self.ide_kind_var.get() == "web":
            self._schedule_browser_update()

        if self._ide_loading:
            return
        self.ide_dirty = True
        if self.ide_current_file is not None:
            shown = self._display_path(self.ide_current_file)
            self.ide_file_var.set(f"{shown} *")
            self.ide_tab_title_var.set(f"{shown} *")
        else:
            self.ide_file_var.set("Unsaved scratch *")
            self.ide_tab_title_var.set("scratch.py *")

    def save_current_file(self) -> None:
        """Handle save current file."""
        if self.ide_current_file is None:
            self.ide_status_var.set("Select a file from the left sidebar first.")
            return
        try:
            content = self.ide_editor.get("1.0", "end-1c")
            self.ide_current_file.write_text(content, encoding="utf-8")
        except OSError as exc:
            self.ide_status_var.set(f"Save failed: {exc}")
            return

        self.ide_dirty = False
        shown = self._display_path(self.ide_current_file)
        self.ide_file_var.set(shown)
        self.ide_tab_title_var.set(shown)
        self.ide_status_var.set(f"Saved {shown}")

    def _handle_ctrl_s(self, _event: tk.Event) -> str | None:
        """Handle Ctrl+S in IDE mode by saving the current file."""
        if self.mode_var.get() == "ide":
            self.save_current_file()
            return "break"
        return None

    def _append_ide_output(self, text: str) -> None:
        """Append ide output to the visible output area."""
        if not text:
            return
        self.ide_output.configure(state="normal")
        self.ide_output.insert("end", text)
        self.ide_output.see("end")
        self.ide_output.configure(state="disabled")

    def clear_ide_output(self) -> None:
        """Clear the IDE console output panel."""
        self.ide_output.configure(state="normal")
        self.ide_output.delete("1.0", "end")
        self.ide_output.configure(state="disabled")

    def _set_ide_running(self, running: bool) -> None:
        """Set ide running state and related controls."""
        self.ide_running = running
        self.run_button.configure(state="disabled" if running else "normal")
        if self.ide_kind_var.get() == "python":
            self.stop_button.configure(state="normal" if running else "disabled")
        else:
            self.stop_button.configure(state="disabled")

    def _cleanup_web_preview_file(self) -> None:
        """Delete the last temporary web preview file, if one exists."""
        if self.ide_preview_temp_path is None:
            return
        try:
            self.ide_preview_temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        self.ide_preview_temp_path = None

    def _wrap_css_preview(self, css_code: str) -> str:
        """Wrap raw CSS into a previewable HTML document."""
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>CSS Preview</title>
    <style>
{css_code}
    </style>
  </head>
  <body>
    <main class="preview-root">
      <h1>CSS Preview</h1>
      <p>Your stylesheet is injected into this preview page.</p>
      <button>Sample Button</button>
    </main>
  </body>
</html>
"""

    def _wrap_js_preview(self, js_code: str) -> str:
        """Wrap raw JavaScript into a previewable HTML document."""
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>JavaScript Preview</title>
    <style>
      body {{
        font-family: "Segoe UI", sans-serif;
        margin: 2rem;
        background: #090d14;
        color: #e8edf5;
      }}
      #app {{
        border: 1px solid #263245;
        border-radius: 12px;
        padding: 1rem;
      }}
    </style>
  </head>
  <body>
    <main id="app">
      <h1>JavaScript Preview</h1>
      <p>Open devtools console to inspect output.</p>
    </main>
    <script>
{js_code}
    </script>
  </body>
</html>
"""

    def _preview_web_code(self, code: str) -> None:
        """Render current web editor content in the browser using file preview."""
        language = self._ide_language_for_path(self.ide_current_file)
        target_url = ""
        opened_label = ""

        # For saved HTML files, opening the real file preserves relative links/assets.
        if (
            self.ide_current_file is not None
            and language == "html"
            and self.ide_current_file.exists()
            and self.ide_current_file.is_file()
        ):
            if self.ide_dirty:
                self.save_current_file()
                if self.ide_dirty:
                    # Save failed, so we cannot reliably preview the latest buffer.
                    return
            target_url = self.ide_current_file.resolve().as_uri()
            opened_label = self._display_path(self.ide_current_file)
        else:
            if language == "css":
                preview_html = self._wrap_css_preview(code)
            elif language == "javascript":
                preview_html = self._wrap_js_preview(code)
            else:
                preview_html = code

            self._cleanup_web_preview_file()
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".html",
                delete=False,
                encoding="utf-8",
            ) as preview_file:
                preview_file.write(preview_html)
                temp_path = Path(preview_file.name).resolve()
            self.ide_preview_temp_path = temp_path
            target_url = temp_path.as_uri()
            opened_label = str(temp_path)

        opened = webbrowser.open_new_tab(target_url)
        self.clear_ide_output()
        self._append_ide_output(f"Web preview target: {opened_label}\n")
        if opened:
            self.ide_status_var.set("Preview opened in browser")
        else:
            self.ide_status_var.set("Preview URL generated (browser may be blocked)")

    def run_ide_code(self) -> None:
        """Run Python code or preview web code based on the selected IDE kind."""
        if self.ide_running:
            return

        code = self.ide_editor.get("1.0", "end-1c")
        if not code.strip():
            if self.ide_kind_var.get() == "web":
                self.ide_status_var.set("Add some HTML/CSS/JS first.")
            else:
                self.ide_status_var.set("Add some Python code first.")
            return

        if self.ide_kind_var.get() == "web":
            try:
                self._preview_web_code(code)
            except Exception as exc:  # noqa: BLE001
                self.clear_ide_output()
                self._append_ide_output(f"Preview failed: {exc}\n")
                self.ide_status_var.set("Preview failed")
            return

        self.clear_ide_output()
        self.ide_status_var.set("Running...")
        self._set_ide_running(True)

        thread = threading.Thread(target=self._execute_ide_code, args=(code,), daemon=True)
        thread.start()

    def stop_ide_code(self) -> None:
        """Stop the running IDE subprocess if one is active."""
        if self.ide_kind_var.get() != "python":
            self.ide_status_var.set("Web preview mode does not use a running subprocess.")
            return
        with self.ide_process_lock:
            process = self.ide_process
        if process is not None and process.poll() is None:
            process.terminate()
            self.ide_status_var.set("Stopping...")

    def _execute_ide_code(self, code: str) -> None:
        """Execute Python code in a temporary file and return captured output."""
        temp_path: str | None = None
        timeout_setting = os.getenv("IDE_RUN_TIMEOUT", "")  # Empty string means no timeout
        timeout_seconds = None if timeout_setting == "" else int(timeout_setting)  # None means no timeout

        try:
            # Run via a temp file so tracebacks include real line numbers from the editor buffer.
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            process = subprocess.Popen(
                # -u forces unbuffered stdio so console output appears promptly.
                [sys.executable, "-u", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            with self.ide_process_lock:
                # Protected write lets stop_ide_code safely terminate the same process.
                self.ide_process = process

            timed_out = False
            if timeout_seconds is None:
                # No timeout - wait indefinitely until process completes or is stopped by user
                stdout, stderr = process.communicate()
            else:
                # Timeout specified - wait up to timeout_seconds
                try:
                    stdout, stderr = process.communicate(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    # Hard-kill on timeout to avoid orphaned child processes.
                    process.kill()
                    stdout, stderr = process.communicate()
                    stderr = (stderr or "") + f"\nProcess timed out after {timeout_seconds} seconds."

            self.event_queue.put(
                {
                    "type": "ide_result",
                    "stdout": stdout or "",
                    "stderr": stderr or "",
                    "returncode": str(process.returncode if process.returncode is not None else -1),
                    "timed_out": "1" if timed_out else "0",
                }
            )
        except Exception as exc:  # noqa: BLE001
            self.event_queue.put({"type": "ide_error", "message": f"Run failed: {exc}"})
        finally:
            with self.ide_process_lock:
                self.ide_process = None
            if temp_path is not None:
                try:
                    # Best-effort cleanup; failures are non-fatal.
                    os.unlink(temp_path)
                except OSError:
                    pass

    def ask_ai_about_code(self) -> None:
        """Send the current editor code to chat mode for feedback and iteration help."""
        code = self.ide_editor.get("1.0", "end-1c").strip()
        if not code:
            self.ide_status_var.set("Editor is empty.")
            return

        ide_kind = self.ide_kind_var.get()
        language = self._ide_language_for_path(self.ide_current_file)
        scratch_name = self._default_scratch_filename_for_kind(ide_kind)
        filename = (
            self._display_path(self.ide_current_file)
            if self.ide_current_file is not None
            else scratch_name
        )
        if ide_kind == "web":
            prompt = (
                f"Help me vibe-code this web file: {filename}\n"
                "Review it, point out issues, and suggest the best next iteration.\n\n"
                f"```{language}\n{code}\n```"
            )
        else:
            prompt = (
                f"Help me vibe-code this Python file: {filename}\n"
                "Review it, point out issues, and suggest the best next iteration.\n\n"
                f"```python\n{code}\n```"
            )
        self.switch_mode("chat")
        self.send_message(preset_text=prompt)

    def _append_agent_output(self, text: str) -> None:
        """Append agent output to the visible output area."""
        if not text:
            return
        self.agent_output.configure(state="normal")
        self.agent_output.insert("end", text)
        self.agent_output.see("end")
        self.agent_output.configure(state="disabled")

    def clear_agent_output(self) -> None:
        """Clear the IDE agent output panel."""
        self.agent_output.configure(state="normal")
        self.agent_output.delete("1.0", "end")
        self.agent_output.configure(state="disabled")

    def _set_agent_running(self, running: bool) -> None:
        """Set agent running state and related controls."""
        self.agent_running = running
        self._set_agent_controls_enabled(not running)

    def run_ide_agent(self) -> None:
        """Run the coding agent with goal text and selected context blocks."""
        if self.agent_running:
            return

        agent_chat = self._current_agent_chat()
        if agent_chat is None:
            self._create_agent_chat()
            agent_chat = self._current_agent_chat()
        if agent_chat is None:
            return

        goal = self.agent_goal_input.get("1.0", "end-1c").strip()
        if not goal:
            self.agent_status_var.set("Enter a goal or request for the agent.")
            return

        # ...existing code...
        context_blocks: list[str] = []
        if self.agent_include_file_var.get():
            code = self.ide_editor.get("1.0", "end-1c").strip()
            filename = (
                self._display_path(self.ide_current_file)
                if self.ide_current_file is not None
                else "scratch.py"
            )
            if code:
                # Filter out temporary attachment paths from the code content
                # This prevents the agent from echoing back attachment paths
                filtered_code = self._filter_attachment_paths_from_text(code)
                
                # Only include in context if there's meaningful content after filtering
                if filtered_code.strip():
                    context_blocks.append(f"Current file ({filename}):\n```python\n{filtered_code}\n```")

        if self.agent_include_console_var.get():
            console = self.ide_output.get("1.0", "end-1c").strip()
            if console:
                # Filter out temporary attachment paths from console output before sending to agent
                filtered_console = self._filter_attachment_paths_from_text(console)
                if filtered_console.strip():  # Only add if there's content after filtering
                    context_blocks.append(f"Console output:\n```\n{filtered_console}\n```")

        # Filter attachment paths from the goal as well
        filtered_goal = self._filter_attachment_paths_from_text(goal)
        user_message = f"Goal:\n{filtered_goal}"
        if context_blocks:
            context_text = "\n\n".join(context_blocks)
            user_message += f"\n\nContext:\n{context_text}"

        messages = agent_chat.get("messages")
        if not isinstance(messages, list):
            messages = []
            agent_chat["messages"] = messages
        messages.append({"role": "user", "content": user_message})

        user_count = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == "user")
        if user_count == 1:
            agent_chat["title"] = self._agent_chat_title_from_text(goal)
            self._refresh_agent_chat_list()

        self._save_conversations()
        self._render_current_agent_chat()
        self._set_agent_running(True)
        self.agent_status_var.set("Thinking...")
        self._append_agent_output("Agent is thinking...\n\n")

        chat_id = str(agent_chat["id"])
        # Thread payload is detached from mutable UI state before background execution.
        history = [dict(item) for item in messages if isinstance(item, dict)]
        # Use agent-specific provider and model if they exist, otherwise fall back to global
        if hasattr(self, 'agent_provider_label_var') and hasattr(self, 'agent_model_var'):
            provider = self._provider_from_label(self.agent_provider_label_var.get()).strip().lower()
            model = self.agent_model_var.get().strip()
        else:
            provider = self.provider_var.get().strip().lower()
            model = self.model_var.get().strip()
        thread = threading.Thread(
            target=self._request_ide_agent,
            args=(history, provider, model, chat_id),
            daemon=True,
        )
        thread.start()

    def _request_ide_agent(
        self,
        history: list[dict[str, str]],
        provider: str,
        model: str,
        chat_id: str,
    ) -> None:
        """Run one IDE-agent provider request and post the response event."""
        # Same validation rules as regular chat path, but different event types/UI targets.
        if provider not in PROVIDERS:
            self.event_queue.put(
                {
                    "type": "ide_agent_error",
                    "chat_id": chat_id,
                    "message": f"Unknown provider: {provider}",
                }
            )
            return

        if not model or model == MODEL_PLACEHOLDER:
            self.event_queue.put(
                {
                    "type": "ide_agent_error",
                    "chat_id": chat_id,
                    "message": "Select a model first.",
                }
            )
            return

        if not self._has_key(provider):
            self.event_queue.put(
                {
                    "type": "ide_agent_error",
                    "chat_id": chat_id,
                    "message": self._missing_key_message(provider),
                }
            )
            return

        try:
            ide_kind = self.ide_kind_var.get()
            messages = self._prepare_agent_messages(history, ide_kind)
            reply, _usage = self._chat_with_provider(provider, model, messages, is_agent=True)
            self.event_queue.put(
                {
                    "type": "ide_agent_reply",
                    "chat_id": chat_id,
                    "message": reply,
                    "provider": provider,
                    "model": model,
                }
            )
        except Exception as exc:  # noqa: BLE001
            # Keep exception text for user feedback while preserving UI thread safety.
            self.event_queue.put(
                {
                    "type": "ide_agent_error",
                    "chat_id": chat_id,
                    "message": f"{self._provider_label(provider)} agent request failed: {exc}",
                }
            )

    def _parse_agent_commands(self, text: str) -> list[dict]:
        """Extract JSON agent commands from assistant text.

        Supported patterns:
        - ```agent\n{...}\n``` fenced blocks (languages: agent, cmd, json, action)
        - <!--AGENT-CMD\n{...}\n--> HTML-style comment block

        Each JSON object must include an "action" key (e.g. "read", "write", "create").
        Returns a list of parsed command dicts (may be empty).
        """
        import re

        commands: list[dict] = []
        if not text:
            return commands

        fence_re = re.compile(r'```(?:agent|cmd|json|action)\n(.*?)\n```', re.S | re.IGNORECASE)
        comment_re = re.compile(r'<!--\s*AGENT-CMD\n(.*?)\n-->', re.S | re.IGNORECASE)

        for m in fence_re.findall(text):
            s = m.strip()
            try:
                obj = json.loads(s)
                if isinstance(obj, dict) and obj.get("action"):
                    commands.append(obj)
            except Exception:
                # ignore parse errors for non-command blocks
                pass

        for m in comment_re.findall(text):
            s = m.strip()
            try:
                obj = json.loads(s)
                if isinstance(obj, dict) and obj.get("action"):
                    commands.append(obj)
            except Exception:
                pass

        return commands

    def _validate_and_resolve_path_for_agent(self, path_str: str) -> Path:
        """Resolve a path string into an absolute Path inside the project root.

        Raises RuntimeError if the path resolves outside the project root.
        """
        if not path_str:
            raise RuntimeError("Empty path")

        p = Path(path_str)
        # If relative, resolve relative to project root (or cwd if not set).
        if not p.is_absolute():
            root = self.project_root or Path.cwd()
            p = (root / p).resolve()
        else:
            p = p.resolve()

        # Ensure project_root exists and the path is inside it.
        root = self.project_root or Path.cwd()
        try:
            p.relative_to(root.resolve())
        except Exception:
            raise RuntimeError("Agent path must be inside the open project folder")
        return p

    def _execute_agent_command(self, cmd: dict) -> dict:
        """Execute a single parsed agent command.

        Supported actions:
        - read: {action: 'read', path: 'rel/or/abs'} -> returns file content
        - write / create / write_file: {action: 'write', path:'', content:'', overwrite: bool}

        Returns a result dict with keys: ok (bool), message (str), and optional content/path.
        """
        action = str(cmd.get("action", "")).strip().lower()
        if action not in {"read", "write", "create", "write_file"}:
            return {"ok": False, "message": f"unsupported action: {action}"}

        try:
            path_raw = str(cmd.get("path", ""))
            path = self._validate_and_resolve_path_for_agent(path_raw)
        except Exception as exc:
            return {"ok": False, "message": f"path error: {exc}"}

        if action == "read":
            if not path.exists() or not path.is_file():
                return {"ok": False, "message": "file not found"}
            try:
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = path.read_text(encoding="utf-8", errors="replace")
                return {"ok": True, "message": "read", "content": content}
            except OSError as exc:
                return {"ok": False, "message": f"read error: {exc}"}

        # For writes/creates: perform atomic write
        content = cmd.get("content", "")
        
        # Filter out temporary attachment paths from content before writing to file
        # This prevents the agent from writing attachment paths to files
        filtered_content = self._filter_attachment_paths_from_text(str(content))
        
        overwrite = bool(cmd.get("overwrite", False))
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and not overwrite:
                return {"ok": False, "message": "file exists and overwrite not allowed"}

            fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp_write_")
            os.close(fd)
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(filtered_content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)

            # Update UI's file list and editor state
            try:
                self._refresh_project_file_list()
                
                # Automatically open the file in the editor if it's a code file
                # This ensures that when the agent writes code, it appears in the editor
                if self._is_code_file(path):
                    self.open_file_in_editor(path)
            except Exception:
                pass

            return {"ok": True, "message": "written", "path": str(path)}
        except Exception as exc:
            return {"ok": False, "message": f"write error: {exc}"}

    def _process_queue(self) -> None:
        """Process async worker events and apply UI updates on the main thread."""
        # Central dispatcher for every async result; Tk widgets are only touched here.
        while True:
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                break

            event_type = event.get("type")

            if event_type == "models_loaded":
                provider = str(event.get("provider", "")).strip().lower()
                raw_models = event.get("models", [])
                models: list[str] = []
                if isinstance(raw_models, list):
                    for item in raw_models:
                        value = str(item).strip()
                        if value:
                            models.append(value)
                if not models:
                    models = self._fallback_models_for_provider(provider)
                # Cache even when provider tab changed; switching back should be instant.
                self.model_cache[provider] = models

                if provider == self.provider_var.get().strip().lower():
                    preferred_model = str(event.get("preferred_model", "")).strip()
                    if preferred_model and preferred_model not in models:
                        preferred_model = ""
                    self._apply_model_menu(provider, preferred_model=preferred_model)
                    chosen_model = self.model_var.get().strip()
                    if chosen_model and chosen_model != MODEL_PLACEHOLDER:
                        self.status_var.set(
                            f"Ready · {self._provider_model_text(provider, chosen_model)}"
                        )
                    else:
                        self.status_var.set("Ready")
                    self._render_current_chat()
                continue

            if event_type == "models_error":
                provider = str(event.get("provider", "")).strip().lower()
                if provider == self.provider_var.get().strip().lower():
                    message = str(event.get("message", "Could not load models.")).strip()
                    self.status_var.set(f"{self._provider_label(provider)} models: {message}")
                continue

            if event_type in {"chat_reply", "chat_error"}:
                chat_id = event.get("chat_id", "")
                chat = next((c for c in self.chats if str(c.get("id")) == chat_id), None)
                if chat is not None:
                    messages = chat.get("messages")
                    if isinstance(messages, list):
                        if event_type == "chat_reply":
                            raw_meta = event.get("meta", {})
                            meta = raw_meta if isinstance(raw_meta, dict) else {}
                            
                            # Extract thought process from the message content
                            message_content = str(event.get("message", "")).strip()
                            visible_text, thought_process = self._extract_thought_process(message_content)
                            
                            # Add thought process to meta if found
                            if thought_process and not meta.get('thought_process'):
                                meta['thought_process'] = thought_process
                            
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": visible_text,  # Store only the visible text
                                    "meta": self._normalize_message_meta(
                                        meta,
                                        role="assistant",
                                        content=visible_text,  # Use visible text for normalization
                                    ),
                                }
                            )
                        else:
                            messages.append(
                                {
                                    "role": "system",
                                    "content": event.get("message", "Unknown error."),
                                    "meta": self._normalize_message_meta(
                                        {},
                                        role="system",
                                        content=str(event.get("message", "Unknown error.")),
                                    ),
                                }
                            )
                    # Persist full transcript changes, including failures shown as system messages.
                    self._save_conversations()

                if self.current_chat_id == chat_id:
                    self._hide_typing()
                    if event_type == "chat_reply":
                        raw_meta = event.get("meta", {})
                        meta = raw_meta if isinstance(raw_meta, dict) else {}
                        self._add_message(
                            "assistant",
                            event.get("message", "").strip(),
                            meta=meta,
                        )
                        provider = str(event.get("provider", self.provider_var.get())).strip()
                        model = str(event.get("model", self.model_var.get())).strip()
                        self.status_var.set(
                            f"Ready · {self._provider_model_text(provider, model)}"
                        )
                    else:
                        self._add_message(
                            "system",
                            event.get("message", "Unknown error."),
                            meta={},
                        )
                        self.status_var.set("Error")

                self.pending = False
                self.pending_chat_id = None
                self._set_chat_controls_enabled(True)
                if self.mode_var.get() == "chat":
                    self.input_box.focus_set()
                continue

            if event_type == "ide_agent_reply":
                # ========== IDE AGENT REPLY HANDLER ==========
                # This handler processes responses from the coding agent and:
                # 1. Extracts code from the response
                # 2. Writes code directly to the IDE editor
                # 3. Shows a clean summary in the agent chat (NOT the full code)
                # 4. Executes any file operation commands (read/write)
                # 5. Saves the conversation history
                #
                # Key insight: The agent chat should show WHAT was done (summary),
                # while the editor shows the actual code. This keeps the UI clean.

                # Mark agent as no longer running
                self._set_agent_running(False)

                # Get the chat ID and raw AI response
                chat_id = event.get("chat_id", "")
                raw_message = str(event.get("message", ""))
                
                # Filter out temporary attachment paths from the agent response BEFORE code extraction
                # This prevents the agent from echoing back file paths instead of generating code
                cleaned_message = self._filter_attachment_paths_from_text(raw_message)

                # Step 1: Extract code from response and write to editor
                # This function looks for markdown fenced code blocks (```python, etc.)
                # Using the cleaned message to avoid extracting attachment paths as code
                code, summary = self._extract_code_from_response(cleaned_message)

                # Build a summary for chat history (not the full code)
                # This is what the user sees in the agent chat window
                chat_summary = ""

                # Process code blocks first
                if code:
                    # Code was found - write it directly to the editor
                    # This updates/replaces the editor content with the new code
                    self._write_code_to_editor(code)

                    # Create a user-friendly summary for the chat window
                    chat_summary = f"✅ Code written to editor: {summary}"

                    # Also show in the agent output panel below the editor
                    self._append_agent_output(f"✅ {summary}\n\n")
                else:
                    # No code blocks found - agent is responding conversationally
                    # (e.g., asking clarifying questions, providing explanations)
                    first_line = cleaned_message.split('\n')[0][:100]
                    chat_summary = f"Agent: {first_line}"
                    self._append_agent_output(f"Agent: {first_line}\n\n")

                # Process commands regardless of whether code was found
                # This allows agents to both write code to editor AND perform file operations
                try:
                    commands = self._parse_agent_commands(cleaned_message)
                    if commands:
                        self._append_agent_output("[File operations executed]\n")
                        chat_summary += "\n[File operations executed]"

                    # Execute each command and show results
                    for cmd in commands:
                        res = self._execute_agent_command(cmd)

                        # Show brief result in agent output panel
                        self._append_agent_output(f"  • {cmd.get('action')}: {res.get('message')}\n")
                        chat_summary += f"\n  • {cmd.get('action')}: {res.get('message')}"

                        # For read operations, show a preview of the file content
                        if res.get("content") and cmd.get("action") == "read":
                            preview = res.get("content")
                            max_preview = 500
                            if len(preview) > max_preview:
                                preview = preview[:max_preview] + "\n... (truncated)"
                            self._append_agent_output(f"\n--- {cmd.get('path')} ---\n{preview}\n--- end ---\n\n")
                except Exception as exc:
                    # Handle any errors in command execution
                    self._append_agent_output(f"Error: {exc}\n")
                    chat_summary += f"\nError: {exc}"

                # Step 3: Store ONLY the summary in chat history, not the full code
                # This is the key fix - we don't want huge code blocks in the chat history
                # The full response is kept as metadata for debugging if needed
                chat = next((c for c in self.agent_chats if str(c.get("id")) == chat_id), None)
                if chat is not None:
                    messages = chat.get("messages")
                    if isinstance(messages, list):
                        messages.append(
                            {
                                "role": "assistant",
                                "content": chat_summary.strip(),  # Clean summary only
                                "full_response": raw_message.strip(),  # Full response saved for reference
                            }
                        )
                        self._save_conversations()

                # Step 4: Update UI status
                provider = str(event.get("provider", self.provider_var.get())).strip()
                model = str(event.get("model", self.model_var.get())).strip()

                # Refresh the agent chat display if this is the active chat
                if self.current_agent_chat_id == chat_id:
                    self._render_current_agent_chat()
                    self.agent_status_var.set(
                        f"Ready · {self._provider_model_text(provider, model)}"
                    )
                else:
                    self.agent_status_var.set("Ready")
                continue

            if event_type == "ide_agent_error":
                self._set_agent_running(False)
                chat_id = event.get("chat_id", "")
                chat = next((c for c in self.agent_chats if str(c.get("id")) == chat_id), None)
                if chat is not None:
                    messages = chat.get("messages")
                    if isinstance(messages, list):
                        messages.append(
                            {
                                "role": "system",
                                "content": event.get("message", "Unknown error."),
                            }
                        )
                        self._save_conversations()
                if self.current_agent_chat_id == chat_id:
                    self._render_current_agent_chat()
                self.agent_status_var.set("Error")
                continue

            if event_type == "ide_result":
                self._set_ide_running(False)
                stdout = event.get("stdout", "")
                stderr = event.get("stderr", "")
                returncode = int(event.get("returncode", "-1"))
                timed_out = event.get("timed_out", "0") == "1"

                if not stdout and not stderr:
                    self._append_ide_output("(no output)\n")
                if stdout:
                    self._append_ide_output(stdout if stdout.endswith("\n") else f"{stdout}\n")
                if stderr:
                    if not stderr.startswith("\n"):
                        self._append_ide_output("\n")
                    self._append_ide_output(stderr if stderr.endswith("\n") else f"{stderr}\n")

                if timed_out:
                    self.ide_status_var.set("Timed out")
                elif returncode == 0:
                    self.ide_status_var.set("Done")
                else:
                    self.ide_status_var.set(f"Exited with code {returncode}")
                continue

            if event_type == "ide_error":
                self._set_ide_running(False)
                self._append_ide_output(f"{event.get('message', 'Unknown IDE error.')}\n")
                self.ide_status_var.set("Run failed")

        # Polling loop keeps processing worker events without blocking Tk's event loop.
        self.after(120, self._process_queue)

    def _extract_code_from_response(self, text: str) -> tuple[str, str]:
        """Extract code from agent response and return (code, summary).

        This function is critical for the IDE agent functionality. It:
        1. Searches for code in markdown fenced blocks (```python, ```html, etc.)
        2. Extracts ONLY the code content (excludes surrounding explanations)
        3. Combines multiple code blocks if present
        4. Generates a human-readable summary of what the code does

        The extracted code goes directly into the IDE editor, while the summary
        is shown in the agent chat window for user feedback.

        Args:
            text: Raw AI response text that may contain code blocks

        Returns:
            Tuple of (code_content, summary_text):
                - code_content: Pure code to write to editor (empty string if none found)
                - summary_text: Brief description of what was done

        Example:
            Input: "I'll create a function.\n```python\ndef hello():\n    pass\n```\nDone!"
            Output: ("def hello():\n    pass", "I'll create a function.")
        """
        import re

        code = ""
        summary = ""

        # Step 1: Extract all code blocks using regex
        # Matches markdown fenced blocks like ```python, ```html, ```css, etc.
        # The (?:...) is a non-capturing group for language identifiers
        # \s* allows optional whitespace after the language identifier
        # (.*?) captures the code content (non-greedy)
        # re.DOTALL makes . match newlines, re.IGNORECASE handles ```Python, ```PYTHON, etc.
        code_blocks = re.findall(
            r'```(?:python|html|css|javascript|js|jsx|tsx?|typescript|web)?\s*\n(.*?)\n```',
            text,
            re.DOTALL | re.IGNORECASE
        )
        
        # If no language-specific blocks found, try to find generic code blocks
        if not code_blocks:
            generic_blocks = re.findall(
                r'```\s*\n(.*?)\n```',
                text,
                re.DOTALL
            )
            code_blocks.extend(generic_blocks)

        if code_blocks:
            # Step 2: Process found code blocks
            # Multiple blocks might exist (e.g., HTML + CSS in same response)
            all_code = []
            for block in code_blocks:
                block_stripped = block.strip()
                if block_stripped:  # Skip empty blocks
                    all_code.append(block_stripped)

            if all_code:
                # Step 3: Combine multiple code blocks with double newlines
                # This maintains separation between different code sections
                code = "\n\n".join(all_code)

                # Step 4: Extract summary from explanatory text BEFORE the code
                # We split on first ``` to get everything before the code block
                before_code = text.split('```')[0].strip()

                # Get the last meaningful line as summary (usually the agent's intro)
                # Filter out comment lines starting with # and empty lines
                lines = [l.strip() for l in before_code.split('\n') if l.strip() and not l.startswith('#')]

                if lines:
                    summary = lines[-1]  # Last line usually describes the action

                    # Limit summary length to prevent UI overflow
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                else:
                    # Fallback if no explanatory text found
                    summary = "Code updated"
            else:
                # Found code blocks but all were empty
                summary = "Empty code block"
        else:
            # Step 5: No code blocks found - agent is just responding conversationally
            # This happens when agent asks clarifying questions or provides explanations
            # Use first line of response as summary (up to 100 chars)
            summary = text.split('\n')[0][:100]

        # Fallback: If no code was found but the response looks like code, try to extract it
        # This handles cases where the agent generates code without proper formatting
        if not code and self._looks_like_code(text):
            # Try to extract content that might be code but not in fenced blocks
            # Look for indented code, function definitions, etc.
            lines = text.split('\n')
            code_lines = []
            in_code_section = False
            
            for line in lines:
                stripped = line.strip()
                # If line starts with common code patterns, consider it code
                if (stripped.startswith('def ') or 
                    stripped.startswith('class ') or 
                    stripped.startswith('import ') or 
                    stripped.startswith('from ') or 
                    stripped.startswith('function ') or 
                    stripped.startswith('<') or  # HTML tags
                    ':' in stripped and '{' in stripped or  # CSS rules
                    stripped.endswith(':') or  # Python class/function headers
                    stripped.startswith('return ') or  # Return statements
                    stripped.startswith('if ') or  # Conditional statements
                    stripped.startswith('for ') or  # Loop statements
                    stripped.startswith('while ') or  # Loop statements
                    stripped.startswith('try:') or  # Try statements
                    stripped.startswith('except ') or  # Except statements
                    stripped.startswith('with ') or  # With statements
                    line.startswith('    ') or  # Indented code
                    line.startswith('\t')):  # Tab-indented code
                    code_lines.append(line)
                    in_code_section = True
                elif in_code_section and not stripped:
                    # Continue including blank lines within code sections
                    code_lines.append(line)
                elif in_code_section and stripped:
                    # If we were in a code section and hit non-code, stop
                    break
            
            if code_lines:
                code = '\n'.join(code_lines).strip()
                summary = "Code extracted from response"

        return code, summary

    def _write_code_to_editor(self, code: str) -> None:
        """Write code to the IDE editor.

        This function replaces the entire editor content with new code from the agent.
        It handles all the necessary UI updates including:
        - Clearing old content and inserting new code
        - Marking the file as dirty (unsaved changes)
        - Refreshing line numbers
        - Updating syntax highlighting
        - Updating browser preview (for web mode)

        The _ide_loading flag prevents certain event handlers from firing during
        the update process (e.g., preventing duplicate syntax highlighting triggers).

        Args:
            code: The code string to write to the editor (should not be empty)

        Side Effects:
            - Modifies editor widget content
            - Sets ide_dirty flag to True
            - Updates line numbers display
            - Schedules syntax highlighting
            - Updates browser preview if in web mode
        """
        # Safety check: Ensure the IDE editor widget exists
        if not hasattr(self, 'ide_editor'):
            return

        # Don't write empty/whitespace-only code
        if not code.strip():
            return

        # Step 1: Replace editor content with generated code
        # Set loading flag to prevent event handlers from triggering during update
        self._ide_loading = True

        # Clear all existing content from the editor
        # "1.0" means line 1, character 0 (beginning of file)
        # "end" means the end of the file
        self.ide_editor.delete("1.0", "end")

        # Insert the new code at the beginning
        self.ide_editor.insert("1.0", code)

        # Clear loading flag - event handlers can fire again
        self._ide_loading = False

        # Step 2: Update file status
        # Mark the file as having unsaved changes
        self.ide_dirty = True
        self.ide_status_var.set("Code generated and loaded in editor")

        # Step 3: Refresh visual elements
        # Update line numbers in the gutter (left side of editor)
        self._refresh_ide_line_numbers()

        # Update the cursor position display (e.g., "Ln 1, Col 1")
        self._update_ide_cursor_position()

        # Schedule syntax highlighting with a small delay
        # The delay allows the editor to finish rendering before highlighting
        self._schedule_ide_syntax_highlight(delay_ms=10)

        # Step 4: Update browser preview if in web mode
        # For HTML/CSS/JS files, refresh the live preview pane
        if self.ide_kind_var.get() == "web":
            self._schedule_browser_update(delay_ms=100)

if __name__ == "__main__":
    app = GroqChatroomApp()
    app.mainloop()
