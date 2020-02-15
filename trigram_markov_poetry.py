"""
This programme builds rhymed poetry using trigrams
It uses William Blake's or Emily Dickinson's pieces for learning (datasets shall not be used simultaneously)
For each poem number of lines and words per line can be specified
"""
import random
import pronouncing
import nltk
from nltk.corpus import gutenberg
from nltk.tokenize import RegexpTokenizer

def load_dickinson():
    f = open("emily_dickinson.txt", 'r')
    text = f.read()
    sentences = nltk.sent_tokenize(text)

    tokenizer = RegexpTokenizer(r'\w+')
    pr_sentences = []
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        preprocesed_sent = []
        for word in words:
            w = tokenizer.tokenize(word)
            if w == []:
                continue  # skipping punctuation

            # REMOVING TITLE LINES
            if w[0].isupper() and len(w[0]) > 1:  # only title lines contain: words written in CAPS, name of author
                preprocesed_sent = []
                break  # won't add the sentence to the final list

            if w[0].isnumeric():  # removing numbers
                continue

            w[0] = w[0].lower()  # turning to lowercase

            if w[0] == 's' or w[0] == 'd':  # handling cases like "shepherd's" = ["shepherd", "s"]
                preprocesed_sent[-1] = preprocesed_sent[-1] + '\'' + w[0]
                continue

            # Handling some abbreviations
            if w[0] == 've':
                w[0] = 'have'
            if w[0] == 'll':
                w[0] = 'will'
            if w[0] == 's':
                continue
            preprocesed_sent.extend(w)  # adding new word to sentence
        pr_sentences.append(preprocesed_sent)  # adding new sentence to the final list
    pr_sentences = [sent for sent in pr_sentences if sent != []]  # dropping empty lists
    return pr_sentences

def load_blake():
    """
    This function loads and prepares for further usage set of William Blake's poems
    :return: list of sentences, each sentence - list of tokens
    """
    tokenizer = RegexpTokenizer(r'\w+')
    sentences = gutenberg.sents('blake-poems.txt')

    pr_sentences = []
    for sentence in sentences:
        preprocesed_sent = []
        for word in sentence:
            w = tokenizer.tokenize(word)
            if w == []:
                continue  # skipping punctuation

            # REMOVING TITLE LINES
            if (w[0].isupper() and len(w[0])>1) or w[0] == 'Blake':  # only title lines contain: words written in CAPS, name of author
                preprocesed_sent = []
                break  # won't add the sentence to the final list

            if w[0].isnumeric():  # removing numbers
                continue

            w[0] = w[0].lower()  # turning to lowercase

            if w[0] == 's' or w[0] == 'd':  # handling cases like "shepherd's" = ["shepherd", "s"]
                preprocesed_sent[-1] = preprocesed_sent[-1] + '\'' + w[0]
                continue

            # Handling some abbreviations
            if w[0] == 've':
                w[0] = 'have'
            if w[0] == 'll':
                w[0] = 'will'
            if w[0] == 's':
                continue

            # Handling archaisms
            if w[0] == 'er':
                if preprocesed_sent[-1] == 'ne':
                    preprocesed_sent[-1] = "never"
                elif preprocesed_sent[-1] == 'o':
                    preprocesed_sent[-1] = "over"
                continue
            if w[0] == 're':
                if preprocesed_sent[-1] == 'o':
                    preprocesed_sent[-1] = "over"
                continue

            preprocesed_sent.extend(w)  # adding new word to sentence
        pr_sentences.append(preprocesed_sent)  # adding new sentence to the final list
    pr_sentences = [sent for sent in pr_sentences if sent != []]  # dropping empty lists
    return pr_sentences


def gen_trigrams(sentences):
    """
    This function generates list of REVERSED trigrams from sentences
    :param sentences: list of sentences, each sentence - list of tokens
    :return: list of trigrams, each trigram - list of 3 tokens
    """
    trigrams = []
    for sentence in sentences:
        i = len(sentence)-1
        while (i-2) >= 0:
            ngram = [sentence[i], sentence[i-1], sentence[i-2]]
            trigrams.append(ngram)
            i -= 1
    return trigrams


def gen_dict(trigrams):
    """
    This function generates dictionary of trigrams and their frequencies
    :param trigrams: list of trigrams, each trigram - list of 3 tokens
    :return: dictionary of trigrams
    if trigrams had following structure:
        [[w4, w3, w2], [w3, w2, w1]]
    then output will look like:
        {
        w4:{w3:{w2:1}}
        w3:{w3:{w3:1}}
        }
    """
    dict = {}
    n = len(trigrams[0])
    for ngram in trigrams:
        temp = dict
        for i in range(0, n):
            if i == n - 1:
                temp.setdefault(ngram[i], 0)
                temp[ngram[i]] += 1
            else:
                try:
                    temp = temp[ngram[i]]
                except KeyError:
                    temp.setdefault(ngram[i], {})
                    temp = temp[ngram[i]]
    return dict


