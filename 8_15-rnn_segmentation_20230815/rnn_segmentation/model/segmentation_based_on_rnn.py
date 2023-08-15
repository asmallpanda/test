import torch
import torch.nn as nn
import jieba
import numpy as np
import random
import json
from torch.utils.data import DataLoader

"""
基于pytorch的网络编写一个分词模型
我们使用jieba分词的结果作为训练数据
"""

class SegmentationModel(nn.Module):
    def __init__(self, embed_dim, hidden_unit, num_rnn_layers, vocab_size):
        super().__init__()
        self.embed_layer = nn.Embedding(vocab_size, embed_dim)
        self.rnn_layer = nn.RNN(input_size=embed_dim, hidden_size=hidden_unit, batch_first=True,
                                num_layers=num_rnn_layers)
        self.classify_layer = nn.Linear(hidden_unit, 2)
        self.loss_layer = nn.CrossEntropyLoss(ignore_index=-100)

    def forward(self, x, y=None):
        # input shape:(batch_size, input_dim), output shape:(batch_size, input_dim, embed_dim)
        x = self.embed_layer(x)
        # output shape:(batch_size, input_dim, hidden_size)
        x, _ = self.rnn_layer(x)
        # output shape:(batch_size, input_dim, 2)
        y_pred = self.classify_layer(x)
        if y is not None:
            # view(-1,2): (batch_size, sen_len, 2) -> (batch_size * sen_len, 2)
            return self.loss_layer(y_pred.view(-1, 2), y.view(-1))
        else:
            return y_pred