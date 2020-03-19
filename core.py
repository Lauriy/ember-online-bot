from typing import Tuple

from PIL import Image

CLASS_MONK = 'monk'
CLASS_CLERIC = 'cleric'
CLASS_MAGEBLADE = 'mageblade'


def get_number_of_items_in_current_tile(screenshot: Image, first_item_x: int = 735, first_item_y: int = 520,
                                        max_item_y: int = 630, item_step_y: int = 30) -> int:
    item_area_empty_colours = [
        (25, 25, 25),
        (26, 26, 26),
        (27, 27, 27),
        (28, 28, 28),
    ]
    current_y = first_item_y
    item_count = 0
    while current_y < max_item_y:
        current_pixel = screenshot.getpixel((first_item_x, current_y))
        if len(current_pixel) == 4:
            # Delete alpha channel
            current_pixel = current_pixel[:3]
        if current_pixel not in item_area_empty_colours:
            item_count += 1
        current_y += item_step_y

    return item_count


def get_number_of_characters_in_current_tile(screenshot: Image, first_character_x: int = 764,
                                             first_character_y: int = 58, max_character_y: int = 415,
                                             enemy_or_npc_step_y: int = 36) -> Tuple[int, int]:
    current_y = first_character_y
    player_count, enemy_or_npc_count = 0, 0
    player_color = (0, 255, 0)
    enemy_or_npc_color = (255, 255, 0)
    scannable_stripe_width = 40
    while current_y < max_character_y:
        for i in range(0, scannable_stripe_width):
            current_pixel = screenshot.getpixel(((first_character_x + 1 * i), current_y))
            if len(current_pixel) == 4:
                current_pixel = current_pixel[:3]
            if current_pixel == player_color:
                player_count += 1
                break
            elif current_pixel == enemy_or_npc_color:
                enemy_or_npc_count += 1
                break
        current_y += enemy_or_npc_step_y

    return player_count, enemy_or_npc_count


def _get_resource_percentage(screenshot: Image, bar_start_x: int, bar_end_x: int, bar_center_y: int,
                             bar_full_colour: Tuple[int, int, int]) -> int:
    bar_full_width = bar_end_x - bar_start_x
    check_step = 1
    current_x = bar_end_x

    while current_x - check_step > bar_start_x:
        current_pixel = screenshot.getpixel((current_x, bar_center_y))
        if len(current_pixel) == 4:
            current_pixel = current_pixel[:3]
        if current_pixel == bar_full_colour:
            return int((current_x - bar_start_x) / bar_full_width * 100)

        current_x -= check_step

    return 0


def get_health(screenshot: Image, bar_start_x: int = 39, bar_end_x: int = 235, bar_center_y: int = 305,
               bar_full_colour: Tuple[int, int, int] = (175, 0, 0)):
    return _get_resource_percentage(screenshot, bar_start_x, bar_end_x, bar_center_y, bar_full_colour)


def get_mana(screenshot: Image, bar_start_x: int = 273, bar_end_x: int = 469, bar_center_y: int = 305,
             bar_full_colour: Tuple[int, int, int] = (0, 111, 175)):
    return _get_resource_percentage(screenshot, bar_start_x, bar_end_x, bar_center_y, bar_full_colour)


def get_stamina(screenshot: Image, bar_start_x: int = 507, bar_end_x: int = 703, bar_center_y: int = 305,
                bar_full_colour: Tuple[int, int, int] = (0, 175, 0)):
    return _get_resource_percentage(screenshot, bar_start_x, bar_end_x, bar_center_y, bar_full_colour)


def get_focus(screenshot: Image, bar_start_x: int = 273, bar_end_x: int = 469, bar_center_y: int = 305,
              bar_full_colour: Tuple[int, int, int] = (175, 175, 0)):
    return _get_resource_percentage(screenshot, bar_start_x, bar_end_x, bar_center_y, bar_full_colour)


def is_health_potion_cooldown(screenshot: Image, check_pixel_x: int = 830, check_pixel_y: int = 695,
                              timer_color: Tuple[int, int, int] = (225, 0, 0)) -> bool:
    pixel = screenshot.getpixel((check_pixel_x, check_pixel_y))
    if len(pixel) == 4:
        pixel = pixel[:3]

    return pixel == timer_color


def is_mana_potion_cooldown(screenshot: Image, check_pixel_x: int = 854, check_pixel_y: int = 695,
                            timer_color: Tuple[int, int, int] = (0, 125, 225)) -> bool:
    pixel = screenshot.getpixel((check_pixel_x, check_pixel_y))
    if len(pixel) == 4:
        pixel = pixel[:3]

    return pixel == timer_color


def is_general_cooldown(screenshot: Image, check_pixel_x: int = 878, check_pixel_y: int = 695,
                        timer_color: Tuple[int, int, int] = (155, 0, 225)) -> bool:
    pixel = screenshot.getpixel((check_pixel_x, check_pixel_y))
    if len(pixel) == 4:
        pixel = pixel[:3]

    return pixel == timer_color
