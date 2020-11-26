const container = document.querySelector('#container');

const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
    background: [0, 0, 0],
});


const renderer = fullScreenRenderer.getRenderer();
const renderWindow = fullScreenRenderer.getRenderWindow();



//const WIDGET_BUILDERS = {
//    stlWidget(widgetManager){
//        const stlReader = widgetManager.addWidget(
//            vtk.IO.Geometry.vtkSTLReader.newInstance({
//                label: 'STL',
//            })
//        );
//        const stlMapper = vtk.Rendering.Core.vtkMapper.newInstance({
//            scalarVisibility: false,
//        });
//        const stlActor = vtk.Rendering.Core.vtkActor.newInstance();
//        stlActor.setMapper(stlMapper);
//        stlMapper.setInputConnection(stlReader.getOuputPort());
//        stlReader.setUrl(stlurl).then(() => {
//            renderer.addActor(stlActor);
//            renderer.resetCamera();
//            renderWindow.render();
//        });
//        return stlReader
//    },
//};

const stlActor = vtk.Rendering.Core.vtkActor.newInstance();


function changeArray(e) {
    mapper.setColorByArrayName(e);
    console.log(e)
};

function stlWidget() {
    const stlurl = 'https://hordurps.github.io/BOI.stl';
    const stlReader = vtk.IO.Geometry.vtkSTLReader.newInstance({
        label: 'STL',
    });
    const stlMapper = vtk.Rendering.Core.vtkMapper.newInstance({
        scalarVisibility: false,
    });
    stlActor.setMapper(stlMapper);
    stlMapper.setInputConnection(stlReader.getOutputPort());
    stlReader.setUrl(stlurl).then(() => {
        renderer.addActor(stlActor);
        renderer.resetCamera();
        renderWindow.render();
    });
    return stlActor

};

//console.log(document.body)

// Pipeline (reader, mapper, actor)

// Need to read VTP files instead of VTK
// let url = 'https://hordurps.github.io/magU.vtp'
let url = 'https://hordurps.github.io/velocities.vtp'
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
//mapper.setColorByArrayName('mag(U)');
mapper.setColorByArrayName('0deg');
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
//const widgetManager = vtk.Widgets.Core.vtkWidgetManager.newInstance();
//widgetManager.setRenderer(renderer);


// ------------------------------------------------
// UI control handling
// ------------------------------------------------
fullScreenRenderer.addController(`<table>
    <thead>
        <tr>
            <th>Focus</th>
            <th>Widget</th>
            <th title="Pickable">P</th>
            <th title="Visibility">V</th>
            <th title="ContextVisibility">C</th>
            <th title="HandleVisibility">H</th>
            <th></th>
        </tr>
    </thead>
    <tbody class="widgetList">
    </tbody>
</table>
<div>
    <select with="100%">
        <option value="stlWidget">STL</option>
    </select>
    <button class="create">+</button>
    <button class="delete">-</button>
</div>
    <div>
        <select name="comfort" id="comfort-select" with="100%">
            <option value="comfortSummer">Summer comfort</option>
            <option value="comfortWinter">Winter comfort</option>
            <option value="Safety">All year safety</option>
        </select>
    </div>
    <div>
        <select name="velocity" id="velocity-select" with="100%">
            <option value="0deg">0 deg</option>
            <option value="30deg">30 deg</option>
            <option value="60deg">60 deg</option>
            <option value="90deg">90 deg</option>
            <option value="120deg">120 deg</option>
            <option value="150deg">150 deg</option>
            <option value="180deg">180 deg</option>
            <option value="210deg">210 deg</option>
            <option value="240deg">240 deg</option>
            <option value="270deg">270 deg</option>
            <option value="300deg">300 deg</option>
            <option value="330deg">330 deg</option>
        </select>
    </div>
    `);
    

const widgetListElem = document.querySelector('.widgetList');
// const selectElem = document.querySelector('select');
const buttonCreate = document.querySelector('button.create');
const buttonDelete = document.querySelector('button.delete');

const comfortElem = document.querySelector('select#comfort-select');
const velocityElem = document.querySelector('select#velocity-select');

