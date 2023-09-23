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
Test module for testing the glm interface used for mindformers.
How to run this:
pytest tests/st/test_model/test_glm_model/test_glm_trainer.py
"""
import numpy as np
import pytest

from mindspore import context
from mindspore.dataset import GeneratorDataset

from mindformers import AutoTokenizer
from mindformers import GLMForPreTraining, GLMChatModel, GLMConfig
from mindformers import Trainer, TrainingArguments


def generator_train():
    """train dataset generator"""
    seq_len = 128
    input_ids = np.random.randint(low=0, high=15, size=(seq_len,)).astype(np.int32)
    label = np.random.randint(low=0, high=15, size=(seq_len,)).astype(np.int32)
    position_ids = np.ones((2, seq_len)).astype(np.int64)
    attention_mask = np.ones(shape=(seq_len, seq_len)).astype(np.int32)
    train_data = (input_ids, label, position_ids, attention_mask)
    for _ in range(512):
        yield train_data


def generator_eval():
    """eval dataset generator"""
    seq_len = 512
    input_ids = np.random.randint(low=0, high=15, size=(seq_len,)).astype(np.int32)
    label = np.random.randint(low=0, high=15, size=(seq_len,)).astype(np.int32)
    eval_data = (input_ids, label)
    for _ in range(8):
        yield eval_data


@pytest.mark.level0
@pytest.mark.platform_x86_ascend_training
@pytest.mark.platform_arm_ascend_training
@pytest.mark.env_onecard
class TestGLMTrainerMethod:
    """A test class for testing pipeline."""

    def setup_method(self):
        """init task trainer."""
        context.set_context(mode=0)

        args = TrainingArguments(num_train_epochs=1, batch_size=2)
        train_dataset = GeneratorDataset(generator_train,
                                         column_names=["input_ids", "label", "position_ids", "attention_mask"])
        eval_dataset = GeneratorDataset(generator_eval, column_names=["input_ids", "label"])
        train_dataset = train_dataset.batch(batch_size=2)
        eval_dataset = eval_dataset.batch(batch_size=2)

        model_config = GLMConfig(num_layers=2, hidden_size=32, inner_hidden_size=None,
                                 num_heads=2, position_encoding_2d=True)
        model = GLMForPreTraining(model_config)
        self.tokenizer = AutoTokenizer.from_pretrained("glm_6b")
        self.task_trainer = Trainer(task='text_generation',
                                    model=model,
                                    tokenizer=self.tokenizer,
                                    args=args,
                                    train_dataset=train_dataset,
                                    eval_dataset=eval_dataset)

    def test_train(self):
        """
        Feature: Trainer.train()
        Description: Test trainer for train.
        Expectation: TypeError, ValueError, RuntimeError
        """
        self.task_trainer.train()

    # def test_eval(self):
    #     """
    #     Feature: Trainer.evaluate()
    #     Description: Test trainer for evaluate.
    #     Expectation: TypeError, ValueError, RuntimeError
    #     """
    #     self.task_trainer.evaluate()

    def test_predict(self):
        """
        Feature: Trainer.predict()
        Description: Test trainer for predict.
        Expectation: TypeError, ValueError, RuntimeError
        """
        model_config = GLMConfig(num_layers=2, hidden_size=32, inner_hidden_size=None,
                                 num_heads=2, position_encoding_2d=True)
        model = GLMChatModel(model_config)
        task_trainer = Trainer(task='text_generation',
                               model=model,
                               tokenizer=self.tokenizer)
        task_trainer.predict(input_data="你好", max_length=20)

    def test_finetune(self):
        """
        Feature: Trainer.finetune()
        Description: Test trainer for finetune.
        Expectation: TypeError, ValueError, RuntimeError
        """
        self.task_trainer.finetune()
