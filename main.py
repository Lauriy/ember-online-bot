import time
import win32gui
import win32ui

import SendKeys
import pyautogui
from PIL import ImageGrab

CHARACTER_NAME = 'Lorkhan'

# Absolute coordinates on my 1920x1200 screen
GAME_TOP_X = 559
GAME_TOP_Y = 246
GAME_BOTTOM_X = 1360
GAME_BOTTOM_Y = 906

# Relative coordinates
HEALTH_BAR_START_X = 46
HEALTH_BAR_END_X = 200
HEALTH_BAR_CENTER_Y = 299

ACTION_BAR_START_X = 447
ACTION_BAR_END_X = 600

FIRST_ENEMY_OR_PLAYER_X = 665
# Possible announcer 94 / 130
FIRST_ENEMY_OR_PLAYER_Y = 130

MAX_ENEMY_PLAYER_SCAN_Y = 415

# Pixel steps for loops
HEALTH_BAR_PERCENTAGE_STEP = 5
HEALTH_BAR_CHECK_STEP = int((HEALTH_BAR_END_X - HEALTH_BAR_START_X) / (100 / HEALTH_BAR_PERCENTAGE_STEP))
ACTION_BAR_PERCENTAGE_STEP = 5
ACTION_BAR_CHECK_STEP = int((ACTION_BAR_END_X - ACTION_BAR_START_X) / (100 / ACTION_BAR_PERCENTAGE_STEP))
ENEMY_OR_PLAYER_STEP = 36

# Colours
HEALTH_BAR_FULL_COLOR = (85, 0, 0)
ACTION_BAR_FULL_COLOR = (0, 85, 0)

# Thresholds
MIN_HEALTH_PERCENTAGE = 20
HEALED_PERCENTAGE = 90


