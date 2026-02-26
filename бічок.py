import pygame
import random
import math
import sys
import os

# --- Ініціалізація Pygame та звуків ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# --- Вікно ---
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Fruit")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# --- Фоновий звук ---
try:
    pygame.mixer.music.load("fon.wav")
    pygame.mixer.music.set_volume(0.4)
except pygame.error as e:
    print("Не вдалося завантажити fon.wav:", e)

try:
    menybe = pygame.image.load("JKL.png")
    bananakatana = pygame.image.load("бананкатана.png.png").convert_alpha()
    morkvanakatana = pygame.image.load("морквакатана.png.png").convert_alpha()
    grytokatana = pygame.image.load("груткатана.png.png").convert_alpha()
    defoltkatana= pygame.image.load("дефолт.png.png").convert_alpha()
    piratzykakatana = pygame.image.load("піратськакатана.png.png").convert_alpha()
    zolotakatana= pygame.image.load("золотакатана.png.png").convert_alpha()
    kavynovakatana = pygame.image.load("кавунокатана.png.png").convert_alpha()

    bananakatana = pygame.transform.scale(bananakatana, (130,42))
    morkvanakatana = pygame.transform.scale(morkvanakatana, (130,42))
    grytokatana = pygame.transform.scale(grytokatana, (130,42))
    defoltkatana = pygame.transform.scale(defoltkatana, (130,42))
    piratzykakatana = pygame.transform.scale(piratzykakatana, (130,42))
    zolotakatana = pygame.transform.scale(zolotakatana, (130,42))
    kavynovakatana = pygame.transform.scale(kavynovakatana, (130,42))
except pygame.error as e:
    print("Помилка завантаження зображень. Перевірте шляхи:", e)
    sys.exit()

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

SKINS = [
    {"name":"defoltkatana", "file": defoltkatana, "price": 0}, 
    {"name":"piratzykakatana", "file": piratzykakatana, "price": 300},
    {"name":"zolotakatana", "file": zolotakatana, "price": 700},
    {"name":"grytokatana", "file": grytokatana, "price": 999},
    {"name":"morkvanakatana", "file": morkvanakatana, "price": 1500},
    {"name":"kavynovakatana", "file": kavynovakatana, "price": 3333},
    {"name":"bananakatana", "file": bananakatana, "price": 9999}
]

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
SKINS_FILE = "skin.txt"
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

def load_skins():
    if os.path.exists(SKINS_FILE):
        with open(SKINS_FILE, "r") as f:
           return [int(x)for x in f.read().split(",")]
    return [0]

def save_skins(skins_kypleni):
    with open(SKINS_FILE, "w") as f:
        f.write(",".join(map(str,skins_kypleni)))

# --- Ініціалізація гри ---
def reset_game():
    return [], [], 0, 10.0, 1

fruits_on_screen = []
bombs_on_screen = []
score = 0
lives = 10.0
coins = load_coins()
game_started = False
game_over = False
spawn_rate = 1
paused = False
state = "menu"
skins_kypleni = load_skins()
pochekayskin = 0
natobibrat = 0

# --- Катана ---
KATANA_LENGTH = 130
BLADE_END = 95
HANDLE_CENTER_X = 112

katana_base = SKINS[natobibrat]["file"]
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

