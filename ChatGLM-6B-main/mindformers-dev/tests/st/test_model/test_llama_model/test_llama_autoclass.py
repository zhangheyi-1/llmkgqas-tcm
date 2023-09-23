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
Test module for testing the gpt interface used for mindformers.
How to run this:
pytest tests/st/test_model/test_llm_model/test_auto_class.py
"""
import os
import pytest

# pylint: disable=W0611
from mindformers import MindFormerBook, AutoModel, AutoConfig, AutoTokenizer, AutoProcessor
# pylint: disable=W0611
from mindformers.models import BaseModel, BaseConfig, BaseTokenizer, BaseProcessor


@pytest.mark.level0
@pytest.mark.platform_x86_cpu
@pytest.mark.env_onecard
class TestAutoClassMethod:
    '''A test class for testing Model classes'''
    def setup_method(self):
        """setup method."""
        self.save_directory = os.path.join(MindFormerBook.get_project_path(), 'checkpoint_save')
        # 可往列表中添加llm类模型type 'pangualpha_2_6b', 'llama_7b', 'glm_6b', 'bloom_7b'
        self.test_llm_list = ['llama_7b']

    # def test_llm_model(self):
    #     """
    #     Feature: AutoModel.
    #     Description: Test to get LL-Model instance by input model type.
    #     Expectation: TypeError, ValueError, RuntimeError
    #     """
    #     # input model name, load model and weights
    #     for model_type in self.test_llm_list:
    #         model = AutoModel.from_pretrained(model_type)
    #         assert isinstance(model, BaseModel)
    #         model.save_pretrained(
    #             save_directory=os.path.join(self.save_directory, model_type),
    #             save_name=model_type + '_model')

    def test_llm_config(self):
        """
        Feature: AutoConfig.
        Description: Test to get config instance by input config type.
        Expectation: TypeError, ValueError, RuntimeError
        """
        # input model config name, load model and weights
        for config_type in self.test_llm_list:
            model_config = AutoConfig.from_pretrained(config_type)
            assert isinstance(model_config, BaseConfig)
            model_config.save_pretrained(
                save_directory=os.path.join(self.save_directory, config_type),
                save_name=config_type + '_config')

    def test_llm_processor(self):
        """
        Feature: AutoConfig.
        Description: Test to get config instance by input config type.
        Expectation: TypeError, ValueError, RuntimeError
        """
        # input processor name
        for processor_type in self.test_llm_list:
            processor = AutoProcessor.from_pretrained(processor_type)
            assert isinstance(processor, BaseProcessor)
            processor.save_pretrained(
                save_directory=os.path.join(self.save_directory, processor_type),
                save_name=processor_type + '_processor')

    def test_llm_tokenizer(self):
        """
        Feature: AutoTokenizer, input config.
        Description: Test to get tokenizer instance by input tokenizer type.
        Expectation: TypeError, ValueError, RuntimeError
        """
        # input processor name
        for tokenizer_type in self.test_llm_list:
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_type)
            assert isinstance(tokenizer, BaseTokenizer)
            tokenizer.save_pretrained(
                save_directory=os.path.join(self.save_directory, tokenizer_type),
                save_name=tokenizer_type + '_tokenizer')
