import dash
import dash_vtk
import dash_bootstrap_components as dbc
#import dash_html_components as html
#import dash_core_components as dcc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State

import random
#import json
import numpy as np
import pyvista as pv
from pyvista import examples
from vtk.util.numpy_support import vtk_to_numpy

from dash_vtk.utils import presets, to_mesh_state 
import os
import vtk as vtk

from app import app

iname="-jan"

def toDropOption(name):
    return {"label": name, "value": name}

####################### VTKS ###############################################

def _load_vtk(vtk_filename, fieldName=None, point_arrays=[], cell_arrays=[]):
    with open(vtk_filename, 'rb') as fr:
        lines = fr.readlines()
        for line in lines:
            if b'DATASET' in line:
                if b'POLYDATA' in line:
                    reader = vtk.vtkPolyDataReader()
                elif b'UNSTRUCTURED_GRID' in line:
                    reader = vtk.vtkUnstructuredGridReader()
                else:
                    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(vtk_filename)
    reader.Update()

    #reader = _compute_normals(reader)
    return to_mesh_state(reader.GetOutput(), fieldName, point_arrays, cell_arrays)

def _compute_normals(reader):
    """
        Attempt to compute normals as per smooth shading in pyvista

        Does not work..
    """
    cell_normals = True
    point_normals = True
    split_vertices = True
    feature_angle = 30
    consistent_normals = True
    auto_orient_normals = False
    non_manifold_traversal = True
    track_vertices = False
    alg = vtk.vtkPolyDataNormals()
    alg.SetInputData(reader.GetOutput())
    alg.SetComputeCellNormals(cell_normals)
    alg.SetComputePointNormals(point_normals)
    alg.SetSplitting(split_vertices)
    alg.SetConsistency(consistent_normals)
    alg.SetAutoOrientNormals(auto_orient_normals)
    alg.SetNonManifoldTraversal(non_manifold_traversal)
    alg.SetFeatureAngle(feature_angle)
    alg.Update()
    return alg






vtk_path = f'assets/vtk{iname}/'
f = [f for f in os.listdir(vtk_path) if f.endswith('.vtk')]
meshes = {f'{mesh}' : pv.read(os.path.join(vtk_path, mesh)) for mesh in f}
mesh_arrays = {mesh_name.replace(".vtk", "") : list(mesh.point_data) for mesh_name, mesh in meshes.items()}

def _get_color_range(values, arrayName, mesh_name=None):
    """
        Velocity should have a range from 0 to 15
        Comfort should have a range from 0 to 4
        Safety should have a range from 0 to 2
    """
    if mesh_name is not None and "probability_analysis" in mesh_name:
        maxVal = 345
        minVal = -15
    else:
        #maxVal = np.min([15, np.max(values)])
        #minVal = np.max([0, np.min(values)])
        if "nen" in arrayName or "lddc" in arrayName:
            minVal, maxVal = -0.5, 2.5
        elif any([u in arrayName for u in ["UsUref", "Us", "magU"]]):
            minVal, maxVal = 0, 15
        else:
            minVal, maxVal = -0.5, 4.5

    color_range = [minVal, maxVal]
    return color_range

def _get_cbar_name(arrayName, mesh_name=None):

        
    if (mesh_name is not None and "probability_analysis" in mesh_name):
        cbar = "Rainbow Desaturated"
    else:
        if "nen" in arrayName or "lddc" in arrayName:
            cbar = "X Ray"
        elif any([u in arrayName for u in ["UsUref", "Us", "magU"]]):
            cbar = "Cool to Warm (Extended)"
        else:
            cbar = "Cool to Warm (Extended)"
    return cbar

