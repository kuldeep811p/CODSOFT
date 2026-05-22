"""
CODSOFT AI Internship — Task 1 UPGRADED
Rule-Based Chatbot — Advanced Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Features:
  ✦ Conversation memory (remembers name, age, hobby, facts)
  ✦ Mood detection & adaptive tone
  ✦ Typing animation effect
  ✦ Safe math expression evaluator
  ✦ Offline mini-dictionary (define words)
  ✦ Number guessing mini-game
  ✦ Chat history export to JSON
  ✦ Session summary on exit
  ✦ Colorized terminal output
  ✦ Help menu with all features listed
"""

import re, os, json, random, time
from datetime import datetime

# ── Terminal Colors ────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    BOT    = "\033[96m"
    USER   = "\033[93m"
    SYS    = "\033[90m"
    OK     = "\033[92m"
    WARN   = "\033[91m"
    ACCENT = "\033[95m"

def col(text, color): return f"{color}{text}{C.RESET}"

# ── Session Memory ─────────────────────────────────────────
class Memory:
    def __init__(self):
        self.user_name       = None
        self.chat_history    = []
        self.topics          = set()
        self.mood            = "neutral"
        self.message_count   = 0
        self.user_facts      = {}

    def add(self, role, text):
        self.chat_history.append({"role": role, "text": text,
                                   "time": datetime.now().strftime("%H:%M:%S")})
        self.message_count += 1

    def export(self, path="chat_history.json"):
        with open(path, "w") as f:
            json.dump(self.chat_history, f, indent=2)
        return path

    def summary(self):
        lines = [col("── Session Summary ──────────────────", C.SYS),
                 f"  Messages   : {self.message_count}"]
        if self.user_name:  lines.append(f"  Name       : {self.user_name}")
        if self.topics:     lines.append(f"  Topics     : {', '.join(sorted(self.topics))}")
        for k, v in self.user_facts.items():
            lines.append(f"  {k.title():<10} : {v}")
        return "\n".join(lines)

MEM = Memory()

# ── Mini Dictionary ────────────────────────────────────────
DICT = {
    "algorithm":       "A step-by-step procedure for solving a problem.",
    "api":             "Application Programming Interface — lets programs talk to each other.",
    "bot":             "A software agent that performs automated tasks.",
    "chatbot":         "A program designed to simulate conversation with humans.",
    "debugging":       "Finding and fixing errors in code.",
    "encryption":      "Converting data into a coded form to prevent unauthorized access.",
    "github":          "A platform for version control and code collaboration.",
    "gpu":             "Graphics Processing Unit — used for parallel computing.",
    "machine learning":"A type of AI where systems learn from data automatically.",
    "neural network":  "A computing system inspired by the human brain.",
    "python":          "A high-level programming language known for readability.",
    "recursion":       "A function that calls itself to solve smaller sub-problems.",
    "variable":        "A named storage location for data in a program.",
    "overfitting":     "When a model learns training data too well and fails on new data.",
    "gradient descent":"An optimisation algorithm used to minimise error in ML models.",
}

# ── Mood Detection ─────────────────────────────────────────
POS = {"great","happy","love","awesome","good","excited","wonderful","fantastic","joy","glad","amazing","nice","cool","perfect","excellent"}
NEG = {"sad","unhappy","bad","hate","awful","terrible","depressed","angry","frustrated","upset","bored","tired","stressed","anxious"}

def detect_mood(text):
    words = set(text.lower().split())
    if len(words & POS) > len(words & NEG): return "positive"
    if len(words & NEG) > len(words & POS): return "negative"
    return "neutral"

# ── Safe Math ──────────────────────────────────────────────
def safe_math(expr):
    expr = re.sub(r"[^0-9+\-*/(). %]", "", expr).strip()
    if not expr: return None
    try:
        result = eval(expr, {"__builtins__": {}}, {})  # noqa: S307
        return round(result, 6)
    except Exception:
        return None

# ── Number Game ────────────────────────────────────────────
def play_number_game():
    secret, attempts = random.randint(1, 100), 0
    print(col("\n🎮  Guess a number between 1 and 100! ('stop' to quit)", C.ACCENT))
    while True:
        raw = input(col("   Your guess: ", C.USER)).strip()
        if raw.lower() in ("stop", "quit", "exit"):
            print(col(f"   The number was {secret}. Better luck next time!", C.SYS))
            break
        try:
            g = int(raw); attempts += 1
            if   g < secret: print(col("   📈 Too low!",  C.WARN))
            elif g > secret: print(col("   📉 Too high!", C.WARN))
            else:
                print(col(f"   🎉 Correct in {attempts} attempt(s)!", C.OK))
                break
        except ValueError:
            print(col("   Enter a valid integer.", C.WARN))

# ── Handlers ───────────────────────────────────────────────
def h_greet(m, t):
    MEM.topics.add("greeting")
    n = f", {MEM.user_name}" if MEM.user_name else ""
    return random.choice([f"Hello{n}! 😊 What can I do for you?",
                          f"Hey{n}! Great to see you. How can I help?",
                          f"Hi there{n}! 👋 What's on your mind?"])

