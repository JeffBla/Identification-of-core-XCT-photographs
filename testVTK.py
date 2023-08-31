# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkIOImage import vtkDICOMImageReader

import numpy as np

import os
from pathlib import Path

shrinkToCenter = 0


def get_program_parameters():
    import argparse
    description = 'Align the center of target cycle, and output the dicom image cut by the target cycle.'
    epilogue = '''
 Output folder default is dcmCutCycleOut.
     '''
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilogue,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'inDirname',
        help=
        'The target dir only contain dicom files, and all files in the dir will be read.'
    )
    parser.add_argument(
        '--isDraw',
        action=argparse.BooleanOptionalAction,
        help='Show images contain circle ,contour and porosity.')

    args = parser.parse_args()
    return args.inDirname, args.isDraw


def checkInCircle(cx, cy, r, idxX, idxY) -> bool:
    if (idxX - cx)**2 + (idxY - cy)**2 < r**2:
        return True
    else:
        return False


inDirname, isDraw = get_program_parameters()

reader = vtkDICOMImageReader()
reader.SetDirectoryName(inDirname)
reader.Update()

files = os.listdir(inDirname)

breakpoint()

dcmImage_CT = np.array(reader.GetOutput().GetPointData().GetScalars()).reshape(
    len(files), reader.GetHeight(), reader.GetWidth())

breakpoint()