#mesh = pv.read(os.path.join(vtk_path, f[0]))
#arrays = list(mesh.point_data)
#points = mesh.points.ravel()
#polys = vtk_to_numpy(mesh.GetPolys().GetData())
meshes_child = {}
mesh_names = []
mesh_ids = {}
f.append(f.pop(f.index([v for v in f if "grades" in v][0])))
#for mesh_filename, mesh in meshes.items():
for i, mesh_filename in enumerate(f):
    mesh_name = mesh_filename.replace(".vtk","")
    mesh = _load_vtk(os.path.join(vtk_path, mesh_filename), point_arrays=mesh_arrays[mesh_name])
    demoArray_name = mesh_arrays[mesh_name][0]
    demoArray_values = meshes[mesh_name+'.vtk'][demoArray_name]
    color_range = _get_color_range(demoArray_values, demoArray_name, mesh_name)
    cbar = _get_cbar_name(demoArray_name, mesh_name)

    if i == len(f)-1:
        visibility = 1
    else:
        visibility = 0
    child = dash_vtk.GeometryRepresentation(
        id=f"{mesh_name}-rep{iname}",
        colorMapPreset=cbar, #"Cool to Warm (Extended)", 
        colorDataRange=color_range,
        showCubeAxes=False,
        cubeAxesStyle={"axisLabels": ["", "", "Altitude"]},
        actor={"visibility" : visibility},
        mapper={"scalarVisibility": True, 
                "colorByArrayName" : demoArray_name,
                "scalarMode" : 3,
                "interpolateScalarsBeforeMapping" : True,},
        children=[dash_vtk.Mesh(id=f"{mesh_name}-mesh{iname}", state=mesh)],
    )
    #points = mesh.points.ravel()
    #polys = vtk_to_numpy(mesh.GetPolys().GetData())
    #arrays = list(mesh.point_data)
    #values = mesh[arrays[0]]
    #child=dash_vtk.GeometryRepresentation(
    #    id=f"{mesh_name}-rep",
    #    colorMapPreset="Cool to Warm (Extended)", 
    #    colorDataRange=[0,15], #color_range
    #    property={"edgeVisibility": False},
    #    showCubeAxes=True,
    #    cubeAxesStyle={"axisLabels": ["", "", "Altitude"]},
    #    actor={"visibility" : 1},
    #    mapper={"scalarVisibility": False},
    #    children=[dash_vtk.PolyData(
    #                id=f"{mesh_name}-polydata",
    #                points=points,
    #                polys=polys,
    #                children=[
    #                    dash_vtk.PointData(
    #                        [
    #                            dash_vtk.DataArray(
    #                                id=f"{mesh_name}-array",
    #                                registration="setScalars",
    #                                name="values",
    #                                values=values,
    #                            )
    #                        ]
    #                    )
    #                ],
    #            )
    #            ],
    #)
    meshes_child[mesh_name] = child
    mesh_ids[mesh_name] = f"{mesh_name}-mesh{iname}"
    mesh_names.append(mesh_name)


##########################################################################
####################### STREAMS ###############################################


def _load_streams(streams_filename, fieldName=None, point_arrays=[], cell_arrays=[]):
    # works for streams from paraview, which are unstructured grid
    # autostreams are polygonal mesh, which isn't read
    streams_reader = vtk.vtkUnstructuredGridReader()
    streams_reader.SetFileName(streams_filename)
    streams_reader.Update()
    streams_mesh = to_mesh_state(streams_reader.GetOutput(), fieldName, point_arrays, cell_arrays)
    return streams_mesh


streams_path = f'assets/streams{iname}/'
#streams = [f for f in os.listdir(streams_path) if f.endswith('.vtp')]
streams = [f for f in os.listdir(streams_path) if f.endswith('.vtk')] # clean_autostreams_wdir.vtk
stream_reps, stream_mesh_ids = [], []
if streams:
    stream_test = pv.read(os.path.join(streams_path, streams[0]))
    stream_arrays = list(stream_test.point_data)
    demoArrayStream_name = stream_arrays[0]
    demoArrayStream_values = stream_test[demoArrayStream_name]
    
    for stream in streams:
        stream_mesh = _load_streams(os.path.join(streams_path, stream), point_arrays=stream_arrays)
        stream_name = stream.replace(".vtk", "") # clean_autostreams_wdir
        child = dash_vtk.GeometryRepresentation(
                id=f"{stream_name}-rep{iname}", # clean_autostreams_wdir-rep{iname}
                mapper={
                    "colorByArrayName": stream_arrays[0],
                    "scalarMode": 3,
                    "interpolateScalarsBeforeMapping": True,
                    "scalarVisibility": True,
                },
                #property={
                #    "edgeVisibility": False,
                #    'representation': 2,
                #},
                actor={"visibility" : 0},
                colorMapPreset="Cool to Warm (Extended)", 
                colorDataRange=[0,15],
                children=[dash_vtk.Mesh(id=f"{stream_name}-mesh{iname}", state=stream_mesh)],
            ) 
        stream_reps.append(child)
        stream_mesh_ids.append(f"{stream}{iname}")
    #streams = {f'{m}' : pv.read(os.path.join(streams_path, m)) for m in s}

##########################################################################
####################### STL ###############################################
def _load_stl(filename):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    mesh_state = to_mesh_state(reader.GetOutput())
    return mesh_state

stl_path = f'assets/stl{iname}/'
stls = [os.path.join(stl_path, s) for s in os.listdir(stl_path) if s.endswith('.stl')]

