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

int
in_group(const int geometry;
         const string group_type;
         const string group_name;
         const int elemnum1, elemnum2)
{
    if (group_type == 'edge')
        return inedgegroup(geometry, group_name, elemnum1, elemnum2);
    else if (group_type == 'vertex')
    {
        int vtxnum;
        if (elemnum1 != -1)
            vtxnum = vertexindex(geometry, elemnum1, elemnum2);
        else
            vtxnum = elemnum2;
        return attrib(geometry, group_type + 'group', group_name, vtxnum);
    }
    else
        return attrib(geometry, group_type + 'group', group_name, elemnum1);
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
        setattrib(geohandle, group_type + 'group', group_name, elemnum1, elemnum2, value);
}

void
copy_group(const int geometry, geohandle;
           const string src_group_type, dst_group_type;
           const string src_group_name, dst_group_name;
           const int src_elemnum1, src_elemnum2;
           const int dst_elemnum1, dst_elemnum2)
{
    int state = in_group(geometry, src_group_type, src_group_name, src_elemnum1, src_elemnum2);
    set_group(geohandle, dst_group_type, dst_group_name, dst_elemnum1, dst_elemnum2, state);
}

void
copy_group(const int geometry, geohandle;
           const string src_group_type, dst_group_type;
           const string src_group_name, dst_group_name;
           const int src_elemnum1, src_elemnum2;
           const int dst_elemnum1, dst_elemnum2;
           const int mode)
{
    int src_state = in_group(geometry, src_group_type, src_group_name, src_elemnum1, src_elemnum2);
    int dst_state = in_group(geohandle, dst_group_type, dst_group_name, dst_elemnum1, dst_elemnum2);
    set_group(geohandle, dst_group_type, dst_group_name, dst_elemnum1, dst_elemnum2, merge_group(dst_state, src_state, mode));
}

int
is_valid_group_name(const string group_name)
{
    if (!isalpha(group_name[0]) && group_name[0] != '_')
        return 0;
    for (string c : group_name)
        if (c != '_' && !isalpha(c) && !isdigit(c))
            return 0;
    return 1;
}

string
fix_group_name(const string group_name)
{
    string new_group_name;
    if (!isalpha(group_name[0]) && group_name[0] != '_')
        new_group_name = '_';
    for (string c : group_name)
    {
        if (c != '_' && !isalpha(c) && !isdigit(c))
            new_group_name += '_';
        else
            new_group_name += c;
    }
    return new_group_name;
}

string
fix_group_name(const string group_name; const int strip)
{
    if (strip)
        return fix_group_name(strip(group_name));
    else
        return fix_group_name(group_name);
}

#endif  // _GROUPUTILS_H_
