import os
from pathlib import Path


class Config(object):
    def __init__(self):
        self.num_epochs = 10  # 训练轮数
        self.batch_size = 32  # 批次字节数
        self.embed_dim = 50  # 每个字的维度
        self.hidden_size = 100
        self.num_rnn_layers = 3
        self.max_length = 20  # 样本最大长度
        self.learn_rate = 1e-3
        self.vocab_path = '../dict/chars.txt'
        self.corpus_path = os.path.join(str(Path(__file__).parent.parent.parent)) + '/data/corpus.txt'
        self.is_shuffle = True
        # self.devices = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
