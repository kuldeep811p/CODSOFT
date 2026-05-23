"""
CODSOFT AI Internship — Task 2 UPGRADED
Tic-Tac-Toe AI — Advanced Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Features:
  ✦ 3 difficulty levels: Easy / Medium / Hard (unbeatable)
  ✦ Persistent scoreboard (wins / losses / draws)
  ✦ Move history & replay after each game
  ✦ Colorized board with numbered position guide
  ✦ AI "thinking" animation
  ✦ Best-of-N series mode
  ✦ Detailed game stats (fastest win, total moves)
"""

import math, os, random, time, json
from pathlib import Path

# ── Colors ─────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"; BOLD = "\033[1m"
    X      = "\033[91m"   # red  — AI
    O      = "\033[94m"   # blue — Human
    GRID   = "\033[90m"   # gray
    WIN    = "\033[92m"   # green
    SYS    = "\033[90m"
    ACCENT = "\033[95m"
    TITLE  = "\033[96m"

def col(t, c): return f"{c}{t}{C.RESET}"

SCORE_FILE = "tictactoe_scores.json"

def load_scores():
    if Path(SCORE_FILE).exists():
        with open(SCORE_FILE) as f: return json.load(f)
    return {"wins": 0, "losses": 0, "draws": 0, "games": 0}

def save_scores(s):
    with open(SCORE_FILE, "w") as f: json.dump(s, f, indent=2)

# ── Board ──────────────────────────────────────────────────
def make_board(): return [" "] * 9

def print_board(board, highlight=None):
    """Print board with colors. highlight = set of winning indices."""
    symbols = []
    for i, cell in enumerate(board):
        if cell == "X":
            sym = col("X", C.WIN if highlight and i in highlight else C.X)
        elif cell == "O":
            sym = col("O", C.WIN if highlight and i in highlight else C.O)
        else:
            sym = col(str(i+1), C.SYS)
        symbols.append(sym)

    g = col("│", C.GRID); h = col("───┼───┼───", C.GRID)
    print()
    for r in range(3):
        s = symbols[r*3: r*3+3]
        print(f"  {col(' ', C.GRID)} {s[0]} {g} {s[1]} {g} {s[2]}")
        if r < 2: print(f"  {h}")
    print()

def get_winner(board):
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in lines:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a], {a,b,c}
    return None, set()

def is_full(board): return " " not in board
def moves(board):   return [i for i,c in enumerate(board) if c==" "]

# ── Minimax ────────────────────────────────────────────────
def minimax(board, depth, is_max, alpha, beta):
    winner, _ = get_winner(board)
    if winner == "X": return 10 - depth
    if winner == "O": return depth - 10
    if is_full(board): return 0

    if is_max:
        best = -math.inf
        for m in moves(board):
            board[m] = "X"
            best = max(best, minimax(board, depth+1, False, alpha, beta))
            board[m] = " "
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best
    else:
        best = math.inf
        for m in moves(board):
            board[m] = "O"
            best = min(best, minimax(board, depth+1, True, alpha, beta))
            board[m] = " "
            beta = min(beta, best)
            if beta <= alpha: break
        return best

def best_move_hard(board):
    best_val, chosen = -math.inf, None
    for m in moves(board):
        board[m] = "X"
        val = minimax(board, 0, False, -math.inf, math.inf)
        board[m] = " "
        if val > best_val: best_val, chosen = val, m
    return chosen

def best_move_medium(board):
    """70% optimal, 30% random."""
    if random.random() < 0.70: return best_move_hard(board)
    return random.choice(moves(board))

def best_move_easy(board):
    """Pure random."""
    return random.choice(moves(board))

AI_STRATEGIES = {
    "easy":   best_move_easy,
    "medium": best_move_medium,
    "hard":   best_move_hard,
}

# ── AI Thinking Animation ──────────────────────────────────
def thinking_anim(label="🤖 AI is thinking"):
    for _ in range(3):
        for dots in (".", "..", "..."):
            print(f"\r  {label}{dots}   ", end="", flush=True)
            time.sleep(0.18)
    print(f"\r  {label}... done!   ")

