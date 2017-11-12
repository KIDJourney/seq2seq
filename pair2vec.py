import datetime
import os

import gensim
import jieba
import gensim.models.word2vec as w2v
from logger import logger

WEIGHT_FILE_FORMAT = "{name}_{data_size}_{date}"
WEIGHT_PATH = "./model_weight/"


def pairs_to_vector(poetry_pairs, **kwargs):
    combined_pairs = []
    for pair in poetry_pairs:
        combined = ' '.join(pair)
        combined_pairs.append(combined)

    return sentence_to_vector(combined_pairs, **kwargs)


def sentence_to_vector(sentences, **kwargs):
    word_response_sentences = []
    for sentence in sentences:
        word_response_sentences.append(convert_sentence_to_words(sentence))

    model = w2v.Word2Vec(word_response_sentences, **kwargs)

    weight_name = generate_weight_name(kwargs.get('name'), len(sentences))
    model.save(os.path.join(WEIGHT_PATH, weight_name))
    logger.info('model saved name=%s', weight_name)

    return model


def generate_weight_name(weight_name, size):
    now = datetime.datetime.now()
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    return WEIGHT_FILE_FORMAT.format(name=weight_name, data_size=size, date="{}-{}_{}:{}".format(month, day, hour, minute))


def convert_sentence_to_words(sentence):
    return [i for i in jieba.cut(sentence) if i.strip()]
