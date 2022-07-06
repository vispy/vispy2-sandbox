# Use cases

## Introduction

The purpose of this document is to collect a range of use-cases that we intend to support. From there we can define the required graphics types, refine the specification, and start working on POC's (proof of concepts).

The focus is on visualization use-cases.


## Generic requirements

### Layout and subplots

A window can have multiple "window-elements". These are all rectangles within the encompasing window.

One window-element is a plot. It should be possible to have multiple **subplots** in a single window. Other elements may be e.g. a legend, colorbar, etc. 

The layout of is low-level: any high-level layout resolutions must be implemented to the client. This means that when the window is resized, the client updates all positions.

### Ticks and scales

Thicks must be supported by the server:

* 2D **Ticks** with a choice between standardized automatic spacing, or set by the client. The server is responsible for positioning the text objects.
* 3D scenes should support ticks as well.

The following scales must be supported:

* Linear scale for 2D and 3D plots.
* (optional) Logarithmic scale for 2D plots.
* (optional) Radial scale for 2D plots.
* (optional) Map projections.

### Cameras and interaction models

There should be support for:

* 2D camera
* orthographic camera
* perspective camera

Interaction models are implemented by the client.

### Picking

The client must be able to get feedback on what object was picked where, given a window coordinate.

### Multiple objects

Any combination of objects can be present in a scene at once, and the resulting rendered image should look "natural". This means e.g. correct depth testing.

There is no scene graph hierarchy in the spec, but the client can implement one.

Rendering multiple objects together can be challenging in the face of semi-transparent objects. There exists no cleancut solution that always works. We therefore expect the server to perform "reasonably well" with respect to transparency. Ideally there is a way to control the blend mode.

### Rendering quality

We expect the server to provide "good quality" out of the box. Ideally there is some control over the rendering quality, e.g. antialiasing.

### Post-processing effects

In principle we do not support post-processing effects. Maybe it can be fit in later, but it should not influence the direction of the protocol.

### Performance

We expect good performance from the server, but good quality and behavior have higher priority. This is not a game engine.


## Viz use cases

### Scatter plot

A plot with scatter data in either 2D or 3D. 

* Settable marker shape per set. Also differentiate between edge and fill.
* Settable color, either same for the whole set, or a different color for each vertex.
* Settable size, either same for the whole set, or a different size for each vertex.

### Line plot

A line in either 2D or 3D.

* Settable color, either same for the whole set, or a different color for each vertex.
* Settable thickness, same for the whole set, maybe also support a different thickness for each vertex.
* Support for continuous lines as well as line pairs (a line between each two vertices).
* Support for configurable dashes. 

### Images

It must be possible to show images in 2D and 3D.

* Color images, optionally with alpha channel.
* Grayscale images with colormap.
* Colormaps to map scalar values to an RGBA color. A variety of (standardized) colormap names, and the ability to provide a custom colormap.
* Contrast limits.
* Choice between filtering methods (nearest, linear, cubic).

### Volumes

It must be possible to show volumes in 3D.

* Support for everything that images have.
* Different render modes, like mip, isosurface, etc.
* (optional?) Ability to show a slice from the volume of an arbitrary plane through the volume.

### Meshes

It must be possible to show meshes in 3D.

* A mesh comprises of an array of vertices, and indices to make up the triangles (no quads).
* Optional support for providing normals.
* Optional support for providing texture coordinates.
* Optional support for providing per-vertex colors.

Lighting and materials:

* Support for meshes that do not respond to light.
* Support for meshes with Phong lighting model.
* (Optional) Support meshes with PBR material / lighting model.

### Backgrounds

* Plain color.
* Gradient (a color in each of the four corners).
* (optional) Image.
* (optional) cube map.


## Architectural use-cases

### Front-end and backend both live in the same process in Python

Probably the most common case. The format does not have to be serialized to json but can stay in the shape of dicts. We can also handle errors more effectively.

### Front-end in the browser, backend in Python

Now we have serialisation. A two-way communication channel is implemented using websockets.

Data can also be specified as a URL, so that the server can download the data (ideally the server is close to the data) without going through the client.

### Front-end in language A, backend in language B

The former can be generalized. Any communication channel that supports sending ordered packages of data in two directions would do. Could be websockets or something else implemented over TCP, memorybuffer etc.

