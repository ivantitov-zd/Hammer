#pragma once
#ifndef _SPLINEUTILS_H_
#define _SPLINEUTILS_H_

#include <math.h>

int
sequence_length(const int start, stop, step)
{
    return (stop - start) / step + (((stop - start) % step) != 0);
}

int
is_in_sequence(const int value, start, stop, step)
{
    int diff = value - start;
    int quitient = diff / step;
    int remainder = diff % step;
    if (remainder == 0 && 0 <= quitient && 
        quitient < sequence_length(start, stop, step))
        return 1;
    return 0;
}

int
is_in_sequence(const int value, start, stop, step, offset)
{
    int diff = value + offset - start;
    int quitient = diff / step;
    int remainder = diff % step;
    if (remainder == 0 && 0 <= quitient && 
        quitient < sequence_length(start, stop, step))
        return 1;
    return 0;
}

int
is_vertex_in_sequence(const int geometry, vtxnum, start, stop, step)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return is_in_sequence(vertex_index, start, stop, step);
}

int
is_vertex_in_sequence(const int geometry, vtxnum, start, stop, step, offset)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return is_in_sequence(vertex_index + offset, start, stop, step);
}

int
is_point_in_sequence(const int geometry, ptnum, start, stop, step)
{
    int vtxnum = pointvertex(geometry, ptnum);
    return is_vertex_in_sequence(geometry, vtxnum, start, stop, step);
}

int
is_point_in_sequence(const int geometry, ptnum, start, stop, step, offset)
{
    int vtxnum = pointvertex(geometry, ptnum);
    return is_vertex_in_sequence(geometry, vtxnum, start, stop, step, offset);
}

int
is_start_vertex(const int geometry, vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    return vertex_index == 0;
}

