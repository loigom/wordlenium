from dataclasses import dataclass
from enum import Enum, auto
from time import sleep
from typing import List
from random import choice

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path
from selenium.webdriver.common.by import By


class TileState(Enum):
    TBD = auto()
    GREY = auto()
    GREEN = auto()
    YELLOW = auto()

    def get(s: str) -> "TileState":
        _map = {
            "present": TileState.YELLOW,
            "correct": TileState.GREEN,
            "absent": TileState.GREY
        }
        if s in _map:
            return _map[s]
        return TileState.TBD


@dataclass
class Element:
    tag_name: str
    class_name: str


@dataclass
class Tile:
    state: TileState
    value: str


def is_match(word: str, max_len: dict, correct: dict, wrong_pos: dict) -> bool:
    for k, v in correct.items():
        if word[k] != v:
            return False
    for k, v in max_len.items():
        if word.count(k) > v:
            return False
    for k, v in wrong_pos.items():
        if v not in word or word[k] == v:
            return False
    return True


def get_user_input(possible_solutions: List[str]) -> str:
    out_print = ["0: random"]
    for i, word in enumerate(possible_solutions, 1):
        out_print.append(f"{i}: {word}")
    out_print = "\n".join(out_print)
    print(out_print)

    user_choice = int(input("Select: "))
    if user_choice == 0:
        return choice(possible_solutions)
    return possible_solutions[user_choice - 1]


TILE_ELEMENT = Element("div", "Tile-module_tile__UWEHN")
CLOSE_BUTTON_ELEMENT = Element("button", "Modal-module_closeIcon__TcEKb")
KEYBOARD_ELEMENT = Element("button", "Key-module_key__kchQI")


class WordleSolver:
    INITIALIZE_SLEEP_TIME_S = 2
    GUESS_SLEEP_TIME_S = 3.5
    PER_ENTRY_SLEEP_TIME_S = 0.5
    FIRST_GUESS = "atone"

    def __init__(self) -> None:
        service_object = Service(binary_path)
        self.driver = webdriver.Chrome(service=service_object)
        self.driver.get("https://www.nytimes.com/games/wordle/index.html")

        close_btn = self.driver.find_element(By.CLASS_NAME, CLOSE_BUTTON_ELEMENT.class_name)
        close_btn.click()

        sleep(self.INITIALIZE_SLEEP_TIME_S)

    def get_keyboard(self) -> dict:
        keyboard = dict()
        for key in self.driver.find_elements(By.CLASS_NAME, KEYBOARD_ELEMENT.class_name):
            key_value = key.get_attribute("data-key")
            if key_value == "↵":
                key_value = "ENTER"
            keyboard[key_value] = key
        return keyboard

    def find_tiles(self) -> List[List[Tile]]:
        rows = [list() for _ in range(6)]
        for i, tile in enumerate(self.driver.find_elements(By.CLASS_NAME, TILE_ELEMENT.class_name)):
            value = tile.get_attribute("aria-label").split(" ")[0]
            state = TileState.get(tile.get_attribute("data-state"))
            rows[i // 5].append(Tile(state, value))
        return rows
    
    def parse_tiles(self, rows: List[List[Tile]]) -> List[str]:
        with open("words.txt") as fptr:
            all_words = fptr.read().strip().split("\n")
        
        self.rows_done = 0
        looping = True
        letters_count = dict()
        max_len = dict()
        correct = dict()
        wrong_pos = dict()

        print("rows", rows)
        for row in rows:
            if looping:
                for i, tile in enumerate(row):
                    print(f"ON TILE {tile.value} {tile.state}")
                    if tile.state is TileState.GREEN:
                        correct[i] = tile.value
                    elif tile.state == TileState.YELLOW:
                        wrong_pos[i] = tile.value
                    elif tile.state == TileState.GREY:
                        if tile.value in letters_count:
                            max_len[tile.value] = letters_count[tile.value]
                        else:
                            max_len[tile.value] = 0
                    else:
                        print("BREAKING 1")
                        looping = False
                        break
                    if tile.state != TileState.GREY:
                        if tile.value in letters_count:
                            letters_count[tile.value] += 1
                        else:
                            letters_count[tile.value] = 1
                self.rows_done += looping
            else:
                print("BREAKNG 2")
                break

        possible_solutions = list()

        print(max_len, correct, wrong_pos)

        for word in all_words:
            if is_match(word, max_len, correct, wrong_pos):
                possible_solutions.append(word)
        
        return possible_solutions

    
    def guess(self, word: str) -> None:
        assert len(word) == 5
        for ch in word:
            self.keyboard[ch].click()
            sleep(self.PER_ENTRY_SLEEP_TIME_S)
        self.keyboard["ENTER"].click()
        sleep(self.GUESS_SLEEP_TIME_S)
    
    def loop(self) -> None:
        while True:
            rows = self.find_tiles()
            possible_solutions = self.parse_tiles(rows)
            assert len(possible_solutions) > 0
            print(self.rows_done)
            self.keyboard = self.get_keyboard()
            if self.rows_done == 0:
                self.guess(self.FIRST_GUESS)
            else:
                #self.guess(get_user_input(possible_solutions))
                self.guess(choice(possible_solutions))


WordleSolver().loop()
