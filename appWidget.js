const container = document.querySelector('#container');
console.log()

const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance();

// VTK renderWindow/renderer
//const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
//const renderer     = vtk.Rendering.Core.vtkRenderer.newInstance();
//renderWindow.addRenderer(renderer);

const renderer = fullScreenRenderer.getRenderer();
const renderWindow = fullScreenRenderer.getRenderWindow();


import controlPanel from './controlPanel.html';

// import vtkWidgetManager from 'vtk.js/Sources/Widgets/Core/WidgetManger';
// import WidgetManagerConstants from 'vtk.js/Sources/Widgets/Core/WidgetManage/Constants';
const { CaptureOn } = WidgetManagerConstants;


const WIDGET_BUILDERS = {
    stlWidget(widgetManager){
        return widgetManager.addWidget(
            vtk.IO.Geometry.vtkSTLReader.newInstance({
                setUrl: 'https://hordurps.github.io/BOI.stl'
            });
        );
    },
}

// WebGL/OpenGL impl
//const openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
//openGLRenderWindow.setContainer(container);
//openGLRenderWindow.setSize(1000, 1000);
//renderWindow.addView(openGLRenderWindow);

// Interactor
//const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
//interactor.setView(openGLRenderWindow);
//interactor.initialize();
//interactor.bindEvents(container);

// Interactor style
//const trackball = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
//interactor.setInteractorStyle(trackball);

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


// ------------------------------------------------
// Widget manager
// ------------------------------------------------
const widgetManager = vtkWidgetManager.newInstance();
widgetManager.setCaptureOn(CaptureOn.MOUSE_RELEASE);
widgetManager.setRenderer(renderer);


// ------------------------------------------------
// UI control handling
// ------------------------------------------------
fullScreenRenderer.addController(controlPanel);


const widgetListElem = document.querySelector('.widgetList');
const selectElem = document.querySelector('select');
const buttonCreate = document.querySelector('button.create');

// create widget
buttonCreate.addEventListener('click', () => {
    const w = WIDGET_BUILDERS[selectElem.value](widgetManager);
    w.placeWidget(reader.getOutputData().getBounds());
    w.setPlaceFactor(2);

    widgetManager.enablePicking();
    renderWindow.render();
    updateUI();
});

// Toggle flag
function toggle(e) {
    const value = !!e.target.checked;
    const name = e.currentTarget.dataset.name;
    const index = Number(
        e.currentTarget.parentElement.dataset.index
    );
    if (name === 'focus') {
        if (value) {
            widgetManager.grabFocus(widgetManager.getWidgets()[index]);
        } else {
            widgetManager.releaseFocus();
        }
    } else {
        const w = widgetManager.getWidgets()[index];
        w.set({ [name]: value });
    }
    widgetManager.enablePicking();
    renderWindow.render();
}

function grabFocus(e) {
    const index = Number(
        e.currentTarget.parentElement.parentElement.dataset.index
    );
    const w = widgetManager.getWidgets()[index];

    if (!w.hasFocus()){
        widgetManager.grabFocus(w);
    } else {
        widgetManager.releaseFocus();
    }
    widgetManager.enablePicking();
    renderWindow.render();
    updateUI();
}

// delete widget
function deleteWidget(e) {
    const index = Number(
        e.currentTarget.parentElement.parentElement.dataset.index
    );
    const w = widgetManager.getWidgets()[index];
    widgetManager.removeWidget(w);
    updateUI();
    widgetManager.enablePicking();
    renderWindow.render();
}


// ------------------------------------------------
// UI generation
// ------------------------------------------------


function toHTML(w, index){
    return `<tr data-index="${index}">
        <td>
            <button class="focus">${!w.focus ? 'Grab' : 'Release'}</button>
        </td>
        <td>${w.name}</td>
        <td>
            <input
                type="checkbox"
                data-name="pickable"
                ${w.pickable ? 'checked' : ''}
            />
        </td>
        <td>
            <input
                type="checkbox"
                data-name="contextVisibility"
                ${w.contextVisibility ? 'checked' : ''}
            />
        </td>
        <td>
            <input
                type="checkbox"
                data-name="handleVisibility"
                ${w.handleVisibility ? 'checked' : ''}
            />
        </td>
        <td>
            <button class='delete'>x</button>
        </td>
        </tr>`;
}


function updateUI() {
    const widgets = widgetManager.getWidgets();
    widgetListElem.innerHTML = widgets
        .map((w) => ({
            name: w.getReferenceByName('label'),
            focus:w.hasFocus(),
            pickable: w.getPickable(),
            visibility: w.getVisibility(),
            contextVisibility: w.getContextVisibility(),
            handleVisibility: w.getHandleVisibility(),
        }))
        .map(toHTML)
        .join('\n');
    const toggleElems = document.querySelectorAll('input[type="checkbox"]');
    for (let i = 0; i < toggleElems.length; i++) {
        toggleElems[i].addEventListener('change', toggle);
    }
    const deleteElems = document.querySelctorAll('button.delete');
    for (let i = 0; i < deleteElems.length; i++){
        deleteElems[i].addEventListener('click', deleteWidget);
    }
    const grabElems = document.querySelectorAll('button.focus');
    for (let i = 0; i < grabElems.length; i++) {
        grabElems[i].addEventListener('click', grabFocus);
    }

}


//document.querySelector('.cmap').addEventListener('change', (e) => {
//    const cmapChange = !!e.target.checked;
//    lut.applyColorMap(cmaps.getPresetByName('Cool to Warm'));
//    renderer.resetCamera();
//    renderWindow.render();
//})
