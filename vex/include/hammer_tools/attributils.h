#pragma once
#ifndef _ATTRIBUTILS_H_
#define _ATTRIBUTILS_H_

// Attrib Type
#define ATTRIB_TYPE_PRIM 1
#define ATTRIB_TYPE_POINT 2
#define ATTRIB_TYPE_VERTEX 8
#define ATTRIB_TYPE_DETAIL 4

string[]
prim_attribs(const int geometry)
{
    return detailintrinsic(geometry, 'primitiveattributes');
}

string[]
point_attribs(const int geometry)
{
    return detailintrinsic(geometry, 'pointattributes');
}

string[]
vertex_attribs(const int geometry)
{
    return detailintrinsic(geometry, 'vertexattributes');
}

string[]
detail_attribs(const int geometry)
{
    return detailintrinsic(geometry, 'detailattributes');
}

string[]
attribs(const int geometry; const int attrib_types)
{
    string attrib_list[];
    if (attrib_types & ATTRIB_TYPE_PRIM)
        push(attrib_list, prim_attribs(geometry));
    if (attrib_types & ATTRIB_TYPE_POINT)
        push(attrib_list, point_attribs(geometry));
    if (attrib_types & ATTRIB_TYPE_VERTEX)
        push(attrib_list, vertex_attribs(geometry));
    if (attrib_types & ATTRIB_TYPE_DETAIL)
        push(attrib_list, detail_attribs(geometry));
    return attrib_list;
}

string[]
attribs(const int geometry; const string attrib_type)
{
    string attrib_list[];
    if (startswith(attrib_type, 'prim'))
        push(attrib_list, prim_attribs(geometry));
    if (startswith(attrib_type, 'point'))
        push(attrib_list, point_attribs(geometry));
    if (startswith(attrib_type, 'vert'))
        push(attrib_list, vertex_attribs(geometry));
    if (startswith(attrib_type, 'detail') || startswith(attrib_type, 'global'))
        push(attrib_list, detail_attribs(geometry));
    return attrib_list;
}

int
has_prim_attrib(const int geometry; const string attrib_name)
{
    return find(prim_attribs(geometry), attrib_name) >= 0;
}

int
has_point_attrib(const int geometry; const string attrib_name)
{
    return find(point_attribs(geometry), attrib_name) >= 0;
}

int
has_vertex_attrib(const int geometry; const string attrib_name)
{
    return find(vertex_attribs(geometry), attrib_name) >= 0;
}

int
has_detail_attrib(const int geometry; const string attrib_name)
{
    return find(detail_attribs(geometry), attrib_name) >= 0;
}

int
has_attrib(const int geometry; const string attrib_name)
{
    return has_prim_attrib(geometry, attrib_name) || has_point_attrib(geometry, attrib_name) ||
           has_vertex_attrib(geometry, attrib_name) || has_detail_attrib(geometry, attrib_name);
}

string
attrib_class(const int geometry; const string attrib_name)
{
    // Priority like in attribclass
    if (has_vertex_attrib(geometry, attrib_name))
        return 'vertex';
    if (has_point_attrib(geometry, attrib_name))
        return 'point';
    if (has_prim_attrib(geometry, attrib_name))
        return 'prim';
    if (has_detail_attrib(geometry, attrib_name))
        return 'detail';
    return '';  // attrib not found or has unsupported type
}

void
copy_attrib(const int geometry, geohandle;
            const string src_attrib_class, dst_attrib_class;
            const string src_attrib_name, dst_attrib_name;
            const int src_elemnum1, src_elemnum2;
            const int dst_elemnum1, dst_elemnum2;
            const string mode)
{
    int attrib_type = attribtype(geometry, src_attrib_class, src_attrib_name);
    if (attrib_type == 1)  // Float-based attributes
    {
        int attribSize = attribsize(geometry, src_attrib_class, src_attrib_name);
        if (attribSize == 1)  // Float
        {
            float value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 3)  // Vector
        {
            vector value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 4)  // Vector4 or Matrix2
        {
            vector4 value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 9)  // Matrtix3
        {
            matrix3 value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 16)  // Matrix
        {
            matrix value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 2)  // Vector2
        {
            vector2 value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else
        {
            error('Unsupported attribute size');
            return;
        }
    } else if (attrib_type == 0)  // Integer
    {
        int value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
        setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
    } else if (attrib_type == 2)  // String
    {
        string value = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
        setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
    } else if (attrib_type == 4)  // Float-based Array
    {
        int attribSize = attribsize(geometry, src_attrib_class, src_attrib_name);
        if (attribSize == 1)  // Float
        {
            float value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 3)  // Vector
        {
            vector value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 4)  // Vector4 or Matrix2
        {
            vector4 value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 9)  // Matrtix3
        {
            matrix3 value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 16)  // Matrix
        {
            matrix value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else if (attribSize == 2)  // Vector2
        {
            vector2 value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
            setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
        } else
        {
            error('Unsupported attribute size');
            return;
        }
    } else if (attrib_type == 3)  // Array of Integers
    {
        int value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
        setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
    } else if (attrib_type == 5)  // Array of Strings
    {
        string value[] = attrib(geometry, src_attrib_class, src_attrib_name, src_elemnum1);
        setattrib(geohandle, dst_attrib_class, dst_attrib_name, dst_elemnum1, dst_elemnum2, value, mode);
    } else
    {
        error('Unsupported attribute type');
        return;
    }
    string attrib_type_info = attribtypeinfo(geometry, src_attrib_class, src_attrib_name);
    setattribtypeinfo(geohandle, dst_attrib_class, dst_attrib_name, attrib_type_info);
}

int
is_valid_attrib_name(const string attrib_name)
{
    if (!isalpha(attrib_name[0]) && attrib_name[0] != '_')
        return 0;
    for (string c : attrib_name)
        if (c != '_' && !isalpha(c) && !isdigit(c))
            return 0;
    return 1;
}

string
fix_attrib_name(const string attrib_name)
{
    string new_attrib_name = '';
    if (isdigit(attrib_name[0]))
        new_attrib_name = '_';
    for (string c : attrib_name)
    {
        if (c != '_' && !isalpha(c) && !isdigit(c))
            new_attrib_name += '_';
        else
            new_attrib_name += c;
    }
    return new_attrib_name;
}

string
fix_attrib_name(const string attrib_name; const int strip)
{
    if (strip)
        return fix_attrib_name(strip(attrib_name));
    else
        return fix_attrib_name(attrib_name);
}

#endif  // _ATTRIBUTILS_H_
