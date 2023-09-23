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
"""MindFormer Self-Define Loss."""

from mindspore import nn, Tensor
from mindspore import ops as P
from mindspore.ops import functional as F
from mindspore.common import dtype as mstype
from mindspore.nn.loss.loss import LossBase

from mindspore.context import ParallelMode
from mindspore.parallel import set_algo_parameters

from mindspore import log as logger
from mindspore.parallel._utils import _get_device_num, _get_pipeline_stages, _get_parallel_mode, _is_sharding_propagation

from mindformers.tools.logger import _LogActionOnce
from mindformers.tools.register import MindFormerRegister, MindFormerModuleType
from mindformers.modules.transformer.op_parallel_config import default_dpmp_config

__all__ = ['SoftTargetCrossEntropy', 'MSELoss', 'L1Loss', 'CrossEntropyLoss']


@MindFormerRegister.register(MindFormerModuleType.LOSS)
class SoftTargetCrossEntropy(LossBase):
    """SoftTargetCrossEntropy for MixUp Augment."""

    def __init__(self, parallel_config=default_dpmp_config):
        super(SoftTargetCrossEntropy, self).__init__()
        dp = parallel_config.data_parallel
        self.mean_ops = P.ReduceMean(keep_dims=False).shard(((1,),))
        self.sum_ops = P.ReduceSum(keep_dims=False).shard(((dp, 1),))
        self.mul = P.Mul().shard(((dp, 1), (dp, 1)))
        self.mul1d = P.Mul().shard(((dp, 1), ()))
        self.log_softmax = P.LogSoftmax().shard(((dp, 1),))

    def construct(self, logit, label):
        logit = P.Cast()(logit, mstype.float32)
        label = P.Cast()(label, mstype.float32)
        logit_softmax = self.log_softmax(logit)
        neg_target = self.mul1d(label, -1)
        soft_target = self.mul(neg_target, logit_softmax)
        loss = self.sum_ops(soft_target, -1)
        return self.mean_ops(loss)


@MindFormerRegister.register(MindFormerModuleType.LOSS)
class MSELoss(nn.Cell):
    """MSELoss for parallel."""
    def __init__(self, norm_pixel_loss=True, parallel_config=default_dpmp_config):
        super(MSELoss, self).__init__()
        dp = parallel_config.data_parallel
        self.add_loss = P.Add().shard(((dp, 1, 1), ()))
        self.sub = P.Sub().shard(((dp, 1, 1), (dp, 1, 1)))
        self.divide = P.RealDiv().shard(((dp, 1, 1), (dp, 1, 1)))
        self.pow = P.Pow().shard(((dp, 1, 1), ()))
        self.divide1 = P.RealDiv().shard(((), ()))
        self.divide2 = P.RealDiv().shard(((dp, 1, 1), ()))
        self.square = P.Square().shard(((dp, 1, 1),))
        self.cast = P.Cast()
        self.mean1 = P.ReduceMean(keep_dims=True).shard(((dp, 1, 1),))
        self.mean2 = P.ReduceMean().shard(((dp, 1, 1),))
        self.mul = P.Mul().shard(((dp, 1), (dp, 1)))
        self.sum = P.ReduceSum().shard(((dp, 1,),))
        self.sum2 = P.ReduceSum(keep_dims=True).shard(((dp, 1, 1),))
        self.norm_pixel_loss = norm_pixel_loss

    def construct(self, pred, target, mask):
        """mse loss construct."""
        pred = self.cast(pred, mstype.float32)
        target = self.cast(target, mstype.float32)
        mask = self.cast(mask, mstype.float32)
        if self.norm_pixel_loss:
            mean = self.mean1(target, -1)
            var = self.variance(target)
            var = self.add_loss(var, 1e-6)
            std = self.pow(var, 0.5)
            sub = self.sub(target, mean)
            target = self.divide(sub, std)
        res = self.sub(pred, target)
        recon_loss = self.square(res)
        recon_loss = self.mean2(recon_loss, -1)
        loss_mask = self.mul(recon_loss, mask)
        loss_sum = self.sum(loss_mask)
        mask_sum = self.sum(mask)
        loss = self.divide1(loss_sum, mask_sum)
        return loss

    def variance(self, x):
        """get variance."""
        axis = (x.ndim - 1,)
        x_mean = self.mean1(x, axis)
        x_sub = self.sub(x, x_mean)
        x_pow = self.pow(x_sub, 2)
        x_sum = self.sum2(x_pow, axis)
        x_var = self.divide2(x_sum, x.shape[-1])
        return x_var


