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
"""Tokenization classes for ChatGLM."""
import os
import logging
from typing import List, Optional, Union
import sentencepiece as spm

from mindformers.mindformer_book import MindFormerBook
from mindformers.models.base_tokenizer import Tokenizer
from mindformers.tools.register import MindFormerRegister, MindFormerModuleType

EncodedInput = List[int]

__all__ = ['ChatGLMTokenizer']

logger = logging.getLogger(__name__)


class TextTokenizer:
    """Base text tokenizer."""

    def __init__(self, model_path):
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(model_path)
        self.num_tokens = self.sp.vocab_size()

    def convert_token_to_id(self, token):
        return self.sp.PieceToId(token)

    def convert_id_to_token(self, idx):
        return self.sp.IdToPiece(idx)

    def tokenize(self, text):
        return self.sp.EncodeAsPieces(text)

    def decode(self, ids: List[int]):
        return self.sp.DecodeIds(ids)

    def __len__(self):
        return self.num_tokens


class SPTokenizer:
    """Tokenizer process special tokens."""

    def __init__(
            self,
            vocab_file,
            num_image_tokens=20000,
            max_blank_length=80,
            byte_fallback=True,
    ):
        assert vocab_file is not None
        self.vocab_file = vocab_file
        self.num_image_tokens = num_image_tokens
        self.special_tokens = ["[MASK]", "[gMASK]", "[sMASK]", "<unused_0>", "<sop>", "<eop>", "<ENC>", "<dBLOCK>"]
        self.max_blank_length = max_blank_length
        self.byte_fallback = byte_fallback
        self.text_tokenizer = TextTokenizer(vocab_file)

    @staticmethod
    def get_blank_token(length: int):
        assert length >= 2
        return f"<|blank_{length}|>"

    @staticmethod
    def get_tab_token():
        return f"<|tab|>"

    @property
    def num_text_tokens(self):
        return self.text_tokenizer.num_tokens

    @property
    def num_tokens(self):
        return self.num_image_tokens + self.num_text_tokens

    @staticmethod
    def _encode_whitespaces(text: str, max_len: int = 80):
        text = text.replace("\t", SPTokenizer.get_tab_token())
        for i in range(max_len, 1, -1):
            text = text.replace(" " * i, SPTokenizer.get_blank_token(i))
        return text

    def _preprocess(self, text: str, linebreak=True, whitespaces=True):
        if linebreak:
            text = text.replace("\n", "<n>")
        if whitespaces:
            text = self._encode_whitespaces(text, max_len=self.max_blank_length)
        return text

    def encode(self, text: str, linebreak=True, whitespaces=True, add_dummy_prefix=True) -> List[int]:
        """
        Encode text to token id.
        Args:
            text: Text to encode.
            linebreak: Whether to encode newline (\n) in text.
            whitespaces: Whether to encode multiple whitespaces or tab in text, useful for source code encoding.
            add_dummy_prefix: Whether to add dummy blank space in the beginning.
        """
        text = self._preprocess(text, linebreak, whitespaces)
        if not add_dummy_prefix:
            text = "<n>" + text
        tmp = self.text_tokenizer.encode(text)
        tokens = [x + self.num_image_tokens for x in tmp]
        return tokens if add_dummy_prefix else tokens[2:]

    def decode(self, text_ids: List[int]) -> str:
        """Decode id to text."""
        ids = [int(id) - self.num_image_tokens for id in text_ids]
        ids = [id for id in ids if id >= 0]
        text = self.text_tokenizer.decode(ids)
        text = text.replace("<n>", "\n")
        text = text.replace(SPTokenizer.get_tab_token(), "\t")
        for i in range(2, self.max_blank_length + 1):
            text = text.replace(self.get_blank_token(i), " " * i)
        return text

    def tokenize(self, text: str, linebreak=True, whitespaces=True, add_dummy_prefix=True) -> List[str]:
        """
        Encode text to id.
        Args:
            text: Text to encode.
            linebreak: Whether to encode newline (\n) in text.
            whitespaces: Whether to encode multiple whitespaces or tab in text, useful for source code encoding.
            add_dummy_prefix: Whether to add dummy blank space in the beginning.
        """
        text = self._preprocess(text, linebreak, whitespaces)
        if not add_dummy_prefix:
            text = "<n>" + text
        tokens = self.text_tokenizer.tokenize(text)
        return tokens if add_dummy_prefix else tokens[2:]

    def __getitem__(self, x: Union[int, str]):
        if isinstance(x, int):
            if x < self.num_image_tokens:
                return "<image_{}>".format(x)
            return self.text_tokenizer.convert_id_to_token(x - self.num_image_tokens)
        if isinstance(x, str):
            if x.startswith("<image_") and x.endswith(">") and x[7:-1].isdigit():
                return int(x[7:-1])
            return self.text_tokenizer.convert_token_to_id(x) + self.num_image_tokens
        raise ValueError("The key should be str or int.")


