import pygame
from pygame import draw

krasula_live = [
    ["         (__)", "         (__)", "         (__)", "         (__)"],
    ["         (oo)", "         (oo)", "         (oo)", "         (oo)"],
    ["  /-------\/ ", "  /-------\/ ", "  /-------\/ ", "  /-------\/ "],
    [" / |     ||  ", " | |     |\  ", " \ |     ||  ", " | |     ||  "],
    ["*  ||----||  ", " * |\----| | ", "  *||----||  ", " * |\---- \  "],
    ["   ^^    ^^  ", "   ^ ^   ^ ^ ", "   ^^    ^^  ", "   ^ ^    ^^ "]]
krasula_dead = [
    ["         (__)", "         (__)", "         (__)", "         (__)"],
    ["         (Oo)", "         (oO)", "         ($$)", "         ($$)"],
    ["  /-------\/ ", "   -------\/ ", "   -------\/ ", "   -------\/ "],
    [" / |     ||  ", " _/|     ||  ", "   |     ||  ", "   |     ||  "],
    ["*  ||----||  ", "*  ||----||  ", " _/||----||  ", "   ||----||  "],
    ["   ^^    ^^  ", "   ^^    ^^  ", "*  ^^    ^^  ", "*--^^    ^^  "]]
dzialo_live = [
    ["     :     ", "           ", "           ", "           "],
    ["    / \    ", "           ", "           ", "     :     "],
    [" ,=| x |=. ", " ,=     =. ", " ,=  :  =. ", " ,= / \ =. "],
    [" | ````` | ", " | ````` | ", " | ````` | ", " | ````` | "],
    [" [=======] ", " [=======] ", " [=======] ", " [=======] "],
    ["  O o o O  ", "  O o o O  ", "  O o o O  ", "  O o o O  "]]
dzialo_dead = [
    ["   ( \_    ", "     `     ", "       .   ", "           "],
    [" _(_\ \)__ ", " ` ( \_  ' ", " , ( \_  , ", "   .___    "],
    ["(____\___))", " _(_\ \)__ ", " _(_\ \)__ ", " _(_\ \)__ "],
    [" | ````` | ", "(____\___))", "(____\___))", "(________))"],
    [" [=======] ", " [=======] ", " [=======] ", ":[=======]|"],
    ["  O o o O  ", "  O o o O  ", "  X o o X  ", "` X x x X `"]]
placek = [
    ["    (   )  ", "  )  (  (  ", " (   )  )  ", "     ) (   "],
    [" (   ) (   ", " (   )   ) ", "  ) (  (   ", "  ) (   )  "],
    ["  ) _   )  ", "  ) _   (  ", "    _   )  ", " (  _  (   "],
    ["   ( \_    ", "   ( \_    ", "   ( \_    ", "   ( \_    "],
    [" _(_\ \)__ ", " _(_\ \)__ ", " _(_\ \)__ ", " _(_\ \)__ "],
    ["(____\___))", "(____\___))", "(____\___))", "(____\___))"]]
pocisk = [
    ["  @  ", "  @  ", "  @  ", "  @  "],
    [" / \ ", " / \ ", " / \ ", " / \ "],
    ["! x !", "! o !", "! x !", "! o !"],
    [" ) ( ", " ) ( ", " ) ( ", " ) ( "],
    [" ^^^ ", " ^^^ ", " ^^^ ", " ^^^ "],
    ["| | |", ": ' :", "' ; '", "; : ;"]]

DEBUG = False
pygame.init()