@MindFormerRegister.register(MindFormerModuleType.LOSS)
class L1Loss(LossBase):
    """L1Loss for parallel."""
    def __init__(self, reduction='mean', parallel_config=default_dpmp_config):
        super(L1Loss, self).__init__()
        dp = parallel_config.data_parallel

        self.abs = P.Abs().shard(((dp, 1, 1, 1),))
        self.sub = P.Sub().shard(((dp, 1, 1, 1), (dp, 1, 1, 1)))

        self.mul = P.Mul().shard(((), (dp, 1, 1, 1)))
        self.reduce_mean = P.ReduceMean().shard(((dp, 1, 1, 1),))
        self.reduce_sum = P.ReduceSum().shard(((dp, 1, 1, 1),))
        self.cast = P.Cast()

        self.average = True
        self.reduce = True
        if reduction == 'sum':
            self.average = False
        if reduction == 'none':
            self.reduce = False

    def get_loss(self, x, weights=1.0):
        """get loss."""
        input_dtype = x.dtype
        x = self.cast(x, mstype.float32)
        weights = self.cast(weights, mstype.float32)
        x = self.mul(weights, x)
        if self.reduce and self.average:
            x = self.reduce_mean(x, self.get_axis(x))
        if self.reduce and not self.average:
            x = self.reduce_sum(x, self.get_axis(x))
        x = self.cast(x, input_dtype)
        return x

    def construct(self, logits, labels):
        """L1Loss construct."""
        x_sub = self.sub(logits, labels)
        x = self.abs(x_sub)
        return self.get_loss(x)


class _Softmax(nn.Cell):
    """
    Calculate the softmax results with given logits.

    Note:
        The bprop of the cell is rewritten, just returns the accepted dout as returns. This cell should be used
        together with _NLLoss, to optimize the bprop of the cross entroy loss.

    Args:
        parallel_config (OpParallelConfig): The parallel configure. Default `default_dpmp_config`,
            an instance of `OpParallelConfig` with default args.

    Inputs:
        - **logits** (Tensor) - Tensor of shape (N, C). Data type must be float16 or float32. The output logits of
          the backbone.

    Outputs:
        Tensor. The corresponding softmax results.
    """
    def __init__(self, parallel_config=default_dpmp_config):
        super(_Softmax, self).__init__()
        dp = parallel_config.data_parallel
        mp = parallel_config.model_parallel
        # on/off value for onehot, for smooth labeling, modify the off_value
        self.on_value = Tensor(1.0, mstype.float32)
        self.off_value = Tensor(0.0, mstype.float32)

        self.sum = P.ReduceSum().shard(((dp, mp),))
        self.max = P.ArgMaxWithValue(axis=-1, keep_dims=True).shard(
            ((dp, mp),))
        self.sub = P.Sub().shard(((dp, mp), (dp, 1)))
        self.exp = P.Exp().shard(((dp, mp),))
        self.div = P.RealDiv().shard(((dp, mp), (dp, 1)))
        self.onehot = P.OneHot().shard(((dp, mp), (), ()))

    def construct(self, logits, label):
        """Forward process """
        # LogSoftmax for logits over last dimension
        logits = F.cast(logits, mstype.float32)
        _, logit_max = self.max(logits)
        logit_sub = self.sub(logits, logit_max)
        logit_exp = self.exp(logit_sub)
        exp_sum = self.sum(logit_exp, -1)
        exp_sum = P.Reshape()(exp_sum, (F.shape(exp_sum)[0], 1))
        softmax_result = self.div(logit_exp, exp_sum)

        one_hot_label = self.onehot(label, F.shape(logits)[-1], self.on_value, self.off_value)
        return softmax_result, one_hot_label

    def bprop(self, logits, label, _, dout):
        """just return the loss of the dout. Note this should be used together with _NLLLoss"""
        d_logits = F.cast(dout[0], F.dtype(logits))
        return d_logits, F.zeros_like(label)


class _NLLLoss(nn.Cell):
    """
    Calculate the NLLLoss results with given softmax results and the label.

    Note:
        The bprop of the cell is rewritten. This cell should be used
        together with _Softmax, to optimize the bprop of the cross entroy loss.

    Args:
        parallel_config (OpParallelConfig): The parallel configure. Default `default_dpmp_config`,
            an instance of `OpParallelConfig` with default args.

    Inputs:
        - **loss** (Tensor) - Tensor of shape (N, C). Data type is float32.

    Outputs:
        Tensor. The corresponding loss results.
    """
    def __init__(self, parallel_config=default_dpmp_config):
        super(_NLLLoss, self).__init__()
        dp = parallel_config.data_parallel
        mp = parallel_config.model_parallel
        self.repeat_loss = 1
        self.eps_const = Tensor(1e-24, mstype.float32)
        # In auto parallel, there will be a virtual div in the back propagation begins. As we use custom bprop function
        # we need to eliminate this virtual div by adding a factor "mp".
        if _get_parallel_mode() in (ParallelMode.AUTO_PARALLEL, ParallelMode.SEMI_AUTO_PARALLEL):
            self.repeat_loss = mp
        if _get_parallel_mode() in (ParallelMode.AUTO_PARALLEL,) and _is_sharding_propagation():
            self.sum = P.ReduceSum()
            self.mul = P.Mul()
            self.neg = P.Neg()
            self.log = P.Log()
            self.add = P.Add().shard(((dp, mp), ()))
        else:
            self.sum = P.ReduceSum().shard(((dp, mp),))
            self.mul = P.Mul().shard(((dp, mp), (dp, mp)))
            self.neg = P.Neg().shard(((dp, mp),))
            self.log = P.Log().shard(((dp, mp),))
            self.add = P.Add().shard(((dp, mp), ()))

    def construct(self, softmax_result, one_hot_label):
        log_softmax_result = self.log(self.add(softmax_result, self.eps_const))
        loss = self.mul(log_softmax_result, one_hot_label)
        loss_unsum = self.neg(loss)
        loss_reduce = self.sum(loss_unsum, -1)
        return loss_reduce

    def bprop(self, softmax_result, one_hot_label, _, dout):
        """A simplified function. Note this should be used together with _Softmax"""
        logits = softmax_result - one_hot_label
        logits = logits * P.ExpandDims()(dout, -1) * self.repeat_loss

        return logits, F.zeros_like(one_hot_label)


