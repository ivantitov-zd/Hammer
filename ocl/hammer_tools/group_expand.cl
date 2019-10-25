kernel void point_edge_expand(int group_length,
                              global int *group,
                              int group_temp_length,
                              global int *group_temp,
                              int neighbours_length,
                              global int *neighbours_index,
                              global int *neighbours)
{
    int idx = get_global_id(0);
    if (idx >= group_length || group[idx])
        return;
    for (int i = neighbours_index[idx]; i < neighbours_index[idx+1]; ++i)
        group_temp[idx] = max(group_temp[idx], group[neighbours[i]]);
}

kernel void point_edge_expand_back(int group_length,
                                   global int *group,
                                   int group_temp_length,
                                   global int * group_temp,
                                   int neighbours_length,
                                   global int *neighbours_index,
                                   global int *neighbours)
{
    int idx = get_global_id(0);
    if (idx >= group_length || group[idx])
        return;
    group[idx] = group_temp[idx];
}

kernel void point_polygon_expand(int group_length,
                                 global int * group,
                                 int group_temp_length,
                                 global int * group_temp,
                                 int points_length,
                                 global int * points_index,
                                 global int * points)
{
    int idx = get_global_id(0);
    if (idx >= group_length || group[idx])
        return;
    for (int pt = points_index[idx]; pt < points_index[idx+1]; ++pt)
    {
        if (group[points[pt]])
        {
            group_temp[idx] = 1;
            return;
        }
    }
}

kernel void point_polygon_expand_back(int group_length,
                                      global int * group,
                                      int group_temp_length,
                                      global int * group_temp,
                                      int points_length,
                                      global int * points_index,
                                      global int * points)
{
    int idx = get_global_id(0);
    if (idx >= group_length)
        return;
    group[idx] = group_temp[idx];
}

kernel void polygon_edge_expand(int group_length,
                                global int *group,
                                int group_temp_length,
                                global int *group_temp,
                                int neighbours_length,
                                global int *neighbours_index,
                                global int *neighbours)
{
    int idx = get_global_id(0);
    if (idx >= group_length || group[idx])
        return;
    for (int i = neighbours_index[idx]; i < neighbours_index[idx+1]; ++i)
        group_temp[idx] = max(group_temp[idx], group[neighbours[i]]);
}

kernel void polygon_edge_expand_back(int group_length,
                                     global int *group,
                                     int group_temp_length,
                                     global int * group_temp,
                                     int neighbours_length,
                                     global int *neighbours_index,
                                     global int *neighbours)
{
    int idx = get_global_id(0);
    if (idx >= group_length || group[idx])
        return;
    group[idx] = group_temp[idx];
}

kernel void polygon_polygon_expand(int group_length,
                                 global int * group,
                                 int group_temp_length,
                                 global int * group_temp,
                                 int prims_length,
                                 global int * prims_index,
                                 global int * prims)
{
    int idx = get_global_id(0);
    if (idx >= group_length || group[idx])
        return;
    for (int pt = prims_index[idx]; pt < prims_index[idx+1]; ++pt)
    {
        if (group[prims[pt]])
        {
            group_temp[idx] = 1;
            return;
        }
    }
}

kernel void polygon_polygon_expand_back(int group_length,
                                      global int * group,
                                      int group_temp_length,
                                      global int * group_temp,
                                      int prims_length,
                                      global int * prims_index,
                                      global int * prims)
{
    int idx = get_global_id(0);
    if (idx >= group_length)
        return;
    group[idx] = group_temp[idx];
}
