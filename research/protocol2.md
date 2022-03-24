# API areas

Asynchronous rendering protocol for scientific visualization.

The protocol encompasses multiple areas:

- **Canvases**: create, update, delete 1 or multiple canvases (rectangular surfaces)
- **Arrays**: 1D, 2D, or 3D arrays containing the data that will be used to render visuals
- **Data requests**: commands that are sent to ask the renderer to fetch the data from some sources and put them in arrays for rendering
- **Transforms**: transformations of data that is stored in the arrays
- **Visuals**: predefined customizable visual elements
- **Draw commands**: the actual rendering commands

There is an asynchronous engine, the renderer, that dynamically receives commands to create, update, render, or delete objects. Clients can receive information from the renderer, for example to receive updated bitmap images of the canvases.

**Platform-agnostic protocol**: as much as possible, we'd like the protocol to assume as little as possible about the renderer. In particular, both CPU-based and GPU-based renderers could be implemented, even if some functionality is missing in some renderers. A renderer should declare the functionality it supports.

**Extensibility**: the renderer should offer ways for users to add or improve functionality. For example:

- there should be a way to create custom visuals for a given renderer
- there should be a way to customize data access, i.e. how a client might request a renderer to fetch the data and update arrays
- there should be a way to define custom transformations


## Canvases

A canvas is defined by:

- An id
- A width
- A height
- A background color
- A DPI resolution?


## Arrays

An array is defined by:

- An id
- The number of dimensions: 1, 2, 3
- A dtype (can be vec2, mat4, etc)
- A shape (can be dynamically reshaped)


## Data requests

A data request is a custom message sent to the renderer that asks the renderer to fetch the data from some data source, and putting it in an array.

A data request is defined by:

- An id
- A request type: how to access the data. There can be native request types, for example file_system or HTTP, with the URI/URL. Most importantly, the user can easily create its own custom request type, for example using dask, fetching data from a cloud service, generating it on the fly, obtaining it from an existing Cupy array. In this case, the renderer should be smart enough to avoid doing a copy of the data into the target array.
- Source metadata: type-specific information that the renderer will need to fetch the data.


## Transforms

A transform is defined by:

- An id
- A type: linear, box1D, box2D, box3D, mvp, colormap... that defines the source type and target type
- Type-dependent parameters

There are commands to create, update, delete transforms, and to change transform parameters on the fly.


## Visuals

A visual is defined by:

- An id
- A visual type (marker, path, text...)


Then, props are defined. Each prop is defined by:

- The prop type
- An array
- An offset
- A shape
- A list of transforms

The list of transforms defines how data is transformed from the array to its final position in normalized device coordinates [-1, +1].


## Draw commands

A draw command is sent only when it changes. The renderer is responsible for "caching" the active commands (for example, in a command buffer for Vulkan renderers).

A draw command is characterized by:

- The canvas: which canvas to render on
- The viewport: a rectangular area within a given canvas on which to draw
- An ordered list of visuals to draw.
