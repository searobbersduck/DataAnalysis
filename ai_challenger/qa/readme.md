## 介绍
[观点型问题阅读理解](https://challenger.ai/competition/oqmrc2018)

## 数据处理
1. 统计训练数据的信息，参见`dataset.py`
2. 调用`spm_train --input=./dataset/ai_challenger_oqmrc_trainingset_20180816/qa_train.txt --model_prefix=subword --vocab_size=8000 --character_coverage=0.9995 --model_type=bpe`生成字典和向量表