int
is_start_point(const int geometry, ptnum)
{
    return is_start_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_start_edge(const int geometry;
              const int elemnum1, elemnum2;
              const string class)
{
    int vtxnum1, vtxnum2;
    if (class == 'point')
    {
        vtxnum1 = pointvertex(geometry, elemnum1);
        vtxnum2 = pointvertex(geometry, elemnum2);
    } else
    {
        vtxnum1 = elemnum1;
        vtxnum2 = elemnum2;
    }
    return is_start_vertex(geometry, vtxnum1) || is_start_vertex(geometry, vtxnum2);
}

int
is_start_edge(const int geometry, edgenum)
{
    return is_start_vertex(geometry, hedge_srcvertex(geometry, edgenum)) ||
           is_start_vertex(geometry, hedge_dstvertex(geometry, edgenum));
}

int
is_end_vertex(const int geometry, vtxnum)
{
    int vertex_index = vertexprimindex(geometry, vtxnum);
    int prim = vertexprim(geometry, vtxnum);
    return vertex_index == primvertexcount(geometry, prim) - 1;
}

int
is_end_point(const int geometry, ptnum)
{
    return is_end_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_end_edge(const int geometry;
            const int elemnum1, elemnum2;
            const string class)
{
    int vtxnum1, vtxnum2;
    if (class == 'point')
    {
        vtxnum1 = pointvertex(geometry, elemnum1);
        vtxnum2 = pointvertex(geometry, elemnum2);
    } else
    {
        vtxnum1 = elemnum1;
        vtxnum2 = elemnum2;
    }
    return is_end_vertex(geometry, vtxnum1) || is_end_vertex(geometry, vtxnum2);
}

int
is_end_edge(const int geometry, edgenum)
{
    return is_end_vertex(geometry, hedge_dstvertex(geometry, edgenum)) ||
           is_end_vertex(geometry, hedge_srcvertex(geometry, edgenum));
}

float
edge_length2(const int geometry;
             const int elemnum1, elemnum2;
             const string class)
{
    vector pos1, pos2;
    if (class == 'vertex')
    {
        int ptnum1 = vertexpoint(geometry, vtxnum1);
        int ptnum2 = vertexpoint(geometry, vtxnum2);
        pos1 = point(geometry, 'P', ptnum1);
        pos2 = point(geometry, 'P', ptnum2);
    } else  // Point
    {
        pos1 = point(geometry, 'P', elemnum1);
        pos2 = point(geometry, 'P', elemnum2);
    }
    return distance2(pos1, pos2);
}

float
edge_length(const int geometry;
            const int elemnum1, elemnum2;
            const string class)
{
    vector pos1, pos2;
    if (class == 'vertex')
    {
        int ptnum1 = vertexpoint(geometry, vtxnum1);
        int ptnum2 = vertexpoint(geometry, vtxnum2);
        pos1 = point(geometry, 'P', ptnum1);
        pos2 = point(geometry, 'P', ptnum2);
    } else  // Point
    {
        pos1 = point(geometry, 'P', elemnum1);
        pos2 = point(geometry, 'P', elemnum2);
    }
    return distance(pos1, pos2);
}

float
edge_length2(const int geometry, edgenum)
{
    if (!hedge_isvalid(geometry, edgenum))
        return 0;
    int vtxnum1 = vertexpoint(geometry, vtxnum1);
    int vtxnum2 = vertexpoint(geometry, vtxnum2);
    return edge_length2(geometry, vtxnum1, vtxnum2, 'vertex');
}

float
edge_length(const int geometry, edgenum)
{
    if (!hedge_isvalid(geometry, edgenum))
        return 0;
    int vtxnum1 = vertexpoint(geometry, vtxnum1);
    int vtxnum2 = vertexpoint(geometry, vtxnum2);
    return edge_length(geometry, vtxnum1, vtxnum2, 'vertex');
}

int
is_valid_spline(const int geometry, primnum)
{
    int type = primintrinsic(geometry, 'typeid', primnum);
    if (type > 3)
        return 0;
    // Todo: check order
    int closed = primintrinsic(geometry, 'closed', primnum);
    int vertex_count = primvertexcount(geometry, primnum);
    if (closed)
        return vertex_count >= 9 && vertex_count % 3 == 0;
    else
        return (vertex_count - 4) % 3 == 0;
}

int
is_valid_spline(const int geometry, primnum, only_bezier)
{
    int type = primintrinsic(geometry, 'typeid', primnum);
    if (type > 3 || type != 3 && only_bezier)
        return 0;
    // Todo: check order
    int closed = primintrinsic(geometry, 'closed', primnum);
    int vertex_count = primvertexcount(geometry, primnum);
    if (closed)
        return vertex_count >= 9 && vertex_count % 3 == 0;
    else
        return (vertex_count - 4) % 3 == 0;
}

int
is_knot_vertex(const int geometry, vtxnum)
{
    int prim = vertexprim(geometry, vtxnum);
    int type = primintrinsic(geometry, 'typeid', prim);
    if (type < 3)  // Poly and NURBS
        return 1;
    if (type == 3)  // Bezier
    {
        int vertex_index = vertexprimindex(geometry, vtxnum);
        return vertex_index % 3 == 0;
    }
    return 1;  // Not supported
}

int
is_knot_point(const int geometry, ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)  // Single point
        return 0;
    if (prim_count != 1)
        warning('Geometry has point shared between two or more splines');
    return is_knot_vertex(geometry, pointvertex(geometry, ptnum));
}

int
is_control_vertex(const int geometry, vtxnum)
{
    return !is_knot_vertex(geometry, vtxnum);
}

int
is_control_point(const int geometry, ptnum)
{
    return !is_knot_point(geometry, ptnum);
}

int
prev_knot_vertex(const int geometry, vtxnum)
{
    if (!is_knot_vertex(geometry, vtxnum))
        return -1;
    int prim = vertexprim(geometry, vtxnum);
    int index = vertexprimindex(geometry, vtxnum);
    index = max(index - 3, 0);
    return primvertex(geometry, prim, index);
}

int
prev_knot_point(const int geometry, ptnum)
{
    if (!is_knot_point(geometry, ptnum))
        return -1;
    int vtxnum = pointvertex(geometry, ptnum);
    vtxnum = prev_knot_vertex(geometry, vtxnum);
    return vertexpoint(geometry, vtxnum);
}

int
next_knot_vertex(const int geometry, vtxnum)
{
    if (!is_knot_vertex(geometry, vtxnum))
        return -1;
    int prim = vertexprim(geometry, vtxnum);
    int count = primvertexcount(geometry, prim);
    int index = vertexprimindex(geometry, vtxnum);
    index = min(index + 3, count - 1);
    return primvertex(geometry, prim, index);
}

int
next_knot_point(const int geometry, ptnum)
{
    if (!is_knot_point(geometry, ptnum))
        return -1;
    int vtxnum = pointvertex(geometry, ptnum);
    vtxnum = next_knot_vertex(geometry, vtxnum);
    return vertexpoint(geometry, vtxnum);
}

int
knot_vertex(const int geometry, vtxnum)
{
    int index = vertexprimindex(geometry, vtxnum);
    int prim = vertexprim(geometry, vtxnum);
    int vertex_count = primvertexcount(geometry, prim);
    index = (int)rint(ceil((index - 1) / 3.0) * 3) % vertex_count;
    return primvertex(geometry, prim, index);
}

int
knot_point(const int geometry, ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)  // Single point
        return -1;
    if (prim_count != 1)
        warning('Geometry has point shared between two or more splines');
    int type = primintrinsic(geometry, 'typeid', prims[0]);
    if (type == 3)  // Bezier
    {
        int vtxnum = knot_vertex(geometry, pointvertex(geometry, ptnum));
        return vertexpoint(geometry, vtxnum);
    }
    return -1;  // Not supported
}

int
opposite_knot_vertex(const int geometry, vtxnum)
{
    int index = vertexprimindex(geometry, vtxnum);
    int prim = vertexprim(geometry, vtxnum);
    int vertex_count = primvertexcount(geometry, prim);
    index = (((index - 1) % 3 == 0) * 3 + index / 3 * 3) % vertex_count;
    return primvertex(geometry, prim, index);
}

