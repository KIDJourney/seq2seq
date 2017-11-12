import logging

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT, filename='./log/seq2seq.log', level=logging.INFO)

logger = logging
