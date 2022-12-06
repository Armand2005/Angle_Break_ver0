import pygame, math
from pygame.math import Vector2
from random import *

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y, pv=100):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.Surface((15, 15))
        self.image.fill("white")
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.pv = pv
        self.isHit = False
        self.damage = 5
        self.speed = 8

    def get_Pv(self):
        return self.pv

    def get_pos(self):
        return [self.rect.centerx, self.rect.centery]

    def perd_vie(self, pv):
        self.pv -= pv

    def is_hit(self, ennemirect):
        if self.rect.colliderect(ennemirect):
            return True
        else:
            return False

    def update(self):
        for sl in game.spawners:
            for s in sl:
                for e in s.ennemis:
                    if e.type == "runner":
                        if self.is_hit(e.rect) and e.has_hit == False:
                            self.perd_vie(e.damage)
                            e.has_hit = True
                    if e.type == "shooter":
                        for b in game.shooter_bullets:
                            if self.is_hit(b.rect) and b.has_hit == False:
                                self.perd_vie(e.damage)
                                b.has_hit = True


class Runner(pygame.sprite.Sprite):

    def __init__(self, x, y, color="red", pv=15):
        super().__init__()
        self.type = "runner"
        self.pv = pv
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.speed = 4
        self.pos = Vector2(x,y)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = Vector2(self.speed, 0)
        self.velocity.rotate_ip(get_Player_Angle(game.player, self))
        self.has_hit = False
        self.damage = 10

    def ennemi_perd_vie(self, pv):
        self.pv -= pv

    def is_hit(self, bulletrect):
        if self.rect.colliderect(bulletrect):
            return True
        else:
            return False

    def is_dead(self):
        self.kill()

    def update(self):

        if 0 <= self.pos[0] <= 1920 and 0 <= self.pos[1] <= 1080:
            self.pos += self.velocity
            self.rect.center = self.pos
            for b in game.player_bullets:
                if self.is_hit(b.rect) and b.has_hit == False:
                    self.ennemi_perd_vie(game.player.damage)
                    b.has_hit = True
            if self.pv <= 0:
                game.score += 5
                self.is_dead()
        else:
            self.is_dead()

class Shooter(pygame.sprite.Sprite):
    def __init__(self, x, y, color="orange", pv=10):
        super().__init__()
        self.type = "shooter"
        self.x = x
        self.y = y
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.pv = pv
        self.damage = 5
        self.munitions = 10
        self.out_of_ammo = False
        self.shoot_cooldown = 100
        self.reload_cooldown = 3000
        self.time0 = pygame.time.get_ticks()

    def ennemi_perd_vie(self, pv):
        self.pv -= pv

    def is_hit(self, bulletrect):
        if self.rect.colliderect(bulletrect):
            return True
        else:
            return False

    def is_dead(self):
        self.kill()

    def fire(self):
        time1 = pygame.time.get_ticks()
        if time1 - self.time0 >= self.shoot_cooldown and self.out_of_ammo == False:
            self.time0 = time1
            game.shooter_bullets.add(self.create_bullet())
            self.munitions -= 1

    def create_bullet(self):
        return Bullet(self.rect.center, get_Player_Angle(game.player, self), 5, "pink")

    def reload(self):
        if self.munitions <= 0:
            self.out_of_ammo = True
            time1 = pygame.time.get_ticks()
            if time1 - self.time0 >= self.reload_cooldown:
                self.munitions = 10
                self.out_of_ammo = False

    def update(self):

        for b in game.player_bullets:
            if self.is_hit(b.rect) and b.has_hit == False:
                self.ennemi_perd_vie(game.player.damage)
                b.has_hit = True
        if self.pv <= 0:
            self.is_dead()
        self.fire()
        self.reload()



class EnnemiSpawner:
    def __init__(self, firstx, endx, firsty, endy, cooldown):
        self.firstx = firstx
        self.endx = endx
        self.firsty = firsty
        self.endy = endy
        self.ennemis = pygame.sprite.Group()
        self.time0 = pygame.time.get_ticks()
        self.cooldown = cooldown

    def create_ennemi(self, ennemi_type):
        if ennemi_type == Runner:
            return ennemi_type(randint(self.firstx, self.endx), randint(self.firsty, self.endy))
        elif ennemi_type == Shooter:
            return ennemi_type(randint(250, game.screen_width - 250), randint(140, game.screen_height - 140))

    def spawn(self, ennemi_type):
        time1 = pygame.time.get_ticks()
        if time1 - self.time0 >= self.cooldown:
            self.time0 = time1
            self.ennemis.add(self.create_ennemi(ennemi_type))