velocityElem.addEventListener('change', (e) => {
    //const selectElem = Number(e.target.value);
    const selectElem = document.getElementById('velocity-select').value;
    changeArray(selectElem);
    renderWindow.render();
});



// create widget
buttonCreate.addEventListener('click', () => {
    const w = stlWidget();
    renderWindow.render();
});

buttonDelete.addEventListener('click', () => {
    renderer.removeActor(stlActor);
    renderWindow.render();
});

// Toggle flag
//function toggle(e) {
//    const value = !!e.target.checked;
//    const name = e.currentTarget.dataset.name;
//    const index = Number(
//        e.currentTarget.parentElement.dataset.index
//    );
//    if (name === 'focus') {
//        if (value) {
//            widgetManager.grabFocus(widgetManager.getWidgets()[index]);
//        } else {
//            widgetManager.releaseFocus();
//        }
//    } else {
//        const w = widgetManager.getWidgets()[index];
//        w.set({ [name]: value });
//    }
//    widgetManager.enablePicking();
//    renderWindow.render();
//}
//
//function grabFocus(e) {
//    const index = Number(
//        e.currentTarget.parentElement.parentElement.dataset.index
//    );
//    const w = widgetManager.getWidgets()[index];
//
//    if (!w.hasFocus()){
//        widgetManager.grabFocus(w);
//    } else {
//        widgetManager.releaseFocus();
//    }
//    widgetManager.enablePicking();
//    renderWindow.render();
//    updateUI();
//}
//
//// delete widget
//function deleteWidget(e) {
//    const index = Number(
//        e.currentTarget.parentElement.parentElement.dataset.index
//    );
//    const w = widgetManager.getWidgets()[index];
//    widgetManager.removeWidget(w);
//    updateUI();
//    widgetManager.enablePicking();
//    renderWindow.render();
//}
//

// ------------------------------------------------
// UI generation
// ------------------------------------------------


//function toHTML(w, index){
//    return `<tr data-index="${index}">
//        <td>
//            <button class="focus">${!w.focus ? 'Grab' : 'Release'}</button>
//        </td>
//        <td>${w.name}</td>
//        <td>
//            <input
//                type="checkbox"
//                data-name="pickable"
//                ${w.pickable ? 'checked' : ''}
//            />
//        </td>
//        <td>
//            <input
//                type="checkbox"
//                data-name="contextVisibility"
//                ${w.contextVisibility ? 'checked' : ''}
//            />
//        </td>
//        <td>
//            <input
//                type="checkbox"
//                data-name="handleVisibility"
//                ${w.handleVisibility ? 'checked' : ''}
//            />
//        </td>
//        <td>
//            <button class='delete'>x</button>
//        </td>
//        </tr>`;
//}


//function updateUI() {
//    const widgets = widgetManager.getWidgets();
//    widgetListElem.innerHTML = widgets
//        .map((w) => ({
//            name: w.getReferenceByName('label'),
//            focus:w.hasFocus(),
//            pickable: w.getPickable(),
//            visibility: w.getVisibility(),
//            contextVisibility: w.getContextVisibility(),
//            handleVisibility: w.getHandleVisibility(),
//        }))
//        .map(toHTML)
//        .join('\n');
//    const toggleElems = document.querySelectorAll('input[type="checkbox"]');
//    for (let i = 0; i < toggleElems.length; i++) {
//        toggleElems[i].addEventListener('change', toggle);
//    }
//    const deleteElems = document.querySelctorAll('button.delete');
//    for (let i = 0; i < deleteElems.length; i++){
//        deleteElems[i].addEventListener('click', deleteWidget);
//    }
//    const grabElems = document.querySelectorAll('button.focus');
//    for (let i = 0; i < grabElems.length; i++) {
//        grabElems[i].addEventListener('click', grabFocus);
//    }
//
//}


//document.querySelector('.cmap').addEventListener('change', (e) => {
//    const cmapChange = !!e.target.checked;
//    lut.applyColorMap(cmaps.getPresetByName('Cool to Warm'));
//    renderer.resetCamera();
//    renderWindow.render();
//})
