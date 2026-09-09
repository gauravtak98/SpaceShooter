import os
import random
import math

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Ellipse, Color, Line
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.audio import SoundLoader


# =========================================================
# GAME DIRECTORY
# =========================================================

GAME_DIR = os.path.dirname(os.path.abspath(__file__))


# =========================================================
# IMAGE PATHS
# =========================================================

PLAYER_IMAGE = os.path.join(GAME_DIR, "player.png")
NORMAL_IMAGE = os.path.join(GAME_DIR, "enemy.png")
FAST_IMAGE = os.path.join(GAME_DIR, "fast_enemy.png")
STRONG_IMAGE = os.path.join(GAME_DIR, "strong_enemy.png")
BOSS_IMAGE = os.path.join(GAME_DIR, "boss.png")
BACKGROUND_IMAGE = os.path.join(GAME_DIR, "background.jpg")


# =========================================================
# SOUND PATHS
# =========================================================

SHOOT_SOUND = os.path.join(GAME_DIR, "shoot.mp3")

BOSS_HIT_SOUND = os.path.join(GAME_DIR, "boss_hit.mp3")
BOSS_SHOOT_SOUND = os.path.join(GAME_DIR, "boss_shoot.mp3")
BOSS_DESTROY_SOUND = os.path.join(GAME_DIR, "boss_destroy.mp3")
BOSS_SPAWN_SOUND = os.path.join(GAME_DIR, "boss_spawn.mp3")

ENEMY_DESTROY_SOUND = os.path.join(
    GAME_DIR,
    "enemy_destroy.mp3"
)

ENEMY_HIT_SOUND = os.path.join(
    GAME_DIR,
    "enemy_hit.mp3"
)

GAME_OVER_SOUND = os.path.join(
    GAME_DIR,
    "game_over.mp3"
)

PLAYER_HIT_SOUND = os.path.join(
    GAME_DIR,
    "player_hit.mp3"
)


# =========================================================
# PLAYER
# =========================================================

class Player(Widget):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        with self.canvas:

            self.image = Rectangle(
                source=PLAYER_IMAGE,
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_image
        )

        self.bind(
            size=self.update_image
        )

    def update_image(self, *args):

        self.image.pos = self.pos
        self.image.size = self.size


# =========================================================
# BULLET
# =========================================================

class Bullet(Widget):

    def __init__(
        self,
        owner="player",
        damage=1,
        speed=10,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.owner = owner
        self.damage = damage
        self.speed = speed

        with self.canvas:

            if owner == "player":

                Color(
                    0,
                    1,
                    1,
                    1
                )

            else:

                Color(
                    1,
                    0.15,
                    0.1,
                    1
                )

            self.rect = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_graphics
        )

        self.bind(
            size=self.update_graphics
        )

    def update_graphics(self, *args):

        self.rect.pos = self.pos
        self.rect.size = self.size


# =========================================================
# ENEMY
# =========================================================

class Enemy(Widget):

    def __init__(
        self,
        enemy_type="normal",
        **kwargs
    ):

        super().__init__(**kwargs)

        self.enemy_type = enemy_type

        # -------------------------
        # NORMAL
        # -------------------------

        if enemy_type == "normal":

            self.speed = 3
            self.hp = 1
            self.damage = 20
            self.score = 10
            self.image_path = NORMAL_IMAGE
            self.size = (90, 90)

        # -------------------------
        # FAST
        # -------------------------

        elif enemy_type == "fast":

            self.speed = 6
            self.hp = 1
            self.damage = 20
            self.score = 20
            self.image_path = FAST_IMAGE
            self.size = (80, 80)

        # -------------------------
        # STRONG
        # -------------------------

        else:

            self.speed = 2
            self.hp = 2
            self.damage = 40
            self.score = 40
            self.image_path = STRONG_IMAGE
            self.size = (115, 115)

        with self.canvas:

            self.image = Rectangle(
                source=self.image_path,
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_image
        )

        self.bind(
            size=self.update_image
        )

    def update_image(self, *args):

        self.image.pos = self.pos
        self.image.size = self.size


# =========================================================
# BOSS
# =========================================================

class Boss(Widget):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.size = (180, 180)

        self.hp = 350
        self.max_hp = 350

        self.speed = 1.2
        self.damage = 10
        self.score = 500

        self.direction = 1

        self.shoot_timer = 0

        with self.canvas:

            self.image = Rectangle(
                source=BOSS_IMAGE,
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_image
        )

        self.bind(
            size=self.update_image
        )

    def update_image(self, *args):

        self.image.pos = self.pos
        self.image.size = self.size


