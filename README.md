# vispy2-sandbox

Discussions, experiments, and proof-of-concept for Vispy 2.0


## Purpose

These are the problems that we hope to solve:

* Vispy uses old GPU tech (OpenGL), which makes it difficult to maintain,
  while modern alternatives are now available (Vulkan, Metal, DX12).
* We now have  vispy, datoviz, pygfx, that each are missing a plotting API.
* GPU technology is evolving (and will keep doing so), while plotting API's
  remain relatively stable. Separating the API and the rendering may make
  the ecosystem more flexible and resilient.
* Some use cases require remote rendering, where the data is not on the
  server, nor on the client.

We have defined the following goals:

* Definition of a protocol to serialise viz commands.
  * These commands can remain objects inside an application, serialized to file
    (as yaml/json/toml), or streamed to a remote renderer.
  * The protocol targets GPU-capable renderers, in particular Datoviz and Pygfx,
    but also the current vispy visuals layer, and Matplotlib as a testing backend.
  * Clients (front-ends) provide a high level API to the user, and generate protocol commands.
* Implementation of at least one complete client.


## VISP

This repo also contains a small Python lib called `visp` (for vis-protocol)
where we define the protocol and provide tools to read/write commands, and validate them.

The `visp` lib can be installed by running `pip install -e .` in the repo root.
