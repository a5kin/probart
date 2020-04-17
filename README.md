# Probart
Probart is a helper library I use in my generative art experiments.

It sits on top of PyCairo and NumPy. Nothing beneficial, only a
draft. Right now, you could draw just multi-line paths with it::

    from probart.canvas import EntropyCanvas
    
    width = 1920
    height = 1080
    background_color = (0, 0, 0, 0)
    canvas = EntropyCanvas(width, height, background_color)
    
    path = [(0, 0), (1, 1)]
    start_color = (0.7, 0, 1, 0.1)
    end_color = (1, 1, 1, 0.1)
    num_clones = 100
    line_width = 1 / width
    main_deviation = 0.01
    sub_deviation = 0.005
    canvas.multiline(path, start_color, end_color, num_clones, line_width, main_deviation, sub_deviation)