buildings_rep, buildings_mesh_ids, buildings_meshes, stl_names = [], [], [], []
if stls:
    toggle_stl_visbility = 'block'
    for stl in stls:
        stl_mesh = _load_stl(stl)
        stl_name = stl.split("/")[-1].replace(".stl","")
        child = dash_vtk.GeometryRepresentation(
            id=f"{stl_name}-rep{iname}",
            actor={"visibility" : 1},
            mapper={"scalarVisibility" : False},
            children=[dash_vtk.Mesh(id=f"{stl_name}-mesh{iname}", state=stl_mesh)]
        )
        buildings_rep.append(child)
        buildings_mesh_ids.append(f"{stl_name}-mesh{iname}")
        buildings_meshes.append(stl_mesh)
        stl_names.append(stl_name)
else:
    toggle_stl_visbility = 'none'


##########################################################################

def update_streams(streams, stream_array):
    stream_arrays = list(streams.point_data)
    if stream_array not in stream_arrays:
        stream_array = stream_arrays[0]
    values = streams[stream_array]
    points = streams.points.ravel()
    polys = vtk_to_numpy(streams.GetPolys().GetData())
    maxVal = np.min([15, np.max(values)])
    minVal = np.max([0, np.min(values)])
    color_range = [minVal, maxVal]
    if "magU" in stream_array:
        cbar = ["Cool to Warm (Extended)"]
    else:
        cbar = ["Cool to Warm (Extended)"]

    return [stream_arrays, points, polys, values, color_range, stream_array, cbar]

#stream_arrays, stream_points, stream_polys, stream_values, stream_color_range, stream_array, stream_cbar = update_streams(stream, stream_arrays[0])

stl_contents = []
for stl_file in stls:
    txt_content=None
    with open(stl_file, 'r') as f:
       txt_content = f.read()
    stl_contents.append(txt_content)


def read_stl_file(stl_file):
    txt_content=None
    with open(stl_file, 'r') as f:
       txt_content = f.read()
    return dash_vtk.GeometryRepresentation([dash_vtk.Reader(vtkClass="vtkSTLReader", parseAsText=txt_content)])

def update_mesh(mesh, array):
    arrays = list(mesh.point_data)
    if array not in arrays:
        array = arrays[0]
    values = mesh[array]
    points = mesh.points.ravel()
    polys = vtk_to_numpy(mesh.GetPolys().GetData())
    maxVal = np.min([15, np.max(values)])
    minVal = np.max([0, np.min(values)])
    color_range = [minVal, maxVal]
    if "UsUref" in array or "Us" in array:
        cbar = ["Cool to Warm (Extended)"]
    elif "nen" in array or "lddc" in array:
        #cbar = ["RdOrYl"]
        #cbar = ["Rainbow Blended White"]
        #cbar = ["Rainbow Desaturated"]
        cbar = ["X Ray"]
    else:
        cbar = ["Cool to Warm (Extended)"]


    #if "UsUref" in array:
    #    #cbar = ["RdYlBu_r", 256]
    #    cbar = ["Cool to Warm (Extended)", 256]
    #elif "Us" in array:
    #    #cbar = ["RdYlBu_r", 256]
    #    cbar = ["Cool to Warm (Extended)", 256]
    #elif "nen" in array or "lddc" in array:
    #    cbar = ["YlOrRd", 2]
    #else:
    #    #cbar = ["RdYlBu_r", 5]
    #    cbar = ["Cool to Warm (Extended)", 5]
    #plt.cm.get_cmap(cbar[0], cbar[1])
    return [arrays, points, polys, values, color_range, array, cbar]



#arrays, points, polys, values, color_range, array, cbar = update_mesh(mesh, arrays[0])
#
def update_streams(streams_filename):
    streams_reader = vtk.vtkXMLPolyDataReader()
    streams_reader.SetFileName(streams_filename)
    streams_reader.Update()
    streams_mesh = to_mesh_state(streams_reader.GetOutput(), "magU")
    return streams_mesh


#####################