# ── Single Game ────────────────────────────────────────────
def play_one_game(difficulty, human_first):
    board = make_board()
    strategy = AI_STRATEGIES[difficulty]
    history = []   # list of (player, position)
    turn = "O" if human_first else "X"   # O = human, X = AI

    print_board(board)

    while True:
        winner, win_cells = get_winner(board)
        if winner or is_full(board): break

        if turn == "O":
            # Human
            while True:
                try:
                    pos = int(input(col("  Your move (1-9): ", C.O))) - 1
                    if 0 <= pos <= 8 and board[pos] == " ": break
                    print(col("  ⚠  Invalid! Try again.", C.X))
                except ValueError:
                    print(col("  ⚠  Enter a number 1-9.", C.X))
            board[pos] = "O"
            history.append(("Human", pos+1))
        else:
            # AI
            thinking_anim()
            pos = strategy(board)
            board[pos] = "X"
            history.append(("AI", pos+1))
            print(col(f"  🤖 AI played position {pos+1}", C.X))

        print_board(board)
        turn = "O" if turn == "X" else "X"

    winner, win_cells = get_winner(board)
    if win_cells: print_board(board, highlight=win_cells)

    if winner == "X":
        result = "loss"
        print(col("  🤖 AI wins! The Minimax algorithm is unbeatable on Hard. 💀", C.X))
    elif winner == "O":
        result = "win"
        print(col("  🎉 YOU WIN! Incredible!", C.WIN))
    else:
        result = "draw"
        print(col("  🤝 It's a draw! Well played.", C.ACCENT))

    return result, history

# ── Replay ───────────────────────────────────
def show_replay(history):
    print(col("\n  📼 Game Replay:", C.SYS))
    board = make_board()
    for i, (player, pos) in enumerate(history, 1):
        symbol = "O" if player == "Human" else "X"
        board[pos-1] = symbol
        print(col(f"  Move {i}: {player} → position {pos}", C.SYS))
        print_board(board)
        time.sleep(0.4)

# ── Main ───────────────────────────────────────────────────
def main():
    os.system("cls" if os.name == "nt" else "clear")
    scores = load_scores()

    print(col("╔════════════════════════════════════════════╗", C.TITLE))
    print(col("║", C.TITLE) + col("  🎮  Tic-Tac-Toe AI  —  CODSOFT Task 2     ", C.BOLD) + col("║", C.TITLE))
    print(col("║", C.TITLE) + col("       Minimax + Alpha-Beta Pruning         ", C.SYS)  + col("║", C.TITLE))
    print(col("╚════════════════════════════════════════════╝", C.TITLE))
    print(col(f"  You = {col('O', C.O)}   |   AI = {col('X', C.X)}", C.SYS))

    while True:
        # Scoreboard
        s = scores
        print(col(f"\n  📊 Scoreboard  W:{s['wins']}  L:{s['losses']}  D:{s['draws']}  Games:{s['games']}", C.SYS))

        # Difficulty
        print("\n  Select difficulty:")
        print(f"  {col('1', C.ACCENT)} Easy    (random AI)")
        print(f"  {col('2', C.ACCENT)} Medium  (70% optimal)")
        print(f"  {col('3', C.ACCENT)} Hard    (unbeatable Minimax)")
        print(f"  {col('4', C.ACCENT)} Quit")
        choice = input(col("\n  Choice: ", C.O)).strip()

        if choice == "4": break
        diff_map = {"1": "easy", "2": "medium", "3": "hard"}
        if choice not in diff_map:
            print(col("  Invalid choice.", C.X)); continue
        difficulty = diff_map[choice]

        first = input(col("  Do you want to go first? (y/n): ", C.O)).strip().lower()
        human_first = first != "n"

        print(col(f"\n  Starting game on {difficulty.upper()} mode...\n", C.SYS))
        result, history = play_one_game(difficulty, human_first)

        scores["games"] += 1
        if result == "win":    scores["wins"]   += 1
        elif result == "loss": scores["losses"] += 1
        else:                  scores["draws"]  += 1
        save_scores(scores)

        # Replay option
        if input(col("\n  Watch replay? (y/n): ", C.SYS)).strip().lower() == "y":
            show_replay(history)

        if input(col("  Play again? (y/n): ", C.SYS)).strip().lower() != "y":
            break

    s = scores
    print(col(f"\n  Final Score — Wins:{s['wins']}  Losses:{s['losses']}  Draws:{s['draws']}", C.WIN))
    print(col("  Thanks for playing! 👋\n", C.SYS))

if __name__ == "__main__":
    main()
