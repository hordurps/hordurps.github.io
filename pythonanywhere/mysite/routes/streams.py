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

def toDropOption(name):
    return {"label": name, "value": name}

#####################

vtk_path = 'assets/vtk/'
f = [f for f in os.listdir(vtk_path) if f.endswith('.vtk')]

meshes = {f'{mesh}' : pv.read(os.path.join(vtk_path, mesh)) for mesh in f}
mesh = pv.read(os.path.join(vtk_path, f[0]))
arrays = list(mesh.point_data)
#points = mesh.points.ravel()
#polys = vtk_to_numpy(mesh.GetPolys().GetData())

stl_path = 'assets/stl/'
stls = [os.path.join(stl_path, s) for s in os.listdir(stl_path) if s.endswith('.stl')]
def update_stl_reader(stls):
    mesh_states = []
    assembly = vtk.vtkAssembly()
    for name in stls:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(name)
        reader.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor((1,0,0))
        assembly.AddPart(actor)
        mesh_state = to_mesh_state(assembly.GetOutput())
        #mesh_state = to_mesh_state(reader.GetOutput())
    return mesh_state

def update_stl_state(stl):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stl)
    reader.Update()
    mesh_state = to_mesh_state(reader.GetOutput())
    return dash_vtk.GeometryRepresentation(dash_vtk.Mesh(state=mesh_state))

#stls_states = update_stl_reader(stls)


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
        cbar = ["RdOrYl"]
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



arrays, points, polys, values, color_range, array, cbar = update_mesh(mesh, arrays[0])


#####################

vtk_view = dash_vtk.View(
    id="vtk-view",
    background=[i/255.0 for i in [25, 34, 61]],
    pickingModes=["hover"],
    children=[
        dash_vtk.GeometryRepresentation(
            id="vtk-representation",
            children=[
                dash_vtk.PolyData(
                    id="vtk-polydata",
                    points=points,
                    polys=polys,
                    children=[
                        dash_vtk.PointData(
                            [
                                dash_vtk.DataArray(
                                    id="vtk-array",
                                    registration="setScalars",
                                    name="values",
                                    values=mesh[arrays[0]],
                                )
                            ]
                        )
                    ],
                )
            ],
            colorMapPreset="coolwarm", #"erdc_blue2green_muted",
            colorDataRange=color_range,
            property={"edgeVisibility": False},
            showCubeAxes=True,
            cubeAxesStyle={"axisLabels": ["", "", "Altitude"]},
        ),
        dash_vtk.GeometryRepresentation(
            id="pick-rep",
            actor={"visibility": False},
            children=[
                dash_vtk.Algorithm(
                    id="pick-sphere",
                    vtkClass="vtkSphereSource",
                    state={"radius": 100},
                )
            ],
        ),
        html.Div(id='stl-div', children=
            [update_stl_state(stl) for stl in stls]
        )
        #dash_vtk.GeometryRepresentation(
        #    children=[
        #        dash_vtk.Mesh(state=update_stl_reader(stls)),
        #        #dash_vtk.Mesh(state=update_stl_state(stls[0])),
        #        #dash_vtk.Mesh(state=update_stl_state(stls[1])),
        #    ]
        #    #dash_vtk.Mesh(state=stls_states),
        #),
    ],
)


