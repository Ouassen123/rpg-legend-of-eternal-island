# src/monster.py
import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GOBLIN_COLOR, WOLF_COLOR, SPIDER_COLOR, GENERIC_MONSTER_COLOR, IMP_COLOR, RED, GREEN # Importer couleurs

class Monster:
    def __init__(self, x, y, level, monster_type="generic"):
        self.x = float(x)
        self.y = float(y)
        self.level = level
        self.monster_type = monster_type.lower()

        self.name = f"{self.monster_type.capitalize()} Lvl {self.level}"
        self.width = 30
        self.height = 30
        self.color = GENERIC_MONSTER_COLOR
        self.speed = 50.0 + (self.level * 5)
        self.hp = 30 + (self.level * 15)
        self.max_hp = self.hp
        self.attack_power = 5 + (self.level * 3)
        self.xp_given = 10 + (self.level * 5)
        
        self.set_type_specific_attributes()

        self.dx_direction = random.choice([-1, 0, 1]) 
        self.dy_direction = random.choice([-1, 0, 1])
        if self.dx_direction == 0 and self.dy_direction == 0: # S'assurer qu'il bouge au début
            self.dx_direction = 1 


    def set_type_specific_attributes(self):
        if self.monster_type == "goblin":
            self.name = f"Gobelin Lvl {self.level}"; self.color = GOBLIN_COLOR; self.hp=20+(self.level*10); self.attack_power=3+(self.level*2); self.xp_given=8+(self.level*4); self.speed=60+(self.level*6)
        elif self.monster_type == "wolf":
            self.name = f"Loup Lvl {self.level}"; self.color = WOLF_COLOR; self.hp=25+(self.level*12); self.attack_power=6+(self.level*3); self.xp_given=12+(self.level*6); self.speed=75+(self.level*7)
        elif self.monster_type == "goblin_shaman":
            self.name = f"Chaman Gobelin Lvl {self.level}"; self.color=(30,180,180); self.hp=15+(self.level*8); self.attack_power=7+(self.level*4); self.xp_given=15+(self.level*7)
        elif self.monster_type == "giant_spider":
            self.name = f"Araignée Géante Lvl {self.level}"; self.color=SPIDER_COLOR; self.width=35; self.height=35; self.hp=40+(self.level*20); self.attack_power=4+(self.level*2); self.xp_given=20+(self.level*8); self.speed=40+(self.level*4)
        elif self.monster_type == "imp":
            self.name = f"Diablotin Lvl {self.level}"; self.color=IMP_COLOR; self.hp=18+(self.level*9); self.attack_power=8+(self.level*3); self.xp_given=18+(self.level*6); self.speed=70+(self.level*5)
        self.max_hp = self.hp

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0: self.hp = 0

    def move_random(self, dt_seconds):
        if random.random() < 0.02: 
            self.dx_direction = random.choice([-1, 0, 1])
            self.dy_direction = random.choice([-1, 0, 1])
            if self.dx_direction == 0 and self.dy_direction == 0: # S'assurer qu'il y a un mouvement
                 self.dx_direction = 1 if random.random() < 0.5 else -1
        
        move_dist = self.speed * dt_seconds
        if self.dx_direction != 0 and self.dy_direction != 0: move_dist *= 0.7071

        self.x += self.dx_direction * move_dist
        self.y += self.dy_direction * move_dist
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def draw_health_bar(self, screen):
        if self.hp < self.max_hp and self.hp > 0:
            bar_width = self.width; bar_height = 5
            bar_x = self.x; bar_y = self.y - bar_height - 2
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height)) # Couleur rouge importée
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * hp_ratio, bar_height)) # Couleur verte importée

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect())
        self.draw_health_bar(screen)