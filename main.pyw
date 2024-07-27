import pygame
import sys
import numpy as np
from random import randint
import ctypes
from ctypes import wintypes
from time import perf_counter
from settings import *


#-- tiles --#
#- hidden -#
# empty: 0
# has number: [1-8]
# mine: 9
#- shown -#
# empty: 10
# has number: [11-18]
# marked and mine: 19
# marked but not mine: [20-28]
# mines when lost: 29


class Game:
    def __init__(self) -> None:
        if N_MINES > WIDTH*HEIGHT - 9:
            raise BaseException(f"can not have {N_MINES} mines with only {WIDTH*HEIGHT} tiles")
        pygame.init()
        self.screen: pygame.SurfaceType = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
        pygame.display.set_caption("Mine Sweeper by Erfan ;D")
        self.game_canvas = pygame.surface.Surface((DISPLAY_W, GAME_CANVAS_DISPLAY_H))
        self.subsurface_game_canvas = self.game_canvas
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, TILE_SIZE)
        self.status_font = pygame.font.Font(FONT_PATH, STATUS_BAR_HEIGHT)
        self.reset_font = pygame.font.Font(FONT_PATH, 40)
        
        self.mine_texture: pygame.SurfaceType = pygame.transform.scale(pygame.image.load(MINE_PATH).convert_alpha(), (STATUS_BAR_HEIGHT, STATUS_BAR_HEIGHT))
        self.flag_texture: pygame.SurfaceType = pygame.transform.scale(pygame.image.load(FLAG_PATH).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.small_mine_texture: pygame.SurfaceType = pygame.transform.scale(self.mine_texture, (TILE_SIZE, TILE_SIZE))
        pygame.display.set_icon(self.mine_texture)
        
        lpBuffer = wintypes.LPWSTR()
        AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
        AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
        ctypes.windll.kernel32.LocalFree(lpBuffer)
        
        self.explode_animation: list[pygame.SurfaceType] = []
        for i in range(1, 8):
            self.explode_animation.append(pygame.transform.scale(pygame.image.load(f"{ANIMATION_PATH}/{i}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)))
        
        self.reset_text = self.reset_font.render("reset", True, (MINES_STATUS_COLOR))
        reset_button_w = 120
        reset_button_h = 50
        reset_button_x = DISPLAY_W - reset_button_w - 20
        reset_button_y = int(STATUS_BAR_HEIGHT/2 - reset_button_h/2)
        self.reset_button_rect = pygame.rect.Rect(reset_button_x, reset_button_y, reset_button_w, reset_button_h)
        
        self.reset()
        self.is_reset = False
    
    def _zoom_stuff(self):
        x = self.game_canvas_topleft[0] - self.delta_mouse_pos[0]
        y = self.game_canvas_topleft[1] - self.delta_mouse_pos[1]
        crop_distance = self.zoom * ASPECT_RATIO[0], self.zoom * ASPECT_RATIO[1]
        if x < 0: x = 0
        if y < 0: y = 0
        if x > crop_distance[0]: x = crop_distance[0]
        if y > crop_distance[1]: y = crop_distance[1]
        cropped_region = x, y , DISPLAY_W - crop_distance[0], GAME_CANVAS_DISPLAY_H - crop_distance[1]
        self.subsurface_game_canvas = self.game_canvas.subsurface(cropped_region)
        self.game_canvas_topleft[0] = x + self.delta_mouse_pos[0]
        self.game_canvas_topleft[1] = y + self.delta_mouse_pos[1]
    
    def _canvas_stuff(self):
        if self.game_canvas_topleft[0] < 0: self.game_canvas_topleft[0] = 0
        elif self.game_canvas_topleft[0] >= DISPLAY_W: self.game_canvas_topleft[0] = DISPLAY_W-1
        if self.game_canvas_topleft[1] < 0: self.game_canvas_topleft[1] = 0
        elif self.game_canvas_topleft[1] >= GAME_CANVAS_DISPLAY_H: self.game_canvas_topleft[1] = GAME_CANVAS_DISPLAY_H-1
        self._zoom_stuff()
    
    def check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] - STATUS_BAR_HEIGHT >= 0:
                if event.button == 2:
                    self.held_middle = True
                    self.origin_mouse_pos = event.pos
                    self.current_mouse_pos = event.pos
                    self.delta_mouse_pos = (0, 0)
                
                elif event.button == 4 and self.zoom < ZOOM_LIMIT:
                    this_crop_distance =  self.zoom                   * ASPECT_RATIO[0],  self.zoom                   * ASPECT_RATIO[1]
                    next_crop_distance = (self.zoom + ZOOM_MULTPLIER) * ASPECT_RATIO[0], (self.zoom + ZOOM_MULTPLIER) * ASPECT_RATIO[1]
                    this_zoom_resolution = DISPLAY_W - this_crop_distance[0], GAME_CANVAS_DISPLAY_H - this_crop_distance[1]
                    next_zoom_resolution = DISPLAY_W - next_crop_distance[0], GAME_CANVAS_DISPLAY_H - next_crop_distance[1]
                    if next_zoom_resolution[0] > 0:
                        factor = this_zoom_resolution[0] / next_zoom_resolution[0]
                        updated_x = (event.pos[0] - self.game_canvas_topleft[0]                    ) * (factor - 1)
                        updated_y = (event.pos[1] - self.game_canvas_topleft[1] - STATUS_BAR_HEIGHT) * (factor - 1)
                        self.game_canvas_topleft[0] += updated_x
                        self.game_canvas_topleft[1] += updated_y
                        self.zoom += ZOOM_MULTPLIER
                        self._canvas_stuff()
                
                elif event.button == 5 and self.zoom > 0:
                    this_crop_distance =  self.zoom                   * ASPECT_RATIO[0],  self.zoom                   * ASPECT_RATIO[1]
                    next_crop_distance = (self.zoom - ZOOM_MULTPLIER) * ASPECT_RATIO[0], (self.zoom - ZOOM_MULTPLIER) * ASPECT_RATIO[1]
                    this_zoom_resolution = DISPLAY_W - this_crop_distance[0], GAME_CANVAS_DISPLAY_H - this_crop_distance[1]
                    next_zoom_resolution = DISPLAY_W - next_crop_distance[0], GAME_CANVAS_DISPLAY_H - next_crop_distance[1]
                    factor = this_zoom_resolution[0] / next_zoom_resolution[0]
                    updated_x = (event.pos[0] - self.game_canvas_topleft[0]                    ) * (factor - 1)
                    updated_y = (event.pos[1] - self.game_canvas_topleft[1] - STATUS_BAR_HEIGHT) * (factor - 1)
                    self.game_canvas_topleft[0] += updated_x
                    self.game_canvas_topleft[1] += updated_y
                    self.zoom -= ZOOM_MULTPLIER
                    self._canvas_stuff()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.held_middle = False
                    self.game_canvas_topleft = [self.game_canvas_topleft[0] - self.delta_mouse_pos[0],
                                     self.game_canvas_topleft[1] - self.delta_mouse_pos[1]]
                    self.origin_mouse_pos = (0, 0)
                    self.current_mouse_pos = (0, 0)
                    self.delta_mouse_pos = (0, 0)
    
    def check_reset(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_r:
                    self.reset()
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN and self.reset_button_rect.collidepoint(event.pos):
                self.reset()
    
    def render_game_canvas(self):
        blit_output = pygame.transform.scale(self.subsurface_game_canvas, (DISPLAY_W, GAME_CANVAS_DISPLAY_H))
        self.screen.blit(blit_output, (0, STATUS_BAR_HEIGHT))
    
    def render_map(self, time: float=0) -> None:
        self.screen.fill(STATUS_BAR_BG_COLOR)
        map_left   = int(self.game_canvas_topleft[0] / TILE_SIZE)
        map_top    = int(self.game_canvas_topleft[1] / TILE_SIZE)
        map_right  = map_left + int(self.subsurface_game_canvas.get_width()  / TILE_SIZE)
        map_bottom = map_top  + int(self.subsurface_game_canvas.get_height() / TILE_SIZE)
        for y in range(map_top, map_bottom):
            for x in range(map_left, map_right):
                if self.game_map[y, x] == 10:
                    color = EMPTY_TILE_COLOR
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif 10 < self.game_map[y, x] < 19:
                    color = NUMBER_BG_TILE_COLOR
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    number_surface = self.font.render(str(self.game_map[y, x]-10), True, NUMBER_FG_TILE_COLOR)
                    self.game_canvas.blit(number_surface, (x*TILE_SIZE+XOFFSET, y*TILE_SIZE+YOFFSET))
                elif self.game_map[y, x] == 29:
                    color = MINE_BG_COLOR
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    self.game_canvas.blit(self.small_mine_texture, (x*TILE_SIZE, y*TILE_SIZE))
                elif self.game_map[y, x] > 18:
                    color = MARKED_TILE_COLOR
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    self.game_canvas.blit(self.flag_texture, (x*TILE_SIZE, y*TILE_SIZE))
                else:
                    color = HIDDEN_TILE_COLOR
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        self.screen.blit(self.mine_texture, (DISPLAY_W//2 - self.mine_texture.get_rect().w, 0))
        remaining_mines_status = self.status_font.render(str(N_MINES - self.total_marked), True, MINES_STATUS_COLOR)
        self.screen.blit(remaining_mines_status, (DISPLAY_W//2+20, -20))
        timer_status = self.font.render("time: %d s"%time, True, TIMER_STATUS_COLOR)
        self.screen.blit(timer_status, (8, -2))
        pygame.draw.rect(self.screen, "#50534d", self.reset_button_rect)
        self.screen.blit(self.reset_text, (DISPLAY_W - 130, STATUS_BAR_HEIGHT//2 - 27))
        
        for hline in range(0, GAME_CANVAS_DISPLAY_H, TILE_SIZE):
            pygame.draw.line(self.game_canvas, "#000000", (0, hline), (DISPLAY_W, hline), 2)
        for vline in range(0, DISPLAY_W, TILE_SIZE):
            pygame.draw.line(self.game_canvas, "#000000", (vline, 0), (vline, GAME_CANVAS_DISPLAY_H), 2)
        
        self.render_game_canvas()
    
    def show_empty_tiles(self, x: int, y: int) -> None:
        if y < 0 or y > HEIGHT or x < 0 or x > WIDTH:
            return
        
        for i in range(y-1, y+2):
            for j in range(x-1, x+2):
                if 0 <= i < HEIGHT and 0 <= j < WIDTH:
                    if self.game_map[i, j] == 0:
                        self.game_map[i, j] = 10
                        self.show_empty_tiles(j, i)
                    elif self.game_map[i, j] < 9:
                        self.game_map[i, j] += 10
    
    def explode(self, x: int, y: int) -> None:
        for a in range(HEIGHT):
            for b in range(WIDTH):
                if self.game_map[a, b] < 9:
                    self.game_map[a, b] += 10
                elif self.game_map[a, b] == 9:
                    self.game_map[a, b] = 29
                elif 20 <= self.game_map[a, b] <= 28:
                    self.game_map[a, b] -= 10
        self.render_map(perf_counter() - self.start_time)
        pygame.display.flip()
        x, y = x*TILE_SIZE, y*TILE_SIZE
        for i in range(7):
            self.check_events()
            self.game_canvas.blit(self.explode_animation[i], (x, y))
            self.render_game_canvas()
            pygame.display.flip()
            self.clock.tick(ANIMATION_SPEED)
        while self.is_running and not self.is_reset:
            self.check_reset()
            self.clock.tick(10)
        self.is_reset = False
    
    def reset(self) -> None:
        self.game_map = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
        self.true_marked: int = 0
        self.total_marked: int = 0
        self.is_running: bool = True
        self.is_reset: bool = True
        self.held_middle: bool = False
        self.no_mine_area: list[tuple[int, int]] = []
        self.zoom = 0
        self.game_canvas_topleft = [0, 0]
        self.origin_mouse_pos: tuple[int, int] = (0, 0)
        self.delta_mouse_pos: tuple[int, int] = (0, 0)
        self._canvas_stuff()
        #-- wait for the first click --#
        while self.is_running:
            self.check_events()
            self.render_map(0)
            if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[1] > STATUS_BAR_HEIGHT:
                mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
                mx: int = mouse_pos[0]//TILE_SIZE
                my: int = (mouse_pos[1]-STATUS_BAR_HEIGHT)//TILE_SIZE
                for i in range(my-1, my+2):
                    for j in range(mx-1, mx+2):
                        if 0 <= i < HEIGHT and 0 <= j < WIDTH:
                            self.no_mine_area.append((j, i))
                            self.game_map[i, j] = 0
                break
            pygame.display.flip()
            self.clock.tick(12)
        if not self.is_running:
            return
        #-- assign numbers to tiles --#
        #- mines -#
        for _ in range(N_MINES):
            y = randint(0, HEIGHT-1)
            x = randint(0, WIDTH-1)
            while self.game_map[y, x] == 9 or (x, y) in self.no_mine_area:
                y = randint(0, HEIGHT-1)
                x = randint(0, WIDTH-1)
            self.game_map[y, x] = 9
        
        #- others -#
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.game_map[y, x] == 0:
                    total_neighbour_mines = 0
                    for i in range(y-1, y+2):
                        for j in range(x-1, x+2):
                            if 0 <= i < HEIGHT and 0 <= j < WIDTH and self.game_map[i, j] == 9:
                                total_neighbour_mines += 1
                    self.game_map[y, x] = total_neighbour_mines
        
        self.show_empty_tiles(mx, my)
        self.start_time = perf_counter()
    
    def run(self) -> None:
        released = True
        while self.is_running:
            self.check_events()
            self.render_map(perf_counter() - self.start_time)
            
            mouse_press = pygame.mouse.get_pressed()
            if mouse_press[1] and self.held_middle:
                self.current_mouse_pos = pygame.mouse.get_pos()
                dx = self.current_mouse_pos[0] - self.origin_mouse_pos[0]
                dy = self.current_mouse_pos[1] - self.origin_mouse_pos[1]
                dxr = dx / DISPLAY_W
                dyr = dy / GAME_CANVAS_DISPLAY_H
                self.delta_mouse_pos = (dxr*self.subsurface_game_canvas.get_width(),
                                        dyr*self.subsurface_game_canvas.get_height())
                self._zoom_stuff()
            
            if not mouse_press[0] and not mouse_press[2]:
                released = True
            
            if released:
                if mouse_press[0]:
                    released = False
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if mouse_pos[1] < STATUS_BAR_HEIGHT:
                        if self.reset_button_rect.collidepoint(mouse_pos):
                            self.reset()
                    
                    else:
                        x = int( (( mouse_pos[0]                      / DISPLAY_W            ) * self.subsurface_game_canvas.get_width()  + self.game_canvas_topleft[0]) / TILE_SIZE )
                        y = int( (((mouse_pos[1] - STATUS_BAR_HEIGHT) / GAME_CANVAS_DISPLAY_H) * self.subsurface_game_canvas.get_height() + self.game_canvas_topleft[1]) / TILE_SIZE )
                        
                        if self.game_map[y, x] == 9:
                            self.explode(x, y)
                        elif self.game_map[y, x] == 0 or self.game_map[y, x] == 10:
                            self.game_map[y, x] = 10
                            self.show_empty_tiles(x, y)
                        elif self.game_map[y, x] < 9:
                            self.game_map[y, x] += 10
                        elif DO_SMART_CLICK and 10 < self.game_map[y, x] < 19:
                            hidden_neighbours: set[tuple[int, int]] = set()
                            marks: set[tuple[int, int]] = set()
                            for i in range(y-1, y+2):
                                for j in range(x-1, x+2):
                                    if 0 <= i < HEIGHT and 0 <= j < WIDTH:
                                        if self.game_map[i, j] < 10:
                                            hidden_neighbours.add((j, i))
                                        elif 18 < self.game_map[i, j] < 29:
                                            marks.add((j, i))
                            marks_len = len(marks)
                            if self.game_map[y, x]-10 == marks_len:
                                for xa, ya in hidden_neighbours:
                                    if self.game_map[ya, xa] == 0:
                                        self.show_empty_tiles(x, y)
                                    if self.game_map[ya, xa] < 9:
                                        self.game_map[ya, xa] += 10
                                    elif self.game_map[ya, xa] == 9:
                                        self.explode(xa, ya)
                            
                            elif len(hidden_neighbours) == self.game_map[y, x]-10-marks_len:
                                for xa, ya in hidden_neighbours:
                                    if self.total_marked != N_MINES:
                                        if self.game_map[ya, xa] < 9:
                                            self.game_map[ya, xa] += 20
                                            self.total_marked += 1
                                        elif self.game_map[ya, xa] == 9:
                                            self.total_marked += 1
                                            self.true_marked += 1
                                            self.game_map[ya, xa] = 19
                
                if mouse_press[2]:
                    released = False
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[1] > STATUS_BAR_HEIGHT:
                        x = int( (( mouse_pos[0]                      / DISPLAY_W            ) * self.subsurface_game_canvas.get_width()  + self.game_canvas_topleft[0]) / TILE_SIZE )
                        y = int( (((mouse_pos[1] - STATUS_BAR_HEIGHT) / GAME_CANVAS_DISPLAY_H) * self.subsurface_game_canvas.get_height() + self.game_canvas_topleft[1]) / TILE_SIZE )
                        if self.game_map[y, x] == 9 and self.total_marked != N_MINES:
                            self.game_map[y, x] = 19
                            self.true_marked += 1
                            self.total_marked += 1
                        
                        elif self.game_map[y, x] < 9 and self.total_marked != N_MINES:
                            self.game_map[y, x] += 20
                            self.total_marked += 1
                        
                        elif self.game_map[y, x] == 19:
                            self.game_map[y, x] = 9
                            self.true_marked -= 1
                            self.total_marked -= 1
                        
                        elif self.game_map[y, x] >= 20:
                            self.game_map[y, x] -= 20
                            self.total_marked -= 1
            
            if self.true_marked == N_MINES == self.total_marked and not self.game_map[self.game_map < 10].any():
                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        if self.game_map[y, x] < 9:
                            self.game_map[y, x] += 10
                self.render_map(perf_counter() - self.start_time)
                win_text = self.status_font.render("YOU WON!", True, WIN_MES_COLOR)
                win_text_rect = win_text.get_rect()
                self.screen.blit(win_text, (DISPLAY_W//2-win_text_rect.w//2, GAME_CANVAS_DISPLAY_H//2-win_text_rect.h//2))
                pygame.display.flip()
                while self.is_running:
                    self.check_reset()
                    if self.is_reset:
                        self.is_reset = False
                        break
                    self.clock.tick(10)
            
            pygame.display.flip()
            self.clock.tick(TFPS)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()