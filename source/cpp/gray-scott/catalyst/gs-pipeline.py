from paraview.simple import *

from paraview import print_info


def SetupRenderView():
    # Create a new 'Render View'
    renderView1 = CreateView('RenderView')

    camera = GetActiveCamera()
    camera.Azimuth(45)
    camera.Elevation(45)

    SetActiveView(None)

    # create new layout object 'Layout #1'
    layout1 = CreateLayout(name='Layout #1')
    layout1.AssignView(0, renderView1)
    layout1.SetSize(824, 656)

    # restore active view
    SetActiveView(renderView1)
    return renderView1


def SetupCatalystProducer():
    producer = TrivialProducer(registrationName='fides')
    return producer


def SetupFidesReader():
    # TODO
    fides = FidesReader(FileName="")


def SetupVisPipeline(producer, renderView1):
    fDisplay = Show(producer, renderView1, 'UniformGridRepresentation')
    renderView1.ResetCamera()

    # get color transfer function/color map for 'U'
    uLUT = GetColorTransferFunction('V')
    uLUT.AutomaticRescaleRangeMode = 'Clamp and update every timestep'
    uLUT.RescaleOnVisibilityChange = 1

    #clip = Clip(registrationName="clip1", Input=producer)
    #clip.ClipType = 'Plane'
    #clip.Scalars = ['POINTS', 'V']
    #clip.Value = 0.3
    #clip.ClipType.Origin = [1.5, 1.5, 1.5]
    #clip.ClipType.Normal = [0.0, 1.0, 0.0]
    #
    #clipDisplay = Show(clip, renderView1, 'GeometryRepresentation')
    #
    #clipDisplay.Representation = 'Surface'
    #clipDisplay.ColorArrayName = ['POINTS', 'V']


    contour1 = Contour(registrationName='Contour1', Input=producer)
    contour1.ContourBy = ['POINTS', 'V']
    contour1.Isosurfaces = [0.1, 0.3, 0.5, 0.7]
    contour1.PointMergeMethod = 'Uniform Binning'

    contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')

    contour1Display.Representation = 'Surface'
    contour1Display.ColorArrayName = ['POINTS', 'V']

    Hide(producer, renderView1)

    # trace defaults for the display properties.
    contour1Display.Representation = 'Surface'
    contour1Display.ColorArrayName = ['POINTS', 'V']
    contour1Display.SetScaleArray = ['POINTS', 'V']
    contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
    contour1Display.LookupTable = uLUT


    uLUTColorBar = GetScalarBar(uLUT, renderView1)
    uLUTColorBar.Title = 'V'
    uLUTColorBar.ComponentTitle = ''

    # show color legend
    contour1Display.SetScalarBarVisibility(renderView1, True)
    return contour1, contour1Display


def SetupExtractor(renderView1):
    # create extractor
    pNG1 = CreateExtractor('PNG', renderView1, registrationName='PNG1')
    # trace defaults for the extractor.
    pNG1.Trigger = 'TimeStep'

    # init the 'PNG' selected for 'Writer'
    pNG1.Writer.FileName = 'output_{timestep:06d}.png'
    pNG1.Writer.ImageResolution = [800, 800]
    pNG1.Writer.Format = 'PNG'


# ------------------------------------------------------------------------------
# Catalyst options
from paraview import catalyst
options = catalyst.Options()
options.GlobalTrigger = 'TimeStep'
options.EnableCatalystLive = 1
options.CatalystLiveTrigger = 'TimeStep'
options.ExtractsOutputDirectory = '/tmp'
#options.ExtractsOutputDirectory = '.'

# print start marker
print_info("begin '%s'", __name__)

renderView1 = SetupRenderView()
producer = SetupCatalystProducer()
globalProducer, globalDisplay = SetupVisPipeline(producer, renderView1)

SetupExtractor(renderView1)

def catalyst_initialize():
    print_info("in '%s::catalyst_initialize'", __name__)
    #renderView1 = SetupRenderView()
    #producer = SetupCatalystProducer()
    #global globalProducer
    #global globalDisplay
    #globalProducer, globalDisplay = SetupVisPipeline(producer, renderView1)

    #SetupExtractor(renderView1)



def catalyst_execute(info):
    print_info("in '%s::catalyst_execute'", __name__)
    #global producer
    #producer.UpdatePipeline()
    #global clip
    #clip.UpdatePipeline()
    global globalProducer
    #sources = GetSources()
    #key = ('', '')
    #for src in sources.keys():
    #    if src[0] == 'fides':
    #        key = src

    globalProducer.UpdatePipeline()
    global globalDisplay
    globalDisplay.RescaleTransferFunctionToDataRange()

    #print("-----------------------------------")
    print_info("executing (cycle={}, time={})".format(info.cycle, info.time))
    #print("U-range:", producer.PointData['U'].GetRange(0))
    print_info("V-range: {}".format(producer.PointData['V'].GetRange(0)))


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print('in __main__()')
    from paraview.simple import SaveExtractsUsingCatalystOptions
    # Code for non in-situ environments; if executing in post-processing
    # i.e. non-Catalyst mode, let's generate extracts using Catalyst options
    SaveExtractsUsingCatalystOptions(options)