# =========================================================
# JOYSTICK
# =========================================================

class Joystick(Widget):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.size = (
            170,
            170
        )

        self.dx = 0
        self.dy = 0

        self.active_touch = None

        with self.canvas:

            Color(
                0.15,
                0.15,
                0.15,
                0.7
            )

            self.base = Ellipse(
                pos=self.pos,
                size=self.size
            )

            Color(
                0.4,
                0.4,
                0.4,
                0.9
            )

            self.knob = Ellipse(
                pos=(
                    self.x + 55,
                    self.y + 55
                ),
                size=(
                    60,
                    60
                )
            )

        self.bind(
            pos=self.update_graphics
        )

    def update_graphics(self, *args):

        self.base.pos = self.pos

        if self.active_touch is None:

            self.knob.pos = (
                self.x + 55,
                self.y + 55
            )

    def on_touch_down(self, touch):

        if self.collide_point(
            *touch.pos
        ):

            self.active_touch = touch

            self.move_knob(touch)

            return True

        return super().on_touch_down(
            touch
        )

    def on_touch_move(self, touch):

        if touch == self.active_touch:

            self.move_knob(touch)

            return True

        return super().on_touch_move(
            touch
        )

    def on_touch_up(self, touch):

        if touch == self.active_touch:

            self.active_touch = None

            self.dx = 0
            self.dy = 0

            self.knob.pos = (
                self.x + 55,
                self.y + 55
            )

            return True

        return super().on_touch_up(
            touch
        )

    def move_knob(self, touch):

        center_x = self.x + 85
        center_y = self.y + 85

        dx = touch.x - center_x
        dy = touch.y - center_y

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        max_distance = 55

        if distance > max_distance:

            dx = (
                dx / distance
            ) * max_distance

            dy = (
                dy / distance
            ) * max_distance

        self.knob.pos = (
            center_x + dx - 30,
            center_y + dy - 30
        )

        self.dx = dx / max_distance
        self.dy = dy / max_distance


# =========================================================
# FIRE BUTTON
# =========================================================

class FireButton(Widget):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.size = (
            120,
            120
        )

        with self.canvas:

            Color(
                1,
                0.1,
                0.1,
                0.8
            )

            self.circle = Ellipse(
                pos=self.pos,
                size=self.size
            )

            Color(
                1,
                1,
                1,
                0.8
            )

            self.border = Line(
                circle=(
                    self.center_x,
                    self.center_y,
                    60
                ),
                width=3
            )

        self.label = Label(
            text="FIRE",
            font_size=22,
            bold=True,
            pos=self.pos,
            size=self.size
        )

        self.add_widget(
            self.label
        )

        self.bind(
            pos=self.update_graphics
        )

        self.bind(
            size=self.update_graphics
        )

    def update_graphics(self, *args):

        self.circle.pos = self.pos
        self.circle.size = self.size

        self.border.circle = (
            self.center_x,
            self.center_y,
            self.width / 2
        )

        self.label.pos = self.pos
        self.label.size = self.size

    def on_touch_down(self, touch):

        if self.collide_point(
            *touch.pos
        ):

            if self.parent:

                self.parent.shoot()

            return True

        return super().on_touch_down(
            touch
        )


# =========================================================
# GAME
# =========================================================

