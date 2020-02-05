#pragma once
#ifndef _GROUPUTILS_H_
#define _GROUPUTILS_H_

int
merge_group(const int old_value;
            const int new_value;
            const int method)
{
    if (method == 0)  // Replace
        return new_value;
    else if (method == 1)  // Union
        return max(old_value, new_value);
    else if (method == 2)  // Intersect
        return old_value * new_value;
    else if (method == 3)  // Subtract
        return max(old_value - new_value, 0);
    error('Invalid merge method');
    return -1;
}

string[]
prim_groups(const int geometry)
{
    return detailintrinsic(geometry, 'primitivegroups');
}

string[]
point_groups(const int geometry)
{
    return detailintrinsic(geometry, 'pointgroups');
}

string[]
edge_groups(const int geometry)
{
    return detailintrinsic(geometry, 'edgegroups');
}

string[]
vertex_groups(const int geometry)
{
    return detailintrinsic(geometry, 'vertexgroups');
}

int
has_prim_group(const int geometry; const string group_name)
{
    return find(prim_groups(geometry), group_name) >= 0;
}

int
has_point_group(const int geometry; const string group_name)
{
    return find(point_groups(geometry), group_name) >= 0;
}

int
has_edge_group(const int geometry; const string group_name)
{
    return find(edge_groups(geometry), group_name) >= 0;
}

int
has_vertex_group(const int geometry; const string group_name)
{
    return find(vertex_groups(geometry), group_name) >= 0;
}

int
has_group(const int geometry; const string group_name)
{
    return has_prim_group(geometry, group_name) || has_point_group(geometry, group_name) ||
           has_edge_group(geometry, group_name) || has_vertex_group(geometry, group_name);
}

string
group_type(const int geometry; const string group_name)
{
    // Priority like in attribclass
    if (has_vertex_group(geometry, group_name))
        return 'vertex';
    if (has_edge_group(geometry, group_name))
        return 'edge';
    if (has_point_group(geometry, group_name))
        return 'point';
    if (has_prim_group(geometry, group_name))
        return 'prim';
    return '';  // Group not found or has unsupported type
}

int
group_pattern_type(const int geometry; const string group_name)
{
    // pass
}

void
set_group(const int geohandle;
          const string group_type;
          const string group_name;
          const int elemnum1, elemnum2;
          const int value)
{
    if (group_type == 'edge')
        setedgegroup(geohandle, group_name, elemnum1, elemnum2, value);
    else
        setattrib(geohandle, group_type + 'group', elemnum1, elemnum2, value);
}

void
copy_group(const int geometry, geohandle;
           const string src_group_type, dst_group_type;
           const string src_group_name, dst_group_name;
           const int src_elemnum1, src_elemnum2;
           const int dst_elemnum1, dst_elemnum2)
{
    // pass
}

#endif  // _GROUPUTILS_H_
