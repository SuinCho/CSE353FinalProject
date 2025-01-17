import torch
from datetime import datetime
import torch.optim as optim
import matplotlib.pyplot as plt
#from data_load import get_loader
#from train import train_model
import torch.nn as nn
import argparse
import numpy as np
import pdb
from collections import OrderedDict, defaultdict
from torchvision import transforms
from torchvision.datasets import CocoCaptions #MNIST
from torch.utils.data import DataLoader
from torchvision import models
from InferSent.models import InferSent
#from InferSent.models import BGRUlastEncoder

class Embed(nn.Module):
    def __init__(self):
        super(Embed, self).__init__()                       
        
def load_sentemb():
    params = {'bsize': 16, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': 1}
    model = InferSent(params).cuda()
    #model = BGRUlastEncoder(params).cuda()
    model.load_state_dict(torch.load('../encoder/infersent2.pkl'))
    model = model.cuda() # gpu
    model.set_w2v_path('../fastText/crawl-300d-2M.vec/crawl-300d-2M.vec')
    model.build_vocab_k_words(K=100000)
    for p in model.parameters(): p.requires_grad = False
    return model

def load_resnet():
    model = models.resnet34(pretrained=True).cuda() # 34: 512, rest: 2048
    modules = list(model.children())[:-1]
    model = nn.Sequential(*modules).cuda() # gpu
    for p in model.parameters(): p.requires_grad = False
    return model # output size: bs x 512