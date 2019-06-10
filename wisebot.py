from telegram.ext import Updater, CommandHandler
from gen_message import *
from gensim.models import Word2Vec


def avg_vector(vectors):
	return np.sum(vectors, axis=0)/len(vectors)

def text_2vec(text):
	if (len(text)>0):
		text = re.sub(r'([!"#$%&\'()*+,-./:;<=>?^_`{|}~])',r" \1"," ".join(text))
		vectors = []
		for word in text.split():
			if word in comments2vec.wv:
				vectors.append(comments2vec.wv[word])
		if len(vectors) > 0:
			return avg_vector(vectors)
	return None

def gen_message(update, context):
	message = update.message.text[1:].split()

	command = message[0]
	if "@" in command:
		command = command [:command.find("@")]

	text = message[1:]

	begin = text_2vec(text)
	context.bot.send_message(chat_id=update.message.chat_id, text=models[command].generate_sentence(begin = begin), reply_to_message_id=update.message.message_id)

def start(update, context):
	text = "Olá eu sou o WiseBot, eu gero mensagens automáticas para: "+ ", ".join(names_to_file.keys())
	context.bot.send_message(chat_id=update.message.chat_id, text=text, reply_to_message_id=update.message.message_id)

names_to_file = {"name1": "processed/name1.txt"
				}

comments2vec = Word2Vec.load("processed/comments.model")

models = train_bots(names_to_file)
print("done training")

updater = Updater(token='yourtoken', use_context=True)
dispatcher = updater.dispatcher
start_handler = CommandHandler(['start', 'help'], start)
dispatcher.add_handler(start_handler)

gen_message_handler = CommandHandler(names_to_file.keys(), gen_message)
dispatcher.add_handler(gen_message_handler)

updater.start_polling()