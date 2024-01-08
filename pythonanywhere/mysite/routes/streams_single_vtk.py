import dash
import dash_vtk
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import random
import json
import numpy as np
import pyvista as pv
from pyvista import examples
from vtk.util.numpy_support import vtk_to_numpy

from dash_vtk.utils import presets
import os

from app import app

random.seed(42)


def toDropOption(name):
    return {"label": name, "value": name}


# Get point cloud data from PyVista
uniformGrid = examples.download_crater_topo()
subset = uniformGrid.extract_subset((500, 900, 400, 800, 0, 0), (5, 5, 1))


def updateWarp(factor=1):
    terrain = subset.warp_by_scalar(factor=factor)
    polydata = terrain.extract_geometry()
    points = polydata.points.ravel()
    polys = vtk_to_numpy(polydata.GetPolys().GetData())
    elevation = polydata["scalar1of1"]
    min_elevation = np.amin(elevation)
    max_elevation = np.amax(elevation)
    return [points, polys, elevation, [min_elevation, max_elevation]]


points, polys, elevation, color_range = updateWarp(1)


#####################

vtk_path = 'assets/vtk/'
f = [f for f in os.listdir(vtk_path) if f.endswith('.vtk')]

#meshes = {f'{mesh.split('.')[0]}' : pv.read(os.path.join(vtk_path, mesh)) for mesh in f}
mesh = pv.read(os.path.join(vtk_path, f[0]))
arrays = list(mesh.point_data)
points = mesh.points.ravel()
polys = vtk_to_numpy(mesh.GetPolys().GetData())

def update_mesh(array=arrays[0]):
    values = mesh[array]
    maxVal = np.min([15, np.max(values)])
    minVal = np.max([0, np.min(values)])
    return [values, [minVal, maxVal]]





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
                        id="dropdown-array-preset",
                        options=arrays,
                        value=arrays[0],
                    ),
                ),
                dbc.Col(
                    children=dcc.Dropdown(
                        id="dropdown-preset",
                        options=list(map(toDropOption, presets)),
                        value="coolwarm", #"erdc_rainbow_bright",
                    ),
                ),
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
    [
        Output("vtk-representation", "showCubeAxes"),
        Output("vtk-representation", "colorMapPreset"),
        Output("vtk-representation", "colorDataRange"),
        Output("vtk-polydata", "points"),
        Output("vtk-polydata", "polys"),
        Output("vtk-array", "values"),
        Output("vtk-view", "triggerResetCamera"),
    ],
    [
        Input("dropdown-preset", "value"),
        Input("dropdown-array-preset", "value"),
        #Input("scale-factor", "value"),
        Input("toggle-cube-axes", "value"),
    ],
)
def updatePresetName(name, array, cubeAxes):
    #points, polys, elevation, color_range = updateWarp(scale_factor)
    values, color_range = update_mesh(array)

    return [
        "grid" in cubeAxes,
        name,
        color_range,
        points,
        polys,
        values,
        random.random(),
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
    ],
)
def onInfo(clickData, hoverData):
    info = hoverData if hoverData else clickData
    if info:
        if (
            "representationId" in info
            and info["representationId"] == "vtk-representation"
        ):
            messages = []
            sphere_state = {"resolution" : 12}
            sphere_state["center"] = info["worldPosition"]
            sphere_state["radius"] = 1
            ds_name = info["representationId"].replace("-rep", "")
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
                    messages.append(f"{name}: {value_str} {norm_str}")


            return (["\n".join(messages)], sphere_state, {"visibility" : True},)
            #return (
            #    [json.dumps(info, indent=2)],
            #    {"center": info["worldPosition"]},
#            #    {"visibility": True},
#            #)
        return dash.no_update, dash.no_update, dash.no_update
    return [""], {}, {"visibility": False}
