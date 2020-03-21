import os
import time

import pyautogui
import win32gui
import win32ui
from PIL import ImageGrab, Image
from dotenv import load_dotenv, find_dotenv

from core import CLASS_MONK, CLASS_CLERIC, get_health, get_stamina, get_mana, is_general_cooldown, \
    get_number_of_items_in_current_tile, get_number_of_characters_in_current_tile, CLASS_MAGEBLADE

load_dotenv(find_dotenv())

GAME_TOP_X = int(os.environ.get('GAME_TOP_X', 0))
GAME_TOP_Y = int(os.environ.get('GAME_TOP_Y', 0))
GAME_BOTTOM_X = int(os.environ.get('GAME_BOTTOM_X', 1920))
GAME_BOTTOM_Y = int(os.environ.get('GAME_BOTTOM_Y', 1080))
PICKUP_MODE_RELATIVE_X = 755
PICKUP_MODE_RELATIVE_Y = 675
FIRST_ITEM_X = 735
FIRST_ITEM_Y = 520
FIRST_ENEMY_OR_PLAYER_X = 764
FIRST_ENEMY_OR_PLAYER_Y = 58

CHARACTER_NAME = os.environ.get('CHARACTER_NAME')
CHARACTER_CLASS = os.environ.get('CHARACTER_CLASS')
STANCE = os.environ.get('STANCE', None)  # Monk only
HEALTH_THRESHOLD = int(os.environ.get('HEALTH_THRESHOLD', 15))
HEALED_THRESHOLD = int(os.environ.get('HEALED_THRESHOLD', 85))
MANA_THRESHOLD = int(os.environ.get('MANA_THRESHOLD', 15))
MANA_HEALED_THRESHOLD = int(os.environ.get('MANA_HEALED_THRESHOLD', 60))
MANA_POTION_THRESHOLD = int(os.environ.get('MANA_POTION_THRESHOLD', 40))

ANNOUNCER_PRESENT = bool(os.environ.get('ANNOUNCER_PRESENT', 0))
ARENA_DIRECTION = os.environ.get('ARENA_DIRECTION', 'n')


class State:
    def __init__(self):
        self.screenshot: Image = None
        self.window_handle: int = 0
        self.is_in_arena: bool = False
        self.current_health = 0
        self.current_mana = 0
        self.is_mana_pot_cooldown = False
        self.current_stamina = 0
        self.item_count = 0
        self.enemy_or_npc_count = 0
        self.player_count = 0


state = State()


def grab_screen() -> Image:
    box = (GAME_TOP_X, GAME_TOP_Y, GAME_BOTTOM_X, GAME_BOTTOM_Y)
    screenshot = ImageGrab.grab(box)
    # For debug purposes, 1 sample image is in test fixtures
    # screenshot.save(os.getcwd() + '\\snap_' + str(int(time.time())) + '.png', 'PNG')

    return screenshot


def enter_arena():
    print('Entering arena')
    if CHARACTER_CLASS == CLASS_CLERIC:
        pyautogui.typewrite('/c aegis self')
        pyautogui.press('enter')
        time.sleep(0.75)
    pyautogui.typewrite(ARENA_DIRECTION)
    pyautogui.press('enter')
    state.is_in_arena = True


def look_around():
    print('Looking around')
    pyautogui.typewrite('look')
    pyautogui.press('enter')


def pull_chain():
    print('Pulling chain')
    pyautogui.typewrite('/pull chain')
    pyautogui.press('enter')


def escape_arena():
    print('Escaping arena')
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
    state.is_in_arena = False


def pick_up_items():
    print('Picking up items')
    pyautogui.click(GAME_TOP_X + FIRST_ITEM_X, GAME_TOP_Y + FIRST_ITEM_Y, clicks=state.item_count, interval=0.5)