@MindFormerRegister.register(MindFormerModuleType.LOSS)
class CrossEntropyLoss(nn.Cell):
    """
    Calculate the cross entropy loss.

    Args:
        parallel_config (OpParallelConfig): The parallel configure. Default `default_dpmp_config`,
            an instance of `OpParallelConfig` with default args.

    Inputs:
        - **logits** (Tensor) - Tensor of shape (N, C). Data type must be float16 or float32. The output logits of
          the backbone.

        - **labels** (Tensor) - Tensor of shape (N, ). The ground truth label of the sample.

        - **input_mask** (Tensor) - Tensor of shape (N, ). input_mask indicates whether there are padded inputs and for
          padded inputs it will not be counted into loss.

    Outputs:
        Tensor. The corresponding cross entropy loss.

    Examples:
        >>> import numpy as np
        >>> from mindspore import dtype as mstype
        >>> from mindspore import Tensor
        >>> from mindformers.core import CrossEntropyLoss
        >>> loss = CrossEntropyLoss()
        >>>
        >>> logits = Tensor(np.array([[3, 5, 6, 9, 12, 33, 42, 12, 32, 72]]), mstype.float32)
        >>> labels_np = np.array([1]).astype(np.int32)
        >>> input_mask = Tensor(np.ones(1).astype(np.float32))
        >>> labels = Tensor(labels_np)
        >>> output = loss(logits, labels, input_mask)
        >>> print(output.shape)
        (1,)
    """
    @_LogActionOnce(m_logger=logger, key='CrossEntropyLoss',
                    no_warning=_get_parallel_mode() in (ParallelMode.STAND_ALONE,))
    def __init__(self, parallel_config=default_dpmp_config):
        super(CrossEntropyLoss, self).__init__()
        dp = parallel_config.data_parallel
        mp = parallel_config.model_parallel
        self.enable_force_redistribute = False
        if _get_parallel_mode() in (ParallelMode.AUTO_PARALLEL, ParallelMode.SEMI_AUTO_PARALLEL):
            self.enable_force_redistribute = True
            self.add = P.Add().shard(((dp, mp), ())).add_prim_attr("keep_alive", True)
            self.add_label = P.Add().shard(((dp,), ())).add_prim_attr("keep_alive", True)
            self._check_and_modify_sharding_context(dp)
        self.sum2 = P.ReduceSum().shard(((1,),))
        self.mul2 = P.Mul().shard(((1,), (1,)))
        self.add2 = P.Add()
        self.div2 = P.RealDiv()
        self.relu = P.ReLU().shard(((1,),))

        self._softmax = _Softmax(parallel_config)
        self._nllloss = _NLLLoss(parallel_config)

    @staticmethod
    def _check_and_modify_sharding_context(dp):
        device_num = _get_device_num()
        stages = _get_pipeline_stages()
        if _get_parallel_mode() in (ParallelMode.AUTO_PARALLEL,) and dp * stages != device_num:
            set_algo_parameters(fully_use_devices=False)

    def construct(self, logits, label, input_mask):
        """Forward process"""
        # The add is used for forcing the redistribution before stepping in sub graphs, when semi/auto parallel enabled.
        if self.enable_force_redistribute:
            logits = self.add(logits, 0)
            label = self.add_label(label, 0)
        softmax, one_hot_label = self._softmax(logits, label)
        loss_reduce = self._nllloss(softmax, one_hot_label)

        # Using input_mask to mask the loss
        input_mask = P.Reshape()(input_mask, (-1,))
        numerator = self.sum2(self.mul2(loss_reduce, input_mask))

        denominator = self.add2(
            self.sum2(input_mask),
            P.Cast()(F.tuple_to_array((1e-5,)), mstype.float32))
        loss = self.div2(numerator, denominator)

        return loss
