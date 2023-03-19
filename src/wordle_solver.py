from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path
from selenium.webdriver.common.by import By

from time import sleep

from .constants import Constants
from .domain import TileState, Tile, GameState
from .word_master import WordMaster

from typing import List


class WordleSolver:
    def __init__(self) -> None:
        self.word_master = WordMaster(Constants.WORDS_FILEPATH)

        service_object = Service(binary_path)
        self.driver = webdriver.Chrome(service=service_object)
        self.driver.get(Constants.URL)

        close_btn = self.driver.find_element(By.CLASS_NAME, Constants.CLOSE_BUTTON_ELEMENT)
        close_btn.click()

        sleep(Constants.INITIALIZE_SLEEP_TIME_S)

        self.keyboard = dict()
        for key in self.driver.find_elements(By.CLASS_NAME, Constants.KEYBOARD_ELEMENT):
            key_value = key.get_attribute("data-key")
            if key_value == Constants.ENTER_UNICODE:
                key_value = Constants.ENTER_REPLACMENT
            self.keyboard[key_value] = key

    def find_tiles(self) -> List[List[Tile]]:
        rows = [list() for _ in range(6)]
        for i, tile in enumerate(self.driver.find_elements(By.CLASS_NAME, Constants.TILE_ELEMENT)):
            value = tile.get_attribute("aria-label").split(" ")[0]
            state = TileState.get(tile.get_attribute("data-state"))
            rows[i // 5].append(Tile(state, value))
        return rows

    def guess(self, word: str) -> None:
        assert len(word) == 5
        for ch in word:
            self.keyboard[ch].click()
            sleep(Constants.PER_ENTRY_SLEEP_TIME_S)
        self.keyboard[Constants.ENTER_REPLACMENT].click()
        sleep(Constants.GUESS_SLEEP_TIME_S)
    
    def loop(self) -> None:
        while True:
            rows = self.find_tiles()
            state = GameState(rows)
            self.word_master.update_with_state(state)
            self.guess(self.word_master.get())
