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

"""TextClassificationPipeline"""
import os.path

import numpy as np
from mindspore import ops, Tensor
from ..auto_class import AutoProcessor, AutoModel
from ..mindformer_book import MindFormerBook
from .base_pipeline import BasePipeline
from ..tools.register import MindFormerRegister, MindFormerModuleType
from ..models import BaseModel, Tokenizer
from ..dataset.labels import mnli_labels

__all__ = ['TextClassificationPipeline']

@MindFormerRegister.register(MindFormerModuleType.PIPELINE, alias="text_classification")
class TextClassificationPipeline(BasePipeline):
    """Pipeline for text classification

    Args:
        model (Union[str, BaseModel]): The model used to perform task,
            the input could be a supported model name, or a model instance
            inherited from BaseModel.
        tokenizer : a tokenizer (None or Tokenizer) for text processing.

    Raises:
        TypeError: If input model and image_processor's types are not corrected.
        ValueError: If the input model is not in support list.

    Examples:
        >>> from mindformers.pipeline import TextClassificationPipeline
        >>> from mindformers import AutoTokenizer, BertForMultipleChoice, AutoConfig
        >>> input_data = ["The new rights are nice enough-Everyone really likes the newest benefits ",
        ...               "i don't know um do you do a lot of camping-I know exactly."]
        >>> tokenizer = AutoTokenizer.from_pretrained('txtcls_bert_base_uncased_mnli')
        >>> txtcls_mnli_config = AutoConfig.from_pretrained('txtcls_bert_base_uncased_mnli')
        >>> model = BertForMultipleChoice(txtcls_mnli_config)
        >>> txtcls_pipeline = TextClassificationPipeline(task='text_classification',
        ...                                              model=model,
        ...                                              tokenizer=tokenizer,
        ...                                              max_length=model.config.seq_length,
        ...                                              padding="max_length")
        >>> results = txtcls_pipeline(input_data, top_k=1)
        >>> print(results)
            [[{'label': 'neutral', 'score': 0.9714198708534241}],
            [{'label': 'contradiction', 'score': 0.9967639446258545}]]
    """
    _support_list = MindFormerBook.get_pipeline_support_task_list()['text_classification'].keys()

    def __init__(self, model, tokenizer=None, **kwargs):
        if isinstance(model, str):
            if model in self._support_list or os.path.isdir(model):
                if tokenizer is None:
                    tokenizer = AutoProcessor.from_pretrained(model).tokenizer
                model = AutoModel.from_pretrained(model)
                if not isinstance(tokenizer, Tokenizer):
                    raise TypeError(f"tokenizer should be inherited from"
                                    f" BaseTokenizer, but got {type(tokenizer)}.")
            else:
                raise ValueError(f"{model} is not supported by {self.__class__.__name__},"
                                 f"please selected from {self._support_list}.")

        if not isinstance(model, BaseModel):
            raise TypeError(f"model should be inherited from BaseModel, but got type {type(model)}.")

        if tokenizer is None:
            raise ValueError(f"{self.__class__.__name__}"
                             " requires for a tokenizer.")

        super().__init__(model, tokenizer, **kwargs)

    def _sanitize_parameters(self, **pipeline_parameters):
        """sanitize parameters for preprocess, forward, and postprocess."""
        if 'batch_size' in pipeline_parameters:
            raise ValueError(f"The {self.__class__.__name__} does not support batch inference, please remove the "
                             f"batch_size")

        postprocess_params = {}

        forward_key_name = ['top_k', 'top_p', 'do_sample', 'eos_token_id', 'repetition_penalty', 'max_length']
        forward_kwargs = {}
        for item in forward_key_name:
            if item in pipeline_parameters:
                forward_kwargs[item] = pipeline_parameters.get(item)

        preprocess_key_name = ['top_k', 'top_p', 'do_sample', 'eos_token_id', 'repetition_penalty', 'max_length',
                               'padding']
        preprocess_params = {k: v for k, v in pipeline_parameters.items() if k in preprocess_key_name}

        if "top_k" in pipeline_parameters:
            postprocess_params["top_k"] = pipeline_parameters.get("top_k")
        return preprocess_params, forward_kwargs, postprocess_params

    def inputs_process(self, inputs_zero, inputs_one):
        """
        process of two sentences relationship classification

        Args:
            inputs_zero (str): the first sentence
            inputs_one (str): the second sentence

        Return:
            processed inputs, mask, token_type about two sentences
        """
        len_inputs = len(inputs_zero["input_ids"])
        inputs_zero_input = list(inputs_zero["input_ids"].asnumpy())
        inputs_one_input = list(inputs_one["input_ids"].asnumpy())
        inputs_zero_input = [x for x in inputs_zero_input if x != 0]
        inputs_one_input = [x for x in inputs_one_input if x != 0]
        token_type = [0] * len(inputs_zero_input) + [1] * (len(inputs_one_input) - 1)
        token_type = token_type + [0] * (len_inputs - len(token_type))
        inputs = inputs_zero_input + inputs_one_input[1:]
        len_inputs_mask = len(inputs)
        inputs = inputs + [0] * (len_inputs - len(inputs))
        mask = [1] * len_inputs_mask + [0] * (len_inputs - len_inputs_mask)
        return inputs, mask, token_type

    def preprocess(self, inputs, **preprocess_params):
        """
        Preprocess of text classification

        Args:
            inputs (str): the str to be classified.
            max_length (int): max length of tokenizer's output
            padding (False / "max_length"): padding for max_length
            return_tensors ("ms"): the type of returned tensors

        Return:
            processed text.
        """
        if not isinstance(inputs, str):
            raise ValueError("Inputs type must be str")
        if '-' not in inputs:
            raise ValueError("two texts of text pair should be split by -")
        inputs = inputs.split('-')
        max_length = preprocess_params.pop("max_length", 128)
        padding = preprocess_params.pop("padding", "max_length")
        inputs_zero = self.tokenizer(inputs[0], max_length=max_length, padding=padding,
                                     return_tensors="ms", **preprocess_params)
        inputs_one = self.tokenizer(inputs[1], max_length=max_length, padding=padding,
                                    return_tensors="ms", **preprocess_params)
        inputs, mask, token_type = self.inputs_process(inputs_zero, inputs_one)
        inputs_final = {}
        inputs_final["input_ids"] = Tensor.from_numpy(np.array(inputs, dtype=np.int32))
        inputs_final["attention_mask"] = Tensor.from_numpy(np.array(mask, dtype=np.int32))
        inputs_final["token_type_ids"] = Tensor.from_numpy(np.array(token_type, dtype=np.int32))
        expand_dims = ops.ExpandDims()
        return {"input_ids": expand_dims(inputs_final["input_ids"], 0),
                "input_mask": expand_dims(inputs_final["attention_mask"], 0),
                "token_type_id": expand_dims(inputs_final["token_type_ids"], 0),
                "label_ids": None}

    def forward(self, model_inputs, **forward_params):
        """
        Forward process

        Args:
            model_inputs (dict): outputs of preprocess.

        Return:
            probs dict.
        """
        forward_params.pop("None", None)
        output_ids = self.model(**model_inputs)
        return output_ids

    def softmax(self, outputs):
        maxes = np.max(outputs, axis=-1, keepdims=True)
        shifted_exp = np.exp(outputs - maxes)
        return shifted_exp / shifted_exp.sum(axis=-1, keepdims=True)

    def postprocess(self, model_outputs, **postprocess_params):
        """
        Postprocess

        Args:
            model_outputs (dict): outputs of forward process.
            top_k (int): Return top_k probs of result

        Return:
            Classification results
        """
        top_k = postprocess_params.pop("top_k", None)
        id2label = {id: label for id, label in enumerate(mnli_labels)}
        outputs = model_outputs[0]
        outputs = outputs.asnumpy()
        scores = self.softmax(outputs)

        dict_scores = [
            {"label": id2label[i], "score": score.item()} for i, score in enumerate(scores)
        ]

        dict_scores.sort(key=lambda x: x["score"], reverse=True)
        if top_k is not None:
            dict_scores = dict_scores[:top_k]
        return [dict_scores]