layout = dbc.Container(
    fluid=True,
    style={"height": "100vh"},
    children=[
        dbc.Row(
            [
                #dbc.Col(
                #    children=dcc.Slider(
                #        id="scale-factor",
                #        min=0.1,
                #        max=5,
                #        step=0.1,
                #        value=1,
                #        marks={0.1: "0.1", 5: "5"},
                #    )
                #),
                dbc.Col(
                    children=dcc.Dropdown(
                        id="dropdown-meshes",
                        options=list(meshes.keys()),
                        value=list(meshes.keys())[0],
                    ),
                ),
                dbc.Col(
                    children=dcc.Dropdown(
                        id="dropdown-array-preset",
                        options=arrays,
                        value=arrays[0],
                    ),
                ),
                #dbc.Col(
                #    children=dcc.Dropdown(
                #        id="dropdown-preset",
                #        options=list(map(toDropOption, presets)),
                #        value="coolwarm", #"erdc_rainbow_bright",
                #    ),
                #),
                dbc.Col(
                    children=dcc.Checklist(
                        id="toggle-cube-axes",
                        options=[
                            {"label": " Show axis grid", "value": "grid"},
                        ],
                        value=[],
                        labelStyle={"display": "inline-block"},
                    ),
                ),
                dbc.Col(
                    children=dcc.Checklist(
                        id="toggle-stls",
                        options=[
                            {"label": " Show STL", "value": "stl"},
                        ],
                        value=["stl"],#[],
                        labelStyle={"display": "inline-block"},
                    ),
                ),
            ],
            style={"height": "12%", "alignItems": "center"},
        ),
        html.Div(
            html.Div(vtk_view, style={"height": "100%", "width": "100%"}),
            style={"height": "88%"},
        ),
        html.Pre(
            id="tooltip",
            style={
                "position": "absolute",
                "bottom": "25px",
                "left": "25px",
                "zIndex": 1,
                "color": "white",
            },
        ),
    ],
)

@app.callback(
    [Output("stl-div","children")],
    [Input("toggle-stls","value"),] 
    )
def update_stl_toggle(toggleSTL):
    if toggleSTL:
        return [[update_stl_state(stl) for stl in stls]]
    else:
        return [[]]


@app.callback(
    [
        Output("vtk-representation", "showCubeAxes"),
        Output("vtk-representation", "colorMapPreset"),
        Output("vtk-representation", "colorDataRange"),
        Output("vtk-polydata", "points"),
        Output("vtk-polydata", "polys"),
        Output("vtk-array", "values"),
        Output("vtk-view", "triggerResetCamera"),
        Output("dropdown-array-preset", "options"),
        Output("dropdown-array-preset", "value"),
    ],
    [
        #Input("dropdown-preset", "value"),
        Input("dropdown-array-preset", "value"),
        Input("dropdown-meshes", "value"),
        #Input("scale-factor", "value"),
        Input("toggle-cube-axes", "value"),
    ],
)
#def updatePresetName(name, array, mesh, cubeAxes):
def updatePresetName(array, mesh, cubeAxes):
    #points, polys, elevation, color_range = updateWarp(scale_factor)
    arrays, points, polys, values, color_range, array, cbar = update_mesh(meshes[mesh], array)

    return [
        "grid" in cubeAxes,
        cbar[0], # name,
        color_range,
        points,
        polys,
        values,
        random.random(),
        arrays,
        array,
    ]


#@app.callback(
#    [
#        Output("tooltip", "children"),
#        Output("pick-sphere", "state"),
#        Output("pick-rep", "actor"),
#    ],
#    [
#        Input("vtk-view", "clickInfo"),
#        Input("vtk-view", "hoverInfo"),
#    ],
#)
#def onInfo(clickData, hoverData):
#    info = hoverData if hoverData else clickData
#    if info:
#        if (
#            "representationId" in info
#            and info["representationId"] == "vtk-representation"
#        ):
#            return (
#                [json.dumps(info, indent=2)],
#                {"center": info["worldPosition"]},
#                {"visibility": True},
#            )
#        return dash.no_update, dash.no_update, dash.no_update
#    return [""], {}, {"visibility": False}
@app.callback(
    [
        Output("tooltip", "children"),
        Output("pick-sphere", "state"),
        Output("pick-rep", "actor"),
    ],
    [
        Input("vtk-view", "clickInfo"),
        Input("vtk-view", "hoverInfo"),
        Input("dropdown-meshes", "value"),
    ],
)
def onInfo(clickData, hoverData, selected_mesh):
    sphere_state = {"resolution" : 12}
    sphere_state["radius"] = 1
    messages = []
    info = hoverData if hoverData else clickData
    if info:
        if (
            "representationId" in info
            and info["representationId"] == "vtk-representation"
        ):
            sphere_state["center"] = info["worldPosition"]
            #ds_name = info["representationId"].replace("-rep", "")
            #mesh = meshes[ds_name]
            mesh = meshes[selected_mesh]

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
