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



class Game:
    def __init__(self) -> None:
        if N_MINES > WIDTH*HEIGHT - 9:
            raise BaseException(f"can not have {N_MINES} mines with only {WIDTH*HEIGHT} tiles")
        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H+STATUS_BAR_HEIGHT))
        self.game_canvas = pygame.surface.Surface((DISPLAY_W, DISPLAY_H))
        self.clock = pygame.time.Clock()
        self.game_map = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
        self.font = pygame.font.Font(FONT_PATH, TILE_SIZE)
        self.status_font = pygame.font.Font(FONT_PATH, STATUS_BAR_HEIGHT)
        self.true_marked = 0
        self.total_marked = 0
        self.is_running = True
        
        self.mine_texture = pygame.transform.scale(pygame.image.load(MINE_PATH).convert_alpha(), (STATUS_BAR_HEIGHT, STATUS_BAR_HEIGHT))
        self.flag_texture = pygame.transform.scale(pygame.image.load(FLAG_PATH).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        pygame.display.set_icon(self.mine_texture)
        self.no_mine_area: list[tuple[int, int]] = []
        
        lpBuffer = wintypes.LPWSTR()
        AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
        AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
        ctypes.windll.kernel32.LocalFree(lpBuffer)
        
        self.explode_animation: list[pygame.SurfaceType] = []
        for i in range(1, 8):
            self.explode_animation.append(pygame.transform.scale(pygame.image.load(f"assets/{i}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)))
        
        #-- wait for the first click --#
        while self.is_running:
            self.check_events()
            self.render_map()
            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                x = mouse_pos[0]//TILE_SIZE
                y = (mouse_pos[1]-STATUS_BAR_HEIGHT)//TILE_SIZE
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        yi = y+i
                        xj = x+j
                        if 0 <= yi < HEIGHT and 0 <= xj < WIDTH:
                            self.no_mine_area.append((xj, yi))
                            self.game_map[yi, xj] = 0
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
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            yi = y+i
                            xj = x+j
                            if 0 <= yi < HEIGHT and 0 <= xj < WIDTH:
                                if self.game_map[yi, xj] == 9:
                                    total_neighbour_mines += 1
                    self.game_map[y, x] = total_neighbour_mines
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
    
    def render_map(self):
        self.screen.fill((127, 130, 124))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.game_map[y, x] == 10:
                    color = (255, 255, 180)
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif 10 < self.game_map[y, x] < 19:
                    color = (240, 255, 225)
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    number_surface = self.font.render(str(self.game_map[y, x]-10), True, (47, 50, 44))
                    self.game_canvas.blit(number_surface, (x*TILE_SIZE+XOFFSET, y*TILE_SIZE+YOFFSET))
                elif self.game_map[y, x] > 18:
                    color = (60, 45, 40)
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    self.game_canvas.blit(self.flag_texture, (x*TILE_SIZE, y*TILE_SIZE))
                else:
                    color = (47, 50, 44)
                    pygame.draw.rect(self.game_canvas, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        self.screen.blit(self.game_canvas, (0, STATUS_BAR_HEIGHT))
        self.screen.blit(self.mine_texture, (DISPLAY_W//2 - self.mine_texture.get_rect().w, 0))
        remaining_mines_status = self.status_font.render(str(N_MINES - self.total_marked), True, (47, 50, 44))
        self.screen.blit(remaining_mines_status, (DISPLAY_W//2+20, -20))
    
    def show_empty_tiles(self, x: int, y: int):
        if y < 0 or y > HEIGHT or x < 0 or x > WIDTH:
            return
        
        for i in range(-1, 2):
            for j in range(-1, 2):
                yi = y+i
                xj = x+j
                if 0 <= yi < HEIGHT and 0 <= xj < WIDTH:
                    if self.game_map[yi, xj] == 0:
                        self.game_map[yi, xj] = 10
                        self.show_empty_tiles(xj, yi)
                    elif self.game_map[yi, xj] < 9:
                        self.game_map[yi, xj] += 10
    
    def explode(self, x: int, y: int):
        x, y = x*TILE_SIZE, y*TILE_SIZE + STATUS_BAR_HEIGHT
        for i in range(7):
            self.screen.blit(self.explode_animation[i], (x, y))
            pygame.display.update(x, y, TILE_SIZE, TILE_SIZE)
            self.clock.tick(12)
    
    def run(self):
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
                        self.is_running = False
                    elif self.game_map[y, x] < 9:
                        self.game_map[y, x] += 10
                    
                    if self.game_map[y, x] == 10:
                        self.show_empty_tiles(x, y)
                
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
            
            if self.true_marked == N_MINES == self.total_marked:
                print("you won!")
                self.is_running = False
            
            pygame.display.flip()
            self.clock.tick(TFPS)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()