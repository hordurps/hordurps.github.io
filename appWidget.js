const container = document.querySelector('#container');

const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
    background: [0.8, 0.8, 0.8],
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
        var widget = 'STL';
        var stlurl = 'https://hordurps.github.io/BOI.stl';
    } else if (selectElem.includes('BDGS')) {
        var widget = 'STL';
        var stlurl = 'https://hordurps.github.io/BDGS.stl';
    } else if (selectElem.includes('SBAR')) {
        var widget = 'SBAR';
    }
    // checkin if the key does NOT exist in dictionary, then create keys
    if (widget.includes('STL')) {
        if (!(selectElem in stlReaders)) {
            var stls = createSTL();
            stlReaders[selectElem] = stls[0]; 
            stlMappers[selectElem] = stls[1]; 
            stlActors[selectElem] = stls[2];
            console.log(stlReaders.selectElem);
            console.log(stlActors.selectElem);
            console.log(stlMappers.selectElem);
        
            stlActors[selectElem].setMapper(stlMappers[selectElem]);
            stlMappers[selectElem].setInputConnection(stlReaders[selectElem].getOutputPort());
            stlReaders[selectElem].setUrl(stlurl).then(() => {
                renderer.addActor(stlActors[selectElem]);
                renderer.resetCamera();
                renderWindow.render();
            });
        
            return stlActors[selectElem]
            } else {
                const visibility = stlActors[selectElem].getVisibility();
                console.log(visibility);
                stlActors[selectElem].setVisibility(!visibility);
                renderWindow.render();
            }
        } else if (widget.includes('SBAR')) {
            if (!(document.getElementById('sliderbar'))) {
            createSBAR();
            } else {
                document.getElementById('sliderbar').remove();
                mapper.setScalarRange([0, 15.0]);
            }
            console.log(widget);
            renderWindow.render();
        }

};

//let comforts = ['winter - LDDC', 'summer - LDDC', 'allyear - LDDC', 'winter - COL', 'summer - COL', 'allyear - COL'];
let all_velocities = ['0deg', '30deg', '60deg', '90deg', '120deg', '150deg', '180deg', '210deg', '240deg', '270deg', '300deg', '330deg'];
//console.log(document.body)

// Pipeline (reader, mapper, actor)

// Need to read VTP files instead of VTK
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
    console.log(polydata);
    const numberOfArrays = polydata.getPointData().getNumberOfArrays();
    let velocities = []
    let comforts = []
    for (let step = 0; step < numberOfArrays; step++) {
        const arrayName = polydata.getPointData().getArrayName(step);
        if (arrayName.includes('deg')) {
            velocities.push(arrayName);
        } else if (arrayName.includes('LDDC')) {
            comforts.push(arrayName);
        }
    }
    console.log(velocities);
    console.log(comforts);
    let new_velocities = intersection_arrays(all_velocities, velocities);
    add_options_to_select(new_velocities, comforts);
    actor.setMapper(mapper);
    mapper.setInputConnection(reader.getOutputPort());
    renderer.addActor(actor);

    // Render
    renderer.resetCamera();
   // renderer.getActiveCamera().setPosition(0, 0, 1050);
   // renderer.getActiveCamera().setFocalPoint(0, 0, 0.41);
   // renderer.getActiveCamera().setParallelScale(980);

    const page_load = document.getElementById('page_load');
    page_load.parentNode.removeChild(page_load);
    renderWindow.render();
});
renderWindow.render();

function intersection_arrays (a,b) {
    return a.filter(Set.prototype.has, new Set(b));

}


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

const lutHighlight = vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
lutHighlight.applyColorMap(cmap);
lutHighlight.setMappingRange(0, 256);
lutHighlight.updateRange();

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
            <th>Wind Comfort</th>
<!--            <th>Widget</th>
            <th title="Pickable">P</th>
            <th title="Visibility">V</th>
            <th title="ContextVisibility">C</th>
            <th title="HandleVisibility">H</th>
            <th></th>
-->
        </tr>
    </thead>
    <tbody class="widgetList">
    </tbody>
</table>
<div>
    <select name="addons" id="addons-select" with="100%" style="width: 60%; padding: 0.5em 0.2em;">
        <option value="BOI">STL - BOI</option>
        <option value="BDGS">STL - BDGS</option>
<!--        <option value="SBAR">Scalarbar</option>  -->
    </select>
<!--    <button class="create">+</button> -->
<!--   <button class="delete">-</button> -->
    <button class="create">Show/Hide</button>
