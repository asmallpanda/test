# BERT原理和结构详解

[BERT](https://so.csdn.net/so/search?q=BERT&spm=1001.2101.3001.7020)，基于transformer的双向编码表示，它是一个预训练模型，模型训练时的两个任务是预测句子中被掩盖的词以及判断输入的两个句子是不是上下句。在预训练好的BERT模型后面根据特定任务加上相应的网络，可以完成NLP的下游任务，比如文本分类、机器翻译等。

​    虽然BERT是基于transformer的，但是它只使用了transformer的encoder部分，它的整体框架是由多层transformer的encoder堆叠而成的。每一层的encoder则是由一层muti-head-attention和一层feed-forword组成，大的模型有24层，每层16个attention，小的模型12层，每层12个attention。每个attention的主要作用是通过目标词与句子中的所有词汇的相关度，对目标词重新编码。所以每个attention的计算包括三个步骤：计算词之间的相关度，对相关度归一化，通过相关度和所有词的编码进行加权求和获取目标词的编码。

​    在通过attention计算词之间的相关度时，首先通过三个权重矩阵对输入的序列向量(512*768)做线性变换，分别生成query、key和value三个新的序列向量，用每个词的query向量分别和序列中的所有词的key向量做乘积，得到词与词之间的相关度，然后这个相关度再通过softmax进行归一化，归一化后的权重与value加权求和，得到每个词新的编码。

**1. 模型输入**

在BERT中，输入的向量是由三种不同的embedding求和而成，分别是：

1. wordpiece embedding：单词本身的向量表示。WordPiece是指将单词划分成一组有限的公共子词单元，能在单词的有效性和字符的灵活性之间取得一个折中的平衡。

2. position embedding：将单词的位置信息编码成特征向量。因为我们的网络结构没有RNN 或者LSTM，因此我们无法得到序列的位置信息，所以需要构建一个position embedding。构建position embedding有两种方法：BERT是初始化一个position embedding，然后通过训练将其学出来；而Transformer是通过制定规则来构建一个position embedding

3. segment embedding：用于区分两个句子的向量表示。这个在问答等非对称句子中是用区别的。

   BERT模型的输入就是wordpiece token embedding + segment embedding + position embedding，如图所示：

![img](https://img-blog.csdnimg.cn/20200814234256151.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

 对于每一种向量的具体表现形式，可以参考这篇文章，可视化的给出了BERT中各种embedding的表现：

 [BERT的嵌入层是如何实现的？看完你就明白了](https://mp.weixin.qq.com/s/DfIAuo775_sHGYi5z9IZyw) 

**2. 网络结构**

 BERT的主要结构是transformer（如图1所示），一个BERT预训练模型的基础结构是标准transformer结构的encoder部分，一个标准transformer结构如图2所示，其中左边的部分就是BERT中使用的encoder部分。

![img](https://img-blog.csdnimg.cn/20200818102421213.PNG?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

一个transformer的encoder单元由一个multi-head-Attention + [Layer](https://so.csdn.net/so/search?q=Layer&spm=1001.2101.3001.7020) Normalization + feedforword + Layer Normalization 叠加产生，BERT的每一层由一个这样的encoder单元构成。在比较大的BERT模型中，有24层encoder，每层中有16个Attention，词向量的维度是1024。在比较小的BERT模型中，有12层encoder，每层有12个Attention，词向量维度是768。在所有情况下，将feed-forward/filter 的大小设置为 4H（H为词向量的维度），即H = 768时为3072，H = 1024时为4096。

​    这种transformer的结构可以使用上下文来预测mask的token，从而捕捉双向关系。

![img](https://img-blog.csdnimg.cn/20200814234510853.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

**2.1 Self-Attention Layer**

（1）self-attention出现的原因

​     a、为了解决RNN、LSTM等常用于处理序列化数据的网络结构无法在GPU中**并行加速计算**的问题

​     b、由于每个目标词是直接与句子中所有词分别计算相关度(attention)的，所以解决了传统的RNN模型中长距离依赖的问题。通过attention，可以将两个距离较远的词之间的距离拉近为1直接计算词的相关度，而传统的RNN模型中，随着距离的增加，词之间的相关度会被削弱。

（2）模型的输入

​    就是前面BERT模型的输入，即 **X=(batch_size, max_len, embedding)，**假设batch_size=1，输入的句子长度为512，每个词的向量表示的长度为768，那么整个模型的输入就是一个512*768的tensor。

（3）单个self-attention 的计算过程

​     每一次的self-attention的计算涉及到三个中间权重矩阵Wq,Wk,Wv，他们分别对输入的X进行线性变换，生成query、key和value这三个新的tensor，整个的计算步骤如 下：

​    step 1：输入X分别与Wq,Wk,Wv矩阵相乘，得到**Q,K,V。**

​    step 2：**Q，K_T**矩阵相乘，得到X中各个词之间的相关度，并scale（为了防止结果过大，除以他们维度的均方根）。

​    step 3：将第二步的相关度通过**Softmax**函数归一化，得到归一化后各个词与其他词的相关度。

​    step 4：将第三步的相关度矩阵与 **V** 相乘，即加权求和，得到每个词新的向量编码。

​    计算图如下所示：

![img](https://img-blog.csdnimg.cn/20200814234732428.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

在BERT小模型中，每个head的神经元个数是64，12个head总的神经元的个数即为768，也就是模型介绍时说的H=768。在上图中单个的的Wq,Wk,Wv都是768*64的矩阵，那么**Q,K,V**则都是512*64的矩阵，**Q，K_T**相乘后的相关度矩阵则为512*512，归一化后跟V相乘后的z矩阵的大小则为512*64，这是一个attention计算出的结果。12个attention则是将12个512*64大小的矩阵横向concat，得到一个512*768大小的多头输出，这个输出再接一层768的全连接层，最后就是整个muti-head-attention的输出了，如图4所示。整个的维度变化过程如下图所示：

![img](https://img-blog.csdnimg.cn/20201011113446535.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

（4）multi-head attention的计算

​    Multi-Head Self-Attention**将多个不同单头的**Self-Attention输出**Concat**成一条，然后再经过一个全连接层降维输出。例如，一个self-attention计算的输出为output_0 = **(batch_size, max_len, w_length)**，那么n个attention进行concat之后，输出就为output_sum = **(batch_size, max_len,n \* w_length)**，这个concat的结果再连一层全连接层即为整个multi-head attention的输出。如下图所示，右边的部分即为一个multi-head attention的计算过程，其中的h指的是attention的个数，即上面例子中的n。

![img](https://img-blog.csdnimg.cn/20200814234822599.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

**2.2 Layer Normalization**

 Self-Attention的输出会经过Layer [Normalization](https://so.csdn.net/so/search?q=Normalization&spm=1001.2101.3001.7020)，为什么选择Layer Normalization而不是Batch Normalization？

​    此时，我们应该先对我们的数据形状有个直观的认识，当一个batch的数据输入模型的时候，形状是长方体如图所示，大小为(batch_size, max_len, embedding)，其中batch_size为batch的批数，max_len为每一批数据的序列最大长度，embedding则为每一个单词或者字的embedding维度大小。而Batch Normalization是在batch间选择同一个位置的值做归一化，相当于是对batch里相同位置的字或者单词embedding做归一化，Layer Normalization是在一个Batch里面的每一行做normalization，相当于是对每句话的embedding做归一化。显然，LN更加符合我们处理文本的直觉。如下图所示。

![img](https://img-blog.csdnimg.cn/20200814234921894.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTE0MTI3Njg=,size_16,color_FFFFFF,t_70)

参考：

[模型优化之Batch Normalization](https://zhuanlan.zhihu.com/p/54171297)

[模型优化之Layer Normalization](https://zhuanlan.zhihu.com/p/54530247)

**2.3 BERT 每一层的学习**

- bert从浅层到高层可以分别学习到surface，短语级别的，句法级别的，和语义级别的信息；
- 长程依赖需要更多层进行建模；
- BERT的self-attention机制能够学习到一些dependency tree的信息

  参考：

  论文：[What does BERT learn about the structure of language?](https://hal.inria.fr/hal-02131630/document)

  [BERT的每一层学习到了哪些语义信息](https://zhuanlan.zhihu.com/p/76066537)

  [理解BERT每一层都学到了什么](https://zhuanlan.zhihu.com/p/74515580)

**3. 模拟预训练**

**3.1 训练任务**

**（1）masked language model**

 随机掩盖掉一些单词，然后通过上下文预测该单词。BERT中有15%的wordpiece token会被随机掩盖，这15%的token中80%用[MASK]这个token来代替，10%用随机的一个词来替换，10%保持这个词不变。这种设计使得模型具有捕捉上下文关系的能力，同时能够有利于token-level tasks例如序列标注。

Q：为什么选中的15%的wordpiece token不能全部用 [MASK]代替，而要用 10% 的 random token 和 10% 的原 token

​    [MASK] 是以一种显式的方式告诉模型『这个词我不告诉你，你自己从上下文里猜』，从而防止信息泄露。如果 [MASK] 以外的部分全部都用原 token，模型会学到『如果当前词是 [MASK]，就根据其他词的信息推断这个词；如果当前词是一个正常的单词，就直接抄输入』。这样一来，在 finetune 阶段，所有词都是正常单词，模型就照抄所有词，不提取单词间的依赖关系了。

​    以一定的概率填入 random token，就是让模型时刻堤防着，在任意 token 的位置都需要把当前 token 的信息和上下文推断出的信息相结合。这样一来，在 finetune 阶段的正常句子上，模型也会同时提取这两方面的信息，因为它不知道它所看到的『正常单词』到底有没有被动过手脚的。

Q：最后怎么利用[MASK] token做的预测？

​    最终的损失函数只计算被mask掉的token的，每个句子里 [MASK] 的个数是不定的。实际代码实现是每个句子有一个 maximum number of predictions，取所有 [MASK] 的位置以及一些 PADDING 位置的向量拿出来做预测（总共凑成 maximum number of predictions 这么多个预测，是定长的），然后再用掩码把 PADDING 盖掉，只计算[MASK]部分的损失。

**（2）next sentence prediction**

​    语料中50%的句子，选择其相应的下一句一起形成上下句，作为正样本；其余50%的句子随机选择一句非下一句一起形成上下句，作为负样本。这种设定，有利于sentence-level tasks，例如问答。注意：作者特意说了语料的选取很关键，要选用document-level的而不是sentence-level的，这样可以具备抽象连续长序列特征的能力。

**3.2 模型训练设置**

**pre-train阶段**

（1）256个句子作为一个batch,每个句子最多512个token。

（2）迭代100万步。

（3）总共训练样本超过33亿。

（4）迭代40个epochs。

（5）用adam学习率， 1 = 0.9, 2 = 0.999。

（6）学习率头一万步保持固定值，之后线性衰减。

（7）L2衰减，衰减参数为0.01。

（8）drop out设置为0.1。

（9）激活函数用GELU代替RELU。

（10）Bert base版本用了16个TPU，Bert large版本用了64个TPU，训练时间4天完成。

（论文定义了两个版本，一个是base版本，一个是large版本。Large版本（L=24, H=1024, A=16, Total Parameters=340M）。base版本（ L=12, H=768, A=12, Total Pa- rameters=110M）。L代表网络层数，H代表隐藏层数，A代表self attention head的数量。）

因为序列长度太大（512）会影响训练速度，所以90%的steps都用seq_len=128训练，余下的10%步数训练512长度的输入。

**fine-tune 阶段**

微调阶段根据不同任务使用不同网络模型。在微调阶段，大部分模型的超参数跟预训练时差不多，除了batchsize，学习率，epochs。

微调参数建议：

Batch size: 16, 32

Learning rate (Adam): 5e-5, 3e-5, 2e-5

Number of epochs: 3, 4

**4. 总结**

**4.1 模型特点**

（1）使用transformer作为算法的主要框架，transformer能**更彻底的捕捉语句中的双向关系**；

（2）使用了mask language model 和next sentence prediction的多任务训练目标，**是一个自监督的过程，不需要数据的标注**；

（3）使用tpu这种强大的机器训练了大规模的预料，是NLP的很多任务达到了全新的高度。

​    BERT本质上是在海量语料的基础上，通过自监督学习的方法为单词学习一个好的特征表示。该模型的优点是可以根据具体的人物进行微调，或者直接使用预训练的模型作为特征提取器。

**4.2 可优化空间**

（1）如何让模型有**捕捉Token序列关系**的能力，而不是简单依靠位置嵌入。

（2）模型太大，太耗机器（后续的Albert有做改进）

**5. Reference**

1. [BERT详解](https://zhuanlan.zhihu.com/p/48612853)
2. [【NLP】Google BERT详解](https://zhuanlan.zhihu.com/p/46652512)
3. [NLP必读：十分钟读懂谷歌BERT模型](https://zhuanlan.zhihu.com/p/51413773)
4. [【NLP】改变NLP格局的利器-BERT(模型和代码解析)](https://zhuanlan.zhihu.com/p/104501321)
5. [论文解读:BERT模型及fine-tuning](https://zhuanlan.zhihu.com/p/46833276)
6. [BERT的原理与应用](https://zhuanlan.zhihu.com/p/101570806)
7. [最强NLP模型BERT可视化学习](https://zhuanlan.zhihu.com/p/55083548)

**6. 看到的比较好的文章**

   （1）BERT模型总结：[BERT模型总结 - ffjsls - 博客园](https://www.cnblogs.com/ffjsls/p/12257158.html)

   （2）图解BERT模型：[图解BERT模型：从零开始构建BERT - 云+社区 - 腾讯云](https://cloud.tencent.com/developer/article/1389555)