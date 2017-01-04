import time
import win32gui
import win32ui

import pyautogui
from PIL import ImageGrab

CHARACTER_NAME = 'Lorkhan'
GAME_TOP_X = 559
GAME_TOP_Y = 246
GAME_BOTTOM_X = 1360
GAME_BOTTOM_Y = 906
HEALTH_BAR_START_X = 46
HEALTH_BAR_END_X = 200
HEALTH_BAR_PERCENTAGE_STEP = 5
HEALTH_BAR_CHECK_STEP = int((HEALTH_BAR_END_X - HEALTH_BAR_START_X) / (100 / HEALTH_BAR_PERCENTAGE_STEP))
HEALTH_BAR_CENTER_Y = 299
HEALTH_BAR_FULL_COLOR = (85, 0, 0)
ACTION_BAR_START_X = 447
ACTION_BAR_END_X = 600
ACTION_BAR_PERCENTAGE_STEP = 5
ACTION_BAR_CHECK_STEP = int((ACTION_BAR_END_X - ACTION_BAR_START_X) / (100 / ACTION_BAR_PERCENTAGE_STEP))
ACTION_BAR_FULL_COLOR = (0, 85, 0)
LOOK_BUTTON_X = 555
LOOK_BUTTON_Y = 347


class EmberOnline:
    def __init__(self):
        self.screen_grab = None
        self.window_handle = win32ui.FindWindow(None, u"Ember Online - %s" % CHARACTER_NAME).GetSafeHwnd()
        win32gui.SetForegroundWindow(self.window_handle)

    def grab_screen(self):
        box = (GAME_TOP_X, GAME_TOP_Y, GAME_BOTTOM_X, GAME_BOTTOM_Y)
        self.screen_grab = ImageGrab.grab(box)

    def get_health_percentage(self):
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

    def look_around(self):
        pyautogui.click(GAME_TOP_X + LOOK_BUTTON_X, GAME_TOP_Y + LOOK_BUTTON_Y)

    def start(self):
        self.grab_screen()
        self.look_around()
        # print self.get_health_percentage()
        # print self.get_action_percentage()


def main():
    ember = EmberOnline()
    time.sleep(3)
    ember.start()


if __name__ == '__main__':
    main()
