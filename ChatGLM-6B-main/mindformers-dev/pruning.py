import mindspore as ms
from mindspore import context
context.set_context(device_target="CPU")
from mindformers.tools.register import MindFormerConfig
from mindformers.models.glm import GLMConfig,GLMChatModel
config = GLMConfig(MindFormerConfig('./checkpoint_download/glm/glm_6b.yaml'))
model_from_config = GLMChatModel(config)
print("模型加载完成")
ckpt_path = "./target_checkpoint/rank_0/glm-6b.ckpt"
param_dict = ms.load_checkpoint(ckpt_path)
print("读取数据完成")
new_param_dict = {}
for key, value in param_dict.items():
    if "adam" not in key.lower():
        new_param_dict[key] = value
print("参数过滤完成")
param_not_load, _ = ms.load_param_into_net(model_from_config, new_param_dict)
print("加载完成")
ms.save_checkpoint(model_from_config, "./target_checkpoint/rank_0/glm-6b_pruning.ckpt")