def draw_button(surface, rect, text, color): 
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 2)
    label = font.render(text, True, BLACK)
    surface.blit(label, (rect.x + rect.width//2 - label.get_width()//2,
                         rect.y + rect.height//2 - label.get_height()//2))

# --- Головний цикл ---
while True:
    clock.tick(60)
    
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_coins(coins)
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_clicked = True

    if state == "menu":
        rostaqag = pygame.transform.scale(menybe,(WIDTH, HEIGHT))
        screen.blit(rostaqag, (0,0))

        buttonplay = pygame.Rect(WIDTH// 2 -100, 250, 200, 67)
        buttonSKIN = pygame.Rect(WIDTH// 2 -100, 320, 200, 67)
        buttonmagazzine = pygame.Rect(WIDTH// 2 -100, 390, 200, 67)

        draw_button(screen, buttonplay, "play", RED)
        draw_button(screen, buttonSKIN, "skin", RED)
        draw_button(screen, buttonmagazzine, "magazzine", RED)

        if mouse_clicked:
            if buttonplay.collidepoint(mouse_pos):
                fruits_on_screen, bombs_on_screen, score, lives, spawn_rate = reset_game()
                state = "game"
                katana_base = SKINS[natobibrat]["file"]
                try:
                    pygame.mixer.music.play(-1)
                except:
                    pass
            elif buttonmagazzine.collidepoint(mouse_pos): 
                state = "magazine"

    elif state == "magazine":
        screen.fill((255, 215, 0))
        nazar = pygame.Rect(10, 10, 100, 42)
        knopkavlivova = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 -25, 52, 52)
        knopkavpravova = pygame.Rect(WIDTH//2 + 200, HEIGHT//2 -25, 52, 52)
        kyputuvovy = pygame.Rect(WIDTH//2 - 111, 450, 222, 67)
        
        draw_button(screen, nazar, "назад", RED)
        draw_button(screen, knopkavlivova, "<", RED)
        draw_button(screen, knopkavpravova, ">", RED)
        
        skin = SKINS[pochekayskin]
        skinmagazini = pygame.transform.scale(skin["file"], (260,80))
        screen.blit(skinmagazini,(WIDTH//2 - 130, HEIGHT//2 - 40))

        name_txt = font.render(skin["name"], True, BLACK)
        screen.blit(name_txt, (WIDTH//2 - name_txt.get_width()//2, HEIGHT//2 - 80))
        draw_coin(screen, (WIDTH - 60, 30), 20)
        screen.blit(font.render(f"{coins}", True, BLACK), (WIDTH - 80, 60))

        if pochekayskin == natobibrat:
            draw_button(screen, kyputuvovy, "Equipped", GREEN)
        elif pochekayskin in skins_kypleni:
            draw_button(screen, kyputuvovy, "Wear", YELLOW)
        else:
            draw_button(screen, kyputuvovy, f"Buy: {skin['price']}", ORANGE)

        if mouse_clicked:
            if nazar.collidepoint(mouse_pos): 
                state = "menu"
            elif knopkavlivova.collidepoint(mouse_pos): 
                pochekayskin = (pochekayskin - 1) % len(SKINS)
            elif knopkavpravova.collidepoint(mouse_pos): 
                pochekayskin = (pochekayskin + 1) % len(SKINS)
            elif kyputuvovy.collidepoint(mouse_pos):
                if pochekayskin in skins_kypleni:
                    natobibrat = pochekayskin 
                elif coins >= skin["price"]:
                    coins -= skin["price"]
                    skins_kypleni.append(pochekayskin) 
                    natobibrat = pochekayskin 
                    save_coins(coins)
                    save_skins(skins_kypleni) 

    elif state == "game":
        draw_background()
        stop_button = pygame.Rect(15, 10, 100, 40) 
        continue_button = pygame.Rect(WIDTH//2-100, HEIGHT//2-25, 200, 50)

        if mouse_clicked and stop_button.collidepoint(mouse_pos) and not paused:
            paused = True

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(OVERLAY)
            screen.blit(overlay, (0,0))
            draw_button(screen, continue_button, "Продовжити", RED)
            knopkadlqmeny = pygame.Rect( WIDTH //2 -100, 367, 200, 67)
            draw_button(screen, knopkadlqmeny, "go to menu", RED)
            if mouse_clicked:
                if continue_button.collidepoint(mouse_pos):
                    paused = False
                elif knopkadlqmeny.collidepoint(mouse_pos):
                    save_coins(coins)
                    paused = False
                    state = "menu"
            
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
            elif bomb.y > HEIGHT + bomb.radius:
                bombs_on_screen.remove(bomb)

        spawn_rate += 0.001

        screen.blit(rotated, katana_rect.topleft)
        draw_button(screen, stop_button, "STOP", RED)
        screen.blit(font.render(f"Lives: {int(lives)}", True, BLACK), (130, 20))
        draw_coin(screen, (WIDTH - 60, 30), 20)
        screen.blit(font.render(f"{coins}", True, BLACK), (WIDTH - 80, 60))
        
        if lives <= 0:
            screen.blit(big_font.render("GAME OVER", True, BLACK), (290, 220))
            pygame.display.flip()
            pygame.time.delay(2000)
            save_coins(coins)
            pygame.mixer.music.stop()
            state = "menu"

    pygame.display.flip()
