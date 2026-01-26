import pygame
import random
import math
import sys
import os

# --- Ініціалізація Pygame та звуків ---
pygame.mixer.pre_init(44100, -16, 2, 512)  # краща сумісність для wav
pygame.init()

# --- Завантаження звуків ---
try:
    sound_fruit = pygame.mixer.Sound("fonarik.wav")
except pygame.error as e:
    print("Не вдалося завантажити fonarik.wav:", e)
    sound_fruit = None

try:
    sound_bomb = pygame.mixer.Sound("oplata.wav")
except pygame.error as e:
    print("Не вдалося завантажити oplata.wav:", e)
    sound_bomb = None

# --- Вікно ---
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Fruit")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# --- Кольори ---
WHITE = (245, 245, 245)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
GREEN = (60, 200, 100)
BROWN = (139, 69, 19)
BROWN_DARK = (101, 67, 33)
GRAY = (120, 120, 120)
OVERLAY = (0, 0, 0, 120)

# --- Фрукти ---
FRUITS = [
    "apple", "banana", "strawberry", "kiwi",
    "pineapple", "cherry", "mango", "peach",
    "coconut", "carrot", "pepper"
]

# --- Функції збереження / завантаження монет ---
COINS_FILE = "coins.txt"

def load_coins():
    if os.path.exists(COINS_FILE):
        with open(COINS_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_coins(coins):
    with open(COINS_FILE, "w") as f:
        f.write(str(int(coins)))

# --- Ініціалізація гри ---
def reset_game():
    return [], [], 0, 10.0, True, False, 1

fruits_on_screen = []
bombs_on_screen = []
score = 0
lives = 10.0
coins = load_coins()
game_started = False
game_over = False
spawn_rate = 1
paused = False

# --- Катана ---
KATANA_LENGTH = 130
BLADE_END = 95
HANDLE_CENTER_X = 112

katana_base = pygame.Surface((KATANA_LENGTH, 26), pygame.SRCALPHA)
pygame.draw.rect(katana_base, (200, 200, 200), (0, 10, 95, 6))
pygame.draw.rect(katana_base, BROWN, (95, 6, 35, 14))

katana_angle = 0
last_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

# --- Класи Fruit і Bomb ---
class Fruit:
    def __init__(self):
        self.type = random.choice(FRUITS)
        self.radius = random.randint(25, 35)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = HEIGHT + self.radius
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-15, -10)

    def update(self):
        self.vy += 0.25
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        x, y, r = int(self.x), int(self.y), int(self.radius)
        if self.type == "apple":
            pygame.draw.circle(screen, RED, (x, y), r)
            pygame.draw.line(screen, BROWN, (x, y-r), (x, y-r-10), 3)
            pygame.draw.circle(screen, WHITE, (x-r//3, y-r//3), r//4)
        elif self.type == "banana":
            pygame.draw.ellipse(screen, YELLOW, (x-r, y-r//2, r*2, r))
        elif self.type == "strawberry":
            pygame.draw.polygon(screen, RED, [(x, y-r), (x-r, y+r), (x+r, y+r)])
            pygame.draw.polygon(screen, GREEN, [(x-5, y-r-5), (x+5, y-r-5), (x, y-r-15)])
        elif self.type == "kiwi":
            pygame.draw.circle(screen, BROWN_DARK, (x, y), r)
            pygame.draw.circle(screen, GREEN, (x, y), int(r*0.8))
        elif self.type == "pineapple":
            pygame.draw.ellipse(screen, ORANGE, (x-r, y-r, r*2, r*2))
            pygame.draw.line(screen, GREEN, (x, y-r), (x, y-r-20), 4)
        elif self.type == "cherry":
            pygame.draw.circle(screen, RED, (x-r//2, y), r//1.3)
            pygame.draw.circle(screen, RED, (x+r//2, y), r//1.3)
            pygame.draw.line(screen, BROWN, (x, y-r), (x, y-r-10), 2)
        elif self.type == "mango":
            pygame.draw.ellipse(screen, ORANGE, (x-r, y-r//2, r*2, r))
        elif self.type == "peach":
            pygame.draw.circle(screen, ORANGE, (x, y), r)
            pygame.draw.circle(screen, RED, (x-r//4, y-r//4), r//3)
        elif self.type == "coconut":
            pygame.draw.circle(screen, BROWN, (x, y), r)
            pygame.draw.circle(screen, WHITE, (x, y), int(r*0.7))
        elif self.type == "carrot":
            pygame.draw.polygon(screen, ORANGE, [(x, y-r), (x-r//2, y+r), (x+r//2, y+r)])
            pygame.draw.polygon(screen, GREEN, [(x-5, y-r-5), (x+5, y-r-5), (x, y-r-15)])
        elif self.type == "pepper":
            pygame.draw.ellipse(screen, GREEN, (x-r, y-r, r*2, int(r*1.5)))

    def hit_by_blade(self, a, b):
        px, py = self.x, self.y
        x1, y1 = a
        x2, y2 = b
        l2 = (x2-x1)**2 + (y2-y1)**2
        if l2 == 0:
            return False
        t = max(0, min(1, ((px-x1)*(x2-x1)+(py-y1)*(y2-y1))/l2))
        cx = x1 + t*(x2-x1)
        cy = y1 + t*(y2-y1)
        return math.hypot(px-cx, py-cy) <= self.radius

class Bomb(Fruit):
    def draw(self):
        x, y, r = int(self.x), int(self.y), int(self.radius)
        pygame.draw.circle(screen, BLACK, (x, y), r)
        pygame.draw.line(screen, GRAY, (x, y-r), (x, y-r-15), 3)
        pygame.draw.circle(screen, RED, (x, y-r-15), 4)

# --- Інші функції (фон, кнопки, HUD) ---
def draw_background():
    for y in range(HEIGHT):
        c = 180 + int(40 * y / HEIGHT)
        pygame.draw.line(screen, (255, c, 180), (0, y), (WIDTH, y))
    pygame.draw.circle(screen, (255, 200, 100), (760, 120), 60)
    pygame.draw.rect(screen, (90, 160, 90), (0, 500, WIDTH, 100))
    pygame.draw.polygon(screen, (130,130,150), [(0,500),(200,300),(400,500)])
    pygame.draw.polygon(screen, (110,110,130), [(300,500),(550,280),(800,500)])

def draw_coin(surface, pos, radius):
    pygame.draw.circle(surface, GOLD, pos, radius)
    pygame.draw.circle(surface, ORANGE, pos, radius-3)
    pygame.draw.circle(surface, YELLOW, pos, radius-6)
    pygame.draw.line(surface, ORANGE, (pos[0]-radius//2, pos[1]), (pos[0]+radius//2, pos[1]), 2)
    pygame.draw.line(surface, ORANGE, (pos[0], pos[1]-radius//2), (pos[0], pos[1]+radius//2), 2)

def draw_button(surface, rect, text):
    pygame.draw.rect(surface, ORANGE, rect)
    pygame.draw.rect(surface, BLACK, rect, 2)
    label = font.render(text, True, BLACK)
    surface.blit(label, (rect.x + rect.width//2 - label.get_width()//2,
                         rect.y + rect.height//2 - label.get_height()//2))

# --- Головний цикл ---
while True:
    clock.tick(60)
    draw_background()
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    mouse_clicked = pygame.mouse.get_pressed()[0]

    stop_button = pygame.Rect(15, 10, 100, 40)
    continue_button = pygame.Rect(WIDTH//2-100, HEIGHT//2-25, 200, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_coins(coins)
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_started or game_over:
                fruits_on_screen, bombs_on_screen, score, lives, game_started, game_over, spawn_rate = reset_game()
            if stop_button.collidepoint(mouse_pos) and not paused:
                paused = True
            if paused and continue_button.collidepoint(mouse_pos):
                paused = False

    if not game_started:
        screen.blit(big_font.render("NINJA FRUIT", True, BLACK), (260, 200))
        screen.blit(font.render("Click to Start", True, BLACK), (360, 280))
        pygame.display.flip()
        continue

    if game_over:
        screen.blit(big_font.render("GAME OVER", True, BLACK), (290, 220))
        screen.blit(font.render("Click to play again", True, BLACK), (330, 300))
        pygame.display.flip()
        continue

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        screen.blit(overlay, (0,0))
        draw_button(screen, continue_button, "Продовжити")
        pygame.display.flip()
        continue

    mouse_delta = mouse_pos - last_mouse_pos
    katana_angle = max(-70, min(70, -mouse_delta.x * 3))
    last_mouse_pos = mouse_pos

    rotated = pygame.transform.rotate(katana_base, katana_angle)
    offset = pygame.Vector2(HANDLE_CENTER_X - KATANA_LENGTH//2, 0).rotate(-katana_angle)
    katana_rect = rotated.get_rect(center=mouse_pos - offset)

    blade_a = pygame.Vector2(0, 13).rotate(-katana_angle) + katana_rect.center
    blade_b = pygame.Vector2(BLADE_END, 13).rotate(-katana_angle) + katana_rect.center

    if random.randint(1, max(1,int(60/spawn_rate))) == 1:
        fruits_on_screen.append(Fruit())
    if random.randint(1, 120) == 1:
        bombs_on_screen.append(Bomb())

    for fruit in fruits_on_screen[:]:
        fruit.update()
        fruit.draw()
        if fruit.hit_by_blade(blade_a, blade_b):
            fruits_on_screen.remove(fruit)
            lives += 1
            coins += 1
            if sound_fruit:
                sound_fruit.play()
        elif fruit.y > HEIGHT + fruit.radius:
            fruits_on_screen.remove(fruit)
            lives -= 0.5
            if lives <= 0:
                lives = 0
                game_over = True

    for bomb in bombs_on_screen[:]:
        bomb.update()
        bomb.draw()
        if bomb.hit_by_blade(blade_a, blade_b):
            bombs_on_screen.remove(bomb)
            lives -= 1
            coins -= 1
            if sound_bomb:
                sound_bomb.play()
            if lives <= 0:
                lives = 0
                game_over = True
        elif bomb.y > HEIGHT + bomb.radius:
            bombs_on_screen.remove(bomb)

    spawn_rate += 0.001

    screen.blit(rotated, katana_rect.topleft)
    draw_button(screen, stop_button, "STOP")
    screen.blit(font.render(f"Lives: {int(lives)}", True, BLACK), (130, 20))
    draw_coin(screen, (WIDTH - 60, 30), 20)
    screen.blit(font.render(f"{coins}", True, BLACK), (WIDTH - 80, 60))

    pygame.display.flip()
