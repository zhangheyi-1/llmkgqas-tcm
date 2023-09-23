# Copyright 2023 Huawei Technologies Co., Ltd
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
"""
Note: Low-Rank Adapter algrithm for mindformers' pretrained model.
Reference: https://arxiv.org/abs/2106.09685
"""
import re

from mindspore import nn
from tk.delta.lora import LoRADense

from mindformers.modules.layers import Linear
from mindformers.tools.logger import logger
from .pet_adapter import PetAdapter
from ..pet_config import PetConfig
from ..utils import re_match_list


def recursive_replace_dense_cell(net, config):
    """default replace all dense."""
    # pylint: disable=W0212
    for name, cell in net._cells.items():
        if cell:
            # add white list spaces.
            if re_match_list(name, config.exclude_layers):
                continue
            if re.match(config.reg_rules, name):
                if not isinstance(cell, nn.Dense) and not isinstance(cell, Linear):
                    continue
                in_channels = cell.in_channels
                out_channels = cell.out_channels
                dest_cell = LoRADense(in_channels=in_channels,
                                      out_channels=out_channels,
                                      lora_rank=config.lora_rank,
                                      lora_alpha=config.lora_alpha,
                                      lora_dropout=config.lora_dropout,
                                      has_bias=cell.has_bias,
                                      activation=cell.activation)

                # load weight of oriangal layers.
                dest_cell.matmul = cell.matmul
                dest_cell.weight = cell.weight
                if cell.has_bias:
                    dest_cell.bias = cell.bias
                    dest_cell.bias_add = cell.bias_add

                # Shard strategies now only support loaded by linear layers.
                if isinstance(cell, Linear):
                    strategy_matmul = cell.matmul.in_strategy

                    dest_cell.lora_dropout.dropout.shard((strategy_matmul[0],))
                    if cell.transpose_b:
                        dest_cell.lora_a_matmul.shard((strategy_matmul[0], (1, strategy_matmul[1][1])))
                        dest_cell.lora_b_matmul.shard(((strategy_matmul[0][0], 1), (strategy_matmul[1][0], 1)))
                        dest_cell.mul.shard(((strategy_matmul[0][0], strategy_matmul[1][0]), ()))
                        dest_cell.add.shard(((strategy_matmul[0][0], strategy_matmul[1][0]),
                                             (strategy_matmul[0][0], strategy_matmul[1][0])))
                    else:
                        dest_cell.lora_a_matmul.shard((strategy_matmul[0], (strategy_matmul[1][0], 1)))
                        dest_cell.lora_b_matmul.shard(((strategy_matmul[0][0], 1), (1, strategy_matmul[1][1])))
                        dest_cell.mul.shard(((strategy_matmul[0][0], strategy_matmul[1][1]), ()))
                        dest_cell.add.shard(((strategy_matmul[0][0], strategy_matmul[1][1]),
                                             (strategy_matmul[0][0], strategy_matmul[1][1])))

                # pylint: disable=W0212
                net._cells[name] = dest_cell
            else:
                recursive_replace_dense_cell(cell, config)
    return net


class LoraAdapter(PetAdapter):
    r"""
    LoraAdapter is the adapter to modify the pretrained model, which uses lora tuning algorithm.

    Args:
        model (BaseModel): The base pretrained model of mindformers.
        pet_config (PetConfig): The configurition of the Pet model.
    Return:
        model (BaseModel): The model replace the linear layer with lora dense layer.
    Examples:
        1.modify certain task of llama
        >>> from mindformers.pet.tuners.lora_adapter import LoraAdapter
        >>> class LlamaForCausalLMWithLora(LlamaForCausalLM):
        >>>        def __init__(self, config: LlamaConfig = None, pet=None):
        >>>            super().__init__(config)
        >>>            # get Pet tuning model.
        >>>            self.pet = pet
        >>>            self.pet.pet_config.reg_rules = r'.*wq|.*wv'
        >>>            self.model = LoraAdapter.get_pet_model(self.model, self.pet.pet_config)
        >>>            # freeze pretrained model
        >>>            PetAdapter.freeze_pretrained_model(self, self.pet.pet_type)
        2.modify certain model of llama
        >>> from mindformers.pet.tuners.lora_adapter import LoraAdapter
        >>> from mindformers.model.llama import LlamaModel
        >>> from mindformers.pet.pet_config import LoraConfig
        >>> llama_model = LlamaModel()
        >>> pet_config = LoraConfig()
        >>> llama_pet_model = LoraAdapter.get_pet_model(llama_model, pet_config)
    """
    @classmethod
    def get_pet_model(cls, model: nn.Cell = None, config: PetConfig = None):
        model = model if model else PetAdapter.get_pretrained_model(config)
        if config.reg_rules is None:
            logger.warning("Lora Adapter use default replace rules: \'.*dense*|*linear*\'")
            config.reg_rules = r'.*dense*|.*linear*'
        model = recursive_replace_dense_cell(model, config)
        return model
