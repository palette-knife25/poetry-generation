"""
This programme builds blank-verse poetry using pure Markov's Chains concept
It uses Rupi Kaur's pieces for learning
For each poem number of lines and words per line can be specified
"""
import glob
import random
from contractions import exp_contr


def load_docs(path):
    """
    This function loads txt files from path
    :param path:
    :return: list of docs
    """
    list_docs = glob.glob(path + "*.txt")
    docs = []
    for file in list_docs:
        f = open(file, encoding='utf-8')
        doc = f.read()
        doc = doc.replace('’', '\'')
        doc = doc.replace(".", "")
        docs.append(doc)
    return docs


def expand_tokens(tokens):
    """
    This function expands such abbreviations as "we'll", "haven't", etc.
    :param tokens: list of tokens(words)
    :return: list of tokens(words) without abbreviations
    """
    exp_tokens = []
    for token in tokens:
        exp_tokens.extend(exp_contr(token))
    return exp_tokens


def build_chains(docs):
    """
    This function builds for each word list of its follow-ups
    It does not drop duplicates, so that words that are more frequent are more probable
    :param docs: dictionary of docs {id: doc}
    :return: dict of follow-ups {word1:[w1, w2, w3, ...], word2:[w1, w2, w3, ...], ...}
    """
    chains = {}
    for doc in docs:
        doc = doc.replace("\n", " ")
        tokens = doc.split(" ")
        tokens = [t for t in tokens if t != '']
        tokens = expand_tokens(tokens)
        for i in range(len(tokens)-1):
            try:
                chains[tokens[i]].append(tokens[i+1])
            except KeyError:
                chains[tokens[i]] = [tokens[i+1]]
    return chains


def build_poem(count_words, chains):
    """
    This function builds a poem of count_words length
    :param count_words: length of poem (in words)
    :param chains: dict of follow-ups {word1:[w1, w2, w3, ...], word2:[w1, w2, w3, ...], ...}
    :return: string - poem
    """
    word1 = random.choice(list(chains.keys()))  # random first word
    poem = [[word1]]

    while len(poem) < count_words:
        try:
            l = chains[word1]
            word2 = random.choice(l)
        except KeyError:
            word1 = random.choice(list(chains.keys()))
            continue
        word1 = word2
        poem.append([word2])
    return poem

def chunker(seq, size):
    """
    This function is used to divide a list into chunks
    :param seq: list
    :param size: chunk size
    :return:
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def compile_poem(words_num, lines_num, chains):
    """
    This function is used for "compiling" a poem:
    Building it, turning it into a string, splitting into lines, adding \n's
    :param words_num: how many words in a line
    :param lines_num: how many lines in a poem
    :param chains: dict of follow-ups {word1:[w1, w2, w3, ...], word2:[w1, w2, w3, ...], ...}
    :return: string - poem
    """
    words_total = words_num*lines_num
    raw_poem = build_poem(words_total, chains)
    poem = ""
    for line in chunker(raw_poem, words_num):
        poem += line[0][0].capitalize()
        for i in range (1, len(line)):
            poem = poem + " " + line[i][0]
        poem += "\n"
    return poem


def main():
    docs = load_docs("rupiKaur/")  # loading dataset

    chains = build_chains(docs)  # building chains

    # Generating 20 5-lines-3-words verses for demonstration
    for i in range(20):
        print(i)
        poem = compile_poem(5, 3, chains)
        print(poem)

if __name__ == "__main__":
    main()