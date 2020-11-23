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

// Pipeline

let url = 'https://hordurps.github.io/magU.vtp'
const reader = vtk.IO.XML.vtkXMLPolyDataReader.newInstance();
const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
const actor  = vtk.Rendering.Core.vtkActor.newInstance();

reader.setUrl(url).then(() => {
    const polydata = reader.getOutputData(0);
    actor.setMapper(mapper);
    mapper.setInputConnection(reader.getOutputPort());
    renderer.addActor(actor);

    // Render
    renderer.resetCamera();
    renderWindow.render();
});
