from mindspore import transform_checkpoints
transform_checkpoints(
    src_checkpoints_dir="./output/checkpoint/", # 原切分权重文件夹
    dst_checkpoints_dir="./target_checkpoint/", # 目标路径
    ckpt_prefix="glm-6b", # .ckpt文件前缀名
    src_strategy_file="./scripts/mf_parallel0/ckpt_strategy.ckpt", # 步骤1中的切分策略文件路径
    dst_strategy_file=None # None表示不切分，权重合一
)