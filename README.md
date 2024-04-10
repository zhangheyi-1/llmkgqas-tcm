# llmkgqas-tcm
联系方式：1183916225@qq.com

待整理后系统相关内容后上传。由于github用户空间不足，bert-filter模块上传至gitee:https://gitee.com/zhangheyijzy/bert-filter。

由于chatGLM版本更新，该项目代码版本和官方模型不适配，请在官网下载最新版本代码进行p-tuning v2。并在p-tuning下启动api.py，以启动模型接口进行推理。

本地知识库构建基于项目langchain-Chatchat（https://github.com/chatchat-space/Langchain-Chatchat） 项目，需要自行在其knowledge_base目录下添加专业语料，并进行向量知识库初始化构建本地知识库。前端和本地知识库由于涉及私有数据涉及版权问题，这里不进行开源上传，请自行构建，注意修改对外访问端口与模型推理端口。


# 目录说明
（待添加）
# 参考：
<br>ChatGLM-6B微调的方式具体请参考https://github.com/THUDM/ChatGLM-6B中的教程，下述微调过程式旧版本的参考，在新版本中此文件已被删除。<br>
1.微调<br>

打开finetuning_pt.py文件，修改instruction为自己领域的instruction<br>

![image](https://github.com/zhangheyi-1/llmkgqas-tcm/assets/70568061/03a296b4-d281-46f8-953d-4dd236ff7674)

参考命令：
```
CUDA_VISIBLE_DEVICES=0 python3 main.py     --do_train     --train_file data/tcm.json     --validation_file data/tcm.json     --prompt_column text     --response_column answer     --overwrite_cache     --model_name_or_path /home/heyi.zhang/huggingface/THUDM/chatglm-6b/     --output_dir output/adgen-chatglm-6b-pt-128     --overwrite_output_dir     --max_source_length 768     --max_target_length 768     --per_device_train_batch_size 2     --per_device_eval_batch_size 2     --gradient_accumulation_steps 16     --predict_with_generate     --max_steps 100     --logging_steps 10     --save_steps 50     --learning_rate 2e-2     --pre_seq_len 128     --quantization_bit 4
```

效果不好可以调整学习率,可以通过以下命令使用命令行的形式测试效果

`CUDA_VISIBLE_DEVICES=1 python cli_demo.py`

注意修改cli_demo.py中的参数，主要是CHECKPOINT_PATH
启动
```
cd /xxx/ChatGLM-6B/ptuning/
CUDA_VISIBLE_DEVICES=2 nohup python ./api.py > info.log 2>&1 &
```

2.LangChain新版<br>
初始化好本地知识库后进行启动的命令参考。
```
cd /xxx/Langchain-Chatchat/
CUDA_VISIBLE_DEVICES=1 nohup python ./server/llm_api.py > info_llm.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 nohup python ./server/api.py > info_api.log 2>&1 &
```

3.管道端口映射<br>
`ssh -L 3000:服务器ip:3000 -L 8100:服务器ip:8100 8200:服务器ip:8200 -L 8300:服务器ip:8300 username@服务器ip `
前端若部署在本地的话就不用映射3000，若是本地可以运行模型服务也可以不映射。3000是前端映射，8100是信息过滤后台端口映射，8200/8300分别是问答推理与知识抽取端口映射。有需要的话也可以将自建的知识图谱端口进行映射。
