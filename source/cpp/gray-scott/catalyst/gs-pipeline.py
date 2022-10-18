from paraview.simple import *

from paraview import print_info

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# Create a new 'Render View'
renderView1 = CreateView('RenderView')

camera = GetActiveCamera()
camera.Azimuth(45)
camera.Elevation(45)

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)
layout1.SetSize(824, 656)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

producer = TrivialProducer(registrationName='fides')

# show data from gsbp
fDisplay = Show(producer, renderView1, 'UniformGridRepresentation')
renderView1.ResetCamera()

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')
#uLUT.AutomaticRescaleRangeMode = 'Grow and update every timestep'
#uLUT.RescaleOnVisibilityChange = 1

# trace defaults for the display properties.
fDisplay.Representation = 'Surface'
fDisplay.ColorArrayName = ['POINTS', 'U']
fDisplay.SetScaleArray = ['POINTS', 'U']
fDisplay.ScaleTransferFunction = 'PiecewiseFunction'
fDisplay.OpacityArray = ['POINTS', 'U']
fDisplay.OpacityTransferFunction = 'PiecewiseFunction'
fDisplay.LookupTable = uLUT
# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
fDisplay.ScaleTransferFunction.Points = [0.14830323427621842, 0.0, 0.5, 0.0, 0.9988113230834544, 1.0, 0.5, 0.0]


uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.Title = 'U'
uLUTColorBar.ComponentTitle = ''

# show color legend
fDisplay.SetScalarBarVisibility(renderView1, True)

contour1 = Contour(registrationName='Contour1', Input=producer)
contour1.ContourBy = ['POINTS', 'U']
contour1.Isosurfaces = [0.3]
contour1.PointMergeMethod = 'Uniform Binning'

contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')

contour1Display.Representation = 'Surface'
contour1Display.ColorArrayName = ['POINTS', 'U']

Hide(producer, renderView1)

#clip = Clip(registrationName="clip1", Input=producer)
#clip.ClipType = 'Plane'
#clip.Scalars = ['POINTS', 'U']
#clip.ClipType.Origin = [1.5, 1.5, 1.5]
#clip.ClipType.Normal = [0.0, 1.0, 0.0]

# ----------------------------------------------------------------
# setup extractors
# ----------------------------------------------------------------

# create extractor
pNG1 = CreateExtractor('PNG', renderView1, registrationName='PNG1')
# trace defaults for the extractor.
pNG1.Trigger = 'TimeStep'

# init the 'PNG' selected for 'Writer'
pNG1.Writer.FileName = 'output_{timestep:06d}.png'
pNG1.Writer.ImageResolution = [800, 800]
pNG1.Writer.Format = 'PNG'

# ----------------------------------------------------------------
# restore active source
SetActiveSource(pNG1)
# ----------------------------------------------------------------

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

def catalyst_execute(info):
    print_info("in '%s::catalyst_execute'", __name__)
    global contour1
    contour1.UpdatePipeline()
    #global fDisplay
    #ColorBy(fDisplay, ('POINTS', 'U'))
    #fDisplay.RescaleTransferFunctionToDataRange(False, True)
    #fDisplay.RescaleTransferFunctionToDataRange(True, False)
    #clip.UpdatePipeline()
    #print("updating pipeline and saving image")

    #print("-----------------------------------")
    #print("executing (cycle={}, time={})".format(info.cycle, info.time))
    #print("bounds:", producer.GetDataInformation().GetBounds())
    #print("U-range:", producer.PointData['U'].GetRange(0))
    #print("V-range:", producer.PointData['V'].GetRange(0))


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print('in __main__()')
    from paraview.simple import SaveExtractsUsingCatalystOptions
    # Code for non in-situ environments; if executing in post-processing
    # i.e. non-Catalyst mode, let's generate extracts using Catalyst options
    SaveExtractsUsingCatalystOptions(options)
