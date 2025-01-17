import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import numpy as np
import pdb

# # NN for Image modality
# class IMG_NN(nn.Module):
#     def __init__(self, input_dim=4096, output_dim=1024):
#         super(IMG_NN, self).__init__()
#         self.denseL1 = nn.Linear(input_dim, output_dim)
        
#     def forward(self, x):
#         out = F.relu(self.denseL1(x))
#         return out

# # NN for Text modality
# class TEXT_NN(nn.Module):
#     def __init__(self, input_dim=1024, output_dim=1024):
#         super(TEXT_NN, self).__init__()
#         self.denseL1 = nn.Linear(input_dim, output_dim)

#     def forward(self, x):
#         out = F.relu(self.denseL1(x))
#         return out

class CC_NN(nn.Module):
    # used LSTM to reduce gradient loss 
    def __init__(self, img_enc_size, sent_enc_size, img_layer_sizes=[250, 200], \
        sent_layer_sizes=[2000, 500, 200], dropout=0.2):
        super().__init__()
        img_layer_sizes = [img_enc_size] + img_layer_sizes
        sent_layer_sizes = [sent_enc_size] + sent_layer_sizes
        self.img_LSTM = nn.Sequential()
        self.sent_LSTM = nn.Sequential()
        self.prob = nn.Sigmoid()    # output layer 
        #self.prob = nn.Softmax() 

        for i, (in_size, out_size) in enumerate( zip(img_layer_sizes[:-1], img_layer_sizes[1:]) ):
            self.img_LSTM.add_module(name="Linear %i"%(i), module=nn.LeakyReLU(in_size, out_size))
            self.img_LSTM.add_module(name="Linear %i"%(i), module=nn.Linear(in_size, out_size))
            #self.img_LSTM.add_module(name="Activation %i"%(i), module=nn.ReLU(inplace=False))
            self.img_LSTM.add_module(name="Dropout %i"%(i), module=nn.Dropout(dropout)) # added
            self.img_LSTM.add_module(name="Activation %i"%(i), module=nn.Tanh())


        for i, (in_size, out_size) in enumerate( zip(sent_layer_sizes[:-1], sent_layer_sizes[1:]) ):
            self.sent_LSTM.add_module(name="Linear %i"%(i), module=nn.LeakyReLU(inplace=True))
            self.sent_LSTM.add_module(name="Linear %i"%(i), module=nn.Linear(in_size, out_size))
            #self.sent_LSTM.add_module(name="Activation %i"%(i), module=nn.ReLU(inplace=False))
            self.sent_LSTM.add_module(name="Dropout %i"%(i), module=nn.Dropout(dropout)) # added
            self.sent_LSTM.add_module(name="Activation %i"%(i), module=nn.Tanh())

        
    def forward(self, img, sent, neg_img=None):
        img_feat = self.img_LSTM(img)
        sent_feat = self.sent_LSTM(sent)
        # # compute dot product of the img_feat and sent_feat 
        dots = (img_feat * sent_feat).sum(dim=1)    
        # # compute L1 distance 
        # dots = ((img_feat - sent_feat).abs()).sum(dim=1)    
        # # compute L2 distance 
        # dots = ((img_feat - sent_feat)**2).sum(dim=1)**.5   
        # # compute infinity norm 
        # dots = ((img_feat - sent_feat).abs()).max(dim=0)     
        # # compute cosine similarity of the two vectors 
        # dots = (img_feat * sent_feat).sum(dim=1) / ((img_feat**2).sum(dim=1)**.5 * (sent_feat**2).sum(dim=1)**.5)   
        # compute cosine similarity of the two vectors 
        # dots = torch.stack([img_feat, sent_feat]).min(dim=0)[0].sum(dim=1) / torch.stack([img_feat, sent_feat]).max(dim=0)[0].sum(dim=1) 
        
        probs = self.prob(dots) 
        if neg_img is not None:
            neg_img_feat = self.img_LSTM(neg_img)
            ###NEEDTO DO SOMETHING HERE FOR PENALIZING 
            neg_dots = (neg_img_feat * sent_feat).sum(dim=1) # Compute dot product for similarity 
            neg_probs = self.prob(neg_dots) 
        else:
            neg_probs = torch.zeros(probs.shape).cuda()

        return probs, neg_probs

