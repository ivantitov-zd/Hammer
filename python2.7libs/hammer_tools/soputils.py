import hou

Primitive = 1
Point = 2
Edge = 4
Vertex = 8
Detail = 4
AllAttribClasses = Primitive | Point | Vertex | Detail
AllGroupTypes = Primitive | Point | Edge | Vertex
Int = 1
Float = 2
String = 4
DataTypes = {hou.attribData.Int: Int,
             hou.attribData.Float: Float,
             hou.attribData.String: String}
AllDataTypes = Int | Float | String
AnyDataSize = range(0, 65)


def readDetailIntrinsic(node_or_geo, name):
    if isinstance(node_or_geo, hou.Node):
        geo = node_or_geo.geometry()
        if geo is None:
            return ()
        else:
            return readDetailIntrinsic(geo, name)
    elif isinstance(node_or_geo, hou.Geometry):
        return node_or_geo.intrinsicValue(name)
    return ()


def forceTuple(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if not isinstance(res, tuple):
            return res,
        else:
            return res

    return wrapper


@forceTuple
def primitiveGroups(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'primitivegroups')


@forceTuple
def pointGroups(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'pointgroups')


@forceTuple
def edgeGroups(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'edgegroups')


@forceTuple
def vertexGroups(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'vertexgroups')


def groups(node_or_geo, group_types=AllGroupTypes):
    group_list = []
    if group_types & Primitive:
        group_list.extend(primitiveGroups(node_or_geo))
    if group_types & Point:
        group_list.extend(pointGroups(node_or_geo))
    if group_types & Edge:
        group_list.extend(edgeGroups(node_or_geo))
    if group_types & Vertex:
        group_list.extend(vertexGroups(node_or_geo))
    return tuple(group_list)


def groupMenu(node, input_index=0, group_types=AllGroupTypes):
    menu = []
    if isinstance(node, str):
        node = hou.node(node)
    inputs = node.inputs()
    if inputs and len(inputs) > input_index and inputs[input_index]:
        group_list = groups(inputs[input_index], group_types)
        for group in group_list:
            menu.extend((group, group))
    return tuple(menu)


def groupTypeFromParm(parm='grouptype'):
    if isinstance(parm, str):
        parm = hou.parm(parm)
    value = parm.evalAsString().lower()
    if value == 'guess':
        return AllGroupTypes
    elif value.startswith('prim'):
        return Primitive
    elif value.startswith('point'):
        return Point
    elif value.startswith('edge'):
        return Edge
    elif value.startswith('vert'):
        return Vertex


groupType = groupTypeFromParm  # Todo: refactor in HDAs


def supportDataTypeAndSize(attrib_class):
    def decorator(func, attrib_class=attrib_class):
        def wrapper(node_or_geo, attrib_data_types=AllDataTypes, attrib_data_size=AnyDataSize, attrib_class=attrib_class):
            attrib_names = func(node_or_geo)
            geo = node_or_geo
            if isinstance(geo, hou.Node):
                geo = node_or_geo.geometry()

            def check(attrib_name):
                attrib = None
                if attrib_class == Primitive:
                    attrib = geo.findPrimAttrib(attrib_name)
                elif attrib_class == Point:
                    attrib = geo.findPointAttrib(attrib_name)
                elif attrib_class == Vertex:
                    attrib = geo.findVertexAttrib(attrib_name)
                elif attrib_class == Detail:
                    attrib = geo.findGlobalAttrib(attrib_name)
                else:
                    raise ValueError('Invalid attribute class')
                if attrib is not None:
                    return DataTypes[attrib.dataType()] & attrib_data_types and attrib.size() in attrib_data_size
                else:
                    raise RuntimeError('Invalid attribute name')

            return tuple(filter(check, attrib_names))

        return wrapper

    return decorator


@supportDataTypeAndSize(Primitive)
@forceTuple
def primitiveAttribs(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'primitiveattributes')


@supportDataTypeAndSize(Point)
@forceTuple
def pointAttribs(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'pointattributes')


@supportDataTypeAndSize(Vertex)
@forceTuple
def vertexAttribs(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'vertexattributes')


@supportDataTypeAndSize(Detail)
@forceTuple
def detailAttribs(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'detailattributes')


def attribs(node_or_geo, attrib_class=AllAttribClasses, attrib_data_types=AllDataTypes, attrib_data_size=AnyDataSize):
    attrib_list = []
    if attrib_class & Primitive:
        attrib_list.extend(primitiveAttribs(node_or_geo, attrib_data_types, attrib_data_size))
    if attrib_class & Point:
        attrib_list.extend(pointAttribs(node_or_geo, attrib_data_types, attrib_data_size))
    if attrib_class & Vertex:
        attrib_list.extend(vertexAttribs(node_or_geo, attrib_data_types, attrib_data_size))
    if attrib_class & Detail:
        attrib_list.extend(detailAttribs(node_or_geo, attrib_data_types, attrib_data_size))
    return tuple(attrib_list)


def attribMenu(node, input_index=0, attrib_class=AllAttribClasses, attrib_data_types=AllDataTypes, attrib_data_size=AnyDataSize):
    menu = []
    if isinstance(node, str):
        node = hou.node(node)
    inputs = node.inputs()
    if inputs and len(inputs) > input_index and inputs[input_index]:
        attrib_list = attribs(inputs[input_index], attrib_class, attrib_data_types, attrib_data_size)
        for attrib in attrib_list:
            menu.extend((attrib, attrib))
    return tuple(menu)


def attribClassFromParm(parm='class'):
    if isinstance(parm, str):
        parm = hou.parm(parm)
    value = parm.evalAsString().lower()
    if value == 'guess' or value == 'auto':
        return AllAttribClasses
    elif value.startswith('prim'):
        return Primitive
    elif value.startswith('point'):
        return Point
    elif value.startswith('vert'):
        return Vertex
    elif value == 'detail' or value.startswith('global'):
        return Detail


attribType = attribClassFromParm  # Todo: refactor in HDAs


def primitiveCount(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'primitivecount')


def pointCount(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'pointcount')


def edgeCount(node_or_geo):
    if isinstance(node_or_geo, hou.Node):
        geo = node_or_geo.geometry()
        if geo is None:
            return 0
        else:
            return edgeCount(geo)
    elif isinstance(node_or_geo, hou.Geometry):
        return node_or_geo.globEdges('*')
    return 0


def vertexCount(node_or_geo):
    return readDetailIntrinsic(node_or_geo, 'vertexcount')