def h_bye(m, t):
    MEM.topics.add("farewell")
    n = f", {MEM.user_name}" if MEM.user_name else ""
    return random.choice([f"Goodbye{n}! 👋 Hope to chat again soon!",
                          f"See you later{n}! Take care! 😊",
                          f"Bye{n}! It was great talking to you! 🌟"])

def h_how_are_you(m, t):
    if MEM.mood == "positive": return "Glad you're doing well! 🌟 How can I help?"
    if MEM.mood == "negative": return "I'm sorry to hear that 😔. How can I cheer you up?"
    return random.choice(["Running perfectly! How about you? 🤖",
                          "All systems go! What can I do for you?"])

def h_set_name(m, t):
    name = m.group(1).strip().title()
    MEM.user_name = name; MEM.user_facts["name"] = name
    return f"Nice to meet you, {col(name, C.ACCENT)}! I'll remember that. 😊"

def h_my_name(m, t):
    if MEM.user_name:
        return f"You told me your name is {col(MEM.user_name, C.ACCENT)}! 😄"
    return "I don't know your name yet! Tell me — what's your name?"

def h_time(m, t):
    MEM.topics.add("time")
    return f"🕐 Current time: {col(datetime.now().strftime('%H:%M:%S'), C.ACCENT)}"

def h_date(m, t):
    MEM.topics.add("date")
    return f"📅 Today is {col(datetime.now().strftime('%A, %B %d, %Y'), C.ACCENT)}"

def h_math(m, t):
    MEM.topics.add("math")
    expr = re.sub(r"(what is|calculate|compute|solve|=)", "", t, flags=re.I)
    result = safe_math(expr)
    if result is not None:
        return f"🧮 {col(expr.strip(), C.ACCENT)} = {col(str(result), C.OK)}"
    return "I couldn't evaluate that. Try: `what is 15 * (3 + 2)`"

def h_define(m, t):
    MEM.topics.add("definitions")
    word = m.group(1).strip().lower()
    if word in DICT:
        return f"📖 {col(word.title(), C.ACCENT)}: {DICT[word]}"
    close = [k for k in DICT if word in k or k in word]
    if close: return f"Did you mean: {', '.join(close)}?"
    return f"I don't know '{word}'. Try: algorithm, python, recursion, api..."

def h_joke(m, t):
    MEM.topics.add("jokes")
    return random.choice([
        "Why don't scientists trust atoms?\nBecause they make up everything! 😂",
        "Why did the programmer quit?\nBecause they didn't get arrays. 😄",
        "Why do Java devs wear glasses? Because they don't C#! 👓",
        "I tried to write a joke about recursion.\nI tried to write a joke about recursion.\n...",
        "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?' 🍺",
    ])

def h_game(m, t):
    MEM.topics.add("game"); print()
    play_number_game()
    return "Hope you enjoyed the game! Anything else? 😊"

def h_export(m, t):
    path = MEM.export()
    return f"💾 Chat history saved to {col(path, C.ACCENT)}"

def h_summary(m, t):
    return MEM.summary()

def h_help(m, t):
    MEM.topics.add("help")
    return (
        col("🤖 What I can do:", C.ACCENT) + "\n"
        "  💬 Chat           — greet me, ask how I am\n"
        "  🕐 Time & Date    — 'what time is it?' / 'today\\'s date'\n"
        "  🧮 Math           — 'what is 12 * (3 + 5)?'\n"
        "  📖 Define         — 'define recursion' / 'what does api mean'\n"
        "  😂 Jokes          — 'tell me a joke'\n"
        "  🎮 Mini-game      — 'play a game'\n"
        "  📊 Summary        — 'session summary'\n"
        "  💾 Export         — 'export chat'\n"
        "  👋 Bye            — 'bye' / 'exit'"
    )

def h_thanks(m, t):
    n = f", {MEM.user_name}" if MEM.user_name else ""
    return random.choice([f"You're welcome{n}! 😊", "Happy to help! 🤖", "Anytime!"])

def h_feeling(m, t):
    return random.choice([
        "I'm sorry you're feeling that way 😔. Want a joke or a game to cheer up?",
        "Tough times don't last 💪. I'm here — what would help right now?",
    ])

def h_bot_q(m, t):
    return "100% bot! Built with Python regex for CODSOFT AI Internship 🤖"

def h_hobby(m, t):
    hobby = m.group(2).strip()
    MEM.user_facts["hobby"] = hobby
    return f"That's awesome — {col(hobby, C.ACCENT)}! I'll remember that. 😊"

def h_age(m, t):
    age = m.group(1).strip()
    MEM.user_facts["age"] = age
    return f"Got it — {col(age, C.ACCENT)} years old! Noted. 📝"

