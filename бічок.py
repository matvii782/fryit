import pygame
import random
import math
import sys

pygame.init()

# --- Вікно ---
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Fruit - Detailed Fruits & Katana")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- Кольори ---
BLACK = (0, 0, 0)
WHITE = (245, 245, 245)
RED = (220, 60, 60)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (60, 200, 100)
PURPLE = (160, 32, 240)
BROWN = (139, 69, 19)
BROWN_DARK = (101, 67, 33)

# --- Фрукти / овочі ---
FRUITS = ["apple", "orange", "banana", "grape", "lemon", "strawberry",
          "kiwi", "pineapple", "cherry", "mango", "plum", "peach",
          "coconut", "carrot", "tomato", "pepper"]

fruits_on_screen = []
score = 0
lives = 10
game_started = False

# --- Катана ---
katana_img = pygame.Surface((100, 20), pygame.SRCALPHA)
pygame.draw.rect(katana_img, (150, 150, 150), (0, 0, 100, 10))  # лезо
pygame.draw.rect(katana_img, (50, 20, 0), (80, 5, 20, 10))      # руків'я
katana_rect = katana_img.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
holding_katana = False

class Fruit:
    def __init__(self):
        self.type = random.choice(FRUITS)
        self.radius = random.randint(25, 35)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = HEIGHT + self.radius
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-15, -10)
        self.growth_rate = random.uniform(0.03, 0.06)

    def update(self):
        self.vy += 0.25
        self.x += self.vx
        self.y += self.vy
        self.radius += self.growth_rate

    def draw(self):
        x, y, r = int(self.x), int(self.y), int(self.radius)
        if self.type == "apple":
            pygame.draw.circle(screen, RED, (x, y), r)
            pygame.draw.line(screen, BROWN, (x, y - r), (x, y - r - 10), 3)
            pygame.draw.circle(screen, WHITE, (x - int(r*0.3), y - int(r*0.3)), int(r*0.2))
        elif self.type == "banana":
            pygame.draw.ellipse(screen, YELLOW, (x - r, y - int(r*0.5), r*2, r))
        elif self.type == "orange":
            pygame.draw.circle(screen, ORANGE, (x, y), r)
            pygame.draw.circle(screen, WHITE, (x - int(r*0.3), y - int(r*0.3)), int(r*0.2))
        elif self.type == "grape":
            for i in range(3):
                pygame.draw.circle(screen, PURPLE, (x, y - i*int(r*0.7)), int(r*0.7))
        elif self.type == "lemon":
            pygame.draw.ellipse(screen, YELLOW, (x - r, y - int(r*0.6), r*2, int(r*1.2)))
        elif self.type == "strawberry":
            pygame.draw.polygon(screen, RED, [(x, y - r), (x - r, y + r), (x + r, y + r)])
            pygame.draw.polygon(screen, GREEN, [(x - 5, y - r - 5), (x + 5, y - r - 5), (x, y - r - 15)])
        elif self.type == "kiwi":
            pygame.draw.circle(screen, BROWN_DARK, (x, y), r)
            pygame.draw.circle(screen, GREEN, (x, y), int(r*0.8))
        elif self.type == "pineapple":
            pygame.draw.ellipse(screen, ORANGE, (x - r, y - r, r*2, r*2))
            pygame.draw.line(screen, GREEN, (x, y - r), (x, y - r - 15), 3)
        elif self.type == "cherry":
            pygame.draw.circle(screen, RED, (x - int(r*0.5), y), int(r*0.6))
            pygame.draw.circle(screen, RED, (x + int(r*0.5), y), int(r*0.6))
            pygame.draw.line(screen, BROWN, (x, y - r), (x, y - r - 8), 2)
        elif self.type == "mango":
            pygame.draw.ellipse(screen, ORANGE, (x - r, y - r//2, r*2, r))
        elif self.type == "plum":
            pygame.draw.circle(screen, PURPLE, (x, y), r)
        elif self.type == "peach":
            pygame.draw.circle(screen, ORANGE, (x, y), r)
            pygame.draw.circle(screen, RED, (x - r*0.2, y - r*0.2), int(r*0.3))
        elif self.type == "coconut":
            pygame.draw.circle(screen, BROWN, (x, y), r)
            pygame.draw.circle(screen, WHITE, (x, y), int(r*0.7))
        elif self.type == "carrot":
            pygame.draw.polygon(screen, ORANGE, [(x, y - r), (x - r//2, y + r), (x + r//2, y + r)])
            pygame.draw.polygon(screen, GREEN, [(x - 5, y - r - 5), (x + 5, y - r - 5), (x, y - r - 15)])
        elif self.type == "tomato":
            pygame.draw.circle(screen, RED, (x, y), r)
            pygame.draw.polygon(screen, GREEN, [(x - 5, y - r), (x + 5, y - r), (x, y - r - 10)])
        elif self.type == "pepper":
            pygame.draw.ellipse(screen, GREEN, (x - r, y - r, r*2, int(r*1.5)))

    def is_hit(self, pos):
        return math.hypot(self.x - pos[0], self.y - pos[1]) < self.radius

while True:
    clock.tick(60)
    screen.fill(WHITE)

    # --- Події ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if katana_rect.collidepoint(event.pos):
                holding_katana = True
            if not game_started:
                game_started = True
        if event.type == pygame.MOUSEBUTTONUP:
            holding_katana = False
        if event.type == pygame.MOUSEMOTION and holding_katana:
            katana_rect.center = event.pos

    # --- Генерація фруктів ---
    if game_started and random.randint(1, 30) == 1:
        fruits_on_screen.append(Fruit())

    # --- Оновлення та малювання фруктів ---
    for fruit in fruits_on_screen[:]:
        fruit.update()
        fruit.draw()
        if fruit.y > HEIGHT + 50:
            fruits_on_screen.remove(fruit)
            lives -= 1
            if lives <= 0:
                game_started = False

        # --- Перевірка удару катаною ---
        if holding_katana and fruit.is_hit(pygame.mouse.get_pos()):
            score += 1
            fruits_on_screen.remove(fruit)

    # --- Малюємо катану ---
    screen.blit(katana_img, katana_rect.topleft)

    # --- Інформація ---
    pygame.draw.rect(screen, WHITE, (0, 0, 200, 60))
    pygame.draw.rect(screen, BLACK, (0, 0, 200, 60), 2)
    score_text = font.render(f"Score: {score}", True, BLACK)
    lives_text = font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(score_text, (10, 5))
    screen.blit(lives_text, (10, 30))

    pygame.display.flip()
