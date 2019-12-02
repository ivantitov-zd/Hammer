#pragma once
#ifndef _SPLINEUTILS_H_
#define _SPLINEUTILS_H_

int
is_control_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
is_control_point(const int geometry; const int ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)
        return -1;  // Single point
    if (prim_count != 1)
        warning('Geometry has point shared between two or more curves');
    int prim = prims[0];
    int type = primintrinsic(geometry, 'type', prim);
    if (type == 1 && primintrinsic(geometry, 'closed', prim) == 0)  // Polyline
    {
        return 1;
    } else if (type == 2)  // NURBS
    {
        return 1;
    } else if (type == 3)  // Bezier
    {
        int vertex_index = vertexprimindex(geometry, pointvertex(geometry, ptnum));
        return vertex_index % 3 == 0;
    }
    return -1;  // Not curve
}

int prev_control_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
prev_control_point(const int geometry; const int ptnum)
{
    // pass
}

int
next_control_point(const int geometry; const int ptnum)
{
    // pass
}

int
control_vertex(const int geometry; const int vtxnum)
{
    // pass
}

int
control_point(const int geometry; const int ptnum)
{
    int prims[] = pointprims(geometry, ptnum);
    int prim_count = len(prims);
    if (prim_count == 0)
        return -1;  // Single point
    if (prim_count != 1)
        warning('Geometry has point shared between two or more curves');
    int prim = prims[0];
    int type = primintrinsic(geometry, 'type', prim);
    if (type == 1 && primintrinsic(geometry, 'closed', prim) == 0)  // Polyline
    {
        return ptnum;
    } else if (type == 2)  // NURBS
    {
        return ptnum;
    } else if (type == 3)  // Bezier
    {
        int vertex_index = vertexprimindex(geometry, pointvertex(geometry, ptnum));
        return (int)rint(ceil((vertex_index - 1) / 3.0) * 3);
    }
    return -1;  // Not curve
}

#endif  // _SPLINEUTILS_H_
