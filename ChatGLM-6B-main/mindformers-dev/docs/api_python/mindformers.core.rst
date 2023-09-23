mindformers.core
==================

.. automodule:: mindformers.core

mindformers.core
-----------------

.. autosummary
    :toctree: core
    :nosignatures:
    :template: classtemplate.rst

    mindformers.core.ClipGradNorm
    mindformers.core.build_context
    mindformers.core.init_context

mindformers.core.callback
--------------------------

.. autosummary
    :toctree: core
    :nosignatures:
    :template: classtemplate.rst

    mindformers.core.callback.CheckpointMointor
    mindformers.core.callback.MFLossMonitor
    mindformers.core.callback.ObsMonitor

mindformers.core.loss
--------------------------

.. autosummary
    :toctree: core
    :nosignatures:
    :template: classtemplate.rst

    mindformers.core.loss.CrossEntropyLoss
    mindformers.core.loss.L1Loss
    mindformers.core.loss.MSELoss
    mindformers.core.loss.SoftTargetCrossEntropy

mindformers.core.lr
--------------------------

.. autosummary
    :toctree: core
    :nosignatures:
    :template: classtemplate.rst

    mindformers.core.lr.ConstantWarmUpLR
    mindformers.core.lr.CosineWithRestartsAndWarmUpLR
    mindformers.core.lr.CosineWithWarmUpLR
    mindformers.core.lr.LinearWithWarmUpLR
    mindformers.core.lr.PolynomialWithWarmUpLR

mindformers.core.metric
--------------------------

.. autosummary
    :toctree: core
    :nosignatures:
    :template: classtemplate.rst

    mindformers.core.metric.EntityScore
    mindformers.core.metric.SQuADMetric

mindformers.core.optim
--------------------------

.. autosummary
    :toctree: core
    :nosignatures:
    :template: classtemplate.rst

    mindformers.core.optim.FusedAdamWeightDecay
