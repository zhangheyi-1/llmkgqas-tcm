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
"""
Test module for testing the t5 trainer used for mindformers.
How to run this:
pytest tests/st/test_model/test_t5_model/test_t5_trainer.py
"""
import os
import shutil

import numpy as np
# import pytest
from mindspore.dataset import MindDataset, GeneratorDataset
from mindspore.mindrecord import FileWriter

from mindformers.trainer import Trainer, TranslationTrainer
from mindformers.trainer.config_args import ConfigArguments, \
    OptimizerConfig, RunnerConfig
from mindformers import T5Config, T5ForConditionalGeneration


def generator(src_length=16, target_length=8):
    """dataset generator"""
    input_ids = np.random.randint(low=0, high=15, size=(src_length,)).astype(np.int32)
    attention_mask = np.ones((src_length,)).astype(np.int32)
    labels = np.random.randint(low=0, high=15, size=(target_length,)).astype(np.int32)

    for _ in range(2):
        yield input_ids, attention_mask, labels


def write_mindrecord(ds_generator, data_record_path):
    """Using the generator to get mindrecords"""
    ds = GeneratorDataset(ds_generator, column_names=["input_ids", "attention_mask", "labels"])

    writer = FileWriter(file_name=data_record_path, shard_num=1, overwrite=True)
    data_schema = {"input_ids": {"type": "int32", "shape": [-1]},
                   "attention_mask": {"type": "int32", "shape": [-1]},
                   "labels": {"type": "int32", "shape": [-1]}}
    writer.add_schema(data_schema, "test_schema")
    for item in ds.create_dict_iterator():
        for k in item.keys():
            item[k] = item[k].asnumpy()
        writer.write_raw_data([item])
    writer.commit()

def modify_attrs(net, key, value):
    if hasattr(net, key):
        setattr(net, key, value)
        print(f"Set the net {net.__class__.__name__} with {key}:{value}")
    for cell in net.cells():
        modify_attrs(cell, key, value)

def write_raw_text_data(stage, data_record_path):
    """writes the fake translation data"""
    source = ["We went through the whole range of emotions during this period.",
              "The positive reaction of pilots and Federation officials makes me hope that this year we will "
              "be organizing champions again"
              " said rally manager, Dan Codreanu."]
    target = ['Am trecut prin toată gama de trăiri în această perioadă.',
              "Reacția pozitivă a piloților și oficialilor Federației mă face să sper că vom fi și în acest an "
              "campion la organizare a spus managerul raliului, Dan Codreanu."]

    src_path = os.path.join(data_record_path, f'{stage}.source')
    tgt_path = os.path.join(data_record_path, f'{stage}.target')
    with open(src_path, 'w') as sfp:
        with open(tgt_path, 'w') as tfp:
            for x, y in zip(source, target):
                sfp.write(x + '\n')
                tfp.write(y + '\n')