def h_repeat(m, t):
    bots = [c for c in MEM.chat_history if c["role"] == "bot"]
    return f"I said: \"{bots[-2]['text']}\"" if len(bots) >= 2 else "Nothing to repeat yet!"

def h_weather(m, t):
    return "☀️ I don't have live weather. Check weather.com or look outside! 😄"

def h_whats_your_age(m, t):
    return "I'm ageless! 🤖 Born the moment this script was launched."

def h_capabilities(m, t):
    return h_help(m, t)

# ── Rule Table ─────────────────────────────────────────────
RULES = [
    (r"\b(hello|hi|hey|howdy|hiya|sup)\b",                         h_greet),
    (r"\b(bye|goodbye|see you|cya|take care|quit|exit)\b",         h_bye),
    (r"\bhow are you\b|\bhow.s it going\b|\bwhat.s up\b",          h_how_are_you),
    (r"\bmy name is ([A-Za-z ]+)",                                  h_set_name),
    (r"\bi am (\d+) years old",                                     h_age),
    (r"\bi (love|like|enjoy) ([A-Za-z ]+)",                        h_hobby),
    (r"\bwhat.s my name\b|\bdo you (know|remember) my name",       h_my_name),
    (r"\bwhat.s your name\b|\bwho are you\b",                      lambda m,t: "I'm RuleBot 🤖 — Advanced Edition!"),
    (r"\bhow old are you\b|\bwhat.s your age\b",                   h_whats_your_age),
    (r"\b(what time|current time|time now|the time)\b",             h_time),
    (r"\b(today.s date|what.s the date|current date)\b",           h_date),
    (r"(what is|calculate|compute|solve)\s+[\d\s+\-*/()%.]+",      h_math),
    (r"\bdefine\s+(.+)",                                            h_define),
    (r"\bwhat does (.+) mean\b",                                    h_define),
    (r"\b(joke|funny|make me laugh|tell me something funny)\b",     h_joke),
    (r"\b(play a game|let.s play|mini.?game|number game|game)\b",   h_game),
    (r"\b(export|save|download).*(chat|history|conversation)\b",    h_export),
    (r"\b(session summary|summary|stats|what have we talked)\b",    h_summary),
    (r"\b(help|what can you do|commands|features)\b",               h_help),
    (r"\b(thanks|thank you|thx|ty|cheers)\b",                      h_thanks),
    (r"\b(sad|unhappy|depressed|bad day|frustrated|stressed)\b",    h_feeling),
    (r"\bare you (a )?(robot|bot|ai|machine|human)\b",              h_bot_q),
    (r"\b(weather|temperature|forecast|rain)\b",                    h_weather),
    (r"\b(repeat|say that again|what did you say)\b",               h_repeat),
    (r"\bwhat can you do\b|\byour (features|abilities)\b",          h_capabilities),
]

FALLBACKS = [
    "🤔 Not sure about that. Type `help` to see what I can do!",
    "Hmm, I didn't catch that. Rephrase or try `help`?",
    "That's outside my rulebook! Ask about time, math, jokes, or play a game.",
    "Interesting! I don't have an answer yet. Try a different question!",
]
_fb_idx = 0

def get_response(user_text):
    text = user_text.lower().strip()
    MEM.mood = detect_mood(text)
    for pattern, handler in RULES:
        match = re.search(pattern, text)
        if match:
            return handler(match, text)
    global _fb_idx
    reply = FALLBACKS[_fb_idx % len(FALLBACKS)]
    _fb_idx += 1
    return reply

# ── Typing Effect ──────────────────────────────────────────
def typewrite(text, delay=0.013):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

# ── Main ───────────────────────────────────────────────────
def run_chatbot():
    os.system("cls" if os.name == "nt" else "clear")
    print(col("╔══════════════════════════════════════════════╗", C.BOT))
    print(col("║", C.BOT) + col("   🤖  RuleBot  —  CODSOFT AI Internship     ", C.BOLD) + col("║", C.BOT))
    print(col("║", C.BOT) + col("        Advanced Rule-Based Chatbot            ", C.SYS)  + col("║", C.BOT))
    print(col("╚══════════════════════════════════════════════╝", C.BOT))
    print(col("  Type 'help' to explore features  |  'bye' to exit\n", C.SYS))

    opening = "Hi! 👋 I'm RuleBot. What's your name?"
    print(col("RuleBot: ", C.BOT), end=""); typewrite(opening)
    MEM.add("bot", opening); print()

    while True:
        try:
            raw = input(col("You: ", C.USER)).strip()
        except (EOFError, KeyboardInterrupt):
            print(col("\nRuleBot: Goodbye! 👋", C.BOT)); break

        if not raw: continue
        MEM.add("user", raw)
        response = get_response(raw)
        MEM.add("bot", response)
        print(col("\nRuleBot: ", C.BOT), end=""); typewrite(response); print()

        if re.search(r"\b(bye|goodbye|quit|exit|cya)\b", raw.lower()):
            print("\n" + MEM.summary()); break

if __name__ == "__main__":
    run_chatbot()
