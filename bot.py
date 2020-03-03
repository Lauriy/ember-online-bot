import os
import time

import pyautogui
import win32gui
import win32ui
from PIL import ImageGrab
from dotenv import find_dotenv
from dotenv import load_dotenv

load_dotenv(find_dotenv())

CHARACTER_NAME = os.environ.get('CHARACTER_NAME')
CHARACTER_CLASS = os.environ.get('CHARACTER_CLASS')
STANCE = os.environ.get('STANCE')  # Monk only

CLASS_MONK = 'monk'
CLASS_CLERIC = 'cleric'

GAME_TOP_X = int(os.environ.get('GAME_TOP_X'))
GAME_TOP_Y = int(os.environ.get('GAME_TOP_Y'))
GAME_BOTTOM_X = int(os.environ.get('GAME_BOTTOM_X'))
GAME_BOTTOM_Y = int(os.environ.get('GAME_BOTTOM_Y'))
ANNOUNCER_PRESENT = int(os.environ.get('ANNOUNCER_PRESENT'))

HEALTH_BAR_FULL_COLOR = (175, 0, 0)
ACTION_BAR_FULL_COLOR = (0, 175, 0)
MANA_BAR_FULL_COLOR = (0, 111, 175)
EMPTY_ITEM_AREA_COLORS = [
    (25, 25, 25),
    (26, 26, 26),
    (27, 27, 27),
    (28, 28, 28),
]

HEALTH_BAR_START_X = 39  # Relative coordinates
HEALTH_BAR_END_X = 235
HEALTH_BAR_CENTER_Y = 305  # Could be 304
HEALTH_BAR_PERCENTAGE_STEP = 5  # Pixel steps for loops
HEALTH_BAR_CHECK_STEP = int((HEALTH_BAR_END_X - HEALTH_BAR_START_X) / (100 / HEALTH_BAR_PERCENTAGE_STEP))

MANA_BAR_START_X = 273
MANA_BAR_END_X = 469
MANA_BAR_CENTER_Y = HEALTH_BAR_CENTER_Y
MANA_BAR_PERCENTAGE_STEP = HEALTH_BAR_PERCENTAGE_STEP
MANA_BAR_CHECK_STEP = int((MANA_BAR_END_X - MANA_BAR_START_X) / (100 / MANA_BAR_PERCENTAGE_STEP))

ACTION_BAR_START_X = 507
ACTION_BAR_END_X = 703
ACTION_BAR_CENTER_Y = HEALTH_BAR_CENTER_Y
ACTION_BAR_PERCENTAGE_STEP = HEALTH_BAR_PERCENTAGE_STEP
ACTION_BAR_CHECK_STEP = int((ACTION_BAR_END_X - ACTION_BAR_START_X) / (100 / ACTION_BAR_PERCENTAGE_STEP))

FIRST_ENEMY_OR_PLAYER_X = 764
# Announcer at 92, next slot 128
# FIRST_ENEMY_OR_PLAYER_Y = 128
FIRST_ENEMY_OR_PLAYER_Y = 58
MAX_ENEMY_PLAYER_SCAN_Y = 415
ENEMY_OR_PLAYER_STEP = 36

PICKUP_MODE_X = 755
PICKUP_MODE_Y = 675
FIRST_ITEM_X = 735
FIRST_ITEM_Y = 520
ITEM_STEP = 30
MAX_ITEM_SCAN_Y = 630

# Thresholds
MIN_HEALTH_PERCENTAGE = 20
MIN_MANA_PERCENTAGE = 10
MANA_POT_PERCENTAGE = 50
HEALED_PERCENTAGE = 80
MANA_HEALED_PERCENTAGE = 80

ARENA_DIRECTION = os.environ.get("ARENA_DIRECTION")


