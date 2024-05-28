from typing import Text
import pygame
import random
import math
import numpy as np

# taichi version 1.5.0
import taichi as ti
import taichi_glsl as ts
from taichi_glsl import vec2, vec3

pygame.init()

w, h = 1280, 720
NumberOfMeteorites = 50
NumberOfAmmo = 5
NumberOfEnergy = 5

Fontforcdisplay = pygame.font.Font(None, 36)
Fontforscore = pygame.font.Font(None, 10)
FontforScoreinM = pygame.font.Font(None, 26)
FontforScoreinMD = pygame.font.Font(None, 34)
ti.init(arch=ti.cpu)
resolution = width, height = vec2(1280, 720)

# Загрузка текстур

StarFighterOFF = pygame.image.load("starfighteroff.png")
StarFighterON = pygame.image.load("starfighteron.png")
StarFighterNITRO = pygame.image.load("starfighternitro.png")
StarFighterOFF = pygame.transform.scale(StarFighterOFF, (60, 60))
StarFighterNITRO = pygame.transform.scale(StarFighterNITRO, (60, 60))
StarFighterON = pygame.transform.scale(StarFighterON, (60, 60))

Boom = pygame.image.load("Boom.png")
Boom = pygame.transform.scale(Boom, (64, 64))

EnergyT = pygame.image.load("Energy.png")
AmmoT = pygame.image.load("Ammo.png")
PageT = pygame.image.load("Page.png")
PageT = pygame.transform.scale(PageT, (248, 148))

BulletT = pygame.image.load("Bullet.png")

Wall = pygame.image.load("Wall.png")
Wall = pygame.transform.scale(Wall, (600, 600))
CosmoFon = pygame.image.load("space.jpg")
CosmoSize = CosmoFon.get_size()
Meteor = pygame.image.load("Meteorite.png")

texture = pygame.image.load("Cosmos.jpg!d")
texture = pygame.transform.scale(texture, (1024, 1024))  # Степень 2
Kabine = pygame.image.load("Kabine.png")
Kabine = pygame.transform.scale(Kabine, (w, h))

texture_size = texture.get_size()[0]

# Преобразование RGB к значениям 0.0-1.0
texture_array = pygame.surfarray.array3d(texture).astype(np.float32) / 255


