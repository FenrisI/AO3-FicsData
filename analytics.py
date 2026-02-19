import string
from typing import TypeAlias
from bs4 import BeautifulSoup
from collections import Counter

PUNCTUATION_1: str = '!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
PUNCTUATION_2: str = "-'‘’\xa0\t"
LETTERS: str = "abcdefghijklmnopqrstuvwxyz1234567890"
SITE: str = "https://archiveofourown.org"
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because",
    "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do",
    "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", 
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his",
    "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
    "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", 
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", 
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
    "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", 
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves"
}

# creating translation tables for text parsing
LETTER_TABLE: dict[int, int] = dict.fromkeys(map(ord, LETTERS), None)
PUNCTUATION_TABLE: dict[int, int|None] = dict.fromkeys(map(ord, PUNCTUATION_1), " ")
for c in PUNCTUATION_2:
    PUNCTUATION_TABLE[ord(c)] = None

FrequencyMap: TypeAlias = dict[int, Counter[str]]

def _get_words(text: str) -> list[str]:
    """Cleans text and returns a list of words."""
    clean_text = text.lower().translate(PUNCTUATION_TABLE)
    return clean_text.split()
    
def _count_words(string: str) -> int:
    return len(_get_words(string))

def _punctuation_frequency(string: str) -> Counter[str]:
    stats = Counter()
    string = string.lower().translate(LETTER_TABLE)
    string = string.replace(" ", "")
    for char in string:
        if char in PUNCTUATION_1 + PUNCTUATION_2:
            stats[char] += 1     
    return stats

def _word_frequency(string: str) -> Counter[str]:
    words = _get_words(string)
    chapter_stats = Counter(words)
    return chapter_stats


def chapter_word_counts(soup: BeautifulSoup) -> dict:
    chapters = soup.find_all('div', attrs={"class": "userstuff module"})
    word_count={}
    for index, chapter in enumerate(chapters):
        chapter = chapter.text
        chapter = chapter.lower()
        chapter = chapter[14:]
        word_count[index+1] = _count_words(chapter)
    return word_count

def chapter_punctuation_frequency(soup: BeautifulSoup) -> FrequencyMap:
    chapter_punctuation_stats = {}
    chapters = soup.find_all('div', attrs={"class": "userstuff module"})
    for index, chapter in enumerate(chapters):
        chapter = chapter.text
        chapter_punctuation_stats[index+1] = _punctuation_frequency(chapter)
    return chapter_punctuation_stats

def work_punctuation_frequency(chapter_stats: FrequencyMap) -> Counter[str]:
    totatl_stats = sum(chapter_stats.values(), start=Counter())
    return totatl_stats

def chapter_word_frequency(soup: BeautifulSoup) -> FrequencyMap:
    total_stats = Counter()
    chapters = soup.find_all('div', attrs={"class": "userstuff module"})
    for index, chapter in enumerate(chapters):
        chapter = chapter.text
        total_stats[index+1] = _word_frequency(chapter)
    return total_stats

def work_word_frequency(chapter_stats: FrequencyMap) -> Counter:
    totatl_stats = sum(chapter_stats.values(), start=Counter())
    return totatl_stats

def filter_frequency(frequency: FrequencyMap, remove_stop_words: bool = True, stop_words: set[str] = STOP_WORDS) -> FrequencyMap:
    filtered = frequency.copy()
    if remove_stop_words:
        for word in stop_words:
            filtered.pop(word, None)
    return filtered