#vtk_view = dash_vtk.View(
#    id="vtk-view",
#    background=[i/255.0 for i in [25, 34, 61]],
#    pickingModes=["hover"],
#    children=[
#        dash_vtk.GeometryRepresentation(
#            id="vtk-representation",
#            children=[
#                dash_vtk.PolyData(
#                    id="vtk-polydata",
#                    points=points,
#                    polys=polys,
#                    children=[
#                        dash_vtk.PointData(
#                            [
#                                dash_vtk.DataArray(
#                                    id="vtk-array",
#                                    registration="setScalars",
#                                    name="values",
#                                    values=mesh[arrays[0]],
#                                )
#                            ]
#                        )
#                    ],
#                )
#            ],
#            colorMapPreset="coolwarm", #"erdc_blue2green_muted",
#            colorDataRange=color_range,
#            property={"edgeVisibility": False},
#            showCubeAxes=True,
#            cubeAxesStyle={"axisLabels": ["", "", "Altitude"]},
#        ),
#        dash_vtk.GeometryRepresentation(
#            id="pick-rep",
#            actor={"visibility": False},
#            children=[
#                dash_vtk.Algorithm(
#                    id="pick-sphere",
#                    vtkClass="vtkSphereSource",
#                    state={"radius": 100},
#                )
#            ],
#        ),
#        #html.Div(id='stl-div', children=
#        #    #[update_stl_state(stl) for stl in stls]
#        #    [read_stl_file(stl) for stl in stls]
#        #),
#        dash_vtk.GeometryRepresentation(
#            id='stl-rep',
#            children=[
#                dash_vtk.Reader(vtkClass="vtkSTLReader", parseAsText=txt_content) for txt_content in stl_contents
#            ],
#            actor={"visibility" : 1},
#            mapper={"scalarVisibility" : False}
#        ),
#        dash_vtk.GeometryRepresentation(
#            id="streams-rep",
#            children=[
#                dash_vtk.Mesh(
#                    id="streams",
#                    state=update_streams(os.path.join(streams_path, s[0]))
#                    )
#                ],
#            mapper={
#                "colorByArrayName":"magU",
#                "scalarMode": 1,
#                "interpolateScalarsBeforeMapping": True,
#                "useLookupTableScalarRange":True,
#                "colorMode":1,
#                "GetArray":1,
#                "scalarVisibility":True,
#                "scalarRange": [0,15]
#            },
#            property={
#                "edgeVisibility": False,
#                'representation': 2,
#            },
#            actor={
#                "visibility":1,
#            },
#            colorMapPreset="Cool to Warm (Extended)", 
#            colorDataRange=[0,15],
#        ) 
#        #dash_vtk.GeometryRepresentation(
#        #    id='vtk-streams',
#        #    children=[
#        #        dash_vtk.PolyData(
#        #            id="vtk-streams-polydata",
#        #            points=stream_points,
#        #            polys=stream_polys,
#        #            children=[
#        #                dash_vtk.DataArray(
#        #                    id="streams-array",
#        #                    registration="setScalars",
#        #                    name="values",
#        #                    values=stream_arrays[0],
#        #                ),
#        #            ],
#        #        ),
#        #    ],
#        #    colorMapPreset="coolwarm",
#        #    colorDataRange=stream_color_range,
#        #),
#        #dash_vtk.GeometryRepresentation(
#        #    children=[
#        #        dash_vtk.Mesh(state=update_stl_reader(stls)),
#        #        #dash_vtk.Mesh(state=update_stl_state(stls[0])),
#        #        #dash_vtk.Mesh(state=update_stl_state(stls[1])),
#        #    ]
#        #    #dash_vtk.Mesh(state=stls_states),
#        #),
#    ],
#)
def check_streams_availability(currentArray):
    if any([u in currentArray for u in ["UsUref", "Us", "magU"]]):
        wdir = currentArray.split('_')[0]
        if any([stream_wdir==wdir for stream_mesh_id in stream_mesh_ids for stream_wdir in stream_mesh_id.split(iname)[0].replace(".vtk","").split("_") ]):
            return False
        else:
            return True
    else:
        return True

toggle_STL_controls = [
html.Div(
    dbc.Card(
        [
            dbc.CardHeader("Geometry"),
            dbc.CardBody(
                [
                    dcc.Checklist(
                        id=f'toggle-stls{iname}',
                        options=[
                            {"label" : f" {stl_name}", "value" : f"{stl_name}"} for stl_name in stl_names
                        ],
                        labelStyle={"display" : "block"},
                        value=stl_names
                        ),
                ]
            ),
        ],
        color="danger",
        outline=True,
    ),
    style={'display' : toggle_stl_visbility}
),
]
other_toggle_controls = [
    dbc.Card(
        [
            dbc.CardHeader("Toggle"),
            dbc.CardBody(
                [
                        dcc.Checklist(
                            id=f"toggle-cube-axes{iname}",
                            options=[
                                {"label": " Show axis grid", "value": "grid"},
                            ],
                            value=[],
                            #labelStyle={"display": "inline-block"},
                            labelStyle={"display": "block"},
                        ),
                        dcc.Checklist(
                            id=f"toggle-streams{iname}",
                            options=[{"label" : " Show streamlines", "value" : "streams", "disabled" : check_streams_availability(demoArray_name)}]
                        ),
                        dcc.Checklist(
                            id=f"toggle-color{iname}",
                            options=[{"label" : " Hide colour", "value" : "colour", "disabled" : False}],
                            value=[],
                            labelStyle={"display": "inline-block"},
                        ),
                ]
            ),
        ],
        color="danger",
        outline=True,
    ),
]
selection_controls = [
    dbc.Card(
        [
            dbc.CardHeader("Selection"),
            dbc.CardBody(
                [
                    dcc.Dropdown(
                            id=f"dropdown-meshes{iname}",
                            options=mesh_names,
                            value=mesh_name,
                        ),
                    dcc.Dropdown(
                            id=f"dropdown-array-preset{iname}",
                            options=mesh_arrays[mesh_name],
                            value=demoArray_name,
                        ),
                ], 
            ),
        ],
        color="danger",
        outline=True,
    ),
]