@ti.data_oriented
class PyShader:
    def __init__(self, app):
        self.app = app
        self.screen_array = np.full((width, height, 3), [0, 0, 0], np.uint8)
        # taichi
        self.screen_field = ti.Vector.field(3, ti.uint8, (width, height))
        self.texture_field = ti.Vector.field(3, ti.float32, texture.get_size())
        self.texture_field.from_numpy(texture_array)

    @ti.kernel
    def render(self, time: ti.float32):
        """fragment shader imitation"""
        for frag_coord in ti.grouped(self.screen_field):

            uv = (frag_coord - 0.5 * resolution) / resolution.y
            col = vec3(0.0)

            phi = ts.atan(uv.y, uv.x)
            rho = ts.length(uv)

            st = vec2(phi / ts.pi * 2, 0.25 / rho)

            st.y += time / 2
            col += self.texture_field[st * texture_size]

            col *= rho + 0.1
            col = ts.clamp(col, 0.0, 1.0)
            self.screen_field[frag_coord.x, resolution.y - frag_coord.y] = col * 255

    def update(self):
        time = pygame.time.get_ticks() * 1e-03  # time in sec
        self.render(time)
        self.screen_array = self.screen_field.to_numpy()

    def draw(self):
        pygame.surfarray.blit_array(self.app.screen, self.screen_array)

    def run(self):
        self.update()
        self.draw()


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode(resolution, pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.shader = PyShader(self)

    def run(self):
        a = open("Scores.txt", "r")
        r = a.readlines()
        a.close
        r = r[0].split(" ")
        ma = 0
        for i in range(len(r) - 1):
            if ma < int(r[i]):
                ma = int(r[i])
        while True:
            self.shader.run()
            # Функционал меню

            Mousepos = pygame.mouse.get_pos()
            Mousepress = pygame.mouse.get_pressed()

            self.screen.blit(Kabine, (0, 0))
            if ((w // 2) - Mousepos[0]) ** 2 + (
                (h // 2 + 290) - Mousepos[1]
            ) ** 2 <= 54**2:
                if Mousepress[0]:
                    Game()
                text1 = Fontforcdisplay.render("Сlick to start", True, (207, 20, 20))
                text2 = Fontforcdisplay.render("the game", True, (207, 20, 20))

                pos = text1.get_rect(center=(w // 2, h // 2 + 140))
                window.blit(text1, pos)

                pos = text2.get_rect(center=(w // 2, h // 2 + 165))
                window.blit(text2, pos)
            if pygame.Rect(Mousepos[0], Mousepos[1], 1, 1).colliderect(
                pygame.Rect(564, 400, 260, 28)
            ):
                text5 = FontforScoreinMD.render("Highest score:", True, (113, 119, 130))
                pos = text5.get_rect(center=(w // 2, h // 2 + 140))
                window.blit(text5, pos)
                text5 = FontforScoreinMD.render(str(ma), True, (113, 119, 130))
                pos = text5.get_rect(center=(w // 2, h // 2 + 165))
                window.blit(text5, pos)

            text3 = FontforScoreinM.render("H S:", True, (113, 119, 130))
            text4 = FontforScoreinM.render(str(ma), True, (113, 119, 130))
            pos = text3.get_rect(center=(w // 2 - 50, h // 2 + 54))
            window.blit(text3, pos)

            pos = text4.get_rect(center=(w // 2 + 30, h // 2 + 54))
            window.blit(text4, pos)

            pygame.display.flip()

            [exit() for i in pygame.event.get() if i.type == pygame.QUIT]

            self.clock.tick(60)


# Вычисление прибавления для изменения X и Y для Gamer
def Magic(Mouse, Player, c1):
    a = float(Mouse[1] - Player[1])
    b = float(Mouse[0] - Player[0])
    c = (a * a + b * b) ** 0.5
    a1 = a * c1 / c
    b1 = b * c1 / c
    return [b1, a1]


# Вычисление прибавления для изменения X и Y для Пули
def MagicForBullet(Mouse, Gamer, c1):
    a = Mouse[1] - Gamer[1]
    b = Mouse[0] - Gamer[0]

    c = (a * a + b * b) ** 0.5
    a1 = int(a * c1 / c)
    b1 = int(b * c1 / c)
    return [b1, a1]


# Проверка на столкновения Gamer с объектами карты
def Collide(Player):
    global Rects
    for Rect in Rects:
        if Player.colliderect(Rect):
            return True
    return False


# Поворот игрока
def blitRotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    surf.blit(rotated_image, rotated_image_rect)


def blitRotate2(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


# Игрок
class Person:
    def __init__(self, x, y):
        self.X = x
        self.Y = y
        self.SpeedY = 0
        self.SpeedX = 0
        self.Size = 60
        self.Speed = 7
        self.NitroSpeed = 14
        self.SpeedK = 0.2
        self.NitroSpeedK = 0.4
        self.Ammo = 1020
        self.Energy = 10000
        self.HP = 3


# Пуля
BulletSpeed = 15
Bullets = []


class Bullet:
    global w, h

    def __init__(self, x, y, SpeedX, SpeedY, GamerX, GamerY):
        self.X = x
        self.Y = y
        self.PX = GamerX + w // 2
        self.PY = GamerY + h // 2
        self.StartX = x
        self.StartY = y
        self.Stop = 1000
        self.T = 0
        self.SpeedX = SpeedX
        self.SpeedY = SpeedY

    def Sum(self, GamerX, GamerY):
        self.X += self.SpeedX - GamerX
        self.Y += self.SpeedY - GamerY
        self.PX += self.SpeedX - GamerX
        self.PY += self.SpeedY - GamerY
        self.T += 1

    def Existence(self):
        global Rects
        for Rect in Rects:
            if pygame.Rect(self.PX, self.PY, 10, 10).colliderect(Rect) or self.T > 36:
                return True
        return False


TempG = [0, 0]
Angle = 0
Gamer = Person(1500, 1500)

FPS = 200

window = pygame.display.set_mode((w, h))
pygame.display.set_caption("Test Game by RK-1207")
clock = pygame.time.Clock()

BackgroundColor = (215, 215, 215)
WallColor = (124, 124, 124)
WallSize = 600
k = w // WallSize

Last = False
image = StarFighterOFF

# Считывание уровня
FileLVL = open("LVLTest1", "r+")
ReadLVl = FileLVL.readlines()
FileLVL.close()


# Генерация координат для объектов карты
Rects = []
for i in range(len(ReadLVl)):
    ReadLVl[i] = ReadLVl[i].split("\n")[0]
for i in range(len(ReadLVl)):
    for j in range(len(ReadLVl[i])):
        if ReadLVl[i][j] == "1":
            Rects.append(pygame.Rect(j * WallSize, i * WallSize, WallSize, WallSize))


LastX = Gamer.X
LastY = Gamer.Y


# Дополнительные патроны и энергия
Ammos = []
Energys = []


class Object:
    def __init__(self, name):
        global Rects, SizeM
        self.Size = SizeM
        self.Name = name
        flag = True
        rand = [0, 0]
        while flag:
            rand = [
                random.randint(
                    2 * WallSize + 50,
                    (WallSize * len(ReadLVl[0])) - (2 * WallSize) - 50,
                ),
                random.randint(
                    2 * WallSize + 50, WallSize * len(ReadLVl) - 2 * WallSize - 50
                ),
            ]
            flag = False
            for Rect in Rects:
                if pygame.Rect(Rect[0], Rect[1], WallSize, WallSize).colliderect(
                    pygame.Rect(
                        rand[0] - self.Size,
                        rand[1] - self.Size,
                        self.Size * 2,
                        self.Size * 2,
                    )
                ):
                    flag = True
        self.X = rand[0]
        self.Y = rand[1]


# Метеориты
Meteorites = []
SizeM = 30


class Meteorite:
    def __init__(self):
        global Rects, SizeM
        self.Size = SizeM
        flag = True
        rand = [0, 0]
        while flag:
            rand = [
                random.randint(
                    WallSize + 50, WallSize * len(ReadLVl[0]) - WallSize - 50
                ),
                random.randint(WallSize + 50, WallSize * len(ReadLVl) - WallSize - 50),
            ]
            flag = False
            for Rect in Rects:
                if pygame.Rect(
                    Rect[0] - Gamer.X + self.Size,
                    Rect[1] - Gamer.Y + self.Size,
                    WallSize,
                    WallSize,
                ).colliderect(
                    pygame.Rect(
                        rand[0] + Gamer.X + w // 2,
                        rand[1] + Gamer.Y + h // 2,
                        self.Size * 2,
                        self.Size * 2,
                    )
                ):
                    flag = True

        # rand = [random.randint(0, len(ReadLVl[0] * WallSize)), random.randint(0, len(ReadLVl * WallSize))]
        self.X = rand[0] + Gamer.X + w // 2
        self.Y = rand[1] + Gamer.Y + h // 2
        self.XonD = rand[0] - Gamer.X + w // 2
        self.YonD = rand[1] - Gamer.Y + h // 2
        self.SpeedX = random.randint(-4, 4)
        self.SpeedY = random.randint(-4, 4)
        self.Time = 70
        self.Boom = False

    def CollideStar(self):
        if (self.XonD - w // 2) ** 2 + (self.YonD - h // 2) ** 2 > (
            self.Size + 21
        ) ** 2:
            return False
        return True

    def CollideBullet(self, Bullet):
        if (self.XonD - Bullet.X) ** 2 + (self.YonD - Bullet.Y) ** 2 > (
            self.Size + 5
        ) ** 2:
            return False
        return True

    def CollideWall(self, Rect):
        global WallSize
        if pygame.Rect(
            Rect[0] - Gamer.X + self.Size,
            Rect[1] - Gamer.Y + self.Size,
            WallSize,
            WallSize,
        ).colliderect(pygame.Rect(self.XonD, self.YonD, self.Size * 2, self.Size * 2)):
            if not pygame.Rect(
                Rect[0] - Gamer.X + self.Size,
                Rect[1] - Gamer.Y + self.Size,
                WallSize,
                WallSize,
            ).colliderect(
                pygame.Rect(
                    self.XonD - self.SpeedX * 2, self.YonD, self.Size * 2, self.Size * 2
                )
            ):
                return [-self.SpeedX, self.SpeedY]
            if not pygame.Rect(
                Rect[0] - Gamer.X + self.Size,
                Rect[1] - Gamer.Y + self.Size,
                WallSize,
                WallSize,
            ).colliderect(
                pygame.Rect(
                    self.XonD, self.YonD - self.SpeedY * 2, self.Size * 2, self.Size * 2
                )
            ):
                return [self.SpeedX, -self.SpeedY]
            if not pygame.Rect(
                Rect[0] - Gamer.X + self.Size,
                Rect[1] - Gamer.Y + self.Size,
                WallSize,
                WallSize,
            ).colliderect(
                pygame.Rect(
                    self.XonD - self.SpeedX * 2,
                    self.YonD - self.SpeedY * 2,
                    self.Size * 2,
                    self.Size * 2,
                )
            ):
                return [-self.SpeedX, -self.SpeedY]
            else:
                return [self.SpeedX, self.SpeedY]
        else:
            return [self.SpeedX, self.SpeedY]

    def Sum(self, GamerX, GamerY):
        self.X += self.SpeedX - GamerX
        self.Y += self.SpeedY - GamerY
        self.XonD += self.SpeedX - GamerX
        self.YonD += self.SpeedY - GamerY
        if self.Boom:
            self.Time -= 1


# Меню...............................................................................................................


def Menu():
    app = App()
    app.run()


# Игра
def Game():
    global Gamer
    BulletSpeed = 25
    Bullets = []

    TimeS = 400
    TimeH = 200
    Stop = False
    Stop2 = False

    CosX = -1500
    CosY = -1200

    TempG = [0, 0]
    Angle = 0
    Gamer = Person(3000, 3000)

    Score = 0
    Fontforscore = pygame.font.Font(None, 30)

    FPS = 200

    window = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Test Game by RK-1207")
    clock = pygame.time.Clock()

    BackgroundColor = (215, 215, 215)
    WallSize = 600
    k = w // WallSize

    Last = False
    image = StarFighterOFF

    # Считывание уровня
    FileLVL = open("LVLTest1", "r+")
    ReadLVl = FileLVL.readlines()
    FileLVL.close()

    # Генерация координат для объектов карты
    Rects = []
    for i in range(len(ReadLVl)):
        ReadLVl[i] = ReadLVl[i].split("\n")[0]
    for i in range(len(ReadLVl)):
        for j in range(len(ReadLVl[i])):
            if ReadLVl[i][j] == "1":
                Rects.append(
                    pygame.Rect(j * WallSize, i * WallSize, WallSize, WallSize)
                )

    LastX = Gamer.X
    LastY = Gamer.Y
    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        Mousepress = pygame.mouse.get_pressed()
        Angle = math.degrees(math.atan2(-(mouse[1] - h // 2), (mouse[0] - w // 2))) - 90

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
        if not Stop:
            Key = pygame.key.get_pressed()
            if (
                (
                    (Key[pygame.K_d] and Key[pygame.K_LSHIFT])
                    or (Key[pygame.K_SPACE] and Key[pygame.K_LSHIFT])
                )
                and (Gamer.Energy > 0)
                and not Collide(
                    pygame.Rect(
                        Gamer.X
                        + Magic(mouse, [w // 2, h // 2], Gamer.Speed)[0]
                        + w // 2
                        - Gamer.Size // 2,
                        Gamer.Y
                        + h // 2
                        - Gamer.Size // 2
                        + Magic(mouse, [w // 2, h // 2], Gamer.Speed)[1],
                        Gamer.Size,
                        Gamer.Size,
                    )
                )
            ):
                image = StarFighterNITRO
                Gamer.Energy -= 4
                TempG = Magic(mouse, [w // 2, h // 2], Gamer.NitroSpeedK)
                if abs(Gamer.SpeedX) + abs(Gamer.SpeedY) < Gamer.NitroSpeed:
                    Gamer.SpeedX += TempG[0]
                    Gamer.SpeedY += TempG[1]
                LastX = Gamer.X
                LastY = Gamer.Y

            elif (
                (Key[pygame.K_d] or Key[pygame.K_SPACE])
                and (Gamer.Energy > 0)
                and not Collide(
                    pygame.Rect(
                        Gamer.X
                        + Magic(mouse, [w // 2, h // 2], Gamer.Speed)[0]
                        + w // 2
                        - Gamer.Size // 2,
                        Gamer.Y
                        + h // 2
                        - Gamer.Size // 2
                        + Magic(mouse, [w // 2, h // 2], Gamer.Speed)[1],
                        Gamer.Size,
                        Gamer.Size,
                    )
                )
            ):
                image = StarFighterON
                Gamer.Energy -= 2
                TempG = Magic(mouse, [w // 2, h // 2], Gamer.SpeedK)
                if abs(Gamer.SpeedX) + abs(Gamer.SpeedY) < Gamer.Speed:
                    TempG = Magic(mouse, [w // 2, h // 2], Gamer.SpeedK)
                    Gamer.SpeedX += TempG[0]
                    Gamer.SpeedY += TempG[1]

                LastX = Gamer.X
                LastY = Gamer.Y
            elif Collide(
                pygame.Rect(
                    Gamer.X
                    + Magic(mouse, [w // 2, h // 2], Gamer.Speed)[0]
                    + w // 2
                    - Gamer.Size // 2,
                    Gamer.Y
                    + h // 2
                    - Gamer.Size // 2
                    + Magic(mouse, [w // 2, h // 2], Gamer.Speed)[1],
                    Gamer.Size,
                    Gamer.Size,
                )
            ):
                image = StarFighterOFF
                Gamer.X = LastX
                Gamer.Y = LastY
                Gamer.SpeedX = 0
                Gamer.SpeedY = 0
            else:
                image = StarFighterOFF
                LastX = Gamer.X
                LastY = Gamer.Y
            if (Key[pygame.K_s] or Mousepress[0]) and not Last and Gamer.Ammo > 0:
                Temp = MagicForBullet(mouse, (w // 2, h // 2), BulletSpeed)

                TempA = [
                    math.sin(math.radians(Angle + 90)) * Gamer.Size // 2,
                    math.cos(math.radians(Angle + 90)) * Gamer.Size // 2,
                ]

                Bullets.append(
                    Bullet(
                        w // 2 + TempA[0],
                        h // 2 + TempA[1] - 5,
                        Temp[0],
                        Temp[1],
                        Gamer.X + TempA[0],
                        Gamer.Y + TempA[1],
                    )
                )

                TempA = [
                    math.sin(math.radians(Angle - 90)) * Gamer.Size // 2,
                    math.cos(math.radians(Angle - 90)) * Gamer.Size // 2,
                ]

                Bullets.append(
                    Bullet(
                        w // 2 + TempA[0],
                        h // 2 + TempA[1] - 5,
                        Temp[0],
                        Temp[1],
                        Gamer.X + TempA[0],
                        Gamer.Y + TempA[1],
                    )
                )

                Last = True
                Gamer.Ammo -= 20

            if not Key[pygame.K_s] and not Mousepress[0]:
                Last = False
        else:
            TimeH -= 1
        if Gamer.Energy <= 0:
            Stop2 = True
        # Создание недостающих элементов
        if len(Meteorites) < NumberOfMeteorites:
            Meteorites.append(Meteorite())

        if len(Energys) < NumberOfEnergy:
            Energys.append(Object("Energy"))
        if len(Ammos) < NumberOfAmmo:
            Ammos.append(Object("Ammo"))

        window.fill(BackgroundColor)

        Gamer.SpeedX -= Gamer.SpeedX / 150
        Gamer.SpeedY -= Gamer.SpeedY / 150
        Gamer.X += Gamer.SpeedX
        Gamer.Y += Gamer.SpeedY
        CosX -= Gamer.SpeedX / 10
        CosY -= Gamer.SpeedY / 10

        window.blit(CosmoFon, (CosX, CosY))
        # Вывод игрока
        pos = (
            window.get_width() / 2 - (Gamer.Size // 2),
            window.get_height() / 2 - (Gamer.Size // 2),
        )
        blitRotate2(window, image, pos, Angle)

        # Вывод пуль
        for i in Bullets:
            if not Collide(pygame.Rect(i.PX, i.PY, 10, 10)) and i.T < 500:
                window.blit(BulletT, (i.X, i.Y))
                i.Sum(Gamer.SpeedX, Gamer.SpeedY)
            else:
                Bullets.remove(i)

        # Вывод объектов
        for i in Energys:
            if (i.X - Gamer.X - w // 2) ** 2 + (i.Y - Gamer.Y - h // 2) ** 2 <= (
                i.Size + 25
            ) ** 2:
                Energys.remove(i)
                Gamer.Energy += 4000
                if Gamer.Energy > 10000:
                    Gamer.Energy = 10000
            else:
                window.blit(EnergyT, (i.X - Gamer.X - i.Size, i.Y - Gamer.Y - i.Size))
        for i in Ammos:
            if (i.X - Gamer.X - w // 2) ** 2 + (i.Y - Gamer.Y - h // 2) ** 2 <= (
                i.Size + 25
            ) ** 2:
                Ammos.remove(i)
                Gamer.Ammo += 300
                if Gamer.Ammo > 1000:
                    Gamer.Ammo = 1000
            else:
                window.blit(AmmoT, (i.X - Gamer.X - i.Size, i.Y - Gamer.Y - i.Size))

        flag = True
        # Вывод Метеоритов
        for i in Meteorites:
            flag = True
            if not i.CollideStar():
                for Rect in Rects:
                    p = i.CollideWall(Rect)
                    i.SpeedX = p[0]
                    i.SpeedY = p[1]
                for j in Bullets:
                    if i.CollideBullet(j):
                        flag = False
                        Score += 10
                if flag:
                    i.Sum(Gamer.SpeedX, Gamer.SpeedY)
                    if not i.Boom:
                        window.blit(Meteor, [i.XonD - 30, i.YonD - 30])
                    else:
                        window.blit(Boom, [i.XonD - 30, i.YonD - 30])
                elif not flag and not i.Boom:
                    i.Boom = True
                    window.blit(Boom, [i.XonD - 30, i.YonD - 30])
                    i.SpeedX = i.SpeedX / 1.5
                    i.SpeedY = i.SpeedY / 1.5
                    Bullets.remove(j)
                else:
                    window.blit(Boom, [i.XonD - 30, i.YonD - 30])
                if i.Time <= 0:
                    Meteorites.remove(i)
            else:
                if not i.Boom:
                    i.SpeedX = i.SpeedX / 4
                    i.SpeedY = i.SpeedY / 4
                    window.blit(Boom, [i.XonD - 30, i.YonD - 30])
                    i.Boom = True
                    Gamer.HP -= 1
                    i.Time = 30
                else:
                    i.Sum(Gamer.SpeedX, Gamer.SpeedY)
                    window.blit(Boom, [i.XonD - 30, i.YonD - 30])

        if Stop2:
            TimeS -= 1
        # Вывод структур карты
        for i in Rects:
            window.blit(Wall, (i[0] - Gamer.X, i[1] - Gamer.Y))

        # Вывод счетчиков
        window.blit(PageT, (0, 0))
        textScore = Fontforscore.render("SCORE: " + str(Score), True, (207, 20, 20))
        window.blit(textScore, (12, 102))
        if Gamer.Energy > 0:
            pygame.draw.rect(window, (0, 187, 212), (12, 12, Gamer.Energy / 50, 16))
        if Gamer.Ammo > 0:
            pygame.draw.rect(window, (255, 86, 34), (12, 40, Gamer.Ammo / 5, 16))
        if Gamer.HP > 0:
            pygame.draw.rect(window, (116, 255, 3), (12, 68, Gamer.HP * 50, 16))
        if Gamer.HP < 3:
            Gamer.HP += 0.0001
        # Кончились хп
        if Gamer.HP <= 0:
            Stop = True

        if TimeH <= 0 or TimeS <= 0:
            file = open("Scores.txt", "a")
            file.write(str(Score) + " ")
            file.close()
            Menu()

        pygame.display.update()
        clock.tick(FPS)


Menu()