class Gun(pygame.sprite.Sprite):

    def __init__(self, player, pos):
        super().__init__()
        # player related
        self.player = player
        self.pos = Vector2(pos)
        self.offset = Vector2(20, 0)
        self.angle = 0
        # init rect and images
        self.image = pygame.image.load("Ak.png").convert_alpha()
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=(player.x,player.y))
        self.reload_font = pygame.font.SysFont(None, 24)
        self.reload_text = self.reload_font.render("reloading...", True, "white")
        self.reload_text_rect = self.reload_text.get_rect(center=(pos[0], pos[1] - 20))
        # bullets
        self.bullets_speed = 15
        # cooldown
        self.time0 = pygame.time.get_ticks()
        self.shoot_cooldown = 250
        self.reload_cooldown = 3000
        self.IsShooting = False
        self.munitions = 50
        self.out_of_ammo = False

    def rotate(self):
        self.image = pygame.transform.rotozoom(self.orig_image, -self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=self.pos + offset_rotated)


    def fire(self):
        time1 = pygame.time.get_ticks()
        if time1 - self.time0 >= self.shoot_cooldown and self.out_of_ammo == False:
            self.time0 = time1
            game.player_bullets.add(self.create_bullet())
            self.munitions -= 1

    def create_bullet(self):
        return Bullet(self.rect.center, get_mouse_Angle(self), self.bullets_speed)

    def reload(self, screen):
        self.out_of_ammo = True
        screen.blit(self.reload_text, self.reload_text_rect)
        self.reload_text_rect = self.reload_text.get_rect(center=(self.rect.centerx, self.rect.centery - 20))
        time1 = pygame.time.get_ticks()
        if time1 - self.time0 >= self.reload_cooldown:
            self.munitions = 50
            self.out_of_ammo = False

    def update(self, screen):
        self.pos = Vector2(game.player.rect.center)
        self.angle = get_mouse_Angle(self)
        self.rotate()
        if self.munitions <= 0:
            self.reload(screen)

class Bullet(pygame.sprite.Sprite):

    def __init__(self, pos, angle, speed=5, color="white"):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(color)
        self.pos = Vector2(pos)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.has_hit = False
        self.velocity = Vector2(self.speed, 0)
        self.velocity.rotate_ip(angle)

    def hit(self, rect):
        if self.rect.colliderect(rect):
            return True
        else:
            return False

    def check_destroy(self):
        if self.has_hit == True:
            self.kill()

    def update(self):
        if 0 <= self.pos[0] <= game.screen_width and 0 <= self.pos[1] <= game.screen_height:
            self.pos += self.velocity
            self.rect.center = self.pos
            self.check_destroy()
        else:
            self.kill()



# CALCUL L'ANGLE DU CURSEUR PAR RAPPORT AU JOUEUR
def get_mouse_Angle(player):
    pos = pygame.mouse.get_pos()
    angle = (math.atan2(pos[1] - player.rect.centery, pos[0] - player.rect.centerx) * 180 / math.pi)
    return angle

def get_Player_Angle(player, ennemi):
    pos = player.get_pos()
    angle = (math.atan2(pos[1] - ennemi.rect.centery, pos[0] - ennemi.rect.centerx) * 180 / math.pi)
    return angle



class Obstacles(pygame.sprite.Sprite):

    def __init__(self, screen, x, y, height, width, color="white"):
        super().__init__()
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.screen = screen
        self.color = color
        self.object = pygame.sprite.Group()
        self.obj = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        pygame.draw.rect(self.screen, self.color, self.obj)


