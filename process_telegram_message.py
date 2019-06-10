import os
from gensim.models import Word2Vec
import gensim.utils
import numpy as np
import re
import string

def process_text(text):
    text = text.replace("<br>","\n")
    text = re.sub(r"<a href.*>(@.*)</a>",r"\1",text)
    text = re.sub(r"<a(.)*>(\n)*","",text)
    text = gensim.utils.decode_htmlentities(text)
    text = text.lower()
    text = re.sub(r"\n",r" ",text)
    text = re.sub(r"  "," ", text)
    text = re.sub(r"(["+string.punctuation+"])",r" \1",text) 
    if text == " ":
    	text = ""
    return text

def avg_vector(vectors):
	return np.sum(vectors, axis=0)/len(vectors)


messages = {}
# create dictionary with user and list of messages
for file in os.listdir("/messages"):
	f = open(file,"r")
	line = f.readline()

	while (line != ""):
		line = line.strip("\n")
		if line == "       <div class=\"from_name\">":
			name = f.readline().strip(" ").strip("\n")
			if name[-1] == " ":
				name = name[:-1]
			if not(name in messages):
				messages[name] = []
		elif line == "       <div class=\"text\">":
			text = process_text(f.readline())
			if text != "":
				messages[name].append(text)
		line = f.readline()
	f.close()

corpus =[]
for name in messages:
	for message in messages[name]:
		corpus.append(list(gensim.utils.tokenize(message)))

model = Word2Vec(corpus, size=200, window=5, min_count=1, workers=4)

messages_vec = {}
#create dictionary with user and vector of preceding message
for file in os.listdir("/messages"):
	f = open(file,"r")
	text = "a"
	line = f.readline()
	while (line != ""):
		line = line.strip("\n")
		if line == "       <div class=\"from_name\">":
			name = f.readline().strip(" ").strip("\n")
			if name[-1] == " ":
				name = name[:-1]
			if not(name in messages_vec):
				messages_vec[name] = []
		elif line == "       <div class=\"text\">":
			if text != "":
				prev_text = text
			text = process_text(f.readline())
			if text != "":
				sentence_vec = []
				for word in prev_text.split():
					if word in model.wv:
						sentence_vec.append(model.wv[word])
				if len(sentence_vec) == 0:
					sentence_vec = [model.wv['a']]
				messages_vec[name].append(avg_vector(sentence_vec))
		line = f.readline()
	f.close()

#creates processed text files
for name in messages:
	fout = open("processed/"+name+".txt","w")
	for message_idx in range(len(messages[name])):
		str_vec = "["+",".join([str(i) for i in messages_vec[name][message_idx]])+"]"
		fout.write(str_vec+"\t")
		fout.write(messages[name][message_idx]+"\n")
	fout.close()

#word2vec model
model.save("processed/comments.model")