</div>
    <div>
        <select name="comfort" id="comfort-select" with="100%" style="width: 100%; padding: 0.5em 0.2em;">
            <option value="comfort">Comfort and Safety</option>
    <!--
            <option value="summer - LDDC">Summer comfort</option>
            <option value="winter - LDDC">Winter comfort</option>
            <option value="allyear - LDDC">All year safety</option>
    -->
        </select>
    </div>
    <div>
        <select name="velocity" id="velocity-select" with="100%" style="width: 100%; padding: 0.5em 0.2em;">
            <option value="Velocity">Velocity</option>
    <!--
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
    -->
        </select>
    </div>
    `);

function add_options_to_select(new_velocities, comforts) {
    const velocitySelectElem = document.getElementById('velocity-select');
    for (var i = 1; i <= new_velocities.length; i++) {
        var opt = document.createElement('option');
        opt.value = new_velocities[i-1];
        opt.name = new_velocities[i-1];
        opt.innerHTML = new_velocities[i-1];
        velocitySelectElem.appendChild(opt);
    }
    
    const comfortSelectElem = document.getElementById('comfort-select');
    for (var i = 1; i <= comforts.length; i++) {
        var opt = document.createElement('option');
        opt.value = comforts[i-1];
        opt.name = comforts[i-1];
        opt.innerHTML = comforts[i-1];
        comfortSelectElem.appendChild(opt);
    }
}


function add_sliderbar_to_options(){
    const addonsSelectElem = document.getElementById('addons-select');
    var opt = document.createElement('option');
    opt.value = 'SBAR';
    opt.id = 'SBAR';
    opt.name = 'SBAR';
    opt.innerHTML = 'Scalarbar';
    addonsSelectElem.appendChild(opt);
    document.querySelector('select#addons-select').selectedIndex = 2;
}


function updateValue(e) {
    const newValue = Number(e.target.value);
    //mapper.setScalarRange([newValue-0.25, newValue+0.25]);
   // lut.setRange([newValue-0.25, newValue+0.25]);
    //lutHighlight.removeAllPoints();
    //lutHighlight.addRGBPoint(newValue, 0.0, 1.0, 1.0);
    lutHighlight.setBelowRangeColor(0.0, 1.0, 1.0, 1.0);
    lutHighlight.setAboveRangeColor(10.0, 1.0, 1.0, 1.0);
    lutHighlight.updateRange();
    mapper.setLookupTable(lutHighlight);
    mapper.setScalarRange([newValue, 15.0]);
    updateSliderUI(newValue);
    renderWindow.render();
}

function createSBAR() {
    createSliderUI();

    var dragValue = document.querySelector('.value');
    const range = mapper.getScalarRange();
    console.log(range);
    dragValue.setAttribute('min', 0.0);
    dragValue.setAttribute('max', 15.0);
    dragValue.setAttribute('value', 0.0)
    dragValue.addEventListener('input', updateValue);
};

const widgetListElem = document.querySelector('.widgetList');
// const selectElem = document.querySelector('select');
const buttonCreate = document.querySelector('button.create');
//const buttonDelete = document.querySelector('button.delete');

const comfortElem = document.querySelector('select#comfort-select');
const velocityElem = document.querySelector('select#velocity-select');

velocityElem.addEventListener('change', (e) => {
    const selectElem = document.getElementById('velocity-select').value;
    document.querySelector('select#comfort-select').selectedIndex = 0;
    changeArray(selectElem);
    changeColours(selectElem);
    if (!(document.getElementById('SBAR'))){
        add_sliderbar_to_options();
    }
    renderWindow.render();
});


comfortElem.addEventListener('change', (e) => {
    const selectElem = document.getElementById('comfort-select').value;
    document.querySelector('select#velocity-select').selectedIndex = 0;
    changeArray(selectElem);
    changeColours(selectElem);
    if (document.getElementById('SBAR')){
        document.getElementById('SBAR').remove()
    }
    if ((document.getElementById('sliderbar'))) {
        document.getElementById('sliderbar').remove();
    }
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

function updateSliderUI(currentValue) {
    document.querySelector('td#minValue').innerHTML = currentValue;
}

function createSliderUI() {
    widgetListElem.innerHTML = `<table>
        <tr id='sliderbar'>
            <td id='minValue'>0.0</td>
            <td>
                <input class='value' type="range" min="0.0" max="15.0" step="1.0" value="0.0" />
            </td>
            <td id='maxValue'>15.0</td>
        </tr>
    </table>`
}
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


