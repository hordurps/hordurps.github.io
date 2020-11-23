const container = document.querySelector('#container');

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
// const cone   = vtk.Filters.Sources.vtkConeSource.newInstance();

let url = 'https://github.com/hordurps/hordurps.github.io/blob/master/0_deg_magU.vtk'
const reader = vtk.IO.Legacy.vtkPolyDataReader.newInstance();
reader.setUrl(url).then(() => {
    const polydata = reader.getOutputData(0);
    const actor  = vtk.Rendering.Core.vtkActor.newInstance();
    const mapper = vtk.Rendering.Core.vtkMapper.newInstance();

    actor.setMapper(mapper);
    mapper.setInputConnection(reader.getOutputPort());
    renderer.addActor(actor);

    // Render
    renderer.resetCamera();
    renderWindow.render();
});
