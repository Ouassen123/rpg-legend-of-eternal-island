# src/main.py
import pygame
import sys
import random

from config import * 
from player import Player
from database import save_player, load_player, init_db, mark_chest_as_looted, is_chest_looted
from maps import get_map_data
from monster import Monster

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nelyria: Aventures et Survie")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
font_medium = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 20)

init_db()

def choose_gender():
    homme_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 200, 300, 50)
    femme_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 300, 300, 50)
    title_font_gender = pygame.font.SysFont(None, 48)
    while True:
        screen.fill(WHITE)
        title = title_font_gender.render("Choisissez votre personnage", True, BLACK)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 100)))
        pygame.draw.rect(screen, BLUE, homme_button)
        pygame.draw.rect(screen, (255,192,203), femme_button) 
        text_h = font.render("Homme", True, WHITE)
        text_f = font.render("Femme", True, WHITE)
        screen.blit(text_h, text_h.get_rect(center=homme_button.center))
        screen.blit(text_f, text_f.get_rect(center=femme_button.center))
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if homme_button.collidepoint(ev.pos): return "homme"
                if femme_button.collidepoint(ev.pos): return "femme"
        pygame.display.flip()
        clock.tick(FPS)

player_save_data = load_player()
player = None
if player_save_data:
    try:
        p_name,p_gender,p_x,p_y,inv_s,p_xp,p_lvl,p_max_xp,p_hp,p_max_hp,p_w_idx,p_map_id,chest_s = player_save_data
        player = Player(p_name, p_gender, int(p_x), int(p_y), p_map_id if p_map_id else "player_house_inside")
        player.inventory = [i.strip() for i in inv_s.split(',') if i.strip()] if inv_s else []
        player.chest_inventory = [i.strip() for i in chest_s.split(',') if i.strip()] if chest_s else []
        if not player.inventory or player.weapons[0].name not in player.inventory:
             if player.weapons[0].name not in player.inventory: player.inventory.insert(0,player.weapons[0].name)
        player.xp,player.level,player.max_xp,player.hp,player.max_hp,player.current_weapon_index = \
            int(p_xp),int(p_lvl),int(p_max_xp),int(p_hp),int(p_max_hp),int(p_w_idx)
        player.calculate_max_hp(); player.calculate_max_xp()
        player.hp = min(player.hp, player.max_hp);
        if player.hp <= 0: player.hp = 1
        player.xp = min(player.xp, player.max_xp)
        if 0<=player.current_weapon_index<len(player.weapons):
            w_equip = player.weapons[player.current_weapon_index]
            if w_equip.name in player.inventory and player.level>=w_equip.min_level: player.current_weapon=w_equip
            else: player.equip_best_available_weapon()
        else: player.equip_best_available_weapon()
        if player.current_weapon is None:
            player.current_weapon=player.weapons[0]; player.current_weapon_index=0
            if player.weapons[0].name not in player.inventory: player.inventory.insert(0,player.weapons[0].name)
    except Exception as e: print(f"Err chargement: {e}. Nouveau joueur."); player_save_data=None
if not player_save_data:
    gender = choose_gender()
    player = Player("Hero", gender, current_map_id="player_house_inside")
    if player.weapons[0].name not in player.inventory: player.inventory.insert(0,player.weapons[0].name)
    player.current_weapon=player.weapons[0]; player.current_weapon_index=0
    player.chest_inventory.extend(["Potion de soin", "Vieux pain", "Pierre"]) 
    save_player(player)

current_map_data=None; monsters_on_map=[]; npcs_on_map=[]
inventory_visible=False; chest_interface_visible=False; show_monster_info_panel=False; world_map_visible=False
action_message=""; action_message_timer=0
last_attack_time=0; last_player_hit_time=0
minimap_surface=pygame.Surface((MINIMAP_WIDTH,MINIMAP_HEIGHT),pygame.SRCALPHA)
selected_item_index=-1; selected_inventory_type=None

