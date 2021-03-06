import os
import sys
import math
import numpy as np
import cntk as ct

def build_model(num_classes, model_name, ft_model=None):
    '''
    Factory function to instantiate the model.
    '''
    if ft_model is not None:
        print(ft_model, ft_model)

    model = getattr(sys.modules[__name__], model_name)
    return model(num_classes, ft_model)

class VGG13(object):
    '''
    A VGG13 like model tweaked for FACS data.
    '''
    @property
    def learning_rate(self):
        return .005

    @property
    def input_width(self):
        return 64

    @property
    def input_height(self):
        return 64

    @property
    def input_channels(self):
        return 1

    @property
    def model(self):
        return None

    @property
    def model(self):
        return self._model

    def __init__(self, num_classes, ft_model):
        self._model = self._create_model(num_classes, ft_model)

    def _create_model(self, num_classes, ft_model):
        if ft_model is None:
            with ct.default_options(activation=ct.relu, init=ct.glorot_uniform()):
                model = ct.layers.Sequential([
                    ct.layers.For(range(2), lambda i: [
                        ct.layers.Convolution((3,3), [64,128][i], pad=True, name='conv{}-1'.format(i+1)),
                        ct.layers.Convolution((3,3), [64,128][i], pad=True, name='conv{}-2'.format(i+1)),
                        ct.layers.MaxPooling((2,2), strides=(2,2), name='pool{}-1'.format(i+1)),
                        ct.layers.Dropout(0.25, name='drop{}-1'.format(i+1))
                    ]),
                    ct.layers.For(range(2), lambda i: [
                        ct.layers.Convolution((3,3), [256,256][i], pad=True, name='conv{}-1'.format(i+3)),
                        ct.layers.Convolution((3,3), [256,256][i], pad=True, name='conv{}-2'.format(i+3)),
                        ct.layers.Convolution((3,3), [256,256][i], pad=True, name='conv{}-3'.format(i+3)),                
                        ct.layers.MaxPooling((2,2), strides=(2,2), name='pool{}-1'.format(i+3)),
                        ct.layers.Dropout(0.25, name='drop{}-1'.format(i+3))
                    ]),            
                    ct.layers.For(range(2), lambda i: [
                        ct.layers.Dense(1024, activation=None, name='fc{}'.format(i+5)),
                        ct.layers.Activation(activation=ct.relu, name='relu{}'.format(i+5)),
                        ct.layers.Dropout(0.5, name='drop{}'.format(i+5))
                    ]),
                    ct.layers.Dense(num_classes, activation=ct.sigmoid, name='output')
                ])
        else:
            model = ct.load_model(ft_model)
            last_node = ct.logging.find_by_name(model,'drop6')
            cloned_layers = ct.combine([last_node.owner]).clone(
                ct.CloneMethod.clone)
            model = ct.layers.Dense(num_classes, activation=ct.sigmoid, name='output') (cloned_layers)
        return model