layout = dbc.Container(
    fluid=True,
    #style={"height": "100vh"},
    children=[
        dbc.Row(
            [
                dbc.Col(width=4, children=selection_controls),
                dbc.Col(width=3, children=other_toggle_controls),
                dbc.Col(width=3, children=toggle_STL_controls),
            ], id=f'top-row{iname}', style = {}
            ),
        dbc.Row(
            [
                dbc.Col(
                    width=12,
                    children=[
                        html.Div(
                                dbc.Spinner(color='light'),
                                style={
                                            #"background-color": "#334c66",
                                            "background-color" : "#19223d",
                                            #"height": "calc(100vh - 230px)",
                                            "height": "calc(100vh - 200px)",
                                            "width": "100%",
                                            "text-align": "center",
                                            "padding-top": "calc(50vh - 105px)",

                                            "border" : "solid red 0.1px",
                                        },
                                id=f"vtk-view-subcontainer{iname}",
                            ),
                    ],
                    id=f"vtk-view-container{iname}",
                    style={"height": "calc(100vh - 230px)", "width": "100%"}
                    )
            
            ],
            #style={"height": "12%", "alignItems": "center"},
            #style={"margin-top" : "15px", "height": "calc(100vh - 230px)"},
            style={"margin-top" : "15px", "height": "100%"},
        ),
        #dbc.Row(
        #    [dbc.Col(
        #        width=8,
        #        children=[
        #            html.Div(
        #                    dbc.Spinner(color='light'),
        #                    style={
        #                                "background-color": "#334c66",
        #                                "height": "calc(100vh - 230px)",
        #                                "width": "100%",
        #                                "text-align": "center",
        #                                "padding-top": "calc(50vh - 105px)",
        #                            },
        #                ),
        #        ],
        #        id="vtk-view-container",
        #        style={"height": "100%", "width": "100%"}
        #        )
        #    ],
        #),
        #html.Div(
        #    html.Div(vtk_view, style={"height": "100%", "width": "100%"}),
        #    style={"height": "88%"},
        #),
        #html.Pre(
        #    id="tooltip",
        #    style={
        #        "position": "absolute",
        #        "bottom": "25px",
        #        "left": "25px",
        #        "zIndex": 1,
        #        "color": "white",
        #    },
        #),
    ],
)

@app.callback(Output(f"vtk-view-container{iname}", "children"),
    [Input(f"toggle-stls{iname}", "value"), Input(f"dropdown-meshes{iname}", "value"), Input(f"dropdown-array-preset{iname}", "value")]
    )
def initial_loading(stls, selected_mesh_name, selected_array_name):
    triggered = dash.callback_context.triggered

    if triggered:
        return dash.no_update

    tooltip = html.Pre(
            id=f"tooltip{iname}",
            style={
                "position": "absolute",
                "bottom": "5px",
                "left": "25px",
                "zIndex": 4,
                "color": "white",
                "display" : "flex",
                "flex-flow" : "column wrap",
                #"background-color"  :"#19223d",
                #"border" : "1px solid red", 
                #"padding" : "10px"
                #"max-height" : "50%"
            },
        )

    pointer = dash_vtk.GeometryRepresentation(
            id=f"pick-rep{iname}",
            actor={"visibility": False},
            children=[
                dash_vtk.Algorithm(
                    id=f"pick-sphere{iname}",
                    vtkClass="vtkSphereSource",
                    state={"radius": 100},
                )
            ],
    )

    vtk_view = dash_vtk.View(
        id=f"vtk-view{iname}",
        children = buildings_rep + list(meshes_child.values()) + stream_reps + [pointer, tooltip],
        pickingModes = ["hover"], # ["click"],
        background=[i/255.0 for i in [25, 34, 61]],
        #cameraViewUp=[0,1,0],
        #cameraPosition=[0,0,1],
        #cameraParallelProjection=False,
        #triggerResetCamera=1,
        style={"width" : "100%", "height" : "100%",}
        )

    vtk_view_return = html.Div(
        vtk_view,
        style={
                    #"background-color": "#334c66",
                    "background-color" : "#19223d",
                    #"height": "calc(100vh - 230px)",
                    #"height": "calc(100vh - 200px)",
                    "height": "100%",
                    "width": "100%",
                    "text-align": "center",
                    #"padding-top": "calc(50vh - 105px)",

                    "border" : "solid red 0.1px",
                },
        id=f"vtk-view-subcontainer{iname}",
    )


    #return vtk_view
    return vtk_view_return

    #return dash_vtk.View(
    #    id=f"vtk-view{iname}",
    #    children = buildings_rep + list(meshes_child.values()) + stream_reps + [pointer, tooltip],
    #    pickingModes = ["hover"], # ["click"],
    #    background=[i/255.0 for i in [25, 34, 61]],
    #    )