def load_map_and_content(map_id, target_player_x=None, target_player_y=None):
    global current_map_data, monsters_on_map, player, npcs_on_map
    current_map_data = get_map_data(map_id)
    player.current_map_id = map_id
    if target_player_x is not None: player.x, player.y = float(target_player_x), float(target_player_y)
    monsters_on_map.clear(); npcs_on_map.clear()
    if "objects" in current_map_data:
        for i, obj in enumerate(current_map_data["objects"]):
            if obj["type"] == "chest":
                key=obj.get("id",f"wc_{map_id}_{i}");obj["uid"]=key;obj["is_looted"]=is_chest_looted(map_id,key)
                obj["content"]=obj.get("content", ["Potion Faible","Os"] if random.random()>0.5 else ["Caillou"])
    if "monsters_spawn_config" in current_map_data:
        for cfg in current_map_data["monsters_spawn_config"]:
            for _ in range(random.randint(cfg["count_range"][0],cfg["count_range"][1])):
                lvl=random.randint(cfg["level_range"][0],cfg["level_range"][1])
                monsters_on_map.append(Monster(random.randint(50,SCREEN_WIDTH-50),random.randint(50,SCREEN_HEIGHT-50),lvl,monster_type=cfg.get("type","generic")))
    if "npcs" in current_map_data:
        for npc_d in current_map_data["npcs"]:
            npcs_on_map.append({"rect":pygame.Rect(npc_d['x']-15,npc_d['y']-25,30,50),"color":CYAN if npc_d.get('type')=="spirit" else MAGENTA,"data":npc_d})
load_map_and_content(player.current_map_id, player.x, player.y)

def draw_hud(s, p):
    bw,bh,m = 200,20,10; hpr=p.hp/p.max_hp if p.max_hp>0 else 0; pygame.draw.rect(s,RED,(m,m,bw,bh)); pygame.draw.rect(s,GREEN,(m,m,bw*hpr,bh)); s.blit(font.render(f"HP:{p.hp}/{p.max_hp}",True,WHITE),(m+5,m))
    xpr=p.xp/p.max_xp if p.max_xp>0 else 0; pygame.draw.rect(s,(50,50,100),(m,m+bh+5,bw,bh)); pygame.draw.rect(s,LIGHT_BLUE,(m,m+bh+5,bw*xpr,bh)); s.blit(font.render(f"XP:{p.xp}/{p.max_xp}(L{p.level})",True,WHITE),(m+5,m+bh+5))
    s.blit(font.render(f"Arme:{p.current_weapon.name}({p.current_weapon.damage}D)",True,WHITE),(m,m+2*(bh+5)))
    s.blit(font.render(f"Inv:{len(p.inventory)}/{p.max_inventory_size}",True,WHITE),(m,m+3*(bh+5)))

