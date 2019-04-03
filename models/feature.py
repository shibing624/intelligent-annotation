# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief:

from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2

from utils.data_utils import dump_pkl, load_pkl, get_char_segment_data, load_list
from utils.io_utils import get_logger

logger = get_logger(__name__)


class Feature(object):
    """
    get feature from raw text
    """

    def __init__(self, data=None,
                 feature_type='tfidf_char',
                 feature_vec_path=None,
                 is_infer=False,
                 word_vocab=None,
                 max_len=400):
        self.data_set = data
        self.feature_type = feature_type
        self.feature_vec_path = feature_vec_path
        self.sentence_symbol = load_list(path='data/sentence_symbol.txt')
        self.stop_words = load_list(path='data/stop_words.txt')
        self.is_infer = is_infer
        self.word_vocab = word_vocab
        self.max_len = max_len

    def get_feature(self):
        if self.feature_type == 'tfidf_word':
            data_feature = self.tfidf_word_feature(self.data_set)
        elif self.feature_type == 'tf_word':
            data_feature = self.tf_word_feature(self.data_set)
        elif self.feature_type == 'vectorize':
            data_feature = self.vectorize(self.data_set)
        else:
            # tfidf_char
            data_feature = self.tfidf_char_feature(self.data_set)
        return data_feature

    def vectorize(self, data_set):
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(data_set)
        sequences = tokenizer.texts_to_sequences(data_set)

        word_index = tokenizer.word_index
        logger.info('Number of Unique Tokens: %d' % len(word_index))
        data_feature = pad_sequences(sequences, maxlen=self.max_len)
        logger.info('Shape of Data Tensor:%s' % data_feature.shape)
        return data_feature

    def tfidf_char_feature(self, data_set):
        """
        Get TFIDF feature by char
        :param data_set:
        :return:
        """
        data_set = get_char_segment_data(data_set)
        if self.is_infer:
            self.vectorizer = load_pkl(self.feature_vec_path)
            data_feature = self.vectorizer.transform(data_set)
        else:
            self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2), sublinear_tf=True)
            data_feature = self.vectorizer.fit_transform(data_set)
        vocab = self.vectorizer.vocabulary_
        logger.debug('Vocab size:%d' % len(vocab))
        logger.debug('Vocab list:')
        count = 0
        for k, v in self.vectorizer.vocabulary_.items():
            if count < 10:
                logger.debug("%s	%s" % (k, v))
                count += 1

        logger.debug(data_feature.shape)
        if not self.is_infer:
            dump_pkl(self.vectorizer, self.feature_vec_path, overwrite=True)
        return data_feature

    def tfidf_word_feature(self, data_set):
        """
        Get TFIDF ngram feature by word
        :param data_set:
        :return:
        """
        if self.is_infer:
            self.vectorizer = load_pkl(self.feature_vec_path)
            data_feature = self.vectorizer.transform(data_set)
        else:
            self.vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2),
                                              vocabulary=self.word_vocab, sublinear_tf=True)
            data_feature = self.vectorizer.fit_transform(data_set)
        vocab = self.vectorizer.vocabulary_
        logger.debug('Vocab size:%d'% len(vocab))
        logger.debug('Vocab list:')
        count = 0
        for k, v in self.vectorizer.vocabulary_.items():
            if count < 10:
                logger.debug("%s	%s" % (k, v))
                count += 1

        logger.debug(data_feature.shape)
        # if not self.is_infer:
        dump_pkl(self.vectorizer, self.feature_vec_path, overwrite=True)
        return data_feature

    def tf_word_feature(self, data_set):
        """
        Get TF feature by word
        :param data_set:
        :return:
        """
        if self.is_infer:
            self.vectorizer = load_pkl(self.feature_vec_path)
            data_feature = self.vectorizer.transform(data_set)
        else:
            self.vectorizer = CountVectorizer(analyzer='word',
                                              encoding='utf-8',
                                              lowercase=True,
                                              vocabulary=self.word_vocab)
            data_feature = self.vectorizer.fit_transform(data_set)
        vocab = self.vectorizer.vocabulary_
        logger.debug('Vocab size:%d' % len(vocab))
        logger.debug('Vocab list:')
        count = 0
        for k, v in self.vectorizer.vocabulary_.items():
            if count < 10:
                logger.debug("%s	%s" % (k, v))
                count += 1
        feature_names = self.vectorizer.get_feature_names()
        logger.debug('feature_names:%s' % feature_names[:20])

        logger.debug(data_feature.shape)
        if not self.is_infer:
            dump_pkl(self.vectorizer, self.feature_vec_path, overwrite=True)
        return data_feature

    def label_encoder(self, labels):
        encoder = preprocessing.LabelEncoder()
        corpus_encode_label = encoder.fit_transform(labels)
        logger.info('corpus_encode_label shape:%s' % corpus_encode_label.shape)
        return corpus_encode_label

    def select_best_feature(self, data_set, data_lbl):
        ch2 = SelectKBest(chi2, k=10000)
        return ch2.fit_transform(data_set, data_lbl), ch2
