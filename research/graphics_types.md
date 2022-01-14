# Graphics types

## Introduction

The purpose of this document is to collect a list of types of graphics to support.

### Properties

The properties listed here generally apply to the whole graphics object (a uniform, in GPU terms), but most of these could also be applied per-vertex.

## The graphics

### BaseGraphics

Properties common to all graphic types:

* id
* opacity (a.k.a. alpha)
* transform
* parent and children?

### Markers

Markers represent a set of points expressed with a specific shape. Vertex data includes positions; a marker is drawn at each position.

Properties:

* size
* type (i.e. shape, e.g. round or square)
* color
* edge_width
* edge_color
* angle

### Line

TODO: I'm confused about the difference between a Path and a Line in Datoviz.

A line represents a continuous line defined by a series of positions.

Properties:

* line_width
* color

### Points

A simpler flavor of points. Not sure if we need these - if you set the type to round and the edge_width to 0 you have the same thing.

### Segments

Segments represent a series of segments a.k.a. line pieces. Vertex data includes positions; a segment is drawn between each pair of positions.

Properties:

* line_width
* color
* cap1 (shape of the cap, e.g. square, round or arrow)
* cap2

### Mesh

The good old 3D object.

Vertex data:

* positions
* faces
* normals (optional)
* texcoords (optional)

Properties:

* color
* light_model
* wireframe (bool)?
* light parameters, or do we attach these to the scene?

### TriangleStrip and TriangleFan

Like mesh, but with different topology. Do we need them? Can we make this a `topology` prop of mesh?

### Spheres

Draw a sphere on each provided position. It's a bit like a marker, but also a bit like a mesh.

Properties:

* size (diameter)
* color
* light params

### Image

Properties:

* data
* clim
* cmap

### Text

Properties:

* color
* size or font_size
* text
* align_x
* align_y
* angle

### Volume

* data
* clim
* cmap

### VolumeSlice

* data
* clim
* cmap
* plane (e.g. a 4-element tuple abcd)

