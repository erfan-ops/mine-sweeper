import pygame
import sys
import numpy as np
from random import randint
import ctypes
from ctypes import wintypes
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
        self.screen: pygame.SurfaceType = pygame.display.set_mode((DISPLAY_W, DISPLAY_H+STATUS_BAR_HEIGHT))
        pygame.display.set_caption("Mine Sweeper by Erfan ;D")
        self.game_canvas = pygame.surface.Surface((DISPLAY_W, DISPLAY_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, TILE_SIZE)
        self.status_font = pygame.font.Font(FONT_PATH, STATUS_BAR_HEIGHT)
        
        self.mine_texture: pygame.SurfaceType = pygame.transform.scale(pygame.image.load(MINE_PATH).convert_alpha(), (STATUS_BAR_HEIGHT, STATUS_BAR_HEIGHT))
        self.flag_texture: pygame.SurfaceType = pygame.transform.scale(pygame.image.load(FLAG_PATH).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.small_mine_texture: pygame.SurfaceType = pygame.transform.scale(pygame.image.load(MINE_PATH).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        pygame.display.set_icon(self.mine_texture)
        
        lpBuffer = wintypes.LPWSTR()
        AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
        AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
        ctypes.windll.kernel32.LocalFree(lpBuffer)
        
        self.explode_animation: list[pygame.SurfaceType] = []
        for i in range(1, 8):
            self.explode_animation.append(pygame.transform.scale(pygame.image.load(f"{ANIMATION_PATH}/{i}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)))
        
        self.reset()
        self.is_reset = False
    
    def check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
    
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
    
    def render_map(self) -> None:
        self.screen.fill(STATUS_BAR_BG_COLOR)
        for y in range(HEIGHT):
            for x in range(WIDTH):
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
        self.screen.blit(self.game_canvas, (0, STATUS_BAR_HEIGHT))
        self.screen.blit(self.mine_texture, (DISPLAY_W//2 - self.mine_texture.get_rect().w, 0))
        remaining_mines_status = self.status_font.render(str(N_MINES - self.total_marked), True, MINES_STATUS_COLOR)
        self.screen.blit(remaining_mines_status, (DISPLAY_W//2+20, -20))
    
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
        self.render_map()
        pygame.display.flip()
        x, y = x*TILE_SIZE, y*TILE_SIZE + STATUS_BAR_HEIGHT
        for i in range(7):
            self.check_events()
            self.screen.blit(self.explode_animation[i], (x, y))
            pygame.display.update(x, y, TILE_SIZE, TILE_SIZE)
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
        self.no_mine_area: list[tuple[int, int]] = []
        #-- wait for the first click --#
        while self.is_running:
            self.check_events()
            self.render_map()
            if pygame.mouse.get_pressed()[0]:
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
                            if 0 <= i < HEIGHT and 0 <= j < WIDTH:
                                if self.game_map[i, j] == 9:
                                    total_neighbour_mines += 1
                    self.game_map[y, x] = total_neighbour_mines
        
        self.show_empty_tiles(mx, my)
    
    def run(self) -> None:
        released = True
        while self.is_running:
            self.check_events()
            self.render_map()
            
            mouse_press = pygame.mouse.get_pressed()
            if not mouse_press[0] and not mouse_press[2]:
                released = True
            
            if released:
                if mouse_press[0]:
                    released = False
                    mouse_pos = pygame.mouse.get_pos()
                    y = (mouse_pos[1]-STATUS_BAR_HEIGHT)//TILE_SIZE
                    x = mouse_pos[0]//TILE_SIZE
                    if self.game_map[y, x] == 9:
                        self.explode(x, y)
                    elif self.game_map[y, x] == 0 or self.game_map[y, x] == 10:
                        self.game_map[y, x] = 10
                        self.show_empty_tiles(x, y)
                    elif self.game_map[y, x] < 9:
                        self.game_map[y, x] += 10
                    elif 10 < self.game_map[y, x] < 19:
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
                                if self.game_map[ya, xa] == 9:
                                    self.explode(xa, ya)
                        
                        elif len(hidden_neighbours) == self.game_map[y, x]-10-marks_len:
                            for xa, ya in hidden_neighbours:
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
                    y = (mouse_pos[1]-STATUS_BAR_HEIGHT)//TILE_SIZE
                    x = mouse_pos[0]//TILE_SIZE
                    if self.game_map[y, x] == 9:
                        self.game_map[y, x] = 19
                        self.true_marked += 1
                        self.total_marked += 1
                    
                    elif self.game_map[y, x] < 9:
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
                self.render_map()
                win_text = self.status_font.render("YOU WON!", True, WIN_MES_COLOR)
                win_text_rect = win_text.get_rect()
                self.screen.blit(win_text, (DISPLAY_W//2-win_text_rect.w//2, DISPLAY_H//2-win_text_rect.h//2))
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