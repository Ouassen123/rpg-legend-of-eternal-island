# src/player.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class Weapon:
    def __init__(self, name, min_level, damage):
        self.name = name
        self.min_level = min_level
        self.damage = damage

class Player:
    def __init__(self, name, gender, x=400, y=300, current_map_id="player_house_inside"):
        self.name = name
        self.gender = gender.lower()
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 32
        self.color = (0, 100, 255) if self.gender == "homme" else (255, 105, 180)

        self.current_map_id = current_map_id

        self.hp = 100
        self.max_hp = 100
        self.xp = 0
        self.level = 1
        self.max_xp = 100

        self.inventory = []
        self.max_inventory_size = 10
        self.chest_inventory = [] # Inventaire du coffre de la maison, initialisé vide
        self.max_chest_size = 10

        self.weapons = [
            Weapon("Mains nues", 1, 2),
            Weapon("Bâton en bois", 1, 5),
            Weapon("Dague en pierre", 3, 8),
            Weapon("Épée en fer", 6, 15),
            Weapon("Hache Elfique", 8, 20),
            Weapon("Lame Démoniaque", 10, 25)
        ]
        self.current_weapon_index = 0
        self.current_weapon = self.weapons[self.current_weapon_index]

        self.level_up_message = ""
        self.level_up_timer = 0
        self.speed = 200.0

        self.calculate_max_hp()
        self.calculate_max_xp()
        self.hp = self.max_hp

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def calculate_max_hp(self):
        self.max_hp = 80 + self.level * 20

    def calculate_max_xp(self):
        self.max_xp = 75 + self.level * 25

    def update_movement(self, keys, dt_seconds, solid_objects_data):
        prev_x, prev_y = self.x, self.y
        move_x_direction = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        move_y_direction = (keys[pygame.K_DOWN] - keys[pygame.K_UP])
        current_move_speed = self.speed
        
        if move_x_direction != 0 and move_y_direction != 0:
            actual_dx = move_x_direction * current_move_speed * dt_seconds * 0.70710678118
            actual_dy = move_y_direction * current_move_speed * dt_seconds * 0.70710678118
        else:
            actual_dx = move_x_direction * current_move_speed * dt_seconds
            actual_dy = move_y_direction * current_move_speed * dt_seconds
            
        self.x += actual_dx
        self.y += actual_dy

        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        player_new_rect = self.get_rect()

        for obj_data in solid_objects_data:
            if obj_data.get("solid", False):
                obj_rect = None
                if obj_data["type"] == "tree":
                    obj_rect = pygame.Rect(
                        obj_data["x"] - obj_data.get("trunk_width", 10) // 2,
                        obj_data["y"] - obj_data.get("trunk_height", 20) // 2,
                        obj_data.get("trunk_width", 10),
                        obj_data.get("trunk_height", 20)
                    )
                elif obj_data["type"] == "rock":
                    radius = obj_data.get("radius", 15)
                    obj_rect = pygame.Rect(
                        obj_data["x"] - radius, obj_data["y"] - radius,
                        radius * 2, radius * 2
                    )
                elif obj_data["type"] == "wall" or obj_data["type"] == "player_chest" or obj_data["type"] == "bed" or obj_data["type"] == "table" or obj_data["type"] == "house_structure": # Rendre ces objets solides
                    obj_rect = pygame.Rect(obj_data["x"], obj_data["y"], obj_data["width"], obj_data["height"])
                elif obj_data.get("width") and obj_data.get("height") and obj_data.get("type") != "rug" and obj_data.get("type") != "window": # Cas générique pour objets rectangulaires solides
                     obj_rect = pygame.Rect(obj_data["x"], obj_data["y"], obj_data["width"], obj_data["height"])

                if obj_rect and player_new_rect.colliderect(obj_rect):
                    self.x = prev_x
                    if self.get_rect().colliderect(obj_rect):
                        self.x = player_new_rect.x
                        self.y = prev_y
                        if self.get_rect().colliderect(obj_rect):
                            self.x = prev_x
                            self.y = prev_y
                    player_new_rect = self.get_rect()
        
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up_this_gain = False
        while self.xp >= self.max_xp:
            self.level += 1
            self.xp -= self.max_xp
            self.calculate_max_xp()
            self.calculate_max_hp()
            self.hp = self.max_hp
            if self.level % 3 == 0: self.max_inventory_size += 1
            self.level_up_message = f"Niveau {self.level} atteint !"
            self.level_up_timer = 180
            leveled_up_this_gain = True
            self.equip_best_available_weapon()
        return leveled_up_this_gain

    def get_possess_and_usable_weapons(self):
        return [
            weapon_obj for weapon_obj in self.weapons
            if weapon_obj.name in self.inventory and self.level >= weapon_obj.min_level
        ]

    def equip_best_available_weapon(self):
        usable_weapons_list = self.get_possess_and_usable_weapons()
        if not usable_weapons_list:
            mains_nues_obj = self.weapons[0]
            if mains_nues_obj.name in self.inventory and self.level >= mains_nues_obj.min_level:
                self.current_weapon = mains_nues_obj
                self.current_weapon_index = 0
            return
        best_weapon_to_equip = usable_weapons_list[0]
        for weapon in usable_weapons_list:
            if weapon.damage > best_weapon_to_equip.damage:
                best_weapon_to_equip = weapon
        if best_weapon_to_equip != self.current_weapon:
            self.current_weapon = best_weapon_to_equip
            try: self.current_weapon_index = self.weapons.index(self.current_weapon)
            except ValueError:
                 self.current_weapon_index = 0
                 self.current_weapon = self.weapons[0]

    def cycle_weapon(self):
        possess_and_usable_list = self.get_possess_and_usable_weapons()
        if not possess_and_usable_list:
            self.equip_best_available_weapon()
            return
        try:
            current_idx_in_filtered_list = possess_and_usable_list.index(self.current_weapon)
            next_idx_in_filtered_list = (current_idx_in_filtered_list + 1) % len(possess_and_usable_list)
            self.current_weapon = possess_and_usable_list[next_idx_in_filtered_list]
        except ValueError:
            self.current_weapon = possess_and_usable_list[0]
        try: self.current_weapon_index = self.weapons.index(self.current_weapon)
        except ValueError:
            self.current_weapon_index = 0
            self.current_weapon = self.weapons[0]

    def add_item(self, item_name_to_add, target_inventory="player"):
        inventory_to_use = None
        max_size = 0

        if target_inventory == "player":
            inventory_to_use = self.inventory
            max_size = self.max_inventory_size
        elif target_inventory == "chest":
            inventory_to_use = self.chest_inventory
            max_size = self.max_chest_size
        else:
            # print(f"Type d'inventaire cible inconnu: {target_inventory}")
            return False

        if len(inventory_to_use) < max_size:
            is_weapon = any(w.name == item_name_to_add for w in self.weapons)
            if is_weapon and item_name_to_add in inventory_to_use:
                return False 
            inventory_to_use.append(item_name_to_add)
            if target_inventory == "player" and is_weapon:
                newly_added_weapon_obj = next((w for w in self.weapons if w.name == item_name_to_add), None)
                if newly_added_weapon_obj and self.level >= newly_added_weapon_obj.min_level:
                    if self.current_weapon.name == "Mains nues" or newly_added_weapon_obj.damage > self.current_weapon.damage:
                        self.current_weapon = newly_added_weapon_obj
                        self.current_weapon_index = self.weapons.index(newly_added_weapon_obj)
            return True
        # else: print(f"Inventaire '{target_inventory}' plein pour {item_name_to_add}.")
        return False

    def remove_item(self, item_name_to_remove, source_inventory="player"):
        inventory_to_use = None
        if source_inventory == "player":
            inventory_to_use = self.inventory
        elif source_inventory == "chest":
            inventory_to_use = self.chest_inventory
        else:
            # print(f"Type d'inventaire source inconnu: {source_inventory}")
            return False

        if item_name_to_remove in inventory_to_use:
            inventory_to_use.remove(item_name_to_remove)
            if source_inventory == "player" and self.current_weapon.name == item_name_to_remove:
                self.equip_best_available_weapon()
            return True
        # else: print(f"'{item_name_to_remove}' non trouvé dans inventaire '{source_inventory}'.")
        return False

    def update(self):
        if self.level_up_timer > 0:
            self.level_up_timer -= 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect())
        if self.level_up_timer > 0:
            try:
                font_for_levelup = pygame.font.SysFont(None, 48)
                level_up_text_surface = font_for_levelup.render(self.level_up_message, True, (255, 215, 0))
                text_rect = level_up_text_surface.get_rect(center=(SCREEN_WIDTH // 2, 70))
                screen.blit(level_up_text_surface, text_rect)
            except pygame.error as e: print(f"Erreur police level up: {e}")

    def save_data(self):
        inventory_str = ",".join(self.inventory)
        chest_inventory_str = ",".join(self.chest_inventory)
        return (
            self.name, self.gender,
            int(self.x), int(self.y),
            inventory_str,
            int(self.xp), int(self.level), int(self.max_xp),
            int(self.hp), int(self.max_hp),
            self.current_weapon_index,
            self.current_map_id,
            chest_inventory_str
        )