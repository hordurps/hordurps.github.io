const container = document.querySelector('#container');

const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
    background: [0, 0, 0],
});


const renderer = fullScreenRenderer.getRenderer();
const renderWindow = fullScreenRenderer.getRenderWindow();



function changeArray(e) {
    mapper.setColorByArrayName(e);
    console.log(e)
};
var stlMappers = {};
var stlActors = {};
var stlReaders = {};

function createSTL() {
    const stlReader = vtk.IO.Geometry.vtkSTLReader.newInstance({
        label: 'STL',
    });
    const stlActor = vtk.Rendering.Core.vtkActor.newInstance();
    const stlMapper = vtk.Rendering.Core.vtkMapper.newInstance({
        scalarVisibility: false,
    });
    return [stlReader,stlMapper, stlActor];
};

function stlWidget(selectElem) {
    if (selectElem.includes('BOI')) {
        var stlurl = 'https://hordurps.github.io/BOI.stl';
    } else {
        var stlurl = 'https://hordurps.github.io/BDGS.stl';
    }
//    stlActors.selectElem = stlActor;
//    stlMappers.selectElem = stlMapper;
//    stlReaders.selectElem = stlReader;
    // checkin if the key does NOT exist in dictionary, then create keys
    if (!(selectElem in stlReaders)) {
        var stls = createSTL();
        //stlReaders.selectElem = stls[0]; 
        //stlMappers.selectElem = stls[1]; 
        //stlActors.selectElem = stls[2];
        stlReaders[selectElem] = stls[0]; 
        stlMappers[selectElem] = stls[1]; 
        stlActors[selectElem] = stls[2];
        console.log(stlReaders.selectElem);
        console.log(stlActors.selectElem);
        console.log(stlMappers.selectElem);
    
    //    stlActors.selectElem.setMapper(stlMapper);
    //    stlMappers.selectElem.setInputConnection(stlReader.getOutputPort());
        stlActors[selectElem].setMapper(stlMappers[selectElem]);
        stlMappers[selectElem].setInputConnection(stlReaders[selectElem].getOutputPort());
        stlReaders[selectElem].setUrl(stlurl).then(() => {
            renderer.addActor(stlActors[selectElem]);
            renderer.resetCamera();
            renderWindow.render();
        });
    
    
        //stlActor.setMapper(stlMapper);
        //stlMapper.setInputConnection(stlReader.getOutputPort());
        //stlReader.setUrl(stlurl).then(() => {
        //    renderer.addActor(stlActor);
        //    renderer.resetCamera();
        //    renderWindow.render();
        //});
        return stlActors[selectElem]
        } else {
            const visibility = stlActors[selectElem].getVisibility();
            console.log(visibility);
            stlActors[selectElem].setVisibility(!visibility);
            renderWindow.render();
        }

};

let comforts = ['winter - LDDC', 'summer - LDDC', 'allyear - LDDC', 'winter - COL', 'summer - COL', 'allyear - COL'];
let velocities = ['0deg', '30deg', '60deg', '90deg', '120deg', '150deg', '180deg', '210deg', '240deg', '270deg', '300deg', '330deg'];
//console.log(document.body)

// Pipeline (reader, mapper, actor)

// Need to read VTP files instead of VTK
// let url = 'https://hordurps.github.io/magU.vtp'
//let magUurl = 'https://hordurps.github.io/velocities.vtp'
let magUurl = 'https://hordurps.github.io/comfortAndVelocity.vtp'
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
//mapper.setColorByArrayName('0deg');
mapper.setColorModeToMapScalars();
mapper.setInterpolateScalarsBeforeMapping();
mapper.setScalarModeToUsePointFieldData();
mapper.setScalarVisibility(true);
//mapper.setScalarRange([0, 15])