def draw_inventory_panel(s, p):
    pw,ph=350,450;px,py=(SCREEN_WIDTH-pw)//2,(SCREEN_HEIGHT-ph)//2;pygame.draw.rect(s,DARK_GRAY,(px,py,pw,ph));pygame.draw.rect(s,WHITE,(px,py,pw,ph),2)
    title=font_large.render("Inventaire Joueur",True,WHITE);s.blit(title,(px+(pw-title.get_width())//2,py+10))
    y_off=60
    for i,it_n in enumerate(p.inventory):
        disp_t=f"({i+1}) {it_n}";w_obj=next((w for w in p.weapons if w.name==it_n),None)
        if w_obj:disp_t+=f" (D:{w_obj.damage} L:{w_obj.min_level})"
        s.blit(font_medium.render(disp_t,True,WHITE),(px+20,py+y_off+i*35))
    s.blit(font.render(f"Capacité:{len(p.inventory)}/{p.max_inventory_size}",True,LIGHT_GRAY),(px+20,py+ph-40))

def draw_chest_interface(s, p, chest_name="Coffre"):
    global selected_item_index, selected_inventory_type; pw,ph=600,450;px,py=(SCREEN_WIDTH-pw)//2,(SCREEN_HEIGHT-ph)//2;pygame.draw.rect(s,DARK_GRAY,(px,py,pw,ph),border_radius=10);pygame.draw.rect(s,WHITE,(px,py,pw,ph),2,border_radius=10)
    title_s=font_large.render(f"Interaction: {chest_name}",True,WHITE);s.blit(title_s,(px+(pw-title_s.get_width())//2,py+15)); col_w=pw//2-30; p_col_x=px+20; c_col_x=px+pw//2+10; y_start=py+80; lh=30
    s.blit(font_medium.render("Votre Inventaire",True,LIGHT_GRAY),(p_col_x,y_start-35))
    for i,it_n in enumerate(p.inventory): item_s=font.render(f"P{i+1}:{it_n}",True,YELLOW if selected_item_index==i and selected_inventory_type=="player" else WHITE); item_r=pygame.Rect(p_col_x,y_start+i*lh,col_w,lh-2);
    if item_r.collidepoint(pygame.mouse.get_pos()):pygame.draw.rect(s,(70,70,70),item_r); s.blit(item_s,(p_col_x+5,y_start+i*lh))
    s.blit(font_medium.render(f"Contenu {chest_name}",True,LIGHT_GRAY),(c_col_x,y_start-35)); c_items=p.chest_inventory
    for i,it_n in enumerate(c_items): item_s=font.render(f"C{i+1}:{it_n}",True,YELLOW if selected_item_index==i and selected_inventory_type=="chest" else WHITE); item_r=pygame.Rect(c_col_x,y_start+i*lh,col_w,lh-2);
    if item_r.collidepoint(pygame.mouse.get_pos()):pygame.draw.rect(s,(70,70,70),item_r); s.blit(item_s,(c_col_x+5,y_start+i*lh))
    s.blit(font_small.render("Clic: sélectionner, Espace: transférer, I/ESC/E: fermer",True,YELLOW),(px+20,py+ph-30))

def display_action_message(s, msg):
    if not msg:return;ts=font.render(msg,True,WHITE);tr=ts.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT-40));bgr=tr.inflate(20,10);pygame.draw.rect(s,BLACK,bgr,border_radius=5);pygame.draw.rect(s,WHITE,bgr,1,border_radius=5);s.blit(ts,tr)

def draw_minimap(s, p, cmap, monsters, npcs_list):
    minimap_surface.fill((50,50,50,MINIMAP_ALPHA))
    map_actual_width = cmap.get("world_width",SCREEN_WIDTH)
    map_actual_height = cmap.get("world_height",SCREEN_HEIGHT)
    scale_x = MINIMAP_WIDTH / map_actual_width if map_actual_width > 0 else 0
    scale_y = MINIMAP_HEIGHT / map_actual_height if map_actual_height > 0 else 0
    pygame.draw.circle(minimap_surface,MINIMAP_PLAYER_DOT_COLOR,(int(p.x*scale_x),int(p.y*scale_y)),3)
    for m_ in monsters: 
        pygame.draw.circle(minimap_surface,MINIMAP_MONSTER_DOT_COLOR,(int(m_.x*scale_x),int(m_.y*scale_y)),2)
    for n_element in npcs_list: # n_element est le dictionnaire {"rect":..., "color":..., "data":...}
        actual_npc_data = None
        if isinstance(n_element, dict) and "data" in n_element and isinstance(n_element["data"], dict):
            actual_npc_data = n_element["data"]
        elif isinstance(n_element, dict) and "x" in n_element and "y" in n_element: # Fallback
            actual_npc_data = n_element

        if actual_npc_data and "x" in actual_npc_data and "y" in actual_npc_data:
            npc_map_x = int(actual_npc_data["x"] * scale_x)
            npc_map_y = int(actual_npc_data["y"] * scale_y)
            pygame.draw.circle(minimap_surface, MINIMAP_NPC_DOT_COLOR, (npc_map_x, npc_map_y), 2)
    pygame.draw.rect(minimap_surface,WHITE,(0,0,MINIMAP_WIDTH,MINIMAP_HEIGHT),MINIMAP_BORDER)
    s.blit(minimap_surface,(SCREEN_WIDTH-MINIMAP_WIDTH-10,10))

def draw_monster_info_panel(s, m_list):
    pw,ph=400,300;px,py=(SCREEN_WIDTH-pw)//2,(SCREEN_HEIGHT-ph)//2;pygame.draw.rect(s,DARK_GRAY,(px,py,pw,ph),border_radius=10);pygame.draw.rect(s,WHITE,(px,py,pw,ph),2,border_radius=10)
    title=font_large.render("Infos Monstres",True,WHITE);s.blit(title,(px+(pw-title.get_width())//2,py+10))
    if not m_list: s.blit(font_medium.render("Aucun monstre.",True,LIGHT_GRAY),(px+(pw-font_medium.render("Aucun monstre.",True,LIGHT_GRAY).get_width())//2,py+100))
    else:
        y_offset=py+70
        for m_idx, m_obj in enumerate(m_list):
            s.blit(font.render(f"{m_obj.name}-HP:{m_obj.hp}/{m_obj.max_hp}",True,WHITE),(px+20,y_offset));y_offset+=30;
            if y_offset > py+ph-50: break
    s.blit(font_small.render("P pour fermer.",True,YELLOW),(px+20,py+ph-30))

def draw_world_map_panel(s, p_obj, current_map_info):
    panel_padding = 20
    map_display_width = SCREEN_WIDTH - panel_padding * 2
    map_display_height = SCREEN_HEIGHT - panel_padding * 2
    map_display_x = panel_padding
    map_display_y = panel_padding
    pygame.draw.rect(s, WORLD_MAP_OCEAN_COLOR, (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.draw.rect(s, WORLD_MAP_BACKGROUND_COLOR, (map_display_x,map_display_y,map_display_width,map_display_height))
    for village_key, village_data in VILLAGE_POSITIONS_ON_WORLD_MAP.items():
        village_unit_x = village_data["x"]; village_unit_y = village_data["y"]
        vx = map_display_x + (village_unit_x / TOTAL_WORLD_WIDTH_UNITS) * map_display_width
        vy = map_display_y + (village_unit_y / TOTAL_WORLD_HEIGHT_UNITS) * map_display_height
        pygame.draw.circle(s,WORLD_MAP_VILLAGE_COLOR,(int(vx),int(vy)),8)
        s.blit(font_small.render(village_data["name_on_map"],True,WORLD_MAP_TEXT_COLOR),(int(vx)+10,int(vy)-5))
    current_map_g_offset_x = current_map_info.get("global_offset_x", 0)
    current_map_g_offset_y = current_map_info.get("global_offset_y", 0)
    current_map_pixel_width = current_map_info.get("world_width", SCREEN_WIDTH)
    current_map_pixel_height = current_map_info.get("world_height", SCREEN_HEIGHT)
    player_local_ratio_x = p_obj.x / current_map_pixel_width if current_map_pixel_width > 0 else 0
    player_local_ratio_y = p_obj.y / current_map_pixel_height if current_map_pixel_height > 0 else 0
    player_world_unit_x = current_map_g_offset_x + player_local_ratio_x * MAP_FOOTPRINT_ON_WORLD_UNITS
    player_world_unit_y = current_map_g_offset_y + player_local_ratio_y * MAP_FOOTPRINT_ON_WORLD_UNITS
    player_render_x = map_display_x + (player_world_unit_x / TOTAL_WORLD_WIDTH_UNITS) * map_display_width if TOTAL_WORLD_WIDTH_UNITS > 0 else map_display_x
    player_render_y = map_display_y + (player_world_unit_y / TOTAL_WORLD_HEIGHT_UNITS) * map_display_height if TOTAL_WORLD_HEIGHT_UNITS > 0 else map_display_y
    pygame.draw.circle(s,WORLD_MAP_PLAYER_COLOR,(int(player_render_x),int(player_render_y)),5)
    area_render_x = map_display_x + (current_map_g_offset_x / TOTAL_WORLD_WIDTH_UNITS) * map_display_width if TOTAL_WORLD_WIDTH_UNITS > 0 else map_display_x
    area_render_y = map_display_y + (current_map_g_offset_y / TOTAL_WORLD_HEIGHT_UNITS) * map_display_height if TOTAL_WORLD_HEIGHT_UNITS > 0 else map_display_y
    area_render_w = (MAP_FOOTPRINT_ON_WORLD_UNITS / TOTAL_WORLD_WIDTH_UNITS) * map_display_width if TOTAL_WORLD_WIDTH_UNITS > 0 else 0
    area_render_h = (MAP_FOOTPRINT_ON_WORLD_UNITS / TOTAL_WORLD_HEIGHT_UNITS) * map_display_height if TOTAL_WORLD_HEIGHT_UNITS > 0 else 0
    highlight_surf = pygame.Surface((max(1,int(area_render_w)), max(1,int(area_render_h))),pygame.SRCALPHA)
    highlight_surf.fill(WORLD_MAP_CURRENT_AREA_HIGHLIGHT_COLOR)
    s.blit(highlight_surf,(int(area_render_x),int(area_render_y)))
    title_surf = font_large.render("Carte de Nelyria",True,WORLD_MAP_TEXT_COLOR)
    s.blit(title_surf,title_surf.get_rect(centerx=SCREEN_WIDTH//2,y=panel_padding+5))
    s.blit(font_medium.render("M ou ESC pour fermer",True,YELLOW),font_medium.render("M ou ESC pour fermer",True,YELLOW).get_rect(centerx=SCREEN_WIDTH//2,bottom=SCREEN_HEIGHT-panel_padding-5))

running = True; game_over_state = False
while running:
    dt_ms=clock.tick(FPS); dt_seconds=dt_ms/1000.0; current_time_ticks=pygame.time.get_ticks(); mouse_pos=pygame.mouse.get_pos()
    if action_message_timer>0: action_message_timer-=dt_ms; 
    if action_message_timer<=0:action_message=""
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            if not game_over_state:save_player(player)
            running=False
        if game_over_state:
            if ev.type==pygame.KEYDOWN:
                game_over_state=False;p_name_temp,p_gender_temp=player.name,player.gender;player=Player(p_name_temp,p_gender_temp,current_map_id="player_house_inside")
                if player.weapons[0].name not in player.inventory:player.inventory.insert(0,player.weapons[0].name) 
                player.current_weapon=player.weapons[0];player.current_weapon_index=0
                player.chest_inventory.clear(); player.chest_inventory.extend(["Potion de soin", "Vieux pain"])
                load_map_and_content("player_house_inside",SCREEN_WIDTH//2,SCREEN_HEIGHT-150) 
                action_message="Vous vous réveillez...";action_message_timer=2500;save_player(player)
            continue
        if world_map_visible:
            if ev.type==pygame.KEYDOWN and (ev.key==SHOW_WORLD_MAP_KEY or ev.key==pygame.K_ESCAPE): world_map_visible=False
            continue
        if inventory_visible:
            if ev.type==pygame.KEYDOWN and (ev.key==INVENTORY_KEY or ev.key==pygame.K_ESCAPE): inventory_visible=False
            continue
        if chest_interface_visible:
            if ev.type==pygame.KEYDOWN:
                if ev.key in [INVENTORY_KEY,pygame.K_ESCAPE,INTERACTION_KEY]: chest_interface_visible=False;selected_item_index=-1;selected_inventory_type=None 
                elif ev.key==pygame.K_SPACE and selected_item_index!=-1 and selected_inventory_type: 
                    source_inventory_list = player.inventory if selected_inventory_type=="player" else player.chest_inventory
                    target_inventory_type_str = "chest" if selected_inventory_type=="player" else "player"
                    if 0<=selected_item_index<len(source_inventory_list):
                        item_name_to_move = source_inventory_list[selected_item_index]
                        if player.add_item(item_name_to_move,target_inventory=target_inventory_type_str): 
                            player.remove_item(item_name_to_move,source_inventory=selected_inventory_type) 
                            action_message=f"'{item_name_to_move}' transféré."
                        else: action_message=f"Échec transfert: '{item_name_to_move}'. Destination pleine?"
                        action_message_timer=1500
                        if len(source_inventory_list)>0: selected_item_index=min(selected_item_index,len(source_inventory_list)-1) 
                        else: selected_item_index=-1 
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1: 
                panel_w, panel_h = 600, 450; panel_x, panel_y = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
                col_w=panel_w//2-30; player_col_x=panel_x+20; chest_col_x=panel_x+panel_w//2+10; item_y_start=panel_y+80; line_h=30
                clicked_on_any_item = False
                for i in range(len(player.inventory)): 
                    if pygame.Rect(player_col_x,item_y_start+i*line_h,col_w,line_h-2).collidepoint(mouse_pos): selected_item_index,selected_inventory_type,clicked_on_any_item=i,"player",True;break
                if not clicked_on_any_item: 
                    for i in range(len(player.chest_inventory)):
                        if pygame.Rect(chest_col_x,item_y_start+i*line_h,col_w,line_h-2).collidepoint(mouse_pos): selected_item_index,selected_inventory_type,clicked_on_any_item=i,"chest",True;break
                if not clicked_on_any_item: selected_item_index,selected_inventory_type = -1,None 
            continue
        if show_monster_info_panel:
            if ev.type==pygame.KEYDOWN and (ev.key==SHOW_MONSTER_INFO_KEY or ev.key==pygame.K_ESCAPE): show_monster_info_panel=False
            continue
        if ev.type==pygame.KEYDOWN:
            if ev.key==INVENTORY_KEY:inventory_visible=True
            elif ev.key==SHOW_MONSTER_INFO_KEY:show_monster_info_panel=True
            elif ev.key==SHOW_WORLD_MAP_KEY: world_map_visible = True
            elif ev.key==WEAPON_CYCLE_KEY: player.cycle_weapon();action_message=f"Arme: {player.current_weapon.name}";action_message_timer=1000
            elif ev.key==INTERACTION_KEY:
                player_rect=player.get_rect();interacted_flag=False
                if player.current_map_id=="player_house_inside":
                    home_chest_obj_data = next((o for o in current_map_data.get("objects",[]) if o.get("type")=="player_chest"),None)
                    if home_chest_obj_data and player_rect.colliderect(pygame.Rect(home_chest_obj_data["x"],home_chest_obj_data["y"],home_chest_obj_data["width"],home_chest_obj_data["height"])):
                        chest_interface_visible=True;selected_item_index=-1;selected_inventory_type=None;action_message="Ouverture du coffre.";action_message_timer=1000;interacted_flag=True
                if not interacted_flag and "objects" in current_map_data:
                    for world_chest_obj_data in current_map_data.get("objects",[]):
                        if world_chest_obj_data.get("type")=="chest" and not world_chest_obj_data.get("is_looted",False): 
                            chest_rect_world=pygame.Rect(world_chest_obj_data["x"],world_chest_obj_data["y"],world_chest_obj_data.get("width",40),world_chest_obj_data.get("height",40))
                            if player_rect.colliderect(chest_rect_world):
                                looted_item_names_list=[]; chest_content_current=world_chest_obj_data.get("content",[]) 
                                if not chest_content_current and not world_chest_obj_data.get("is_looted"): action_message="Ce coffre est vide.";world_chest_obj_data["is_looted"]=True;mark_chest_as_looted(player.current_map_id,world_chest_obj_data["uid"])
                                for item_to_loot_from_world in list(chest_content_current): 
                                    if player.add_item(item_to_loot_from_world, target_inventory="player"): chest_content_current.remove(item_to_loot_from_world);looted_item_names_list.append(item_to_loot_from_world)
                                    else: action_message="Inventaire joueur plein!";break 
                                if looted_item_names_list: action_message=f"Pillé: {','.join(looted_item_names_list)}"
                                if not chest_content_current: world_chest_obj_data["is_looted"]=True;mark_chest_as_looted(player.current_map_id,world_chest_obj_data["uid"]); 
                                if looted_item_names_list:action_message+=" (Coffre maintenant vide)"
                                action_message_timer=2000;interacted_flag=True;break 
    if not (game_over_state or inventory_visible or chest_interface_visible or show_monster_info_panel or world_map_visible):
        keys_pressed=pygame.key.get_pressed(); player.update_movement(keys_pressed,dt_seconds,current_map_data.get("objects",[])); player.update()
        player_rect_logic=player.get_rect()
        if "transition_zones" in current_map_data:
            for zone_definition in current_map_data.get("transition_zones",[]):
                if player_rect_logic.colliderect(pygame.Rect(zone_definition["rect"])): 
                    load_map_and_content(zone_definition["target_map_id"],zone_definition["target_player_x"],zone_definition["target_player_y"]) 
                    action_message=f"Vous arrivez à: {current_map_data['name']}";action_message_timer=2000;break 
        for monster_object in monsters_on_map[:]: 
            monster_object.move_random(dt_seconds) 
            if monster_object.get_rect().colliderect(player_rect_logic): 
                if current_time_ticks-last_player_hit_time > PLAYER_HIT_COOLDOWN_DURATION: 
                    damage_val=monster_object.attack_power;player.hp=max(0,player.hp-damage_val);last_player_hit_time=current_time_ticks;action_message=f"Subi {damage_val} dégâts de {monster_object.name}!";action_message_timer=1500
                    if player.hp<=0:game_over_state=True;break 
            if game_over_state:break 
            if keys_pressed[ATTACK_KEY] and (current_time_ticks-last_attack_time > ATTACK_COOLDOWN_DURATION): 
                attack_hitbox_player=player_rect_logic.inflate(player.current_weapon.damage+30,player.current_weapon.damage+30) 
                if attack_hitbox_player.colliderect(monster_object.get_rect()): 
                    damage_dealt_val=player.current_weapon.damage;monster_object.take_damage(damage_dealt_val);last_attack_time=current_time_ticks;action_message=f"Vous infligez {damage_dealt_val} à {monster_object.name}.";action_message_timer=1000
                    if monster_object.hp<=0: player.gain_xp(monster_object.xp_given);action_message=f"{monster_object.name} vaincu! (+{monster_object.xp_given}XP)";monsters_on_map.remove(monster_object);action_message_timer=2000;break 
    
    if world_map_visible: 
        draw_world_map_panel(screen, player, current_map_data)
    elif game_over_state: 
        screen.fill(BLACK);go_text_render=font_large.render("GAME OVER",True,RED);screen.blit(go_text_render,go_text_render.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-50)))
        restart_text_render=font.render("Appuyez sur une touche pour recommencer...",True,WHITE);screen.blit(restart_text_render,restart_text_render.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+20)))
    else: 
        screen.fill(current_map_data.get("background_color",BLACK))
        if "objects" in current_map_data:
            for obj_map_item in current_map_data.get("objects",[]):
                obj_item_rect=pygame.Rect(obj_map_item["x"],obj_map_item["y"],obj_map_item.get("width",32),obj_map_item.get("height",32));obj_item_color=obj_map_item.get("color",GRAY)
                obj_type = obj_map_item["type"]
                if obj_type=="wall":pygame.draw.rect(screen,obj_item_color,obj_item_rect)
                elif obj_type=="bed":pygame.draw.rect(screen,obj_item_color,obj_item_rect);pygame.draw.rect(screen,LIGHT_GRAY,(obj_item_rect.x+5,obj_item_rect.y+5,obj_item_rect.width-10,obj_item_rect.height//3)) 
                elif obj_type=="table":pygame.draw.rect(screen,obj_item_color,obj_item_rect) 
                elif obj_type=="rug":pygame.draw.ellipse(screen,obj_item_color,obj_item_rect) 
                elif obj_type=="window":pygame.draw.rect(screen,obj_item_color,obj_item_rect);pygame.draw.line(screen,BLACK,(obj_item_rect.centerx,obj_item_rect.top),(obj_item_rect.centerx,obj_item_rect.bottom),2);pygame.draw.line(screen,BLACK,(obj_item_rect.left,obj_item_rect.centery),(obj_item_rect.right,obj_item_rect.centery),2) 
                elif obj_type=="player_chest":pygame.draw.rect(screen,CHEST_COLOR,obj_item_rect);pygame.draw.rect(screen,BLACK,obj_item_rect,2);pygame.draw.rect(screen,YELLOW,(obj_item_rect.centerx-7,obj_item_rect.top+7,14,7)) 
                elif obj_type=="chest":chest_draw_color=CHEST_LOOTED_COLOR if obj_map_item.get("is_looted") else obj_map_item.get("color",CHEST_COLOR);pygame.draw.rect(screen,chest_draw_color,obj_item_rect);pygame.draw.rect(screen,BLACK,obj_item_rect,2); 
                if not obj_map_item.get("is_looted"):pygame.draw.rect(screen,YELLOW,(obj_item_rect.centerx-5,obj_item_rect.top+5,10,5)) 
                elif obj_type=="tree":tr_w,tr_h,cr_r=obj_map_item.get("trunk_width",20),obj_map_item.get("trunk_height",40),obj_map_item.get("crown_radius",30);pygame.draw.rect(screen,BROWN,(obj_map_item["x"]-tr_w//2,obj_map_item["y"]-tr_h//2,tr_w,tr_h));pygame.draw.circle(screen,DARK_GREEN,(obj_map_item["x"],int(obj_map_item["y"]-tr_h//2-cr_r//1.5)),cr_r) 
                elif obj_type=="rock":pygame.draw.circle(screen,obj_item_color,(obj_map_item["x"],obj_map_item["y"]),obj_map_item.get("radius",15)) 
                elif obj_type in ["house_door_marker","path","market_square_floor","elven_arch","lava_crack_visual"]:pygame.draw.rect(screen,obj_item_color,obj_item_rect) 
                elif obj_type=="house_structure":pygame.draw.rect(screen,obj_item_color,obj_item_rect);pygame.draw.rect(screen,BLACK,obj_item_rect,2);d_w,d_h=obj_item_rect.width//4,obj_item_rect.height//2;pygame.draw.rect(screen,BLACK if obj_map_item.get("door_message") else DARK_GRAY,(obj_item_rect.centerx-d_w//2,obj_item_rect.bottom-d_h,d_w,d_h)) 
                else:pygame.draw.rect(screen,obj_item_color,obj_item_rect) 
        for npc_display_data in npcs_on_map:pygame.draw.rect(screen,npc_display_data["color"],npc_display_data["rect"])
        player.draw(screen)
        for monster_to_draw in monsters_on_map:monster_to_draw.draw(screen)
        draw_hud(screen,player); draw_minimap(screen,player,current_map_data,monsters_on_map,npcs_on_map)
        if inventory_visible:draw_inventory_panel(screen,player)
        if chest_interface_visible:draw_chest_interface(screen,player,"Coffre Personnel")
        if show_monster_info_panel:draw_monster_info_panel(screen,monsters_on_map)
    
    if action_message and action_message_timer > 0 and not world_map_visible: 
        display_action_message(screen,action_message)
        
    pygame.display.flip()
if not game_over_state:save_player(player)
pygame.quit();sys.exit()