int
opposite_knot_point(const int geometry, ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)  // Single point
        return -1;
    if (prim_count != 1)
        warning('Geometry has point shared between two or more splines');
    int type = primintrinsic(geometry, 'typeid', prims[0]);
    if (type == 3)  // Bezier
    {
        int vtxnum = opposite_knot_vertex(geometry, pointvertex(geometry, ptnum));
        return vertexpoint(geometry, vtxnum);
    }
    return -1;  // Not supported
}

int
prev_control_vertex(const int geometry, vtxnum)
{
    if (!is_knot_vertex(geometry, vtxnum))
        return -1;
    int prim = vertexprim(geometry, vtxnum);
    int index = vertexprimindex(geometry, vtxnum);
    index = max(index - 3, 0);
    return primvertex(geometry, prim, index);
}

int
prev_control_point(const int geometry, ptnum)
{
    // pass
}

int
next_control_vertex(const int geometry, vtxnum)
{
    // pass
}

int
next_control_point(const int geometry, ptnum)
{
    // pass
}

float
angle(const vector vec1, vec2)
{
    return acos(dot(vec1, vec2) / sqrt(length2(vec1) * length2(vec2)));
}

float
signed_angle(const vector vec1, vec2)
{
    // pass
}

float
internal_angle(const int geometry;
               const int elemnum;
               const string class)
{
    int ptnum;
    if (class == 'vertex')
        ptnum = vertexpoint(geometry, elemnum);
    else
        ptnum = elemnum;
    int neighbours[] = neighbours(geometry, elemnum);
    if (len(neighbours) < 2)
        return 0;
    vector pos0 = point(geometry, 'P', ptnum);
    vector pos1 = point(geometry, 'P', neighbours[0]);
    vector pos2 = point(geometry, 'P', neighbours[1]);
    vector dir1 = pos1 - pos0;
    vector dir2 = pos2 - pos0;
    return angle(dir1, dir2);
}

float
external_angle(const int geometry;
               const int elemnum;
               const string class)
{
    return M_TWO_PI - internal_angle(geometry, elemnum, class);
}

float
forward_angle(const int geometry;
              const int elemnum;
              const string class)
{
    int ptnum;
    if (class == 'vertex')
        ptnum = vertexpoint(geometry, elemnum);
    else
        ptnum = elemnum;
    int neighbours[] = neighbours(geometry, elemnum);
    if (len(neighbours) < 2)
        return 0;
    vector curr_pos = point(0, 'P', ptnum);
    vector prev_pos = point(0, 'P', neighbours[0]);
    vector next_pos = point(0, 'P', neighbours[1]);
    return angle(curr_pos - prev_pos, next_pos - curr_pos);
}

float
backward_angle(const int geometry;
               const int elemnum;
               const string class)
{
    // pass
}

int
is_straight_point(const int geometry;
                  const int ptnum;
                  const float tolerance)
{
    int neighbours[] = neighbours(geometry, ptnum);
    if (len(neighbours) != 2)
        return 0;
    vector pos1 = point(geometry, 'P', neighbours[0]);
    vector pos2 = point(geometry, 'P', neighbours[1]);
    vector pos = normalize(pos2 - pos1) * 10;
    pos1 -= pos;
    pos2 += pos;
    pos = point(geometry, 'P', ptnum);
    if (ptlined(pos1, pos2, pos) > tolerance)
        return 0;
    return 1;
}

int
is_straight_vertex(const int geometry;
                   const int vtxnum;
                   const float tolerance)
{
    int ptnum = vertexpoint(geometry, vtxnum);
    return is_straight_point(geometry, ptnum, tolerance);
}

int
is_straight_spline(const int geometry;
                   const int primnum;
                   const float tolerance)
{
    int vertex_count = primvertexcount(geometry, primnum);
    if (vertex_count < 3)
        return 1;
    int points[] = primpoints(geometry, primnum);
    vector pos1 = point(geometry, 'P', points[0]);
    vector pos2 = point(geometry, 'P', points[-1]);
    vector pos = normalize(pos2 - pos1) * 10;
    pos1 -= pos;
    pos2 += pos;
    for (int v = 1; v < vertex_count - 1; ++v)
    {
        pos = point(geometry, 'P', points[v]);
        if (ptlined(pos1, pos2, pos) > tolerance)
            return 0;
    }
    return 1;
}

int
is_flat_spline(const int geometry;
               const int primnum;
               const float tolerance)
{
    int vertex_count = primvertexcount(geometry, primnum);
    if (vertex_count < 4)
        return 1;
    int points[] = primpoints(geometry, primnum);
    vector pos0 = point(geometry, 'P', points[0]);
    vector pos1 = point(geometry, 'P', points[1]);
    vector pos2 = point(geometry, 'P', points[2]);
    vector base_plane_dir = normalize(cross(pos0 - pos1, pos0 - pos2));
    for (int i = 3; i < vertex_count; ++i)
    {
        pos1 = pos2;
        pos2 = point(geometry, 'P', points[i]);
        if ((1.0 - abs(dot(base_plane_dir, normalize(cross(pos0 - pos1, pos0 - pos2))))) > tolerance)
            return 0;
    }
    return 1;
}

#endif  // _SPLINEUTILS_H_
