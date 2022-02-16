# Rendering protocol

This document describes a **platform-independent asynchronous protocol for scientific rendering**.

It is designed from the ground up for **performance** and **scalability** to large datasets. It  primarily targets graphics processing units (GPU), but it is meant to support pure software implementations as well.



## Concepts

The protocol describes a general rendering architecture that could be implemented with various technologies, on totally different platforms (desktop, mobile, web, client-server).

The architecture defines several actors:

* The **Renderer** is a standalone system that continuously runs an event loop. It receives and processes asynchronous **Rendering requests**, and may asynchronously send back **Response messages** via two independent **Channels**. It manages a dynamic collection of rectangular **Canvases**, and dynamically renders **Visuals** organized in a **Scene graph** following requests. It also provides a dedicated **Bitmap channel** that returns or streams rendered images to the **Client**.

* The **Client** may run on the same system or on a different one. It connects to the **Renderer**, it sends **Rendering requests**, and it receives **Response messages**. It may also display **Canvases** rendered by the **Renderer** and sent via the **Bitmap channel**.

* The **Visualization interface** exposes a high-level visualization programming interface to the user. It uses the **Client** to generate **Rendering requests** dynamically. The requests are sent to the **Renderer**, which processes them and returns bitmaps to the **Client**.



## Motivations

* **Modularity**: this system distinguishes the low-level rendering functionality from the high-level scientific visualization logic. Both systems can be independently developed and tested in parallel.
* **Platform independence**: a given **Renderer** may support different high-level interfaces as long as they follow the same rendering protocol. Conversely, a given high-level interface may be rendered by different **Renderers**.
* **Multithreading**: when implementing a multithreaded application, multiple threads may generate **Rendering requests** in parallel, and send them to the same **Renderer**.



## Visuals

The architecture relies on the concept of **Visual**: a visual element to display on the canvas. There is a predefined set of **Visual types**.

A **Visual type** is determined by:

* a set of **Props**

A **Visual** is determined by:

* an ID
* a **Visual type**
* an **Array** or **Value** for each **Prop** of that **Visual type**

**Values** can be of one of the predefined **Data types**.

An **Array** is defined by:

* ndim (uint8): 1, 2, or 3
* dtype (enum): a **Data type**, or a list of pairs (name, dtype)
* shape (uvec3)

There is no notion of "collection": multiple visuals of the same type sharing the same scene graph node may be collected by the **Renderer** if it supports batch rendering.


## Scene graph

Every **Canvas** comes with a **Scene graph**, a graph where the **Root node** represents the entire surface, and every **Node** represents a different coordinate system defined by a triplet of matrices (model, view, projection) relative to the node's parent.

A **Node** is defined by:

* an ID
* a parent ID
* a **Transform type** (currently, only linear)
* a triplet of mat4 (model, view, projection)



## Rendering requests

A **Rendering request** is defined by:

* A mandatory **request ID**
* A mandatory **action**
* A mandatory **object type**
* A mandatory **object ID**
* An optional request-specific **payload**
* Optional flags


### Actions

The following **actions** are supported:

* create
* delete
* resize
* update
* draw
* upload
* download
* insert
* remove
* get


### Object types

The following **object types** are supported:

* canvas
* visual
* array
* prop
* item
* node


### Object ID

Every object has a unique and fixed ID within the context of a given **Renderer**.

The **Client** has the responsibility of assigning unique IDs to all objects.


### Payloads

#### Create canvas

* width (int32)
* height (int32)
* background_color (color)

#### Create visual

* canvas (id)
* type (enum)
* node (id)

#### Create node

* canvas (id)
* parent (id)
* transform_type (enum, only linear for now)
* model (mat4)
* view (mat4)
* proj (mat4)

#### Draw canvas

* canvas(id)
* viewport (x, y, width, height), in logical pixels
* visuals (list of visual ids)

#### Update prop

* __visual (id)__
* prop (enum)
* array (id)
* offset (uvec3)
* shape (uvec3)

#### Create array

* __array (id)__
* ndim (1, 2, or 3)
* dtype (dtype)
* shape (uint32)

#### Resize array

* __array (id)__
* shape (uvec3)

#### Delete array

* __array (id)__

#### Upload array

* __array (id)__
* offset (uvec3)
* shape (uvec3)
* data (1D, 2D, or 3D)

#### Insert item

* __visual (id)__
* item_idx (uint32)
* data (array)

#### Update item

* __visual (id)__
* item_idx (uint32)
* data (array)

#### Remove item

* __visual (id)__
* item_idx (uint32)


#### Update node

* __node (id)__
* model (mat4)
* view (mat4)
* proj (mat4)


#### Update visual

* __visual (id)__
* node (id)


#### Delete visual

* __visual (id)__


#### Delete node

* __node (id)__


#### Delete canvas

* __canvas (id)__


#### Pick canvas

* __canvas (id)__
* pos0 (vec2)
* pos1 (vec2)



### Enumerations

#### Visual type

* point
* line
* segment
* path
* text
* image
* mesh
* volume

#### Prop types

##### Common

* pos (vec3)
* color (cvec4, str)
* model (mat44)
* view (mat44)
* proj (mat44)


##### Visual-specific

###### Marker

* marker (enum)

###### Line, Segment, Path

* width (float)

###### Image

* image (array)

###### Volume

* volume (array)

###### Text

* weight (int)
* font (str)


#### Marker types

* disc
* asterisk
* chevron
* clover
* club
* cross
* diamond
* arrow
* ellipse
* hbar
* heart
* infinity
* pin
* ring
* spade
* square
* tag
* triangle
* vbar


#### Data types

* int8
* int16
* int32
* int64
* uint8
* uint16
* uint32
* uint64
* float32
* float64
* cvec2 (uint8)
* cvec3
* cvec4
* ivec2 (int32)
* ivec3
* ivec4
* uvec2 (uint32)
* uvec3
* uvec4
* vec2 (float32)
* vec3
* vec4
* mat42 (float32)
* mat44
* dvec2 (float64)
* dvec3
* dvec4


## Data access

Arrays may be specified directly, or indirectly with some metadata indicating the **Renderer** how to access the data. The user may write plugins that tell the **Renderer** how to access data.

## Response messages

A **Response message** is defined by:

* a **Response type** (enum)
    * status
    * pick
* a payload
    * status code: enum (pending, processing, success, fail)
    * message (eg: error message)
    * picking return array