class Sprite:
    def __init__(self, font, pak, frame, scale=1):
        self.w = (font.get_height() // 2 + 1) * len(pak[0][frame])
        self.h = (font.get_height() + 2) * len(pak)
        self.surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for i in range(len(pak)):
            t = pak[i][frame]
            self.surf.blit(font.render(t, True, (240, 240, 240)),
                           (0, i*font.get_height()))

        if scale > 1:
            self.w //= scale
            self.h //= scale
            self.surf = pygame.transform.smoothscale(
                self.surf, (self.w, self.h))

    def blit(self, win, pos):
        win.blit(self.surf, pos)
        if not DEBUG:
            return
        (x, y) = pos
        pygame.draw.rect(win, (160, 250, 160), (x, y, self.w, self.h), 1)


class Pocisk:
    def __init__(self, font, speed):
        self.y = 0
        self.x = 0
        self.idx = 0
        self.visible = False
        self.sprites = [Sprite(font, pocisk, i) for i in range(4)]
        self.speed = speed

    def update(self, win):
        if not self.visible:
            return
        spr = self.sprites[(self.idx // 4) % 4]
        self.idx += 1
        ny = self.y - self.speed
        if ny + spr.h < 0:
            self.visible = False
            return
        self.y = ny
        spr.blit(win, (self.x, self.y))

    def boxes(self):
        return [pygame.Rect(self.x + 7, self.y+2, 10, 10)]


class Dzialo:
    fire = pygame.mixer.Sound('shot.sfx')
    died = pygame.mixer.Sound('dirty.sfx')

    def __init__(self, font, speed, pocisk):
        self.x = 320
        self.live = [Sprite(font, dzialo_live, i) for i in range(4)]
        self.dead = [Sprite(font, dzialo_dead, i) for i in range(4)]
        self.y = 480 - self.live[0].h
        self.hit = False
        self.dir = 1
        self.idx = 0
        self.lives = 3
        self.speed = speed
        self.pocisk = pocisk
        self.font = font

    def kill(self):
        if not self.hit:
            self.hit = True
            self.idx = 1
            self.died.play()
            self.lives -= 1

    def update(self, win):
        if self.hit:
            spr = self.dead[(self.idx // 5) % 4]
            if self.idx == 19:
                if self.lives == 0:
                    return
                self.hit = False
                self.idx = 0
        else:
            nx = self.x + self.speed * self.dir
            spr = self.live[self.idx // 5]
            if nx < 0 or nx > win.get_width() - spr.w:
                self.dir *= -1
            else:
                self.x = nx
        spr.blit(win, (self.x, self.y))
        self.pocisk.update(win)
        if self.idx > 0 and (self.hit or not self.pocisk.visible):
            self.idx = (self.idx + 1) % 20

    def shoot(self):
        if self.pocisk.visible or self.idx != 0:
            return
        self.fire.play()
        self.pocisk.x = self.x + 24
        self.pocisk.y = self.y - 8
        self.pocisk.visible = True
        self.idx = 5

    def boxes(self):
        spr = self.live[self.idx // 5]
        return [pygame.Rect(self.x+4, self.y+spr.h//4, spr.w-8, spr.h//2)]


class Placek:
    def __init__(self, font, speed):
        self.y = 0
        self.x = 0
        self.idx = 0
        self.visible = False
        self.sprites = [Sprite(font, placek, i) for i in range(4)]
        self.speed = speed

    def update(self, win):
        if not self.visible:
            return
        spr = self.sprites[(self.idx // 4) % 4]
        self.idx += 1
        ny = self.y + self.speed
        if ny > win.get_height():
            self.visible = False
            return
        self.y = ny
        spr.blit(win, (self.x, self.y))

    def boxes(self):
        spr = self.sprites[(self.idx // 4) % 4]
        return [pygame.Rect(self.x, self.y+spr.h//3, spr.w, spr.h//2)]


class Krasula:
    fire = pygame.mixer.Sound('shit.sfx')
    died = pygame.mixer.Sound('deadcow.sfx')

    def __init__(self, font, speeds, dzialo, placek):
        self.x = 0
        self.y = 32
        (self.speedx, self.speedy) = speeds
        self.live = [Sprite(font, krasula_live, i, 1) for i in range(4)]
        self.dead = [Sprite(font, krasula_dead, i, 1) for i in range(4)]
        self.dzialo = dzialo
        self.placek = placek
        self.idx = 0
        self.hit = False
        self.lives = 3

    def kill(self):
        if not self.hit:
            self.hit = True
            self.idx = 0
            self.died.play()

    def update(self, win):
        if self.hit:
            spr = self.dead[(self.idx // 5) % 4]
            if self.idx == 19:
                self.x = 0
                self.y = 32
                self.hit = False
        else:
            spr = self.live[(self.idx // 5) % 4]
            self.x += self.speedx
            if self.x >= win.get_width():
                self.x = -spr.w
                self.y += self.speedy
            tof = (self.y + spr.h - (self.dzialo.y + 20)) // self.placek.speed
            predx = self.dzialo.x + 40 + self.dzialo.speed * tof
            if abs(self.x - predx) < 40 and not self.placek.visible and not self.dzialo.hit:
                self.placek.x = self.x + 12
                self.placek.y = self.y + spr.h
                self.placek.visible = True
                self.fire.play()
        self.idx += 1
        spr.blit(win, (self.x, self.y))
        self.placek.update(win)

    def boxes(self):
        return [pygame.Rect(self.x + 24, self.y + 34, 62, 40),
                pygame.Rect(self.x + 95, self.y, 10, 12),
                pygame.Rect(self.x + 73, self.y, 10, 12),
                pygame.Rect(self.x + 79, self.y + 17, 20, 10)]


class Scoreboard:
    def __init__(self, font, dzialo, krasul):
        self.score = 0
        self.lives = 5
        self.stage = 0
        self.font = font
        self.dzialo = dzialo
        self.krasul = krasul
        self.stages = [100 * (1 << i) for i in range(23)]
        self.speeds = [3 + i for i in range(23)]

    def update(self, win):
        pygame.draw.rect(win, (0, 0, 255), (0, 0, win.get_width(), 14))
        txt = "Level: {:02d}    ".format(self.stage + 1)
        txt += "Lives: {:01d}   ".format(self.dzialo.lives)
        txt += "          K R A S U L A!           "
        txt += "Score: {:06d}    ".format(self.score)
        txt += "High: {:06d}".format(999999)
        win.blit(self.font.render(txt, True, (250, 250, 200)), (16, 0))

    def add(self, value, krasul):
        self.score += value * (self.stage + 1) * (self.stage + 1)
        if self.score > self.stages[self.stage]:
            self.stage += 1
            krasul.speedx = self.speeds[self.stage]


pygame.display.set_caption("K R A S U L A !")

info = pygame.display.Info()
if info.current_h >= 480*3:
    screen = pygame.display.set_mode((640*3, 480*3))
elif info.current_h >= 480*2:
    screen = pygame.display.set_mode((640*2, 480*2))
else:
    screen = pygame.display.set_mode((640, 480))

win = pygame.Surface([640, 480])

pygame.display.set_caption("Krasula")
pygame.event.clear()
pygame.mixer.music.load("music.ogg")
pygame.mixer.music.play(loops = -1)

class Game:
    family = "Inconsolata_Expanded"
    font1 = pygame.font.Font( family + '-Regular.ttf', 14)
    font2 = pygame.font.Font( family + '-Bold.ttf', 12)
    font3 = pygame.font.Font( family + '-Bold.ttf', 8)
    endgame = pygame.mixer.Sound('endgame.sfx')

    def __init__(self):
        self.dzialo = Dzialo(self.font3, 5, Pocisk(self.font3, 16))
        self.krasul = Krasula(self.font1, (3, 5), self.dzialo, Placek(self.font3, 6))
        self.scores = Scoreboard(self.font2, self.dzialo, self.krasul)
        self.over = False
        return

    def find_collision(self, a, b, win):
        ab = a.boxes()[0]
        bb = b.boxes()
        if DEBUG:
            pygame.draw.rect(win, (255,100,100), ab, 1)
        for bi in range(len(bb)):
            if DEBUG:
                pygame.draw.rect(win, (100,255,100), bb[bi], 1)
            if ab.colliderect(bb[bi]):
                return bi + 1
        return 0

    def update(self, win):
        self.dzialo.update(win)
        self.krasul.update(win)
        self.scores.update(win)
        if self.dzialo.pocisk.visible:
            ci = self.find_collision(self.dzialo.pocisk, self.krasul, win)
            if ci > 0:
                self.dzialo.pocisk.visible = False
                self.krasul.kill()
                self.scores.add((12-self.krasul.y//100)*ci, self.krasul)
        if self.krasul.placek.visible and self.find_collision(self.krasul.placek, self.dzialo, win) > 0:
            self.krasul.placek.visible = False
            self.dzialo.kill()
        if self.dzialo.lives == 0 and not self.over:
            self.over = True
            self.endgame.play()
        if self.over:
            win.blit(self.font2.render("G A M E   O V E R", True, (250, 120, 120)), 
                     (win.get_width()//2-64, win.get_height()//2-30))
            win.blit(self.font2.render("ESC - QUIT | FIRE - RETRY", True, (200, 250, 200)), 
                     (win.get_width()//2-88, win.get_height()//2+30))


quit = False
game = Game()

while not quit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit = True
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if game.over:
                    print("Restarting")
                    game = Game()
                else:
                    game.dzialo.shoot()
            if event.key == pygame.K_LEFT:
                game.dzialo.dir = -1
            if event.key == pygame.K_RIGHT:
                game.dzialo.dir = 1

    win.fill((0, 0, 0))
    game.update(win)
    frame = pygame.transform.scale(
        win, (screen.get_width(), screen.get_height()))
    screen.blit(frame, frame.get_rect())
    pygame.display.flip()
    pygame.time.wait(50 if DEBUG else 10)

pygame.quit()
