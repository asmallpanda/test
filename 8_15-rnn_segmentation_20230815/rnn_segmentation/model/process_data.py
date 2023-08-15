import torch
from torch.utils.data import DataLoader
import jieba


class Dataset(object):
    def __init__(self, corpus_path, vocab, max_len):
        self.corpus_path = corpus_path
        self.vocab = vocab
        self.max_len = max_len
        self.__load_data()

    def __load_data(self):
        self.data = []
        with open(self.corpus_path, mode='r', encoding='utf-8') as f:
            for line in f:
                sequence = sentence_to_sequence(line, self.vocab)
                label = sequence_to_label(line)
                sequence, label = self.padding(sequence, label)
                sequence = torch.LongTensor(sequence)
                label = torch.LongTensor(label)
                self.data.append([sequence, label])
                # 使用部分数据做展示，使用全部数据训练时间会相应变长
                if len(self.data) > 10000:
                    break

    # 将文本截断或补齐到固定长度
    def padding(self, sequence, label):
        sequence = sequence[:self.max_len]
        sequence += [0] * (self.max_len - len(sequence))
        label = label[:self.max_len]
        label += [-100] * (self.max_len - len(label))
        return sequence, label

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


# 文本转化为数字序列，为embedding做准备
def sentence_to_sequence(sentence, vocab):
    sequence = [vocab.get(char, vocab['unk']) for char in sentence]
    return sequence


# 基于jieba生成分级结果的标注
def sequence_to_label(sentence):
    words = jieba.lcut(sentence)
    label = [0] * len(sentence)
    pointer = 0
    for word in words:
        pointer += len(word)
        label[pointer - 1] = 1
    return label


# 加载字表
def build_vocab(vocab_path):
    vocab = {}
    with open(vocab_path, mode='r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            char = line.strip()
            vocab[char] = index + 1
    vocab['unk'] = len(vocab) + 1
    return vocab


def make_dataset(corpus_path, vocab, max_len, batch_size, is_shuffle=True):
    dataset = Dataset(corpus_path, vocab, max_len)
    return DataLoader(dataset, batch_size=batch_size, shuffle=is_shuffle)