def launch_attacks():
    # TODO: Handle Announcer gracefully
    y_step = 36
    current_first_enemy_y = FIRST_ENEMY_OR_PLAYER_Y + state.player_count * y_step + (y_step if ANNOUNCER_PRESENT else 0)
    pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X, GAME_TOP_Y + current_first_enemy_y, clicks=5)
    pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X, GAME_TOP_Y + current_first_enemy_y - y_step, clicks=5)
    pyautogui.click(GAME_TOP_X + FIRST_ENEMY_OR_PLAYER_X, GAME_TOP_Y + current_first_enemy_y + y_step, clicks=5)


def try_long_heal_routine():
    print('Trying long heal')
    is_cooldown = is_general_cooldown(state.screenshot)
    if CHARACTER_CLASS == CLASS_MONK and not is_cooldown:
        pyautogui.hotkey('F1')
        time.sleep(9)
    elif CHARACTER_CLASS == CLASS_CLERIC and state.current_mana < MANA_THRESHOLD and not is_cooldown:
        pyautogui.hotkey('F1')
        time.sleep(16)
    if CHARACTER_CLASS == CLASS_CLERIC and state.current_health < HEALED_THRESHOLD:
        pyautogui.hotkey('F3')
        pyautogui.hotkey('F3')
        pyautogui.hotkey('F3')
        pyautogui.hotkey('F3')



def tick():
    print('Tick')
    look_around()
    state.screenshot = grab_screen()
    state.current_health = get_health(state.screenshot)
    state.current_stamina = get_stamina(state.screenshot)
    state.current_mana = get_mana(state.screenshot)
    state.player_count, state.enemy_or_npc_count = get_number_of_characters_in_current_tile(state.screenshot)
    if ANNOUNCER_PRESENT:
        state.enemy_or_npc_count -= 1
    if state.is_in_arena:
        if CHARACTER_CLASS == CLASS_MAGEBLADE and state.current_health < HEALTH_THRESHOLD and state.current_stamina > 0:
            # Just self-heal, should be enough ad infinitum
            pyautogui.hotkey('F3')
            pyautogui.hotkey('F3')
            pyautogui.hotkey('F3')
            pyautogui.hotkey('F3')
            pyautogui.hotkey('F3')
        if (state.current_health < HEALTH_THRESHOLD or state.current_mana < MANA_THRESHOLD) \
                and state.current_stamina > 0:
            escape_arena()
        elif state.current_stamina > 0:
            if state.enemy_or_npc_count > 0:
                launch_attacks()
            else:
                pull_chain()
        else:
            if CHARACTER_CLASS == CLASS_CLERIC and state.current_mana < MANA_POTION_THRESHOLD:
                pyautogui.hotkey('F2')
            state.item_count = get_number_of_items_in_current_tile(state.screenshot)
            if state.item_count > 0:
                pick_up_items()
    else:
        if state.current_health < HEALTH_THRESHOLD or state.current_mana < MANA_THRESHOLD:
            print('here')
            try_long_heal_routine()
        elif state.current_stamina > 0:
            enter_arena()


def main():
    state.window_handle = win32ui.FindWindow(None, f'Ember Online - {CHARACTER_NAME}').GetSafeHwnd()
    win32gui.SetForegroundWindow(state.window_handle)
    time.sleep(0.5)
    if CHARACTER_CLASS == CLASS_MONK:
        print('Switching to simple attacks')
        pyautogui.hotkey('ctrl', '2', interval=0.005)
        if STANCE:
            print('Activating stance')
            pyautogui.typewrite('/stance ' + STANCE)
            pyautogui.press('enter')
    elif CHARACTER_CLASS == CLASS_CLERIC:
        print('Switching to red spell')
        pyautogui.hotkey('ctrl', '3', interval=0.005)
    # Switch to item pickup mode
    print('Switching to pickup mode')
    pyautogui.click(GAME_TOP_X + PICKUP_MODE_RELATIVE_X, GAME_TOP_Y + PICKUP_MODE_RELATIVE_Y)
    while True:
        tick()
        time.sleep(1)


if __name__ == '__main__':
    main()