@app.callback(
    [Output(f"vtk-view{iname}", "triggerRender")]
    + [Output(item.id, "actor") for item in buildings_rep]
    + [Output(item.id, "mapper") for item in buildings_rep]
    + [Output(item.id, "actor") for item in meshes_child.values()]
    + [Output(item.id, "mapper") for item in meshes_child.values()]
    + [Output(f"dropdown-array-preset{iname}", "options"), Output(f"dropdown-array-preset{iname}", "value")]
    + [Output(item.id, "colorMapPreset") for item in meshes_child.values()]
    + [Output(item.id, "colorDataRange") for item in meshes_child.values()]
    + [Output(item.id, "showCubeAxes") for item in meshes_child.values()]
    + [Output(item.id, "actor") for item in stream_reps]
    + [Output(f"toggle-streams{iname}", "options"), Output(f"toggle-streams{iname}", "value")]
    + [Output(f"toggle-color{iname}", "value")],
    [
        Input(f"toggle-stls{iname}", "value"),
        Input(f"dropdown-meshes{iname}", "value"),
        Input(f"dropdown-array-preset{iname}", "value"),
        Input(f"toggle-cube-axes{iname}", "value"),
        Input(f"toggle-streams{iname}", "value"),
        Input(f"toggle-color{iname}", "value")
    ],
    prevent_initial_call=True
    )
