

if __name__ == '__main__':
    import numpy as np
    import matplotlib
    from pathlib import Path
    filename = Path(__file__).with_suffix(".yaml")
    
    # Write yaml
    # -------------------------------------------------------------------------
    matplotlib.use("module://frontend")
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = plt.subplot()
    ax.set_facecolor("yellow")
    fig.savefig(filename, format='yaml')

    
    # Read yaml
    # -------------------------------------------------------------------------
    import backend 
    for output in backend.parse(filename): pass
    
    matplotlib.use('MacOSX')
    height,width,depth = output.shape
    dpi = 100
    fig = plt.figure(figsize = (width/dpi, height/dpi), dpi=dpi)
    ax = fig.add_axes([0,0,1,1])
    ax.imshow(output)
    ax.set_axis_off()
    plt.show()

    
    # with open("test.yaml") as file:
    #     print (file.read())
    
    # dpi = 100
    # width = 500
    # height = 500
    # depth = -100
    # fig = plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi, frameon=False)
    # ax = fig.add_axes([0.2,0.2,.8,.8])
    # ax.zorder = depth
    # ax.set_xlim(0, width)
    # ax.set_ylim(0, height)
    # ax.get_xaxis().set_visible(False)
    # ax.get_yaxis().set_visible(False)
    # for pos in ["top", "bottom", "right", "left"]:
    #     ax.spines[pos].set_visible(False)
    # ax.set_facecolor("yellow")

