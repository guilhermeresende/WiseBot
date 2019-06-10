import numpy as np
import re
from gensim.utils import tokenize
import string
from sklearn.metrics.pairwise import cosine_similarity

def make_pairs(corpus):
        for i in range(len(corpus)-1):
            yield (corpus[i], corpus[i+1])

def make_triples(corpus):
        for i in range(len(corpus)-2):
            yield (corpus[i], corpus[i+1], corpus[i+2])

class ChainTextGenerator:
    
    def train(self, Comments, Vecs):
        self.text = Comments
        self.Vecs = np.array(Vecs)
        self.train_word_probs()
        

    def train_word_probs(self):
        corpus = []
        
        # dictionary of vectors to messages
        self.vec_dict = {}
        i = 0
        for sentence in self.text:
            splitted_sentence = sentence.split(" ") + ["<END>"]
            corpus += ["<BEG>"] + splitted_sentence
            self.vec_dict[str(self.Vecs[i])] = "<//>".join(splitted_sentence[:3])
            i += 1

        #one state markov chain of words
        pairs = make_pairs(corpus)
        self.word_dict = {}
        for word_1, word_2 in pairs:
            if word_1 in self.word_dict.keys():
                self.word_dict[word_1].append(word_2)
            else:
                self.word_dict[word_1] = [word_2]
        
        #two state markov chain of words
        triples = make_triples(corpus)
        self.double_word_dict = {}
        for word_1, word_2, word_3 in triples:
            if word_1+"<//>"+word_2 in self.word_dict.keys():
                self.double_word_dict[word_1+"<//>"+word_2].append(word_3)
            else:
                self.double_word_dict[word_1+"<//>"+word_2] = [word_3]
                

    def closest_vector(self, x):
        max_similar = float("-inf")
        for vec in self.Vecs:
            similar = cosine_similarity([vec],[x])[0][0]
            if similar > max_similar:
                max_similar = similar
                max_vec = vec
        return max_vec

    
    def generate_sentence(self, begin = None,double_chain_prob = 0.5):

        chain = ["<BEG>"]
        if begin is None:       #no message was given to bot
            chain.append(np.random.choice(self.word_dict[chain[0]]))
            while (chain[1] in string.punctuation):
                chain[1] = np.random.choice(self.word_dict[chain[0]])
        else:                   #message was given to bot
            closest = self.closest_vector(begin)
            words = self.vec_dict[str(closest)].split("<//>")
            assert len(words) >= 2
            chain += words

        while chain[-1] != "<END>":
            past_two_words = chain[-2]+"<//>"+chain[-1]
            if past_two_words in self.double_word_dict:
                if (np.random.uniform() < double_chain_prob):
                    chain.append(np.random.choice(self.double_word_dict[past_two_words]))
                else:
                    chain.append(np.random.choice(self.word_dict[chain[-1]]))
            else:
                chain.append(np.random.choice(self.word_dict[chain[-1]]))
        
        chain = list(filter(lambda c: c != "", chain))
        sentence = ' '.join(chain[1:-1])
        
        return re.sub(r' ([!"#$%&\'()*+,-./:;<=>?^_`{|}~])',r"\1",sentence)


def train_bots(names_to_files):
    models = {}
    for name in names_to_files:
        filepath = names_to_files[name]
        Comments = []
        Vecs = []
        with open(filepath) as f:
            for line in f:
                comment = line.split("\t")
                vec = eval(comment[0])
                text = "\t".join(comment[1:])
                if text != '':
                    Comments.append(text)
                    Vecs.append(vec)
                else:
                    print("caiu no else")
        model_T = ChainTextGenerator()
        model_T.train(Comments, Vecs)
        models[name] = model_T
    return models