def update_scene(stls, selected_mesh_name, selected_array_name, cubeAxes, showStreams, showColor):
    triggered = dash.callback_context.triggered
    triggered_mesh, triggered_array, derived_array = None, None, None
    # update geom visibility
    geom_visibility = []
    if triggered and f"toggle-stls{iname}" in triggered[0]["prop_id"]:
        geom_visibility = [
            {"visibility" : 1}
        if part.id.replace(f"-rep{iname}", "") in triggered[0]["value"]
        else {"visibility" : 0}
        for part in buildings_rep
        ]
    else:
        geom_visibility = [dash.no_update for item in buildings_rep]

    if triggered and f"toggle-streams{iname}" in triggered[0]["prop_id"]:
        if showStreams:
            streams_visibility = [
            {"visibility" : 1}
            #if selected_array_name.split("_")[0] in part.id
            if selected_array_name.split("_")[0] == part.id.split(f"-rep{iname}")[0].split('_')[-1]
            else {"visibility" : 0}
            for part in stream_reps
            ]
        else:
            streams_visibility = [{"visibility" : 0 }] * len(stream_reps)
    else:
        streams_visibility = [dash.no_update for item in stream_reps]


    vtk_mapper_triggered = False

    if triggered and f"dropdown-meshes{iname}" in triggered[0]["prop_id"]:
        triggered_mesh = triggered[0]["value"]
        derived_array = mesh_arrays[triggered_mesh][0]

        vtk_visibility = [
        {"visibility" : 1}
        #if mesh_name in triggered[0]["value"]
        if mesh_name in triggered_mesh
        else {"visibility" : 0}
        for mesh_name in meshes_child.keys()
        ]

        #dropdown_array = [mesh_arrays[triggered[0]["value"]], mesh_arrays[triggered[0]["value"]][0]]
        dropdown_array = [mesh_arrays[triggered_mesh], derived_array]
        vtk_mapper = _trigger_mapper(derived_array, triggered_mesh)
        #vtk_mapper = _trigger_mapper(mesh_arrays[triggered[0]["value"]][0], triggered[0]["value"])
        vtk_mapper_triggered = True
    else:
        vtk_visibility = [dash.no_update] * len(meshes_child)
        dropdown_array = [dash.no_update] * 2

    if triggered and f"dropdown-array-preset{iname}" in triggered[0]["prop_id"]:
        triggered_array = triggered[0]["value"]
        vtk_mapper = [
            {
                #"colorByArrayName" : triggered[0]["value"],
                "colorByArrayName" : triggered_array,
                #"scalarMode" : 3,
                #"interpolateScalarsBeforeMapping" : True,
                "scalarVisibility" : True,
            }
        #if mesh_array in triggered[0]["values"]
        if mesh_name in selected_mesh_name
        else {"scalarVisibility" : False}
        for mesh_name in meshes_child.keys()
        ]
        if showStreams:
            streams_visibility = [
            {"visibility" : 1}
            #if selected_array_name.split("_")[0] in part.id
            if selected_array_name.split("_")[0] == part.id.split(f"-rep{iname}")[0].split('_')[-1]
            else {"visibility" : 0}
            for part in stream_reps
            ]
    else:
        if not vtk_mapper_triggered:
            vtk_mapper = [dash.no_update] * len(meshes_child)

    vtk_cbar_name = []
    vtk_cbar_range = []
    for mesh_name in meshes_child.keys():
        if mesh_name == selected_mesh_name:
            for array in mesh_arrays[mesh_name]: 
                if array == triggered_array:
                    cbar = _get_cbar_name(triggered_array, mesh_name)
                    color_range = _get_color_range(meshes[selected_mesh_name+'.vtk'][triggered_array], triggered_array, mesh_name)
                    break
                elif array == derived_array:
                    cbar = _get_cbar_name(derived_array, mesh_name)
                    color_range = _get_color_range(meshes[selected_mesh_name+'.vtk'][derived_array], derived_array, mesh_name)
                    break
                else:
                    cbar = _get_cbar_name(selected_array_name, mesh_name)
                    try:
                        color_range = _get_color_range(meshes[selected_mesh_name+'.vtk'][selected_array_name], selected_array_name, mesh_name)
                    except:
                        color_range = [0,1]
        else: 
            cbar = "Cool to Warm (Extended)"
            color_range = [0, 15]
        vtk_cbar_name.append(cbar)
        vtk_cbar_range.append(color_range)

    if triggered_array is not None:
        disable_streams = check_streams_availability(triggered_array)
    elif derived_array is not None: 
        disable_streams = check_streams_availability(derived_array)
    else:
        disable_streams = check_streams_availability(selected_array_name)

    if disable_streams:
        toggle_streams = [[{"label" : " Show streamlines", "value" : "streams", "disabled" : disable_streams}], [] ]
        streams_visibility = [{"visibility" : 0 }] * len(stream_reps)
    elif showStreams is None:
        toggle_streams = [[{"label" : " Show streamlines", "value" : "streams", "disabled" : disable_streams}], [] ]
    else:
        toggle_streams = [[{"label" : " Show streamlines", "value" : "streams", "disabled" : disable_streams}], showStreams ]

    if triggered and f"toggle-color{iname}" in triggered[0]["prop_id"]:
        vtk_mapper = [
        {"scalarVisibility" : False}
        if "colour" in showColor
        else {"scalarVisibility" : True} 
        for mesh in meshes_child.keys()
        ]

    if triggered and (f"dropdown-array-preset{iname}" in triggered[0]["prop_id"] or f"dropdown-meshes{iname}" in triggered[0]["prop_id"]):
        toggleColor = [[]]
    else:
        toggleColor = [showColor]

    # update surface coloring
    if triggered and triggered[0]["value"] == "solid":
        mapper = {"scalarVisibility" : False}
        surface_state = [mapper for item in buildings_rep]
    else:
        surface_state = [dash.no_update] * len(buildings_rep)


    #cubeAxisVisible = ["grid" in cubeAxes] * len(meshes_child) #2
    cubeAxisVisible = ["grid" in cubeAxes
        if selected_mesh_name in mesh_name
        else False
        for mesh_name in meshes_child.keys()
        ]


    #print(streams_visibility)

    return [random.random()] + geom_visibility + surface_state + vtk_visibility + vtk_mapper + dropdown_array + vtk_cbar_name + vtk_cbar_range + cubeAxisVisible + streams_visibility + toggle_streams + toggleColor

def _trigger_mapper(arrayName, selected_mesh_name):
    vtk_mapper = [
        {
            "colorByArrayName" : arrayName,
            #"scalarMode" : 3,
            #"interpolateScalarsBeforeMapping" : True,
            "scalarVisibility" : True,
        }
    #if mesh_array in triggered[0]["values"]
    if mesh_name in selected_mesh_name
    else {"scalarVisibility" : False}
    for mesh_name in meshes_child.keys()
    ]
    return vtk_mapper


