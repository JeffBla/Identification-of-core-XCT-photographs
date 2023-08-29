import sys

sys.path.append('/home/jeffbla/resourceDPProject/model')
sys.path.append('/home/jeffbla/resourceDPProject/dcmCutCycleOut_copy')
sys.path.append('/home/jeffbla/下載/dcgan/calPorosityFlow2_CNN')

import numpy as np
import argparse
import matplotlib.pyplot as plt

import torch.nn as nn
import torch

from trainFunc import rescaleCTToN1and1
from ctToPercentModel import CtToPercentModel
from readDicomCntCT_findInnerCircle_findPorosityByVTK_Output import getTargetMaskImg, getTargetCtImage

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size",
                    type=int,
                    default=32,
                    help="size of the batches")
parser.add_argument(
    "--n_cpu",
    type=int,
    default=4,
    help="number of cpu threads to use during batch generation")
opt = parser.parse_args()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)

model = CtToPercentModel()

model.load_state_dict(torch.load('./model/ct2Percent/ct2PercentCNN.pt'))

dcmInDir = '/home/jeffbla/resourceDPProject/bh-3 DICOM-20230421T075124Z-001/bh3 15 dicom_20'
_, _, ctImageSet = getTargetCtImage(dcmInDir)
ctImageSet = ctImageSet[:, np.newaxis, 0:512, 0:512]
maskImgSet = np.array(getTargetMaskImg(dcmInDir))
maskImgSet = maskImgSet[:, 0:512, 0:512]

model.eval()
with torch.inference_mode():
    porosityList = []
    # for idx, imgCt in enumerate(ctImageSet):
    ctImageSet = torch.tensor(ctImageSet).type(torch.float32)
    percentImgSet = model(ctImageSet).detach().numpy()

    for idx, sSet in enumerate(percentImgSet[:, 0]):
        sTargetSet = sSet[maskImgSet[idx]]

        porositySet = 1 - sTargetSet
        porosityList.append(porositySet.sum() / porositySet.size)

print(porosityList)