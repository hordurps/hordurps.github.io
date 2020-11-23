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

const lut = vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
const cmaps = vtk.Rendering.Core.vtkColorTransferFunction.vtkColorMaps;
const cmap = cmaps.getPresetByName('jet');
lut.applyColorMap(cmap);
const mapper = vtk.Rendering.Core.vtkMapper.newInstance({
    interpolateScalarsBeforeMapping: false,
    useLookupTableScalarRange: false,
    lut,
    scalarVisibility: true,
});
mapper.setScalarModeToDefault();
mapper.setColorModeToMapScalars();
mapper.setScalarRange([0, 15])
const actor  = vtk.Rendering.Core.vtkActor.newInstance();

reader.setUrl(url).then(() => {
    const polydata = reader.getOutputData(0);
    actor.setMapper(mapper);
    mapper.setInputConnection(reader.getOutputPort());
    renderer.addActor(actor);

    // Render
    renderer.getActiveCamera().setPosition(0, 0, 750);
    renderer.getActiveCamera().setFocalPoint(0, 0, 0,41);
    renderer.getActiveCamera().setParallelScale(980);

    renderer.resetCamera();
    renderWindow.render();
});
