# Graphics libs

## Introduction

The purpose of this document is to collect a list of graphics libraries and their properties.

### Properties of interest

* Uses the GPU (and via opengl /vulkan / other)
* 2D, 3D or both
* What language (if Python, is it pure Python?)
* ...



## The libs

### Matplotlib

[Matpltolib](https://matplotlib.org/) is a comprehensive library for creating static, animated, and interactive visualizations in Python.

### Vispy

Vispy is a high-performance interactive 2D/3D data visualization library leveraging the computational power of modern Graphics Processing Units (GPUs) through the OpenGL library to display very large datasets. It's (almost) pure Python. Well, we know what this is.

### Plotly

[Plot.ly](https://plot.ly/)’s Python graphing library makes interactive, publication-quality graphs. Examples of how to make line plots, scatter plots, area charts, bar charts, error bars, box plots, histograms, heatmaps, subplots, multiple-axes, polar charts, and bubble charts. 

### Bokeh

[Bokeh](https://bokeh.org/) is a Python library for creating interactive visualizations for modern web browsers. It helps you build beautiful graphics, ranging from simple plots to complex dashboards with streaming datasets. 

### Datoviz

DatoViz  is a high-performance interactive scientific data visualization library that Cyrille can probably explain better :)

### Pygfx

[PyGfx](https://github.com/pygfx/pygfx) is a render engine written in pure Python, based on wgpu (which, in turn, is a wrapper for Vulkan/Metal/DX12). Its architecture is heavily inspired by ThreeJS (WorldObjects have a geometry and a material) making things very composable. The focus includes 3D graphics, medical visualizations and scientific visualizations in general (2D and 3D).

### Fury

Fury](https://fury.gl/) is a Python library available for scientific visualization. FURY was created to address the growing necessity of high-performance 3D scientific visualization in an easy-to-use API fully compatible with the Pythonic ecosystem. 

### ThreeJS

[ThreeJS](https://threejs.org/) is a JavaScript render engine aimed at 3D graphics. It's based on WebGL but also has an SVG backend. Object3D instances are composed in a scene. These each have a Geometry and Material associated with them, which makes things very composable. It has been praised for making WebGL easier accessible. It's rather focused on 3D graphics, and not on (scientific) visualizations though.

### D3.js

[D3.js](https://d3js.org/) is a JavaScript library for producing dynamic, interactive data visualizations in web browsers. It makes use of Scalable Vector Graphics, HTML5, and Cascading Style Sheets standards.

### Gplot2

[Ggplot2](https://ggplot2.tidyverse.org/) is a system for declaratively creating graphics, based on [The Grammar of Graphics](https://www.amazon.com/Grammar-Graphics-Statistics-Computing/dp/0387245448/ref=as_li_ss_tl). You provide the data, tell ggplot2 how to map variables to aesthetics, what graphical primitives to use, and it takes care of the details.

### PyVista

[PyVista](https://www.pyvista.org/) is a helper module for the Visualization Toolkit (VTK) that takes a different approach on interfacing with VTK through NumPy and direct array access. 

### Mayavi 

[Mayavi](https://docs.enthought.com/mayavi/mayavi/)2 is a general purpose, cross-platform tool for 3-D scientific data visualization. 
