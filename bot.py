import logging
import random
import time
import pandas as pd
import re
import dateparser

import re
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from dateutil.parser import parse , parser
import nltk
# from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from string import punctuation


from telegram.ext import Updater, CommandHandler, MessageHandler,Filters

from newsapi import NewsApiClient
import os

YOUR_API_KEY='your_telegrambot_apikey'

newsapi = NewsApiClient(api_key=YOUR_API_KEY)

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('stopwords')

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level = logging.INFO)
logger = logging.getLogger(__name__)					
TOKEN = YOUR_API_KEY
	

greetings = ["hello", "hi", "hey", "good","morning", "afternoon", "evening", "howdy", "greetings", "salutations", "hiya", "yo", "meet", "pleased",  "sup"]
goodbyes = ["goodbye", "bye", "see you later", "see", "care", "farewell", "solong", "catch you later", "until next time", "talk to you soon", "see you soon", "see you tomorrow", "have a good one", "later", "peace out", "gotta go", "bye for now", "have a great day", "have a good weekend", "have a good night", "good night", "sleep well", "sweet dreams", "until we meet again", "adios", "cheerio", "ciao", "au revoir", "sayonara", "fare thee well", "Godspeed", "be well", "stay safe", "take it easy", "keep in touch", "keep well"]
cuss_words = ["fuck", "shit", "asshole", "bitch", "idiot", "moron", "dick", "cunt", "damn", "hell", "bastard", "son of a bitch", "motherfucker", "ass", "screw you", "screw off", "piss off", "go to hell", "eat shit", "suck my dick", "fucking", "bullshit", "douchebag", "dumbass", "shithead", "cock", "pussy", "jackass", "wanker", "twat", "fucker", "fucked up", "shit-faced", "goddamn", "motherfucking", "cocksucker", "douche", "dipshit", "prick", "arsehole", "bollocks", "knob", "bugger off", "bloody hell", "what the fuck", "for fuck's sake", "shit happens", "go fuck yourself", "asshat", "assclown", "clusterfuck", "shitstorm", "fucktard", "twatwaffle", "cockwomble"]
responses = [
    "Please refrain from using that language.",
    "That's not a very polite thing to say.",
    "Let's try to keep things civil.",
    "Please use respectful language.",
    "That kind of language is not acceptable.",
    "Let's keep things respectful, please.",
    "That's not a very nice word to use.",
    "Please refrain from using that language."
]

def categorize_intent(user_input):
    tokens = word_tokenize(user_input.lower())
    print(tokens)
    if any(greeting in tokens for greeting in greetings):
        return "greeting"
    elif any(goodbye in tokens for goodbye in goodbyes):
        return "goodbye"
    elif any(cuss_word in tokens for cuss_word in cuss_words):
        return "cussing"
    else:
        return "neutral"

def extract_date(input_string):
    # Try to extract the date in the "dd month" format
    date = dateparser.parse(input_string, languages=['en'], settings={'DATE_ORDER': 'DMY'})
    if date is not None:
        return date.strftime('%Y-%m-%d')
    
    # Try to extract the date in the "dd-mm-yyyy" format
    pattern = r'\b\d{1,2}-\d{1,2}-\d{4}\b'
    match = re.search(pattern, input_string)  #regular expression
    if match:
        date = dateparser.parse(match.group(0), settings={'DATE_ORDER': 'DMY'})
        if date is not None:
            return date.strftime('%Y-%m-%d')
    
    return None



def extract_title(text):
    # tokenize 
    sentences = sent_tokenize(text)

    # create a list of stopwords and punctuation to remove from the text
    stop_words = set(stopwords.words('english'))
    stop_words.update(list(punctuation))

    # initialize a list to hold the noun phrases found in the text
    noun_phrases = []

    # loop through each sentence in the text
    for sentence in sentences:
        words = word_tokenize(sentence)
        tagged_words = nltk.pos_tag(words)

        # extract noun phrases from the tagged words
        chunk_parser = nltk.RegexpParser('NP: {<DT>?<JJ>*<NN.*>+}')
        tree = chunk_parser.parse(tagged_words)
        for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
            # extract the words from the subtree and join them into a phrase
            phrase = ' '.join(word for word, pos in subtree.leaves())

            # add the phrase to the list of noun phrases, if it is not a stop word
            if phrase.lower() not in stop_words:
                noun_phrases.append(phrase)
    
    print(noun_phrases)
    # return the most common noun phrase as the topic
    if 'news' in noun_phrases:
        noun_phrases.remove('news')
    if 'some news' in noun_phrases:
        noun_phrases.remove('some news')
    if len(noun_phrases) > 0:
        return max(set(noun_phrases), key=noun_phrases.count)
    else:
        return None


def sweetTalk(update,context):
    inp = update.message.text.lower()
    print(inp)
    a = categorize_intent(update.message.text)
    if a == 'greeting':
        context.bot.send_message(chat_id=update.effective_chat.id, text =  random.choice(greetings))
    elif a == 'goodbye':
        context.bot.send_message(chat_id=update.effective_chat.id, text =  random.choice(goodbyes))
    elif a == 'cussing':
        context.bot.send_message(chat_id=update.effective_chat.id, text =  random.choice(responses))
    else:
        return
        # context.bot.send_message(chat_id=update.effective_chat.id, text =  "Please be more precise with your query :)")
            

def start(update, context):
    author_name = update.message.from_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text = f'Hello {author_name}!!!\n/news - Follow it with your query\n /help - What is this bot\n /details - Details of this project')

def helpp(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You can use this bot to search for top 5 news regarding topic of your choice. If you want you can also provide the date on which you want to filter the news. Date should be provided in dd-mm-yyyy format and it should not be older than a month.\n Enjoy ;) ")

def detail(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="This bot is created by Nilay Vatsal for the personal project of NLP. Kudos to everyone :)")

def getNews(update, context):
    query = ' '.join(context.args)
    print(query)
    dates = extract_date(query)
    print("Dates", dates)


    titles = extract_title(query)

    print("title",titles)
    print("\n")
    if dates == None and titles is not None:
        articles = newsapi.get_everything(q= titles)
    elif dates and titles:
        articles = newsapi.get_everything(q= titles, from_param= dates, to= dates)
    else:
        articles = "do more"

    if articles == "do more":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Something is wrong")
    else:
        df = pd.DataFrame(articles)
        if df.empty:
            context.bot.send_message(chat_id=update.effective_chat.id, text= ("No news found for this topic.. :("))
        else:
            r,c = df.shape
            print("Total news:",r)
            for i in range(min(5,r)):
                print(df['articles'][i]['title'])
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"{df['articles'][i]['title']} '\n' {df['articles'][i]['url']}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpp))
    dp.add_handler(CommandHandler("details", detail))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, sweetTalk))
    dp.add_handler(CommandHandler("news", getNews))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()