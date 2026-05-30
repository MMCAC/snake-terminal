import os
import sys
import time
import random
import json
import msvcrt
from collections import deque

# --- Config ---
WIDTH = 30
HEIGHT = 20
TICK = 0.12
RECORD_FILE = os.path.join(os.path.dirname(__file__), "record.json")

# --- Colors (ANSI) ---
RESET  = "\033[0m"
GREEN  = "\033[92m"
BRIGHT = "\033[1m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"

def enable_ansi():
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def clear():
    os.system("cls")

def load_record():
    try:
        with open(RECORD_FILE) as f:
            return json.load(f).get("record", 0)
    except Exception:
        return 0

def save_record(score):
    try:
        with open(RECORD_FILE, "w") as f:
            json.dump({"record": score}, f)
    except Exception:
        pass

def get_key():
    """Non-blocking key read on Windows."""
    if msvcrt.kbhit():
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):   # special key prefix
            ch2 = msvcrt.getwch()
            return {
                'H': 'UP', 'P': 'DOWN', 'K': 'LEFT', 'M': 'RIGHT'
            }.get(ch2)
        return ch.lower()
    return None

DIRS = {
    'UP':    (0, -1),
    'DOWN':  (0,  1),
    'LEFT':  (-1, 0),
    'RIGHT': (1,  0),
    'w':     (0, -1),
    's':     (0,  1),
    'a':     (-1, 0),
    'd':     (1,  0),
}

OPPOSITES = {
    (0,-1):(0,1), (0,1):(0,-1),
    (-1,0):(1,0), (1,0):(-1,0),
}

def draw(snake, food, score, record, level):
    buf = []

    # Top border
    buf.append(f"{BRIGHT}{CYAN}╔{'═'*WIDTH}╗{RESET}")

    for y in range(HEIGHT):
        row = [f"{BRIGHT}{CYAN}║{RESET}"]
        for x in range(WIDTH):
            pos = (x, y)
            if pos == snake[0]:
                row.append(f"{BRIGHT}{GREEN}@{RESET}")
            elif pos in snake:
                row.append(f"{GREEN}o{RESET}")
            elif pos == food:
                row.append(f"{YELLOW}★{RESET}")
            else:
                row.append(f"{DIM}.{RESET}")
        row.append(f"{BRIGHT}{CYAN}║{RESET}")
        buf.append("".join(row))

    # Bottom border
    buf.append(f"{BRIGHT}{CYAN}╚{'═'*WIDTH}╝{RESET}")

    # Stats
    buf.append(
        f"  Pontos: {BRIGHT}{score}{RESET}   "
        f"Recorde: {BRIGHT}{YELLOW}{record}{RESET}   "
        f"Nível: {BRIGHT}{CYAN}{level}{RESET}"
    )
    buf.append(f"  {DIM}W A S D  ou  ↑ ↓ ← →   Q = sair{RESET}")

    print("\033[H" + "\n".join(buf), end="", flush=True)

def place_food(snake_set):
    while True:
        pos = (random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1))
        if pos not in snake_set:
            return pos

def level_for_score(score):
    return min(10, 1 + score // 5)

def tick_for_level(lvl):
    return max(0.04, TICK - (lvl - 1) * 0.008)

def run_game():
    record = load_record()
    enable_ansi()

    while True:
        # Init state
        cx, cy = WIDTH // 2, HEIGHT // 2
        snake = deque([(cx, cy), (cx-1, cy), (cx-2, cy)])
        snake_set = set(snake)
        direction = (1, 0)
        pending = direction
        food = place_food(snake_set)
        score = 0

        clear()
        print("\033[?25l", end="")  # hide cursor

        last_tick = time.time()

        try:
            while True:
                key = get_key()
                if key == 'q':
                    return
                if key in DIRS:
                    d = DIRS[key]
                    if d != OPPOSITES.get(direction):
                        pending = d

                now = time.time()
                lvl = level_for_score(score)
                tick = tick_for_level(lvl)

                if now - last_tick >= tick:
                    direction = pending
                    hx, hy = snake[0]
                    dx, dy = direction
                    nx, ny = hx + dx, hy + dy

                    # Wall collision
                    if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
                        break

                    npos = (nx, ny)

                    # Self collision
                    if npos in snake_set:
                        break

                    snake.appendleft(npos)
                    snake_set.add(npos)

                    if npos == food:
                        score += 1
                        food = place_food(snake_set)
                    else:
                        tail = snake.pop()
                        snake_set.discard(tail)

                    draw(snake, food, score, record, lvl)
                    last_tick = now

                time.sleep(0.01)

        finally:
            print("\033[?25h", end="")  # restore cursor

        # Game over screen
        if score > record:
            record = score
            save_record(record)
            msg = f"{BRIGHT}{YELLOW}Novo recorde! {score} pontos!{RESET}"
        else:
            msg = f"{RED}Game Over!{RESET} Pontos: {BRIGHT}{score}{RESET}"

        clear()
        lines = HEIGHT + 4
        pad = "\n" * (lines // 2 - 2)
        print(
            pad +
            f"  {'='*28}\n"
            f"  {msg}\n"
            f"  Recorde: {BRIGHT}{YELLOW}{record}{RESET}\n"
            f"  {'='*28}\n\n"
            f"  {DIM}[Enter] jogar de novo   [Q] sair{RESET}\n"
        )

        while True:
            k = get_key()
            if k == 'q':
                return
            if k == '\r' or k == '\n' or k == ' ':
                break
            time.sleep(0.05)

def main():
    clear()
    enable_ansi()
    print(
        f"\n\n"
        f"  {BRIGHT}{GREEN}╔══════════════════════════╗{RESET}\n"
        f"  {BRIGHT}{GREEN}║   🐍  SNAKE  TERMINAL    ║{RESET}\n"
        f"  {BRIGHT}{GREEN}╚══════════════════════════╝{RESET}\n\n"
        f"  Controles: {BRIGHT}W A S D{RESET} ou {BRIGHT}↑ ↓ ← →{RESET}\n"
        f"  Coma {YELLOW}★{RESET} para crescer e ganhar pontos.\n"
        f"  A velocidade aumenta a cada 5 pontos.\n\n"
        f"  {DIM}[Enter] para começar   [Q] sair{RESET}\n"
    )

    while True:
        k = get_key()
        if k == 'q':
            return
        if k in ('\r', '\n', ' '):
            break
        time.sleep(0.05)

    run_game()
    clear()
    print(f"\n  {DIM}Até a próxima!{RESET}\n")

if __name__ == "__main__":
    main()
