import os
from unittest import mock

from PIL import Image

from bot import EmberOnline


class TestEmberOnline:
    ember = EmberOnline()

    @mock.patch('PIL.ImageGrab.grab')
    def test_all(self, mocked_image_grab):
        mocked_image_grab.return_value = Image.open(
            os.path.dirname(os.path.realpath(__file__)) + '/fixtures/snap_1583267560.png')
        self.ember.grab_screen()

        health = self.ember.get_health_percentage()
        assert health == 95

        mana = self.ember.get_mana_percentage()
        assert mana == 100

        stamina = self.ember.get_action_percentage()
        assert stamina == 35

        self.ember.update_numbers_of_characters_in_current_tile()
        assert self.ember.player_count == 1
        assert self.ember.enemy_or_npc_count == 2

        self.ember.update_number_of_items_in_current_tile()
        assert self.ember.item_count == 4