const actor  = vtk.Rendering.Core.vtkActor.newInstance();
reader.setUrl(magUurl).then(() => {
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

const lutComfort = vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
lutComfort.addRGBPoint(0.0, 0.56, 0.74, 0.56); // DarkSeaGreen
lutComfort.addRGBPoint(0.25, 0.53, 0.81, 0.98); // LightSkyBlue
lutComfort.addRGBPoint(0.50, 0.94, 0.92, 0.55); // Khaki
lutComfort.addRGBPoint(0.75, 1.0, 0.65, 0.0); // Orange
lutComfort.addRGBPoint(1.0, 0.69, 0.09, 0.12); // IndianRed
//lutComfort.setDiscretize(true);
lutComfort.setNumberOfValues(5);

const lutSafety = vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
//lutSafety.addRGBPoint(0.0, 0.83, 0.83, 0.83); // lightGrey
lutSafety.addRGBPoint(0.0, 0.83, 0.83, 1.0); // lightGrey
lutSafety.addRGBPoint(1.0, 0.69, 0.09, 0.12); // IndianRed
//lutComfort.setDiscretize(true);
lutComfort.setNumberOfValues(2);

function changeColours(selectElem) {
    console.log(selectElem);
    
    if (selectElem.includes('summer') || selectElem.includes('winter')) {
        mapper.setLookupTable(lutComfort);
        mapper.setScalarRange([0, 5]);

    } else if (selectElem.includes('allyear')) {
        mapper.setLookupTable(lutSafety);
        mapper.setScalarRange([0, 2]);
    } else {
        mapper.setLookupTable(lut);
        mapper.setScalarRange([0, 15]);
    }

    //mapper.setLookupTable(lut);
};


// ------------------------------------------------
// Widget manager
// ------------------------------------------------
//const widgetManager = vtk.Widgets.Core.vtkWidgetManager.newInstance();
//widgetManager.setRenderer(renderer);


// ------------------------------------------------
// UI control handling
// ------------------------------------------------
fullScreenRenderer.addController(`<table width="250">
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
    <select name="addons" id="addons-select" with="100%" style="width: 60%; padding: 0.5em 0.2em;">
        <option value="BOI">STL - BOI</option>
        <option value="BDGS">STL - BDGS</option>
    </select>
<!--    <button class="create">+</button> -->
<!--   <button class="delete">-</button> -->
    <button class="create">Show/Hide</button>
</div>
    <div>
        <select name="comfort" id="comfort-select" with="100%" style="width: 100%; padding: 0.5em 0.2em;">
            <option value="comfort">Comfort and Safety</option>
            <option value="summer - LDDC">Summer comfort</option>
            <option value="winter - LDDC">Winter comfort</option>
            <option value="allyear - LDDC">All year safety</option>
        </select>
    </div>
    <div>
        <select name="velocity" id="velocity-select" with="100%" style="width: 100%; padding: 0.5em 0.2em;">
            <option value="Velocity">Velocity</option>
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
//const buttonDelete = document.querySelector('button.delete');

const comfortElem = document.querySelector('select#comfort-select');
const velocityElem = document.querySelector('select#velocity-select');

velocityElem.addEventListener('change', (e) => {
    const selectElem = document.getElementById('velocity-select').value;
    changeArray(selectElem);
    changeColours(selectElem);
    renderWindow.render();
});


comfortElem.addEventListener('change', (e) => {
    const selectElem = document.getElementById('comfort-select').value;
    changeArray(selectElem);
    changeColours(selectElem);
    renderWindow.render();
});

// create widget
buttonCreate.addEventListener('click', () => {
    const selectElem = document.getElementById('addons-select').value;
    var w = stlWidget(selectElem);
    renderWindow.render();
});

//buttonDelete.addEventListener('click', () => {
//    const selectElem = document.getElementById('addons-select').value;
//    console.log(selectElem);
//    //renderer.removeActor(stlActor);
//    //renderer.removeActor(stlActors.selectElem);
//    console.log(stlActors);
//    const visibility = stlActors[selectElem].getVisibility();
//    console.log(visibility);
//    stlActors[selectElem].setVisibility(!visibility);
//    renderWindow.render();
//});

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
