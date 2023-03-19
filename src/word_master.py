from .domain import GameState
from typing import Dict


def is_match(word: str, state: GameState) -> bool:
    for pos, ch in state.correct.items():
        if word[pos] != ch:
            return False
    for pos, ch_set in state.wrong_pos.items():
        for ch in ch_set:
            if ch not in word or word[pos] == ch:
                return False
    for ch, _max in state.max_len.items():
        if word.count(ch) > _max:
            return False
    return True


class WordMaster:
    def __init__(self, path_to_words: str) -> None:
        self.ranked_words_cache: Dict[str, int] = dict()

        with open(path_to_words) as fptr:
            self.words = fptr.read().splitlines()
        self.words = self.words
        self.ch_rankings: Dict[str, int] = dict()
        for word in self.words:
            for ch in word:
                if ch in self.ch_rankings:
                    self.ch_rankings[ch] += 1
                else:
                    self.ch_rankings[ch] = 1
    
    def update_with_state(self, state: GameState) -> None:
        filtered_and_ranked: Dict[str, int] = dict()
        for word in self.words:
            if is_match(word, state):
                filtered_and_ranked[word] = self.rank_word(word)
        self.words = sorted(filtered_and_ranked, key=lambda word: filtered_and_ranked[word], reverse=True)

    def get(self) -> str:
        assert len(self.words) > 0
        selected = self.words[0]
        assert len(selected) == 5
        return selected

    def rank_word(self, word: str) -> int:
        if word in self.ranked_words_cache:
            return self.ranked_words_cache[word]

        ch_seen = set()
        rank = 0

        for ch in word:
            if ch in ch_seen:
                rank -= 10000
            else:
                ch_seen.add(ch)
            rank += self.ch_rankings[ch]

        self.ranked_words_cache[word] = rank
        return rank