def find_rhyme(word, dict):
    """
    This function tries to find a rhyme in a dictionary for a given word
    :param word: word that needs to be rhymed
    :param dict: dictionary of trigrams
    :return: word, if found, None otherwise
    """
    rhymes = pronouncing.rhymes(word)  # getting all possible rhymes
    if len(rhymes) == 0:
        return None  # rhyme not found
    elif len(rhymes) == 1:
        try:
            dict[rhymes[0]]  # trying to find it in a dictionary
            return rhymes[0]
        except KeyError:
            return None  # only rhyme is not in a dictionary
    else:
        trial = rhymes
        while len(trial) != 0:
            random_rhyme = random.choice(trial)  # choosing random rhyme
            try:
                dict[random_rhyme]  # looking it in a dictionary
                return random_rhyme
            except KeyError:
                trial.remove(random_rhyme)  # not found in dictionary
        return None  # none of possible rhymes was in the dictionary


def find_second(first, dict):
    """
    This function finds random second word based on the first
    :param first: first word
    :param dict: dictionary of trigrams
    :return: one word - second word in REVERSED trigram
    """
    first_words = list(dict.keys())  # getting list of first words in reversed trigrams
    try:
        words = list(dict[first].keys())  # list of candidates
    except KeyError:
        return random.choice(first_words)  # if there's no reverse ngram that starts with "first"

    return random.choice(words)


def find_third(first, second, dict):
    """
    This function finds random third word based on the first and the second
    :param first: first word
    :param second: second word
    :param dict: dictionary of trigrams
    :return: one word - third word in REVERSED trigram
    """
    try:
        words = list(dict[first][second].keys())  # list of candidates
    except KeyError:
        return find_second(second, dict)  # if there's no reverse ngram that starts with "first" followed by "second"

    return random.choice(words)

# Builds sentences word by word
def extend_sent(sentence, first, second, dict):
    """
    This function builds sentence word by word
    :param sentence: list of words that sre already in the sentence (reversed order)
    :param first: first word of new trigram
    :param second: second word of new trigram
    :param dict: dictionary of trigrams
    :return: first and second word of NEXT NEW trigram
    """
    third = find_third(first, second, dict)
    sentence.append(third)  # add new word
    first, second = second, third  # choose new first and second
    return first, second


def make_poem(dict, num_lines, num_words):
    """
    This function makes a poem of num_lines with num_words in each line
    Lines are rhymed in pairs
    :param dict: dictionary of trigrams
    :param num_lines: number of lines in a poem
    :param num_words: number of words in one line
    :return: list of lines, each line - list of words
    """
    first_words = list(dict.keys())
    poem = []
    for l in range(num_lines):
        line = []
        if l%2 == 0:  # first line in pair
            w2 = None
            while w2 == None:  # searching for two last words in lines, that must be rhymed
                w1 = random.choice(first_words)
                w2 = find_rhyme(w1, dict)
            first = w1  # first from the end
            second = find_second(first, dict)  # searching for second
            line += [first, second]
        if l%2 == 1:  # second line in pair
            first = w2  # first from the end (already found)
            second = find_second(first, dict)  # searching for second
            line += [first, second]

        # Building the line
        for i in range(num_words-2):
            first, second = extend_sent(line, first, second, dict)

        line.reverse()  # it was built from the end, so we need to reverse the line
        poem.append(line)
    return poem

def compile_poem(lines):
    """
    This function compiles a poem to a string
    :param lines: list of lines, each line - list of words
    :return: one string - poem
    """
    poem = ""
    for line in lines:
        line[0] = line[0].capitalize()
        l = " ".join(line)
        poem = poem + l + "\n"
    return poem


def main():

    dickinson = load_dickinson()  # loading Dickinson's dataset
    blake = load_blake()  # loading Blake's dataset

    print("------------------------------------------ William Blake ------------------------------------------\n")
    trigrams = gen_trigrams(blake)  # generating trigrams
    dict = gen_dict(trigrams)  # generating dictionary
    # Generate 20 4-lines-7-words verses for demonstration
    for i in range(20):
        lines = make_poem(dict, 4, 7)
        poem = compile_poem(lines)
        print(poem)

    print("\n\n------------------------------------------ Emily Dickinson ------------------------------------------\n")
    trigrams = gen_trigrams(dickinson)  # generating trigrams
    dict = gen_dict(trigrams)  # generating dictionary
    # Generate 20 6-lines-5-words verses for demonstration
    for i in range(20):
        lines = make_poem(dict, 6, 5)
        poem = compile_poem(lines)
        print(poem)

if __name__ == "__main__":
    main()