class EmberOnline:
    def __init__(self):
        self.screen_grab = None
        self.window_handle = None
        self.is_in_arena = False
        self.player_count = 0
        self.enemy_or_npc_count = 0
        self.item_count = 0

    def do_init_logic(self):
        self.window_handle = win32ui.FindWindow(None, u"Ember Online - %s" % CHARACTER_NAME).GetSafeHwnd()
        win32gui.SetForegroundWindow(self.window_handle)
        time.sleep(0.5)
        if CHARACTER_CLASS == CLASS_MONK:
            # Switch mouse to attack mode
            pyautogui.hotkey('ctrl', '2', interval=0.005)
            pyautogui.typewrite('/stance ' + STANCE)
            pyautogui.press('enter')
        elif CHARACTER_CLASS == CLASS_CLERIC:
            # Attack spell
            pyautogui.hotkey('ctrl', '3', interval=0.005)
            # TODO: Use Aegis every x
            pyautogui.typewrite('/c aegis self')
            pyautogui.press('enter')
            time.sleep(0.5)
        # Switch to pickup mode
        pyautogui.click(GAME_TOP_X + PICKUP_MODE_X, GAME_TOP_Y + PICKUP_MODE_Y)

    def grab_screen(self):
        box = (GAME_TOP_X, GAME_TOP_Y, GAME_BOTTOM_X, GAME_BOTTOM_Y)
        self.screen_grab = ImageGrab.grab(box)
        # self.screen_grab.save(os.getcwd() + '\\snap_' + str(int(time.time())) + '.png', 'PNG')

    def _get_resource_percentage(self, kind='HEALTH'):
        # TODO: Better percentage reporting (currently says 35 at 50% stamina...)
        current_x = globals().get(kind + '_BAR_END_X')
        start_x = globals().get(kind + '_BAR_START_X')
        check_step = globals().get(kind + '_BAR_CHECK_STEP')
        percentage_step = globals().get(kind + '_BAR_PERCENTAGE_STEP')
        center_y = globals().get(kind + '_BAR_CENTER_Y')
        full_color = globals().get(kind + '_BAR_FULL_COLOR')
        percentage = 100

        while current_x - check_step > start_x:
            current_pixel = self.screen_grab.getpixel((current_x, center_y))
            if len(current_pixel) == 4:
                # Delete alpha channel
                current_pixel = current_pixel[:3]
            if current_pixel == full_color:
                return percentage

            percentage -= percentage_step
            current_x -= check_step

        return 0

    def get_health_percentage(self):
        return self._get_resource_percentage()

    def get_action_percentage(self):
        return self._get_resource_percentage('ACTION')

    def get_mana_percentage(self):
        return self._get_resource_percentage('MANA')

    def update_numbers_of_characters_in_current_tile(self):
        current_y = FIRST_ENEMY_OR_PLAYER_Y
        self.look_around()
        self.player_count, self.enemy_or_npc_count = 0, 0
        while current_y < MAX_ENEMY_PLAYER_SCAN_Y:
            for i in range(0, 40):
                current_pixel = self.screen_grab.getpixel(((FIRST_ENEMY_OR_PLAYER_X + 1 * i), current_y))
                # ~(0, 255, 0)
                if current_pixel[0] == 0 and current_pixel[1] == 255:
                    # Distinctive player green
                    self.player_count += 1
                    break
                # ~(255, 255, 0)
                elif current_pixel[0] == 255 and current_pixel[1] == 255:
                    # Enemy/announcer yellow
                    self.enemy_or_npc_count += 1
                    break
            current_y += ENEMY_OR_PLAYER_STEP

    def update_number_of_items_in_current_tile(self):
        current_y = FIRST_ITEM_Y
        self.look_around()
        self.item_count = 0
        while current_y < MAX_ITEM_SCAN_Y:
            current_pixel = self.screen_grab.getpixel((FIRST_ITEM_X, current_y))
            if len(current_pixel) == 4:
                # Delete alpha channel
                current_pixel = current_pixel[:3]
            if current_pixel not in EMPTY_ITEM_AREA_COLORS:
                # Distinctive empty item area gray
                self.item_count += 1
            current_y += ITEM_STEP

    def look_around(self):
        pyautogui.typewrite('look')
        pyautogui.press('enter')

    def meditate(self):
        pyautogui.typewrite('/meditate')
        pyautogui.press('enter')

    def do_cleric_heal_routine(self):
        for i in range(0, 4):
            pyautogui.hotkey('F5', interval=0.005)

    def escape_arena(self):
        if ARENA_DIRECTION == 'n':
            escape_direction = 's'
        elif ARENA_DIRECTION == 'e':
            escape_direction = 'w'
        elif ARENA_DIRECTION == 'w':
            escape_direction = 'e'
        else:
            escape_direction = 'n'
        pyautogui.typewrite(escape_direction)
        pyautogui.press('enter')
        self.is_in_arena = False

    def back_to_arena(self):
        pyautogui.typewrite(str(ARENA_DIRECTION))
        pyautogui.press('enter')
        self.is_in_arena = True

    def pull_chain(self):
        # For new enemy
        pyautogui.typewrite('/pull chain')
        pyautogui.press('enter')

    def attack_first_enemy(self):
        # TODO: Handle Announcer gracefully
        current_first_enemy_y = FIRST_ENEMY_OR_PLAYER_Y + self.player_count * ENEMY_OR_PLAYER_STEP + (
            ENEMY_OR_PLAYER_STEP if ANNOUNCER_PRESENT else 0)
        # Ugly Announcer workaround for now
        for i in range(0, 5):
            pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X, GAME_TOP_Y + current_first_enemy_y)
            time.sleep(0.1)
        for i in range(0, 5):
            pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X,
                            GAME_TOP_Y + current_first_enemy_y - ENEMY_OR_PLAYER_STEP)
            time.sleep(0.1)
        for i in range(0, 5):
            pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X,
                            GAME_TOP_Y + current_first_enemy_y + ENEMY_OR_PLAYER_STEP)
            time.sleep(0.1)

    def pick_up_items(self):
        for i in range(0, self.item_count):
            pyautogui.click(GAME_TOP_X + FIRST_ITEM_X, GAME_TOP_Y + FIRST_ITEM_Y + ITEM_STEP * i)

    def drink_mana_potion(self):
        pyautogui.hotkey('F2', interval=0.005)

    def tick(self):
        print('Tick...')
        self.grab_screen()
        current_health_percentage = self.get_health_percentage()
        current_mana_percentage = self.get_mana_percentage()
        current_action_percentage = self.get_action_percentage()
        print('Health at %i, mana at %i, action at %i' % (
            current_health_percentage, current_mana_percentage, current_action_percentage))
        if current_mana_percentage < MANA_POT_PERCENTAGE:
            self.drink_mana_potion()
        if current_health_percentage <= MIN_HEALTH_PERCENTAGE and current_action_percentage > 0 and self.is_in_arena:
            print('Low on health, escaping arena')
            self.escape_arena()
        elif current_mana_percentage <= MIN_MANA_PERCENTAGE and current_action_percentage > 0 and self.is_in_arena:
            print('Low on mana, escaping arena')
            self.escape_arena()
        elif current_mana_percentage <= MIN_MANA_PERCENTAGE and not self.is_in_arena \
                and CHARACTER_CLASS == CLASS_CLERIC:
            print('Drinking...')
            time.sleep(5)
            pyautogui.hotkey('F1', interval=0.05)
            time.sleep(8)
        elif current_health_percentage < HEALED_PERCENTAGE and not self.is_in_arena:
            if CHARACTER_CLASS == CLASS_MONK:
                print('Meditating...')
                time.sleep(9)
                self.meditate()
                checks = 0
                while current_health_percentage < HEALED_PERCENTAGE and checks < 5:
                    time.sleep(3)
                    checks += 1
                    self.grab_screen()
                    current_health_percentage = self.get_health_percentage()
            elif CHARACTER_CLASS == CLASS_CLERIC:
                print('Casting heals...')
                time.sleep(5)
                self.do_cleric_heal_routine()
        elif current_health_percentage >= HEALED_PERCENTAGE and not self.is_in_arena:
            print('Healed and not in arena, heading back')
            self.back_to_arena()
        elif current_health_percentage > MIN_HEALTH_PERCENTAGE and self.is_in_arena and current_action_percentage > 0:
            print('Scanning for items...')
            self.update_number_of_items_in_current_tile()
            print('Found %i items' % self.item_count)
            if self.item_count > 0:
                self.pick_up_items()
            print('Scanning for enemies...')
            self.update_numbers_of_characters_in_current_tile()
            print('Found %i enemies or NPCs, %i players' % (self.enemy_or_npc_count, self.player_count))
            if (ANNOUNCER_PRESENT and self.enemy_or_npc_count == 1) or (
                    not ANNOUNCER_PRESENT and self.enemy_or_npc_count == 0):
                print('Pulling chain...')
                self.pull_chain()
            else:
                print('At least one enemy present, attacking')
                self.attack_first_enemy()

    def start(self):
        while True:
            self.tick()
            time.sleep(1)
