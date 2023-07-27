import os
import shutil
from pathlib import Path

dcmDir = Path('./bh-3 DICOM-20230421T075124Z-001/bh-3 DICOM/')
targetDir = Path('./allDcmHere')

for p_d in os.listdir(dcmDir):
    if not p_d.startswith('.'):
        filePath = dcmDir / p_d

        for d in os.listdir(filePath):
            if not d.endswith('_dcm'):
                filePath = dcmDir / p_d / d

                for f in os.listdir(filePath):
                    newF = p_d + '_' + f
                    shutil.copy(filePath / f, targetDir / newF)
