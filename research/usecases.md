# Use cases

## Introduction

The purpose of this document is to collect a range of use-cases that we intend to support. From there we can define the required graphics types, refine the specification, and start working on POC's (proof of concepts).

The focus is on visualization use-cases.



## Viz use cases



### Scatter plot case 1

### Scatter plot case 2

### Scatter plot case 3

### Picking

### Rendering a volume, mesh, plus annotations



## Architectural use-cases



### Front-end and backend both live in the same process in Python

Probably the most common case. The format does not have to be serialized to json but can stay in the shape of dicts. We can also handle errors more effectively.

### Front-end in the browser, backend in Python

Now we have serialisation.

### Front-end in the browser, backend in Python, data on a server close to the backend

Data can be specified as a URL.



## Use cases that we probably won't support



### Fancy post-processing effects

### Video game performance
