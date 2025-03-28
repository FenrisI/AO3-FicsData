PUNCTUATION_1 = '!"#$%&()*+,–—./:;<=>?@[\\]^_`{|}~”“…\n'
PUNCTUATION_2 = "-'‘’\xa0\t"
LETTERS = "abcdefghijklmnopqrstuvwxyz1234567890"

# creating translation tables for text parsing
letterTable = dict.fromkeys(map(ord, LETTERS), None)
punctuationTable = dict.fromkeys(map(ord, PUNCTUATION_1), " ")
for c in PUNCTUATION_2:
    punctuationTable[ord(c)] = None


def chapterWords(soup) -> int:
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    chapter = chapter.text
    chapter = chapter.lower()
    # getting rid of punctuations
    chapter.translate(punctuationTable)
    # because the find function takes in 2 extra unseen words
    wordCount = len(chapter.split()) - 2

    return wordCount


def chapterWordFrequency(soup) -> dict:
    frequency = {}
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    chapter = chapter.text
    chapter = chapter.lower()
    chapter = chapter.translate(punctuationTable)
    for i in chapter.split():
        if i in frequency:
            frequency[i] += 1
        else:
            frequency[i] = 1
    frequency["chapter"] -= 1
    frequency["text"] -= 1
    return frequency


def chapterPunctuationFrequency(soup) -> dict:
    frequency = {}
    chapter = soup.find('div', attrs={"class": "userstuff module"})
    chapter = chapter.text.lower()
    chapter = chapter.translate(letterTable)
    for i in chapter:
        if i in frequency:
            frequency[i] += 1
        else:
            frequency[i] = 1

    return frequency
