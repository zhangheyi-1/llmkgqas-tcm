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
"""Base Dataset."""
import os

import mindspore as ms
import mindspore.dataset as ds

from mindformers.tools.logger import logger


class BaseDataset:
    """Base Dataset."""
    def __init__(self, dataset_config: dict = None):
        self.dataset_config = dataset_config

    @classmethod
    def init_dataset_config(cls, dataset_config):
        """Init dataset config."""
        if dataset_config is None:
            raise ValueError("dataset_config cannot be None!")

        ds.config.set_seed(dataset_config.seed)
        ds.config.set_prefetch_size(dataset_config.prefetch_size)
        ds.config.set_numa_enable(dataset_config.numa_enable)

        if dataset_config.auto_tune:
            if dataset_config.profile:
                raise EnvironmentError(
                    "MindSpore's AutoTune is enabled, so Profile cannot be enabled,"
                    "now Profile's flag is True, please set to False!")
            os.makedirs(dataset_config.filepath_prefix, exist_ok=True)
            dataset_config.filepath_prefix = os.path.join(dataset_config.filepath_prefix, "autotune")
            ds.config.set_enable_autotune(True, filepath_prefix=dataset_config.filepath_prefix)
            ds.config.set_autotune_interval(dataset_config.autotune_per_step)

        if cls._is_semi_full_batch():
            logger.info("Now the semi auto parallel mode is used and full_batch is True,"
                        "and the shuffle of the dataset is required to be False,"
                        "so as to ensure that the data loaded on each card is consistent "
                        "and to avoid the problem of non-convergence of loss.")
            dataset_config.data_loader.shuffle = False

    @classmethod
    def _check_device_rank_for_parallel(cls, rank_id, device_num):
        """Check device num and rank id in auto parallel mode."""
        if cls._is_semi_full_batch():
            rank_id = None
            device_num = None
        return rank_id, device_num

    @classmethod
    def _is_semi_full_batch(cls):
        return ((ms.context.get_auto_parallel_context("parallel_mode") in ['semi_auto_parallel', 'auto_parallel'])
                and ms.context.get_auto_parallel_context("full_batch"))

    @classmethod
    def _is_data_parallel(cls):
        return ms.context.get_auto_parallel_context("parallel_mode") == ms.context.ParallelMode.DATA_PARALLEL
