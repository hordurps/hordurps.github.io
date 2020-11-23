const container = document.querySelector('#container');
console.log()

// VTK renderWindow/renderer
const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
const renderer     = vtk.Rendering.Core.vtkRenderer.newInstance();
renderWindow.addRenderer(renderer);

// WebGL/OpenGL impl
const openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
openGLRenderWindow.setContainer(container);
openGLRenderWindow.setSize(1000, 1000);
renderWindow.addView(openGLRenderWindow);

// Interactor
const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
interactor.setView(openGLRenderWindow);
interactor.initialize();
interactor.bindEvents(container);

// Interactor style
const trackball = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
interactor.setInteractorStyle(trackball);

// Pipeline (reader, mapper, actor)

// Need to read VTP files instead of VTK
let url = 'https://hordurps.github.io/magU.vtp'
const reader = vtk.IO.XML.vtkXMLPolyDataReader.newInstance();

// decide the colormaps
const cmaps = vtk.Rendering.Core.vtkColorTransferFunction.vtkColorMaps;
const cmap = cmaps.getPresetByName('jet');

// create a lookup table
const lut = vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
lut.applyColorMap(cmap);
lut.setMappingRange(0, 256);
lut.updateRange();

const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
mapper.setLookupTable(lut);
mapper.setColorByArrayName('mag(U)');
mapper.setColorModeToMapScalars();
mapper.setInterpolateScalarsBeforeMapping();
mapper.setScalarModeToUsePointFieldData();
mapper.setScalarVisibility(true);
mapper.setScalarRange([0, 15])

const actor  = vtk.Rendering.Core.vtkActor.newInstance();
reader.setUrl(url).then(() => {
    const polydata = reader.getOutputData(0);
    actor.setMapper(mapper);
    mapper.setInputConnection(reader.getOutputPort());
    renderer.addActor(actor);

    // Render
    renderer.resetCamera();
    renderer.getActiveCamera().setPosition(0, 0, 1050);
    renderer.getActiveCamera().setFocalPoint(0, 0, 0.41);
    renderer.getActiveCamera().setParallelScale(980);

    renderWindow.render();
});