# TODO: Pick up items
# TODO: Handle crashes?
class EmberOnline:
    def __init__(self):
        self.screen_grab = None
        self.window_handle = win32ui.FindWindow(None, u"Ember Online - %s" % CHARACTER_NAME).GetSafeHwnd()
        self.is_in_arena = False
        self.player_count = 0
        self.enemy_count = 0
        self.npc_count = 0
        win32gui.SetForegroundWindow(self.window_handle)
        time.sleep(0.5)
        # Switch mouse to attack mode
        SendKeys.SendKeys('^2{ENTER}', pause=0.005)

    def grab_screen(self):
        box = (GAME_TOP_X, GAME_TOP_Y, GAME_BOTTOM_X, GAME_BOTTOM_Y)
        self.screen_grab = ImageGrab.grab(box)
        # self.screen_grab.save(os.getcwd() + '\\snap__' + str(int(time.time())) + '.png', 'PNG')

    def get_health_percentage(self):
        # TODO: Better percentage reporting (currently says 10 at 20)
        current_x = HEALTH_BAR_END_X
        percentage = 100
        while current_x - HEALTH_BAR_CHECK_STEP > HEALTH_BAR_START_X:
            current_pixel = self.screen_grab.getpixel((current_x, HEALTH_BAR_CENTER_Y))
            if current_pixel == HEALTH_BAR_FULL_COLOR:
                return percentage

            percentage -= HEALTH_BAR_PERCENTAGE_STEP
            current_x -= HEALTH_BAR_CHECK_STEP

        return 0

    def get_action_percentage(self):
        current_x = ACTION_BAR_END_X
        percentage = 100
        while current_x - ACTION_BAR_CHECK_STEP > ACTION_BAR_START_X:
            current_pixel = self.screen_grab.getpixel((current_x, HEALTH_BAR_CENTER_Y))
            if current_pixel == ACTION_BAR_FULL_COLOR:
                return percentage

            percentage -= ACTION_BAR_PERCENTAGE_STEP
            current_x -= ACTION_BAR_CHECK_STEP

        return 0

    def update_numbers_of_characters_in_current_tile(self):
        # TODO: Multi pixel enemy scan with better tolerances
        current_y = FIRST_ENEMY_OR_PLAYER_Y
        self.look_around()
        self.player_count, self.enemy_count, self.npc_count = 0, 0, 0
        while current_y < MAX_ENEMY_PLAYER_SCAN_Y:
            current_pixel = self.screen_grab.getpixel((FIRST_ENEMY_OR_PLAYER_X, current_y))
            # print current_pixel
            # ~(204, 134, 175)
            if current_pixel[0] > 190 and current_pixel[1] > 130 and current_pixel[2] > 160:
                self.npc_count += 1
            # ~(0, 240, 53)
            elif current_pixel[0] > 240 and current_pixel[1] > 230 and current_pixel[2] > 50:
                self.player_count += 1
            # ~(255, 255, 0)
            elif current_pixel[0] > 240 and current_pixel[1] > 199 and current_pixel[2] < 100:
                self.enemy_count += 1
            current_y += ENEMY_OR_PLAYER_STEP

    def look_around(self):
        SendKeys.SendKeys('look{ENTER}', pause=0.005)
        time.sleep(0.5)

    def meditate(self):
        # /meditate
        SendKeys.SendKeys('+?meditate{ENTER}', pause=0.005)

    def escape_arena(self):
        SendKeys.SendKeys('n{ENTER}', pause=0.005)
        self.is_in_arena = False

    def back_to_arena(self):
        SendKeys.SendKeys('s{ENTER}', pause=0.005)
        self.is_in_arena = True

    def pull_chain(self):
        # For new enemy
        SendKeys.SendKeys('+?pull{SPACE}chain{ENTER}', pause=0.005)

    def attack_first_enemy(self):
        # TODO: Handle Announcer gracefully
        current_first_enemy_y = FIRST_ENEMY_OR_PLAYER_Y + self.player_count * ENEMY_OR_PLAYER_STEP + self.npc_count * ENEMY_OR_PLAYER_STEP
        # Ugly Announcer workaround for now
        for i in range(0, 5):
            pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X,
                            GAME_TOP_Y + current_first_enemy_y - ENEMY_OR_PLAYER_STEP)
            time.sleep(0.1)
        for i in range(0, 5):
            pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X, GAME_TOP_Y + current_first_enemy_y)
            time.sleep(0.1)
        for i in range(0, 5):
            pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X,
                            GAME_TOP_Y + current_first_enemy_y + ENEMY_OR_PLAYER_STEP)
            time.sleep(0.1)

    def tick(self):
        print 'Tick...'
        self.grab_screen()
        current_health_percentage = self.get_health_percentage()
        current_action_percentage = self.get_action_percentage()
        print 'Health at %i, action at %i' % (current_health_percentage, current_action_percentage)
        if current_health_percentage <= MIN_HEALTH_PERCENTAGE and current_action_percentage > 0 and self.is_in_arena:
            print 'Low on health, escaping arena'
            self.escape_arena()
        elif current_health_percentage < HEALED_PERCENTAGE and not self.is_in_arena:
            # TODO: Correct meditation seconds, stop meditating if healed early
            print 'Healing...'
            time.sleep(9)
            self.meditate()
            time.sleep(15)
        elif current_health_percentage >= HEALED_PERCENTAGE and not self.is_in_arena:
            print 'Healed and not in arena, heading back'
            self.back_to_arena()
        elif current_health_percentage > MIN_HEALTH_PERCENTAGE and self.is_in_arena and current_action_percentage > 0:
            print 'Scanning for enemies...'
            self.update_numbers_of_characters_in_current_tile()
            print 'Found %i enemies, %i players, %i npcs' % (self.enemy_count, self.player_count, self.npc_count)
            if self.enemy_count == 0:
                print 'Pulling chain...'
                self.pull_chain()
            else:
                print 'At least one enemy present, attacking'
                self.attack_first_enemy()

    def start(self):
        while True:
            self.tick()
            time.sleep(1)


def main():
    ember = EmberOnline()
    ember.start()


if __name__ == '__main__':
    main()
