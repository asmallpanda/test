import numpy as np
import torch.optim

from config import Config
from process_data import build_vocab, make_dataset
from process_data import sentence_to_sequence
from segmentation_based_on_rnn import SegmentationModel


def main():
    vocab = build_vocab(cfg.vocab_path)
    data_loader = make_dataset(cfg.corpus_path, vocab, cfg.max_length, cfg.batch_size, is_shuffle=cfg.is_shuffle)
    model = SegmentationModel(cfg.embed_dim, cfg.hidden_size, cfg.num_rnn_layers, len(vocab) + 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.learn_rate)

    for epoch in range(cfg.num_epochs):
        model.train()
        watch_loss = []
        for x, y in data_loader:
            optimizer.zero_grad()
            loss = model(x, y)
            loss.backward()
            optimizer.step()
            watch_loss.append(loss.item())
        print('............\n第{}轮平均loss:{}'.format(epoch + 1, np.mean(watch_loss)))
    torch.save(model, '../output_model/seg_model.pth')
    return


def predict(model_path, input_strings):
    vocab = build_vocab(cfg.vocab_path)
    model = torch.load(model_path)
    model.eval()
    for input_string in input_strings:
        x = sentence_to_sequence(input_string, vocab)
        with torch.no_grad():
            res = model.forward(torch.LongTensor([x]))[0] # [input_len, 2]
            res = torch.argmax(res, dim=-1)
            # 在预测为1的地方切分，将切分后文本打印出来
            for index, p in enumerate(res):
                if p == 1:
                    print(input_string[index], end='  ')
                else:
                    print(input_string[index], end='')
            print('\n-------------------------------------------------------')


if __name__ == '__main__':
    cfg = Config()
    main()

    test_strings = ["同时国内有望出台新汽车刺激方案",
                    "沪胶后市有望延续强势",
                    "经过两个交易日的强势调整后",
                    "昨日上海天然橡胶期货价格再度大幅上扬"]
    predict('../output_model/seg_model.pth', test_strings)
