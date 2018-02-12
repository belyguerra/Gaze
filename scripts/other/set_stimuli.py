from random import shuffle
new_vals = {
    'shape1' : set_df['shape1'].tolist(),
    'shape2' : set_df['shape2'].tolist(),
    'shape3' : set_df['shape3'].tolist(),
    'shape4' : set_df['shape4'].tolist(),
    'span' : set_df['span'].tolist()
}

cols = ['shape1', 'shape2', 'shape3', 'shape4']
spans_to_set = {1:True, 2:True}
for indx, span in enumerate(new_vals['span']):
    if span not in spans_to_set:
        continue
    shapes = {shape:False for shape in pictures_dict['shapes']}
    cols_to_set = []
    for col in cols:
        if pd.isnull(new_vals[col][indx]):
            cols_to_set.append(col)
        else:
            shape = new_vals[col][indx]
            shapes[shape] = True

    if len(cols_to_set) == 0:
        continue
    random_shapes = list(shapes.keys())
    shuffle(random_shapes)
    for shape in random_shapes:
        if not shapes[shape]:
            new_vals[cols_to_set.pop()][indx] = shape
            if len(cols_to_set) == 0:
                break

new_vals_df = pd.DataFrame(new_vals)
for col in cols:
    set_df[col] = new_vals_df[col]



    from random import shuffle
    new_vals = {
        'color1' : set_df['color1'].tolist(),
        'color2' : set_df['color2'].tolist(),
        'color3' : set_df['color3'].tolist(),
        'color4' : set_df['color4'].tolist(),
        'span' : set_df['span'].tolist()
    }

    cols = ['color1', 'color2', 'color3', 'color4']
    spans_to_set = {1:True, 2:True}
    for indx, span in enumerate(new_vals['span']):
        if span not in spans_to_set:
            continue
        shapes = {shape:False for shape in pictures_dict['colors']}
        cols_to_set = []
        for col in cols:
            if pd.isnull(new_vals[col][indx]):
                cols_to_set.append(col)
            else:
                shape = new_vals[col][indx]
                shapes[shape] = True

        if len(cols_to_set) == 0:
            continue
        random_shapes = list(shapes.keys())
        shuffle(random_shapes)
        for shape in random_shapes:
            if not shapes[shape]:
                new_vals[cols_to_set.pop()][indx] = shape
                if len(cols_to_set) == 0:
                    break

    new_vals_df = pd.DataFrame(new_vals)
    for col in cols:
        set_df[col] = new_vals_df[col]
