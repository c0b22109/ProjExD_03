import random
import sys
import time
import math

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 3


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Beam:
    def __init__(self, bird):
        self.vx, self.vy = bird.dire
        self.img = pg.transform.rotozoom(pg.image.load("fig/beam.png"), math.degrees(math.atan2(-self.vy, self.vx)), 1)
        self.rect = self.img.get_rect()
        self.rect.center = [
            bird.rct.centerx + bird.rct.width * self.vx / 5,
            bird.rct.centery + bird.rct.height * self.vy / 5
        ]

    def update(self, screen):
        self.rect.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rect)
        

class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.img = pg.transform.rotozoom(  # 2倍に拡大
            pg.image.load(f"fig/{num}.png"), 
            0, 
            2.0
        )

        self.img_dict: dict = {
            (i * 5, j * 5): pg.transform.flip(pg.transform.rotozoom(self.img, 90 * j, 1), True, False) if i == 0 \
            else pg.transform.flip(pg.transform.rotozoom(self.img, 45 * j, 1), True, False) if i >= 0 \
            else pg.transform.rotozoom(self.img, 45 * j, 1) for i in range(-1, 2) for j in range(-1, 2)
        }   #移動量の合計値をキーとするこうかとんの画像Surfaceの辞書を作成
        self.dire = (+5, 0)
        self.img = self.img_dict[self.dire]
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if sum_mv != [0, 0]:
            self.dire = sum_mv
        self.img = self.img_dict[tuple(self.dire)]
        screen.blit(self.img, self.rct)
            

class Bomb:
    """
    爆弾に関するクラス
    """

    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        bomb_color_lst = [
            [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255], [0, 255, 255]
        ]
        bomb_move_direction = [[i, j] for i in range(-5, 10, 5) for j in range(-5, 10, 5) if i != 0 or j != 0]
        rad = random.randint(5, 30)
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, random.choice(bomb_color_lst), (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        (self.vx, self.vy) = random.choice(bomb_move_direction)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Explosion:
    def __init__(self, bomb: Bomb):
        exp_img = pg.image.load("fig/explosion.gif")
        self.exp_img_lst = [
            pg.transform.flip(exp_img, i, j) for i in [True, False] for j in [True, False]
        ]
        self.rect = exp_img.get_rect()
        self.rect.center = bomb.rct.center
        self.life = 10

    def update(self, screen: pg.Surface):
        self.life -= 1
        screen.blit(self.exp_img_lst[self.life % len(self.exp_img_lst)], self.rect)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bomb_lst = [Bomb() for i in range(NUM_OF_BOMBS)]
    beam = None
    explosion_lst = []

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        screen.blit(bg_img, [0, 0])
    
        for (bomb_lst_index, bomb) in enumerate(bomb_lst):
            if bomb is not None:    
                if bird.rct.colliderect(bomb.rct):
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    beam = None
                    bomb_lst[bomb_lst_index] = None
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
            if beam is not None and bomb is not None: 
                if beam.rect.colliderect(bomb.rct):
                    explosion_lst.append(Explosion(bomb))
                    beam = None
                    bomb_lst[bomb_lst_index] = None
                    bird.change_img(6, screen)

        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_SPACE]:
            beam = Beam(bird)
        bird.update(key_lst, screen)
        for bomb in bomb_lst:
            if bomb is not None:
                bomb.update(screen)
        if beam is not None:
            beam.update(screen)
        for (explosion_lst_index, explosion) in enumerate(explosion_lst):
            if explosion.life <= 0:
                del explosion_lst[explosion_lst_index]
            else:
                explosion.update(screen) 
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
