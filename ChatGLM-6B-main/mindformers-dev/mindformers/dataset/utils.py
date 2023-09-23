# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Dataset Utils."""


def check_dataset_config(config):
    """Check dataset config."""
    if config.train_dataset is not None:
        config.train_dataset.do_eval = False
        config.train_dataset.seed = config.seed
        config.train_dataset.auto_tune = config.auto_tune
        config.train_dataset.filepath_prefix = config.filepath_prefix
        config.train_dataset.autotune_per_step = config.autotune_per_step
        config.train_dataset.profile = config.profile
        config.train_dataset.batch_size = config.runner_config.batch_size
        if config.train_dataset.mixup_op:
            config.train_dataset.mixup_op.num_classes = config.runner_config.num_classes
        config.train_dataset_task.dataset_config = config.train_dataset

    if config.eval_dataset is not None:
        config.eval_dataset.do_eval = True
        config.eval_dataset.seed = config.seed
        config.eval_dataset.auto_tune = config.auto_tune
        config.eval_dataset.filepath_prefix = config.filepath_prefix
        config.eval_dataset.autotune_per_step = config.autotune_per_step
        config.eval_dataset.profile = config.profile
        config.eval_dataset.batch_size = config.runner_config.batch_size
        config.eval_dataset_task.dataset_config = config.eval_dataset
