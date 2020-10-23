"use strict";
var app = b4w.require("app");
var data = b4w.require("data");

app.init({
canvas_container_id: "container_id",
physics_enabled: false,
autoresize: true,
callback: load_cb
});

function load_cb() {
	data.load("cube.json", loaded_cb);
}

function loaded_cb(){
}