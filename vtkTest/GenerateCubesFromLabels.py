#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import (vtkDataObject, vtkDataSetAttributes)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkFiltersGeneral import vtkTransformFilter
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader, vtkDICOMImageReader
from vtkmodules.vtkImagingCore import vtkImageWrapPad
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (vtkActor, vtkPolyDataMapper,
                                         vtkRenderWindow,
                                         vtkRenderWindowInteractor,
                                         vtkRenderer)


def main():
    colors = vtkNamedColors()

    target_name, start_label, end_label, mode = get_program_parameters()
    if start_label > end_label:
        end_label, start_label = start_label, end_label

    # Generate cubes from labels
    # 1) Read the meta file or dicom file
    # 2) Convert point data to cell data
    # 3) Convert to geometry and display

    if mode == 1:
        # use mha/mhd
        reader = vtkMetaImageReader()
        reader.SetFileName(target_name)
    elif mode == 2:
        # use dicom
        reader = vtkDICOMImageReader()
        reader.SetDirectoryName(target_name)
    else:
        print('Mode value is incorrect.')
        return
    reader.Update()

    # The DICOM import by VTK includes the conversion to HU units.

    # Pad the volume so that we can change the point data into cell
    # data.
    extent = reader.GetOutput().GetExtent()
    pad = vtkImageWrapPad()
    pad.SetInputConnection(reader.GetOutputPort())
    pad.SetOutputWholeExtent(extent[0], extent[1] + 1, extent[2],
                             extent[3] + 1, extent[4], extent[5] + 1)
    pad.Update()

    # Copy the scalar point data of the volume into the scalar cell data
    pad.GetOutput().GetCellData().SetScalars(
        reader.GetOutput().GetPointData().GetScalars())

    selector = vtkThreshold()
    selector.SetInputArrayToProcess(0, 0, 0,
                                    vtkDataObject().FIELD_ASSOCIATION_CELLS,
                                    vtkDataSetAttributes().SCALARS)
    selector.SetInputConnection(pad.GetOutputPort())
    selector.SetLowerThreshold(start_label)
    selector.SetUpperThreshold(end_label)
    selector.Update()

    # Shift the geometry by 1/2
    transform = vtkTransform()
    transform.Translate(-0.5, -0.5, -0.5)

    transform_model = vtkTransformFilter()
    transform_model.SetTransform(transform)
    transform_model.SetInputConnection(selector.GetOutputPort())

    geometry = vtkGeometryFilter()
    geometry.SetInputConnection(transform_model.GetOutputPort())

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(geometry.GetOutputPort())
    mapper.SetScalarRange(start_label, end_label)
    mapper.SetScalarModeToUseCellData()
    mapper.SetColorModeToMapScalars()

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Gray'))

    renderer = vtkRenderer()
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(640, 480)
    render_window.SetWindowName('GenerateCubesFromLabels')

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.SetInteractorStyle(
        vtkInteractorStyleTrackballCamera())
    render_window_interactor.SetRenderWindow(render_window)

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('DarkSlateBlue'))
    render_window.Render()

    render_window_interactor.Start()


def get_program_parameters():
    import argparse
    description = 'Convert the point data from a labeled volume into cell data.'
    epilogue = '''
 The surfaces are displayed as vtkPolydata.
     '''
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilogue,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'targetname',
        help=
        'Input volume e.g. Frog/frogtissue.mhd. Or specify dir_name containing dicom files '
    )
    parser.add_argument(
        'startlabel',
        type=int,
        help=
        'The starting label in the input volume, e,g, 1.\ni.e. The smallest value in array. It may be CT value.'
    )
    parser.add_argument('endlabel',
                        type=int,
                        help='The ending label in the input volume e.g. 29.')
    parser.add_argument('mode',
                        type=int,
                        help='1 is for mha/mhd file. 2 is for dicom file.')
    args = parser.parse_args()
    return args.targetname, args.startlabel, args.endlabel, args.mode


if __name__ == '__main__':
    main()