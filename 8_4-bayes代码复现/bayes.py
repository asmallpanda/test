import json
from collections import defaultdict
import jieba

jieba.initialize()


class BayesApproach:
    def __init__(self, data_path):
        self.p_class = defaultdict(int)
        self.word_class_prob = defaultdict(dict)
        self.load_data(data_path)

    def load_data(self, data_path):
        self.class_name_to_word_freq = defaultdict(dict)
        self.all_words = set()  # 汇总一个词表
        with open(data_path, encoding='utf-8') as f:
            for line in f:
                line = json.loads(line)
                class_name = line['tag']
                title = line['title']
                words = jieba.lcut(title)
                self.all_words.union(set(words))
                self.p_class[class_name] += 1  # 记录每个类别的样本数量
                word_freq = self.class_name_to_word_freq[class_name]
                # 记录每个类别下的词频
                for word in words:
                    if word not in word_freq:
                        word_freq[word] = 1
                    else:
                        word_freq[word] += 1
        self.freq_to_prob()
        return

    # 将记录的词频和样本频率都转化为概率
    def freq_to_prob(self):
        # 样本概率计算
        total_sample_count = sum(self.p_class.values())
        self.p_class = dict([c, self.p_class[c] / total_sample_count] for c in self.p_class)
        # 词概率计算
        self.word_class_prob = defaultdict(dict)
        for class_name, word_freq in self.class_name_to_word_freq.items():
            total_word_count = sum(count for count in word_freq.values())
            for word in word_freq:
                # 加1平滑，避免出现概率为0，计算P(wn|x1)
                prob = (word_freq[word] + 1) / (total_word_count + len(self.all_words))
                self.word_class_prob[class_name][word] = prob
            self.word_class_prob[class_name]["<unk>"] = 1 / (total_word_count + len(self.all_words))
        return

    # P(w1|x1) * P(w2|x1)...P(wn|x1)
    def get_words_class_prob(self, words, class_name):
        result = 1
        for word in words:
            unk_prob = self.word_class_prob[class_name]['<unk>']
            result *= self.word_class_prob[class_name].get(word, unk_prob)
        return result

    # 计算P(w1,w2...wn|x1) * P(x1)
    def get_class_prob(self, words, class_name):
        # P(x1)
        p_x = self.p_class[class_name]
        # P(w1,w2...wn|x1) = P(w1|x1) * P(W2|X1)...P(wn|x1)
        p_w_x = self.get_words_class_prob(words, class_name)
        return p_x * p_w_x

    # 做文本分来
    def classify(self, sentence):
        words = jieba.lcut(sentence)  # 切词
        results = []
        for class_name in self.p_class:
            prob = self.get_class_prob(words, class_name)  # 计算class_name类概率
            results.append([class_name, prob])
        results = sorted(results, key=lambda x: x[1], reverse=True)  # 排序（降序）

        # 计算公共分母：P(w1, w2, ...wn) = P(w1, w2,...,wn|x1)*P(x1) + P(w1, w2,...,wn|x2)*P(x2) + .. + P(w1, w2,...,wn|xn)*P(xn)
        # 不做这一步也可以，对顺序没影响，只不过得到的不是0-1间的概率值
        pw = sum([x[1] for x in results])  # P(w1, w2, ...wn)
        results = [[c, prob / pw] for c, prob in results]

        # 打印结果
        for class_name, prob in results:
            print("属于类别[%s]的概率为%f" % (class_name, prob))
        return results


if __name__ == '__main__':
    path = './data/train_tag_news.json'
    bayes = BayesApproach(path)
    query = "IEF09电子竞技大赛武汉站预选赛公告"
    bayes.classify(query)