class Game(Widget):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # =================================================
        # VARIABLES
        # =================================================

        self.score = 0

        self.health = 100
        self.max_health = 100

        self.bullets = []
        self.enemies = []

        self.boss = None
        self.boss_bullets = []

        self.boss_timer = 0

        self.game_over = False

        # =================================================
        # LOAD SOUNDS
        # =================================================

        self.shoot_sound = SoundLoader.load(
            SHOOT_SOUND
        )

        self.enemy_hit_sound = SoundLoader.load(
            ENEMY_HIT_SOUND
        )

        self.enemy_destroy_sound = SoundLoader.load(
            ENEMY_DESTROY_SOUND
        )

        self.player_hit_sound = SoundLoader.load(
            PLAYER_HIT_SOUND
        )

        self.game_over_sound = SoundLoader.load(
            GAME_OVER_SOUND
        )

        self.boss_hit_sound = SoundLoader.load(
            BOSS_HIT_SOUND
        )

        self.boss_shoot_sound = SoundLoader.load(
            BOSS_SHOOT_SOUND
        )

        self.boss_destroy_sound = SoundLoader.load(
            BOSS_DESTROY_SOUND
        )

        self.boss_spawn_sound = SoundLoader.load(
            BOSS_SPAWN_SOUND
        )

        # =================================================
        # BACKGROUND
        # =================================================

        with self.canvas.before:

            self.background = Rectangle(
                source=BACKGROUND_IMAGE,
                pos=(0, 0),
                size=Window.size
            )

        Window.bind(
            size=self.update_background
        )

        # =================================================
        # PLAYER
        # =================================================

        self.player = Player(
            size=(
                110,
                110
            )
        )

        self.player.pos = (
            Window.width / 2 - 55,
            120
        )

        self.add_widget(
            self.player
        )

        # =================================================
        # SCORE
        # =================================================

        self.score_label = Label(
            text="SCORE: 0",
            font_size=22,
            bold=True,
            size_hint=(None, None),
            size=(
                200,
                50
            ),
            pos=(
                10,
                Window.height - 60
            )
        )

        self.add_widget(
            self.score_label
        )

        # =================================================
        # HEALTH TEXT
        # =================================================

        self.health_label = Label(
            text="HEALTH: 100",
            font_size=22,
            bold=True,
            size_hint=(None, None),
            size=(
                220,
                50
            ),
            pos=(
                Window.width - 230,
                Window.height - 60
            )
        )

        self.add_widget(
            self.health_label
        )

        # =================================================
        # HEALTH BAR
        # =================================================

        self.health_bg = Widget(
            size=(
                220,
                22
            ),
            pos=(
                Window.width - 230,
                Window.height - 90
            )
        )

        with self.health_bg.canvas:

            Color(
                0.25,
                0.25,
                0.25,
                1
            )

            self.health_background = Rectangle(
                pos=self.health_bg.pos,
                size=self.health_bg.size
            )

            Color(
                0.1,
                1,
                0.2,
                1
            )

            self.health_fill = Rectangle(
                pos=self.health_bg.pos,
                size=self.health_bg.size
            )

            Color(
                1,
                1,
                1,
                1
            )

            self.health_border = Line(
                rectangle=(
                    self.health_bg.x,
                    self.health_bg.y,
                    self.health_bg.width,
                    self.health_bg.height
                ),
                width=2
            )

        self.add_widget(
            self.health_bg
        )

        # =================================================
        # JOYSTICK
        # =================================================

        self.joystick = Joystick(
            pos=(
                30,
                30
            )
        )

        self.add_widget(
            self.joystick
        )

        # =================================================
        # FIRE BUTTON
        # =================================================

        self.fire_area = FireButton(
            pos=(
                Window.width - 150,
                40
            )
        )

        self.add_widget(
            self.fire_area
        )

        # =================================================
        # BOSS HEALTH TEXT
        # =================================================

        self.boss_label = Label(
            text="",
            font_size=22,
            bold=True,
            size_hint=(None, None),
            size=(
                400,
                45
            ),
            pos=(
                Window.width / 2 - 200,
                Window.height - 150
            )
        )

        self.add_widget(
            self.boss_label
        )

        # =================================================
        # BOSS HEALTH BAR
        # =================================================

        self.boss_health_bg = Widget(
            size=(
                400,
                25
            ),
            pos=(
                Window.width / 2 - 200,
                Window.height - 180
            )
        )

        with self.boss_health_bg.canvas:

            Color(
                0.2,
                0.2,
                0.2,
                1
            )

            self.boss_background = Rectangle(
                pos=self.boss_health_bg.pos,
                size=self.boss_health_bg.size
            )

            Color(
                1,
                0.05,
                0.05,
                1
            )

            self.boss_fill = Rectangle(
                pos=self.boss_health_bg.pos,
                size=self.boss_health_bg.size
            )

            Color(
                1,
                1,
                1,
                1
            )

            self.boss_border = Line(
                rectangle=(
                    self.boss_health_bg.x,
                    self.boss_health_bg.y,
                    self.boss_health_bg.width,
                    self.boss_health_bg.height
                ),
                width=2
            )

        self.boss_health_bg.opacity = 0
        self.boss_label.opacity = 0

        self.add_widget(
            self.boss_health_bg
        )

        # =================================================
        # WARNING
        # =================================================

        self.warning_label = Label(
            text="",
            font_size=35,
            bold=True,
            color=(
                1,
                0.1,
                0.1,
                1
            ),
            size_hint=(None, None),
            size=(
                600,
                80
            ),
            pos=(
                Window.width / 2 - 300,
                Window.height / 2 + 100
            )
        )

        self.add_widget(
            self.warning_label
        )

        # =================================================
        # GAME OVER
        # =================================================

        self.game_over_label = Label(
            text="",
            font_size=45,
            bold=True,
            color=(
                1,
                0.2,
                0.2,
                1
            ),
            halign="center",
            valign="middle",
            size_hint=(None, None),
            size=(
                500,
                200
            ),
            pos=(
                Window.width / 2 - 250,
                Window.height / 2 - 100
            )
        )

        self.add_widget(
            self.game_over_label
        )

        # =================================================
        # LOOPS
        # =================================================

        Clock.schedule_interval(
            self.update,
            1 / 60
        )

        Clock.schedule_interval(
            self.spawn_enemy,
            1.5
        )

        # Boss timer
        Clock.schedule_interval(
            self.boss_countdown,
            1
        )

    # =====================================================
    # BACKGROUND
    # =====================================================

    def update_background(self, *args):

        self.background.size = Window.size

        self.score_label.pos = (
            10,
            Window.height - 60
        )

        self.health_label.pos = (
            Window.width - 230,
            Window.height - 60
        )

        self.health_bg.pos = (
            Window.width - 230,
            Window.height - 90
        )

        self.joystick.pos = (
            30,
            30
        )

        self.fire_area.pos = (
            Window.width - 150,
            40
        )

        self.boss_label.pos = (
            Window.width / 2 - 200,
            Window.height - 150
        )

        self.boss_health_bg.pos = (
            Window.width / 2 - 200,
            Window.height - 180
        )

        self.warning_label.pos = (
            Window.width / 2 - 300,
            Window.height / 2 + 100
        )

        self.game_over_label.pos = (
            Window.width / 2 - 250,
            Window.height / 2 - 100
        )

    # =====================================================
    # PLAY SOUND
    # =====================================================

    def play_sound(self, sound):

        if sound:

            try:

                sound.stop()
                sound.play()

            except Exception:

                pass

    # =====================================================
    # SHOOT
    # =====================================================

    def shoot(self):

        if self.game_over:
            return

        bullet = Bullet(
            owner="player",
            damage=1,
            speed=10,
            size=(
                8,
                30
            )
        )

        bullet.pos = (
            self.player.center_x - 4,
            self.player.top
        )

        self.bullets.append(
            bullet
        )

        self.add_widget(
            bullet
        )

        self.play_sound(
            self.shoot_sound
        )

    # =====================================================
    # SPAWN ENEMY
    # =====================================================

    def spawn_enemy(self, dt):

        if self.game_over:
            return

        # No normal enemies while boss is alive
        if self.boss:
            return

        number = random.randint(
            1,
            100
        )

        if number <= 60:

            enemy_type = "normal"

        elif number <= 85:

            enemy_type = "fast"

        else:

            enemy_type = "strong"

        enemy = Enemy(
            enemy_type
        )

        enemy.x = random.randint(
            0,
            max(
                0,
                int(
                    Window.width -
                    enemy.width
                )
            )
        )

        enemy.y = Window.height + 20

        self.enemies.append(
            enemy
        )

        self.add_widget(
            enemy
        )

    # =====================================================
    # BOSS TIMER
    # =====================================================

    def boss_countdown(self, dt):

        if self.game_over:
            return

        if self.boss:
            return

        self.boss_timer += 1

        if self.boss_timer >= 60:

            self.boss_timer = 0

            self.spawn_boss()

    # =====================================================
    # SPAWN BOSS
    # =====================================================

    def spawn_boss(self):

        if self.boss:
            return

        # Remove remaining enemies
        for enemy in self.enemies[:]:

            if enemy.parent:

                self.remove_widget(
                    enemy
                )

            if enemy in self.enemies:

                self.enemies.remove(
                    enemy
                )

        self.boss = Boss()

        self.boss.pos = (
            Window.width / 2 - 90,
            Window.height - 240
        )

        self.add_widget(
            self.boss
        )

        self.boss_label.text = (
            "☠️ BOSS   HP: 350 / 350"
        )

        self.boss_label.opacity = 1

        self.boss_health_bg.opacity = 1

        self.update_boss_bar()

        self.warning_label.text = (
            "⚠️ BOSS INCOMING! ⚠️"
        )

        self.play_sound(
            self.boss_spawn_sound
        )

        Clock.schedule_once(
            self.remove_warning,
            3
        )

    # =====================================================
    # REMOVE WARNING
    # =====================================================

    def remove_warning(self, dt):

        self.warning_label.text = ""

    # =====================================================
    # UPDATE BOSS BAR
    # =====================================================

    def update_boss_bar(self):

        if not self.boss:

            self.boss_fill.size = (
                0,
                25
            )

            return

        percentage = (
            self.boss.hp /
            self.boss.max_hp
        )

        self.boss_fill.size = (
            400 * percentage,
            25
        )

        self.boss_label.text = (
            "☠️ BOSS   HP: "
            + str(
                max(
                    0,
                    self.boss.hp
                )
            )
            + " / "
            + str(
                self.boss.max_hp
            )
        )

    # =====================================================
    # BOSS SHOOT
    # =====================================================

    def boss_shoot(self):

        if not self.boss:
            return

        bullet = Bullet(
            owner="boss",
            damage=10,
            speed=-5,
            size=(
                10,
                30
            )
        )

        bullet.pos = (
            self.boss.center_x - 5,
            self.boss.y
        )

        self.boss_bullets.append(
            bullet
        )

        self.add_widget(
            bullet
        )

        self.play_sound(
            self.boss_shoot_sound
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if self.game_over:
            return

        # =================================================
        # PLAYER MOVEMENT
        # =================================================

        self.player.x += (
            self.joystick.dx * 6
        )

        self.player.y += (
            self.joystick.dy * 6
        )

        # Screen limits

        if self.player.x < 0:

            self.player.x = 0

        if self.player.right > Window.width:

            self.player.right = Window.width

        if self.player.y < 0:

            self.player.y = 0

        if self.player.top > Window.height:

            self.player.top = Window.height

        # =================================================
        # PLAYER BULLETS
        # =================================================

        for bullet in self.bullets[:]:

            bullet.y += bullet.speed

            if bullet.y > Window.height:

                self.remove_player_bullet(
                    bullet
                )

                continue

            # -----------------------------
            # BULLET VS ENEMY
            # -----------------------------

            for enemy in self.enemies[:]:

                if (
                    bullet in self.bullets
                    and
                    self.check_collision(
                        bullet,
                        enemy
                    )
                ):

                    self.hit_enemy(
                        bullet,
                        enemy
                    )

                    break

            # -----------------------------
            # BULLET VS BOSS
            # -----------------------------

            if (
                bullet in self.bullets
                and
                self.boss
                and
                self.check_collision(
                    bullet,
                    self.boss
                )
            ):

                self.hit_boss(
                    bullet
                )

        # =================================================
        # ENEMIES
        # =================================================

        for enemy in self.enemies[:]:

            if enemy not in self.enemies:
                continue

            enemy.y -= enemy.speed

            # Enemy leaves screen

            if enemy.top < 0:

                self.remove_enemy(
                    enemy
                )

                continue

            # Player collision

            if self.check_collision(
                self.player,
                enemy
            ):

                self.player_hit(
                    enemy
                )

        # =================================================
        # BOSS
        # =================================================

        if self.boss:

            # Horizontal movement

            self.boss.x += (
                self.boss.speed *
                self.boss.direction
            )

            if self.boss.x <= 0:

                self.boss.x = 0

                self.boss.direction = 1

            if self.boss.right >= Window.width:

                self.boss.right = Window.width

                self.boss.direction = -1

            # Boss shooting timer

            self.boss.shoot_timer += dt

            if self.boss.shoot_timer >= 1.8:

                self.boss.shoot_timer = 0

                self.boss_shoot()

        # =================================================
        # BOSS BULLETS
        # =================================================

        for bullet in self.boss_bullets[:]:

            bullet.y += bullet.speed

            if bullet.top < 0:

                self.remove_boss_bullet(
                    bullet
                )

                continue

            if self.check_collision(
                bullet,
                self.player
            ):

                self.remove_boss_bullet(
                    bullet
                )

                self.damage_player(
                    10
                )

    # =====================================================
    # COLLISION
    # =====================================================

    def check_collision(self, a, b):

        return (
            a.x < b.right
            and
            a.right > b.x
            and
            a.y < b.top
            and
            a.top > b.y
        )

    # =====================================================
    # HIT ENEMY
    # =====================================================

    def hit_enemy(
        self,
        bullet,
        enemy
    ):

        if bullet not in self.bullets:
            return

        if enemy not in self.enemies:
            return

        # Remove bullet

        self.remove_player_bullet(
            bullet
        )

        # Enemy gets damage

        enemy.hp -= 1

        # Enemy hit sound

        if enemy.hp > 0:

            self.play_sound(
                self.enemy_hit_sound
            )

        # Enemy destroyed

        if enemy.hp <= 0:

            self.remove_enemy(
                enemy
            )

            self.score += enemy.score

            self.score_label.text = (
                "SCORE: "
                + str(
                    self.score
                )
            )

            self.play_sound(
                self.enemy_destroy_sound
            )

    # =====================================================
    # HIT BOSS
    # =====================================================

    def hit_boss(self, bullet):

        if not self.boss:
            return

        if bullet not in self.bullets:
            return

        self.remove_player_bullet(
            bullet
        )

        self.boss.hp -= 1

        if self.boss.hp > 0:

            self.play_sound(
                self.boss_hit_sound
            )

        self.update_boss_bar()

        if self.boss.hp <= 0:

            self.destroy_boss()

    # =====================================================
    # DESTROY BOSS
    # =====================================================

    def destroy_boss(self):

        if not self.boss:
            return

        old_boss = self.boss

        self.boss = None

        if old_boss.parent:

            self.remove_widget(
                old_boss
            )

        self.score += 500

        self.score_label.text = (
            "SCORE: "
            + str(
                self.score
            )
        )

        self.boss_label.text = ""

        self.boss_label.opacity = 0

        self.boss_health_bg.opacity = 0

        self.play_sound(
            self.boss_destroy_sound
        )

    # =====================================================
    # PLAYER HIT BY ENEMY
    # =====================================================

    def player_hit(self, enemy):

        if enemy not in self.enemies:
            return

        damage = enemy.damage

        self.remove_enemy(
            enemy
        )

        self.damage_player(
            damage
        )

    # =====================================================
    # DAMAGE PLAYER
    # =====================================================

    def damage_player(self, damage):

        if self.game_over:
            return

        self.health -= damage

        if self.health < 0:

            self.health = 0

        self.health_label.text = (
            "HEALTH: "
            + str(
                self.health
            )
        )

        # Update health bar

        percentage = (
            self.health /
            self.max_health
        )

        self.health_fill.size = (
            220 * percentage,
            22
        )

        self.play_sound(
            self.player_hit_sound
        )

        # Game Over

        if self.health <= 0:

            self.end_game()

    # =====================================================
    # REMOVE PLAYER BULLET
    # =====================================================

    def remove_player_bullet(
        self,
        bullet
    ):

        if bullet in self.bullets:

            self.bullets.remove(
                bullet
            )

        if bullet.parent:

            self.remove_widget(
                bullet
            )

    # =====================================================
    # REMOVE BOSS BULLET
    # =====================================================

    def remove_boss_bullet(
        self,
        bullet
    ):

        if bullet in self.boss_bullets:

            self.boss_bullets.remove(
                bullet
            )

        if bullet.parent:

            self.remove_widget(
                bullet
            )

    # =====================================================
    # REMOVE ENEMY
    # =====================================================

    def remove_enemy(
        self,
        enemy
    ):

        if enemy in self.enemies:

            self.enemies.remove(
                enemy
            )

        if enemy.parent:

            self.remove_widget(
                enemy
            )

    # =====================================================
    # GAME OVER
    # =====================================================

    def end_game(self):

        if self.game_over:
            return

        self.game_over = True

        self.game_over_label.text = (
            "GAME OVER\n\n"
            "SCORE: "
            + str(
                self.score
            )
        )

        self.play_sound(
            self.game_over_sound
        )


# =========================================================
# APP
# =========================================================

class SpaceShooterApp(App):

    def build(self):

        Window.clearcolor = (
            0,
            0,
            0,
            1
        )

        return Game()


# =========================================================
# RUN
# =========================================================

SpaceShooterApp().run()
