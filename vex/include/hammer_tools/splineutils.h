#pragma once
#ifndef _SPLINEUTILS_H_
#define _SPLINEUTILS_H_

int
is_start_vertex(const int geometry; const int vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return vertex_index == 0;
}

int
is_start_point(const int geometry; const int ptnum)
{
    return is_start_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_end_vertex(const int geometry; const int vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return vertex_index == primvertexcount(geometry, vertexprim(geometry, vtxnum)) - 1;
}

int
is_end_point(const int geometry; const int ptnum)
{
    return is_end_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_valid_spline(const int geometry; const int primnum)
{
    int type = primintrinsic(geometry, 'typeid', primnum);

    return (primvertexcount(geometry, primnum) - 4) % 3 == 0;
}

int
is_knot_vertex(const int geometry; const int vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return vertex_index % 3 == 0;
}

int
is_control_vertex(const int geometry; const int vtxnum)
{
    return !is_knot_vertex(geometry, vtxnum);
}

int
is_knot_point(const int geometry; const int ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)
        return -1;  // Single point
    if (prim_count != 1)
        warning('Geometry has point shared between two or more curves');
    int type = primintrinsic(geometry, 'typeid', prims[0]);
    if (type == 3)  // Bezier
        return is_knot_vertex(geometry, pointvertex(geometry, ptnum));
    return -1;  // Not supported
}

int
is_control_point(const int geometry; const int ptnum)
{
    return !is_knot_point(geometry, ptnum);
}

int
prev_knot_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
prev_knot_point(const int geometry; const int ptnum)
{
    // pass
}

int
next_knot_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
next_knot_point(const int geometry; const int ptnum)
{
    // pass
}

int
knot_vertex(const int geometry; const int vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return (int)rint(ceil((vertex_index - 1) / 3.0) * 3);
}

int
knot_point(const int geometry; const int ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)
        return -1;  // Single point
    if (prim_count != 1)
        warning('Geometry has point shared between two or more curves');
    int type = primintrinsic(geometry, 'typeid', prims[0]);
    if (type == 3)  // Bezier
        return knot_vertex(geometry, pointvertex(geometry, ptnum));
    return -1;  // Not supported
}

int
prev_control_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
prev_control_point(const int geometry; const int ptnum)
{
    // pass
}

int
next_control_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
next_control_point(const int geometry; const int ptnum)
{
    // pass
}

#endif  // _SPLINEUTILS_H_
