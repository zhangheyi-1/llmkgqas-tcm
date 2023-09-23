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
"""MindFormers Pipeline API."""
from .pipeline import pipeline
from .build_pipeline import build_pipeline
from .base_pipeline import BasePipeline
from .image_classification_pipeline import ImageClassificationPipeline
from .zero_shot_image_classification_pipeline import ZeroShotImageClassificationPipeline
from .translation_pipeline import TranslationPipeline
from .fill_mask_pipeline import FillMaskPipeline
from .text_classification_pipeline import TextClassificationPipeline
from .token_classification_pipeline import TokenClassificationPipeline
from .question_answering_pipeline import QuestionAnsweringPipeline
from .text_generation_pipeline import TextGenerationPipeline
from .masked_image_modeling_pipeline import MaskedImageModelingPipeline


__all__ = ['ZeroShotImageClassificationPipeline',
           'ImageClassificationPipeline', 'pipeline', 'BasePipeline']

__all__.extend(translation_pipeline.__all__)
__all__.extend(fill_mask_pipeline.__all__)
__all__.extend(text_classification_pipeline.__all__)
__all__.extend(token_classification_pipeline.__all__)
__all__.extend(question_answering_pipeline.__all__)
__all__.extend(text_generation_pipeline.__all__)
__all__.extend(masked_image_modeling_pipeline.__all__)