# @pytest.mark.level0
# @pytest.mark.platform_arm_ascend_training
# @pytest.mark.env_onecard
class TestTranslationTrainer:
    """Test Translation Trainer"""
    def setup_class(self):
        self.dir_path = os.path.join(os.path.dirname(__file__), 'fake_dataset')
        os.makedirs(self.dir_path, exist_ok=True)
        self.abs_path = os.path.join(self.dir_path, 't5_dataset')
        write_mindrecord(generator(src_length=16, target_length=8), self.abs_path)

        self.raw_text_path = os.path.join(os.path.dirname(__file__), 'raw_text_dataset')
        os.makedirs(self.raw_text_path, exist_ok=True)
        write_raw_text_data(stage='train', data_record_path=self.raw_text_path)

    def teardown_class(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)
        shutil.rmtree(self.raw_text_path, ignore_errors=True)

    def get_mindfiles_from_path(self, dir_path):
        dataset_files = []
        for r, _, f in os.walk(dir_path):
            for file in f:
                if not file.endswith("db"):
                    dataset_files.append(os.path.join(r, file))
        return dataset_files

    def test_trainer_with_translation_args_train(self):
        """
        Feature: Create Trainer From Config
        Description: Test Trainer API to train from config
        Expectation: TypeError
        """
        batch_size = 1
        runner_config = RunnerConfig(epochs=1, batch_size=batch_size)  # 运行超参
        optim_config = OptimizerConfig(optim_type='AdamWeightDecay', beta1=0.9, learning_rate=0.001)

        dataset = MindDataset(dataset_files=self.get_mindfiles_from_path(self.dir_path),
                              columns_list=["input_ids", "attention_mask", "labels"])
        dataset = dataset.batch(batch_size=batch_size)
        dataset = dataset.repeat(1)

        config = ConfigArguments(seed=2022, runner_config=runner_config, optimizer=optim_config)
        model_config = T5Config(batch_size=batch_size, num_heads=8, num_layers=1, hidden_size=32,
                                seq_length=16, max_decode_length=8)
        # Model
        model = T5ForConditionalGeneration(model_config)
        mim_trainer = Trainer(task='translation',
                              model=model,
                              args=config,
                              train_dataset=dataset)
        mim_trainer.train(resume_or_finetune_from_checkpoint=False)

    def test_trainer_predict(self):
        """
        Feature: Test Predict of the Trainer
        Description: Test Predict
        Expectation: TypeError
        """
        # change the length for quick training
        model = T5ForConditionalGeneration.from_pretrained('t5_small', seq_length=32, max_decode_length=32)
        mim_trainer = TranslationTrainer(model_name="t5_small")
        res = mim_trainer.predict(input_data="hello world", network=model)
        assert res == [{'translation_text': ['hello world']}]

        res = mim_trainer.predict(input_data="hello world", network=model, max_length=1)
        assert len(res[0]['translation_text']) == 1

        res = mim_trainer.predict(input_data=["hello world", "I am not happy"], network=model)
        assert res == [{'translation_text': ['hello world']}, {'translation_text': ['.']}]

        res = mim_trainer.predict(input_data=os.path.join(self.raw_text_path, 'train.source'), network=model)
        assert res == [{'translation_text': ['Wir haben während dieser Period die ganze Reihe '
                                             'von emotions durchlebt.']},
                       {'translation_text': ['Die positive Reaktion der Piloten und der Föderation-Beamten macht mich '
                                             'erfreut, dass wir dieses Jahr wieder']}]

        from mindformers.dataset.dataloader.wmt16_dataloader import WMT16DataLoader
        dataset = WMT16DataLoader(self.raw_text_path, column_names=['src_language', 'tgt_language'])
        res = mim_trainer.predict(input_data=dataset,
                                  network=model,
                                  max_length=32,
                                  keys={'src_language': 'src_language', 'tgt_language': 'tgt_language'},
                                  batch_size=1)
        assert res == [{'translation_text': ['Die positive Reaktion der Piloten und der Föderation-Beamten macht mich '
                                             'erfreut, dass wir dieses Jahr wieder']},
                       {'translation_text': ['Wir haben während dieser Period die ganze Reihe von '
                                             'emotions durchlebt.']}]

    # def test_translation_trainer_train(self):
    #     """
    #     Feature: Create Trainer From Config
    #     Description: Test Trainer API to train from config
    #     Expectation: TypeError
    #     """
    #     batch_size = 1
    #     model_name = 't5_small'
    #     runner_config = RunnerConfig(epochs=1, batch_size=batch_size)  # 运行超参
    #     optim_config = OptimizerConfig(optim_type='AdamWeightDecay', beta1=0.9, learning_rate=1e-5)
    #
    #     dataset = MindDataset(dataset_files=self.get_mindfiles_from_path(self.dir_path),
    #                           columns_list=["input_ids", "attention_mask", "labels"])
    #     dataset = dataset.batch(batch_size=batch_size)
    #     dataset = dataset.repeat(1)
    #
    #     config = ConfigArguments(seed=2022, runner_config=runner_config, optimizer=optim_config)
    #     # make the batch size inconsistent with the mindtaset, to check batch size will not cause the error.
    #     model_config = T5Config(batch_size=batch_size*2, num_heads=8,
    #                             num_layers=1, hidden_size=512,
    #                             seq_length=16, max_decode_length=8)
    #
    #     mim_trainer = TranslationTrainer(model_name=model_name)
    #     config = MindFormerConfig("configs/t5/run_t5_tiny_on_wmt16.yaml")
    #
    #     # 1) test train using config
    #     config.model.model_config.seq_length = model_config.seq_length
    #     config.model.model_config.max_decode_length = model_config.max_decode_length
    #     mim_trainer.train(config=config, dataset=dataset)
    #     # 2) test train using network as inputs
    #     dataset = MindDataset(dataset_files=self.get_mindfiles_from_path(self.dir_path),
    #                           columns_list=["input_ids", "attention_mask", "labels"])
    #     dataset = dataset.batch(batch_size=batch_size)
    #     dataset = dataset.repeat(1)
    #
    #     model = T5ForConditionalGeneration.from_pretrained(model_name, seq_length=16, max_decode_length=8)
    #     mim_trainer.train(config=config, dataset=dataset, network=model)
