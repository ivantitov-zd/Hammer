#pragma once
#ifndef _SPLINEUTILS_H_
#define _SPLINEUTILS_H_

int
is_in_range(const int start, end, step)
{
    // pass
}

int
is_vertex_in_range(const int geometry;
                   const int vtxnum;
                   const int start;
                   const int end;
                   const int step)
{
    // pass
}

int
is_point_in_range(const int geometry;
                  const int ptnum;
                  const int start;
                  const int end;
                  const int step)
{
    // pass
}

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
is_start_edge(const int geometry; const int edgenum)
{
    // pass
}

int
is_start_edge(const int geometry; const int vtxnum1, vtxnum2)
{
    // pass
}

int
is_start_edge(const int geometry; const int ptnum1, ptnum2)
{
    // pass
}

int
is_end_vertex(const int geometry; const int vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    int prim = vertexprim(geometry, vtxnum);
    return vertex_index == primvertexcount(geometry, prim) - 1;
}

int
is_end_point(const int geometry; const int ptnum)
{
    return is_end_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_end_edge(const int geometry; const int vtxnum1, vtxnum2)
{
    // pass
}

int
is_end_edge(const int geometry; const int ptnum1, ptnum2)
{
    // pass
}

int
is_end_edge(const int geometry; const int edgenum)
{
    // pass
}

int
edge_length(const int geometry; const int vtxnum1, vtxnum2)
{
    // pass
}

int
edge_length(const int geometry; const int ptnum1, ptnum2)
{
    // pass
}

int
edge_length(const int geometry; const int edgenum)
{
    // pass
}

int
is_valid_spline(const int geometry; const int primnum)
{
    int type = primintrinsic(geometry, 'typeid', primnum);
    // Todo
    return (primvertexcount(geometry, primnum) - 4) % 3 == 0;
}

int
is_knot_vertex(const int geometry; const int vtxnum)
{
    int prim = vertexprim(geometry, vtxnum);
    int type = primintrinsic(geometry, 'typeid', prim);
    if (type == 3)  // Bezier
    {
        int vertex_index = vertexprimindex(geometry, vtxnum);
        return vertex_index % 3 == 0;
    }
    return 1;  // Not supported
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
    return is_knot_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_control_vertex(const int geometry; const int vtxnum)
{
    return !is_knot_vertex(geometry, vtxnum);
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

float
vertex_internal_angle(const int geometry; const int vtxnum)
{
    // pass
}

float
point_internal_angle(const int geometry; const int ptnum)
{
    // pass
}

float
vertex_external_angle(const int geometry; const int vtxnum)
{
    // pass
}

float
point_external_angle(const int geometry; const int ptnum)
{
    // pass
}

float
vertex_forward_angle(const int geometry; const int vtxnum)
{
    // pass
}

float
point_forward_angle(const int geometry; const int ptnum)
{
    // pass
}

float
vertex_backward_angle(const int geometry; const int vtxnum)
{
    // pass
}

float
point_backward_angle(const int geometry; const int ptnum)
{
    // pass
}

#endif  // _SPLINEUTILS_H_