@MindFormerRegister.register(MindFormerModuleType.TOKENIZER)
class ChatGLMTokenizer(Tokenizer):
    """
    Construct a ChatGLM tokenizer. Based on byte-level Byte-Pair-Encoding.

    Args:
        vocab_file(str): The vocabulary file path.
        do_lower_case(bool): Lower input text. Default False.
        remove_space(str): The merge file path.
        bos_token(str): The token that represents the begin-of-sentence. Default '<sop>'.
        eos_token(str): The token that represents the end-of-sentence. Default '<eop>'.
        end_token(str): The token that represents the end-of-sentence. Default '</s>'.
        mask_token(str): The token that represents the special mask. Default '[MASK]',
        gmask_token(str): The token that represents the special mask. Default '[gMASK]',
        pad_token(str): The token that represents the pad. Default "<pad>".
        unk_token(str): The token that represents the unknown. Default '<unk>'.
        add_prefix_space(bool): whether to add a whitespace in the front of text. Default "False"
        **kwargs: Other kwargs that will be passed into the base class of the `Tokenizer`.

    Examples:
        >>> from mindformers import AutoTokenizer
        >>> tokenize = AutoTokenizer.from_pretrained('glm_6b')
        >>> tokenize("你好")
        {'input_ids': [5, 74874, 130001, 130004], 'token_type_ids': [0, 0, 0, 0], 'attention_mask': [1, 1, 1, 1]}
        >>> from mindformers.models.glm.chatglm_6b_tokenizer import ChatGLMTokenizer
        >>> tokenizer = ChatGLMTokenizer('ice_text.model')
        >>> prompts_list = ["晚上睡不着应该怎么办"]
        >>> token_id = tokenizer(prompts)
        >>> input_ids = token_id['input_ids']
        >>> print(input_ids)
        [[74747, 83400, 64213, 66846, 130001, 130004]]
        >>> response = tokenizer.decode(input_ids)
        >>> print(response)
        ['晚上睡不着应该怎么办']


    Outputs:
        A dict contains the processed ids, attention_mask that specific by the member `MODEL_INPUT_NAME`
        of the subclass.
    """
    VOCAB_FILES = {"vocab_file": "ice_text.model"}
    model_input_names = ["input_ids"]
    _support_list = MindFormerBook.get_tokenizer_support_list()['glm']

    def __init__(
            self,
            vocab_file,
            do_lower_case=False,
            remove_space=False,
            bos_token='<sop>',
            eos_token='<eop>',
            end_token='</s>',
            mask_token='[MASK]',
            gmask_token='[gMASK]',
            padding_side="left",
            pad_token="<pad>",
            unk_token="<unk>",
            num_image_tokens=0,
            **kwargs
    ) -> None:
        super().__init__(
            do_lower_case=do_lower_case,
            remove_space=remove_space,
            padding_side=padding_side,
            bos_token=bos_token,
            eos_token=eos_token,
            end_token=end_token,
            mask_token=mask_token,
            gmask_token=gmask_token,
            pad_token=pad_token,
            unk_token=unk_token,
            num_image_tokens=num_image_tokens,
            **kwargs
        )

        self.do_lower_case = do_lower_case
        self.remove_space = remove_space
        self.vocab_file = vocab_file

        self._bos_token = bos_token
        self._eos_token = eos_token
        self._end_token = end_token
        self._mask_token = mask_token
        self._gmask_token = gmask_token

        self.sp_tokenizer = SPTokenizer(vocab_file, num_image_tokens=num_image_tokens)

        self.added_tokens_encoder = {}
        self.added_tokens_decoder = {}

    @property
    def gmask_token_id(self) -> Optional[int]:
        if self._gmask_token is None:
            return None
        return self.convert_tokens_to_ids(self._gmask_token)

    @property
    def end_token_id(self) -> Optional[int]:
        """
        `Optional[int]`: Id of the end of context token in the vocabulary. Returns `None` if the token has not been
        set.
        """
        if self._end_token is None:
            return None
        return self.convert_tokens_to_ids(self._end_token)

    @property
    def vocab_size(self):
        """ Returns vocab size """
        return self.sp_tokenizer.num_tokens

    def get_vocab(self):
        """ Returns vocab as a dict """
        vocab = {self._convert_id_to_token(i): i for i in range(self.vocab_size)}
        vocab.update(self.added_tokens_encoder)
        return vocab

    def preprocess_text(self, inputs):
        """Preprocess text."""
        if self.remove_space:
            outputs = " ".join(inputs.strip().split())
        else:
            outputs = inputs

        if self.do_lower_case:
            outputs = outputs.lower()

        return outputs

    def tokenize(self, text):
        """ Returns a tokenized string. """
        return self._tokenize(text)

    def _tokenize(self, text, **kwargs):
        """ Returns a tokenized string. """
        text = self.preprocess_text(text)
        seq = self.sp_tokenizer.tokenize(text)
        return seq

    def _decode(self, token_ids, skip_special_tokens=False, **kwargs):
        """ Decode id to text. """
        # unused in this tokenizer.
        _, _ = skip_special_tokens, kwargs
        if isinstance(token_ids, int):
            token_ids = [token_ids]
        if self.pad_token_id in token_ids:  # remove pad
            token_ids = list(filter((self.pad_token_id).__ne__, token_ids))
        return self.sp_tokenizer.decode(token_ids)

    # pylint:disable=arguments-differ
    def convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        """
        Converts a token string (or a sequence of tokens) in a single integer id (or a sequence of ids), using the
        vocabulary.

        Args:
            tokens (`str` or `List[str]`): One or several token(s) to convert to token id(s).

        Returns:
            `int` or `List[int]`: The token id or list of token ids.
        """

        return self._convert_tokens_to_ids(tokens)

    def _convert_tokens_to_ids(self, tokens: Union[str, List[str]]) -> Union[int, List[int]]:
        """
        Converts a token string (or a sequence of tokens) in a single integer id (or a sequence of ids), using the
        vocabulary.

        Args:
            tokens (`str` or `List[str]`): One or several token(s) to convert to token id(s).

        Returns:
            `int` or `List[int]`: The token id or list of token ids.
        """
        if tokens is None:
            return None

        if isinstance(tokens, str):
            return self._convert_token_to_id_with_added_voc(tokens)

        ids = []
        for token in tokens:
            ids.append(self._convert_token_to_id_with_added_voc(token))
        return ids

    def _convert_token_to_id_with_added_voc(self, token):
        if token is None:
            return None

        if token in self.added_tokens_encoder:
            return self.added_tokens_encoder[token]
        return self.sp_tokenizer[token]

    # pylint:disable=arguments-differ
    def convert_ids_to_tokens(self, ids: Union[int, List[int]], skip_special_tokens: bool = False):
        """
        Converts a single index or a sequence of indices in a token or a sequence of tokens, using the vocabulary and
        added tokens.

        Args:
            ids (`int` or `List[int]`):
                The token id (or token ids) to convert to tokens.
            skip_special_tokens (`bool`, *optional*, defaults to `False`):
                Whether or not to remove special tokens in the decoding.

        Returns:
            `str` or `List[str]`: The decoded token(s).
        """
        if isinstance(ids, int):
            if ids in self.added_tokens_decoder:
                return self.added_tokens_decoder[ids]
            return self._convert_id_to_token(ids)
        tokens = []
        for index in ids:
            index = int(index)
            if skip_special_tokens and index in self.all_special_ids:
                continue
            if index in self.added_tokens_decoder:
                tokens.append(self.added_tokens_decoder[index])
            else:
                tokens.append(self._convert_id_to_token(index))
        return tokens

    def _convert_id_to_token(self, index):
        """Converts an index (integer) in a token (str) using the vocab."""
        return self.sp_tokenizer[index]

    def build_inputs_with_special_tokens(self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None):
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification tasks by concatenating and
        adding special tokens. A BERT sequence has the following format:

        - single sequence: `[CLS] X [SEP]`
        - pair of sequences: `[CLS] A [SEP] B [SEP]`

        Args:
            token_ids_0 (`List[int]`):
                List of IDs to which the special tokens will be added.
            token_ids_1 (`List[int]`, *optional*):
                Optional second list of IDs for sequence pairs.

        Returns:
            `List[int]`: List of [input IDs](../glossary#input-ids) with the appropriate special tokens.
        """
        gmask_id = self.sp_tokenizer[self._gmask_token]
        eos_id = self.sp_tokenizer[self._eos_token]
        token_ids_0 = token_ids_0 + [gmask_id, self.sp_tokenizer[self._bos_token]]
        if token_ids_1 is not None:
            token_ids_0 = token_ids_0 + token_ids_1 + [eos_id]
        return token_ids_0

    def save_vocabulary(self, save_directory, filename_prefix=None):
        """
        Save the vocabulary and special tokens file to a directory.

        Args:
            save_directory (`str`):
                The directory in which to save the vocabulary.
            filename_prefix (`str`, *optional*):
                An optional prefix to add to the named of the saved files.

        Returns:
            `Tuple(str)`: Paths to the files saved.
        """
        if os.path.isdir(save_directory):
            vocab_file = os.path.join(save_directory, self.VOCAB_FILES["vocab_file"])
        else:
            vocab_file = save_directory

        with open(self.vocab_file, 'rb') as fin:
            proto_str = fin.read()

        with open(vocab_file, "wb") as writer:
            writer.write(proto_str)

        return (vocab_file,)