#@app.callback(
#    [Output(item.id, "actor") for item in buildings_rep]
#    + [Output(item.id, "mapper") for item in buildings_rep]
#    [Input("toggle-stls","value"),] 
#    )
#def update_stl_toggle(toggleSTL):
#    if toggleSTL:
#        return [{"visibility" : 1} for item in buildings_rep]
#    else:
#        return [{"visibility" : False} for item in buildings_rep]
##def update_stl_toggle(toggleSTL):
##    if toggleSTL:
##        return [[update_stl_state(stl) for stl in stls]]
##    else:
##        return [[]]
#
#
#@app.callback(
#    [
#        Output("vtk-representation", "showCubeAxes"),
#        Output("vtk-representation", "colorMapPreset"),
#        Output("vtk-representation", "colorDataRange"),
#        Output("vtk-polydata", "points"),
#        Output("vtk-polydata", "polys"),
#        Output("vtk-array", "values"),
#        Output("vtk-view", "triggerResetCamera"),
#        Output("dropdown-array-preset", "options"),
#        Output("dropdown-array-preset", "value"),
#    ],
#    [
#        #Input("dropdown-preset", "value"),
#        Input("dropdown-array-preset", "value"),
#        Input("dropdown-meshes", "value"),
#        #Input("scale-factor", "value"),
#        Input("toggle-cube-axes", "value"),
#    ],
#)
##def updatePresetName(name, array, mesh, cubeAxes):
#def updatePresetName(array, mesh, cubeAxes):
#    #points, polys, elevation, color_range = updateWarp(scale_factor)
#    arrays, points, polys, values, color_range, array, cbar = update_mesh(meshes[mesh], array)
#    return [
#        "grid" in cubeAxes,
#        cbar[0], # name,
#        color_range,
#        points,
#        polys,
#        values,
#        random.random(),
#        arrays,
#        array,
#    ]
#
#
##@app.callback(
##    [
##        Output("tooltip", "children"),
##        Output("pick-sphere", "state"),
##        Output("pick-rep", "actor"),
##    ],
##    [
##        Input("vtk-view", "clickInfo"),
##        Input("vtk-view", "hoverInfo"),
##    ],
##)
##def onInfo(clickData, hoverData):
##    info = hoverData if hoverData else clickData
##    if info:
##        if (
##            "representationId" in info
##            and info["representationId"] == "vtk-representation"
##        ):
##            return (
##                [json.dumps(info, indent=2)],
##                {"center": info["worldPosition"]},
##                {"visibility": True},
##            )
##        return dash.no_update, dash.no_update, dash.no_update
##    return [""], {}, {"visibility": False}
@app.callback(
    [
        Output(f"tooltip{iname}", "children"),
        Output(f"pick-sphere{iname}", "state"),
        Output(f"pick-rep{iname}", "actor"),
    ],
    [
        Input(f"vtk-view{iname}", "clickInfo"),
        Input(f"vtk-view{iname}", "hoverInfo"),
        Input(f"dropdown-meshes{iname}", "value"),
        Input(f"dropdown-array-preset{iname}", "value"),
    ],
)
def onInfo(clickData, hoverData, selected_mesh, selected_array_name):
    sphere_state = {"resolution" : 12}
    sphere_state["radius"] = 1
    messages = []
    info = hoverData if hoverData else clickData
    if info:
        if (
            "representationId" in info
            and info["representationId"] == selected_mesh+f'-rep{iname}'
        ):
            sphere_state["center"] = info["worldPosition"]
            #ds_name = info["representationId"].replace("-rep", "")
            #mesh = meshes[ds_name]
            mesh = meshes[selected_mesh+'.vtk']

            if "probability_analysis" in selected_mesh:
                filterOutput = True
                season, vel, field, order = selected_array_name.split('_')
            else:
                filterOutput = False

            if mesh: 
                xyx = info["worldPosition"]
                idx = mesh.FindPoint(xyx)
                if idx > -1:
                    sphere_state["center"] = mesh.GetPoints().GetPoint(idx)
                    point_data = mesh.GetPointData()
                    size = point_data.GetNumberOfArrays()
                    for i in range(size):
                        array = point_data.GetArray(i)
                        name = array.GetName()
                        if filterOutput and f"{vel}" not in name:
                            continue
                        nb_comp = array.GetNumberOfComponents()
                        value = array.GetValue(idx)
                        value_str = f"{array.GetValue(idx):.2f}"
                        norm_str = ""
                        if nb_comp == 3:
                            value = array.GetTuple3(idx)
                            norm = (value[0]**2 + value[1]**2 + value[2]**2)**0.5
                            norm_str = f" norm({norm:.2f})"
                            value_str = ", ".join([f"{v:.2f}" for v in value])
                        mstr = f"{name}: {value_str} {norm_str}"
                        messages.append(mstr)

                    return (["\n".join(messages)], sphere_state, {"visibility" : True},)
                return ([json.dumps(info, indent=2)], sphere_state, {"visibility" : True},)
            #return (
            #    [json.dumps(info, indent=2)],
            #    sphere_state, #{"center": info["worldPosition"]},
            #    {"visibility": True},
            #)
        return dash.no_update, dash.no_update, dash.no_update
    return [""], {}, {"visibility": False}