class Game:
    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.running = True
        self.state = "main"
        self.player = Player(self.screen_width / 2, self.screen_height / 2)
        self.pgun = Gun(self.player, self.player.rect.center)
        self.player_gun = pygame.sprite.Group(self.pgun)
        self.player_bullets = pygame.sprite.Group()

        # ========================
        self.player_pv_font = pygame.font.SysFont(None, 25)
        self.player_pv_text = self.player_pv_font.render(f"PV:{self.player.pv}", True, "white")
        self.player_pv_text_rect = self.player_pv_text.get_rect(center=(280, 180))


        # ========================

        # ========================
        self.dead_font = pygame.font.SysFont(None, 200)
        self.dead_text = self.dead_font.render("/DEAD/", True, "red")
        self.dead_text_rect = self.dead_text.get_rect(center=(self.screen_width/2, self.screen_height/2))

        self.restart_font = pygame.font.SysFont(None, 50)
        self.restart_text = self.restart_font.render("=== press SPACE for restart ===", True, "white")
        self.restart_text_rect = self.restart_text.get_rect(center=(self.screen_width / 2,  (self.screen_height - self.screen_height/4)))
        # ========================

        self.crosshair = pygame.image.load('Crosshair00.png').convert_alpha()
        self.shooter_bullets = pygame.sprite.Group()

        self.runner_spawners = []
        self.shooter_spawners =[]
        self.spawners = [self.runner_spawners, self.shooter_spawners]
        self.shooterspawntime = 5000
        self.runnerspawntime = 3000


        # === create spawners ===
        self.runner_spawner1 = EnnemiSpawner(0, self.screen_width, 0, 0, self.runnerspawntime)
        self.runner_spawner2 = EnnemiSpawner(0, self.screen_width, self.screen_height, self.screen_height, self.runnerspawntime+ 500)
        self.runner_spawners.append(self.runner_spawner1)
        self.runner_spawners.append(self.runner_spawner2)
        # =======================
        self.shooter_spawner1 = EnnemiSpawner(0, self.screen_width, 0, 0, self.shooterspawntime)
        self.shooter_spawners.append(self.shooter_spawner1)
        # =======================

        self.timer = pygame.time.get_ticks()
        self.score = 0
        self.meilleur_score = 0

        self.score_font = pygame.font.SysFont(None, 24)
        self.score_text = self.score_font.render(f"SCORE:{self.score}", True, "white")
        self.score_text_rect = self.score_text.get_rect(center=(self.screen_width - 300, 180))

        self.mscore_font = pygame.font.SysFont(None, 30)
        self.mscore_text = self.mscore_font.render(f"( MEILLEUR SCORE: {self.meilleur_score} )", True, "gold")
        self.mscore_text_rect = self.mscore_text.get_rect(center=(self.screen_width/2, 180))

    def intro(self):
        pass

    def stage(self):

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pgun.IsShooting = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.pgun.IsShooting = False
            if event.type == pygame.QUIT:
                self.running = False

        if self.pgun.IsShooting:
            self.pgun.fire()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_q]) and self.player.rect.centerx > 0:
            self.player.rect.centerx -= self.player.speed
        elif self.player.rect.centerx < 0:
            self.player.rect.centerx = 0
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.player.rect.centerx < self.screen_width:
            self.player.rect.centerx += self.player.speed
        elif self.player.rect.centerx > self.screen_width:
            self.player.rect.centerx = self.screen_width
        if (keys[pygame.K_UP] or keys[pygame.K_z]) and self.player.rect.centery > 0:
            self.player.rect.centery -= self.player.speed
        elif self.player.rect.centery < 0:
            self.player.rect.centery = 0
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.player.rect.centery < self.screen_height:
            self.player.rect.centery += self.player.speed
        elif self.player.rect.centery > self.screen_height:
            self.player.rect.centery = self.screen_height

        if keys[pygame.K_ESCAPE]:
            self.running = False

    # update
        # make spawners spawn enemies
        time1 = pygame.time.get_ticks()
        if time1 - self.timer >= 10000:
            self.score += 10
            for s in game.runner_spawners:
                if s.cooldown > 0 and s.cooldown > 300:
                    s.cooldown -= 200
                else:
                    s.cooldown = 300
            for s in game.shooter_spawners:
                if s.cooldown > 0 and s.cooldown > 1000:
                    s.cooldown -= 100
                else:
                    s.cooldown = 1500
            self.timer = time1
        for s in game.runner_spawners:
            s.spawn(Runner)
        if self.score >= 30:
            for s in game.shooter_spawners:
                s.spawn(Shooter)
        self.player.update()
        self.pgun.update(self.screen)
        game.player_bullets.update()
        for sl in self.spawners:
            for s in sl:
                s.ennemis.update()
        game.shooter_bullets.update()
        if self.score > self.meilleur_score:
            self.meilleur_score = self.score

    # display
        self.screen.fill("black")
        self.screen.blit(self.crosshair, pygame.mouse.get_pos())
        self.screen.blit(self.player.image, self.player.rect)
        # display gun and bullets
        self.player_gun.draw(self.screen)
        self.player_bullets.draw(self.screen)
        # display enemies
        for sl in self.spawners:
            for s in sl:
                s.ennemis.draw(self.screen)
        self.shooter_bullets.draw(self.screen)
        self.screen.blit(self.player_pv_text, self.player_pv_text_rect)
        self.player_pv_text = self.player_pv_font.render(f"PV: {self.player.pv}", True, "green")
        self.screen.blit(self.score_text, self.score_text_rect)
        self.score_text = self.score_font.render(f"SCORE: {self.score}", True, "gold")


        pygame.display.flip()

    def shop(self):
        pass

    def lose(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.score = 0
                    self.player.pv = 100
                    for s in game.runner_spawners:
                        s.cooldown = 3000
                    for s in game.shooter_spawners:
                        s.cooldown = 5000

                    for sl in self.spawners:
                        for s in sl:
                            for e in s.ennemis:
                                e.kill()
                    for b in self.shooter_bullets:
                        b.kill()


            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False

        self.screen.fill("black")
        self.screen.blit(self.dead_text, self.dead_text_rect)
        self.screen.blit(self.restart_text, self.restart_text_rect)
        self.mscore_text = self.mscore_font.render(f"( MEILLEUR SCORE: {self.meilleur_score} )", True, "gold")
        self.screen.blit(self.mscore_text, self.mscore_text_rect)
        pygame.display.flip()


pygame.init()

clock = pygame.time.Clock()
game = Game()

pygame.mouse.set_visible(False)
while game.running:
    if game.player.pv > 0:
        game.stage()
        clock.tick(60)
    elif game.player.pv <= 0:
        game.lose()
        clock.tick(60)

pygame.quit()