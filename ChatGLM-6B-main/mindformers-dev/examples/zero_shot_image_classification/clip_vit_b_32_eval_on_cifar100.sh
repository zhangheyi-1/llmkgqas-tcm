#!/bin/bash
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

echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash examples/zero_shot_image_classification/clip_vit_b_32_eval_on_cifar100.sh"
echo "The data setting could refer to ./docs/task_cards/zero_shot_image_classification.md"
echo "It is better to use absolute path."
echo "=============================================================================================================="

python run_mindformer.py --config ./configs/clip/run_clip_vit_b_32_zero_shot_image_classification_cifar100.yaml
