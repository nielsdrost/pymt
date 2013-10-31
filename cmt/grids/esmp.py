#! /bin/env python

"""
Examples
========

Create a grid that looks like this,

::

    (0) --- (1) --- (2)
     |       |       |
     |   0   |   1   |
     |       |       |
    (3) --- (4) --- (5)


>>> ESMP.ESMP_Initialize()

>>> g = EsmpUnstructured ([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], [0, 1, 4, 3, 1, 2, 5, 4], [4, 8])

>>> g = EsmpStructured ([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], (3, 2))

The as_mesh method provides a view of the grid as an ESMP_Mesh.

>>> ESMP.ESMP_MeshGetLocalElementCount (g.as_mesh ())
2
>>> ESMP.ESMP_MeshGetLocalNodeCount (g.as_mesh ())
6

ESMP elements are the same as the grids cells. Likewise with nodes and points.

>>> g = EsmpRectilinear ([0, 1, 2], [0, 1])
>>> ESMP.ESMP_MeshGetLocalElementCount (g.as_mesh ()) == g.get_cell_count ()
True
>>> ESMP.ESMP_MeshGetLocalNodeCount (g.as_mesh ()) == g.get_point_count ()
True

>>> g = EsmpUniformRectilinear ([3, 2], [1., 1.], [0., 0.])


Uniform Rectilinear Field
-------------------------

Create a field on a grid that looks like this,

::

    (0) --- (1) --- (2)
     |       |       |
     |   0   |   1   |
     |       |       |
    (3) --- (4) --- (5)

Create the field,

    >>> g = EsmpRasterField ((3,2), (2,1), (0, 0))
    >>> g.get_cell_count ()
    2
    >>> g.get_point_count ()
    6

Add some data at the points of our grid.

    >>> data = np.arange (6)
    >>> g.add_field ('var0', data, centering='point')
    >>> f = g.get_field ('var0')
    >>> f
    array([ 0.,  1.,  2.,  3.,  4.,  5.])
    >>> print f.dtype
    float64

The data can be given either as a 1D array or with the same shape
as the point grid. In either case, though, it will be flattened.

    >>> data = np.arange (6)
    >>> data.shape = (2, 3)
    >>> g.add_field ('var0', data, centering='point')
    >>> f = g.get_field ('var0')
    >>> f
    array([ 0.,  1.,  2.,  3.,  4.,  5.])

If the size or shape doesn't match, it's an error.

    >>> data = np.arange (2)
    >>> g.add_field ('bad var', data, centering='point')
    Traceback (most recent call last):
        ...
    DimensionError: 2 != 6

    >>> data = np.ones ((3, 2))
    >>> g.add_field ('bad var', data, centering='point')
    Traceback (most recent call last):
        ...
    DimensionError: (3, 2) != (2, 3)


Map between two fields
----------------------
    >>> from cmt.grids.raster import UniformRectilinear
    >>> from cmt.grids.rectilinear import Rectilinear

    >>> #ESMP.ESMP_Initialize()

    >>> src = EsmpRasterField ((3,3), (1,1), (0, 0))
    >>> data = np.arange (src.get_cell_count (), dtype=np.float64)
    >>> src.add_field ('srcfield', data, centering='zonal')
    >>> src.get_point_count ()
    9
    >>> src.get_cell_count ()
    4
    >>> src.get_x ()
    array([ 0., 1., 2., 0., 1., 2., 0., 1., 2.])
    >>> src.get_y ()
    array([ 0., 0., 0., 1., 1., 1., 2., 2., 2.])
    >>> src.get_connectivity () + 1
    array([1, 2, 5, 4, 2, 3, 6, 5, 4, 5, 8, 7, 5, 6, 9, 8], dtype=int32)

    >>> # EsmpRectilinearField.__mro__
    >>> dst = EsmpRectilinearField ([0., .5, 1.5, 2.], [0., .5, 1.5, 2.])
    >>> data = np.empty (dst.get_cell_count (), dtype=np.float64)
    >>> dst.add_field ('dstfield', data, centering='zonal')
    >>> dst.get_point_count ()
    16
    >>> dst.get_cell_count ()
    9
    >>> dst.get_x ()
    array([ 0. , 0.5, 1.5, 2. , 0. , 0.5, 1.5, 2. , 0. , 0.5, 1.5, 2. , 0. , 0.5, 1.5, 2. ])
    >>> dst.get_y ()
    array([ 0. , 0. , 0. , 0. , 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 2. , 2. , 2. , 2. ])
    >>> dst.get_connectivity () + 1
    array([ 1,  2,  6,  5,  2,  3,  7,  6,  3,  4,  8,  7,  5,  6, 10,  9,  6,
            7, 11, 10,  7,  8, 12, 11,  9, 10, 14, 13, 10, 11, 15, 14, 11, 12,
            16, 15], dtype=int32)

    >>> src_field = src.as_esmp ('srcfield')
    >>> dst_field = dst.as_esmp ('dstfield')
    >>> ESMP.ESMP_MeshGetLocalElementCount (src.as_mesh ())
    4
    >>> ESMP.ESMP_MeshGetLocalNodeCount (src.as_mesh ())
    9
    >>> ESMP.ESMP_MeshGetLocalElementCount (dst.as_mesh ())
    9
    >>> ESMP.ESMP_MeshGetLocalNodeCount (dst.as_mesh ())
    16

    #>>> ESMP.ESMP_FieldPrint (src_field)
    #>>> ESMP.ESMP_FieldPrint (dst_field)

    >>> f = run_regridding (src_field, dst_field)
    >>> field_ptr = ESMP.ESMP_FieldGetPtr(f, 0)

A bigger grid
-------------

    >>> (M, N) = (300, 300)
    >>> src = EsmpRasterField ((M, N), (1, 1), (0, 0))

Map values on cells
-------------------

    >>> (X, Y) = np.meshgrid (np.arange (0.5, 299.5, 1.), np.arange (0.5, 299.5, 1.))
    >>> data = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
    >>> src.add_field ('srcfield', data, centering='zonal')

    >>> dst = EsmpRasterField ((M*2-1, N*2-1), (1./2, 1./2), (0, 0))
    >>> data = np.empty (dst.get_cell_count (), dtype=np.float64)
    >>> dst.add_field ('dstfield', data, centering='zonal')

    >>> src_field = src.as_esmp ('srcfield')
    >>> dst_field = dst.as_esmp ('dstfield')

    >>> f = run_regridding (src_field, dst_field)
    >>> ans = ESMP.ESMP_FieldGetPtr(f, 0)

    >>> (X, Y) = np.meshgrid (np.arange (0.5, 299.5, .5), np.arange (0.5, 299.5, .5))
    >>> exact = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
    >>> np.sum (np.abs (exact.flat-ans))/(M*N*4.) < 1e-2
    True

Map values on points
--------------------

    >>> (X, Y) = np.meshgrid (np.arange (0.5, 300.5, 1.), np.arange (0.5, 300.5, 1.))
    >>> data = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
    >>> src.add_field ('srcfield_at_points', data, centering='point')

    >>> data = np.empty (dst.get_point_count (), dtype=np.float64)
    >>> dst.add_field ('dstfield_at_points', data, centering='point')

    >>> src_field = src.as_esmp ('srcfield_at_points')
    >>> dst_field = dst.as_esmp ('dstfield_at_points')

    >>> f = run_regridding (src_field, dst_field, method=ESMP.ESMP_REGRIDMETHOD_BILINEAR)
    >>> ans = ESMP.ESMP_FieldGetPtr(f, 0)

    >>> (X, Y) = np.meshgrid (np.arange (0.5, 300., .5), np.arange (0.5, 300., .5))
    >>> exact = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
    >>> np.sum (np.abs (exact.flat-ans))/(M*N*4.) < 1e-5
    True

    >>> ESMP.ESMP_Finalize()
"""

import numpy as np

from cmt.grids import (UniformRectilinear, Rectilinear, Structured,
                       Unstructured)
from cmt.grids.igrid import (IGrid, IField, DimensionError,
                             CenteringValueError, centering_choices)

import ESMP


class EsmpGrid (IGrid):
    def __init__ (self):
        self._mesh = ESMP.ESMP_MeshCreate (2, 2)

        self._mesh_add_nodes ()
        self._mesh_add_elements ()

        super (EsmpGrid, self).__init__ ()

    def as_mesh (self):
        return self._mesh

    def _mesh_add_nodes (self):
        node_ids = np.arange (1, self.get_point_count ()+1, dtype=np.int32)
        (x, y) = (self.get_x (), self.get_y ())

        node_coords = np.empty (x.size+y.size, dtype=np.float64)
        (node_coords[0::2], node_coords[1::2]) = (x, y)

        node_owner = np.zeros (self.get_point_count (), dtype=np.int32)

        ESMP.ESMP_MeshAddNodes (self._mesh, self.get_point_count (), node_ids, node_coords, node_owner)

    def _mesh_add_elements (self):
        cell_ids = np.arange (1, self.get_cell_count ()+1, dtype=np.int32)
        cell_types = (np.ones (self.get_cell_count (), dtype=np.int32) *
                      ESMP.ESMP_MESHELEMTYPE_QUAD)

        cell_conn = np.array (self.get_connectivity (), dtype=np.int32)+1

        ESMP.ESMP_MeshAddElements (self._mesh, self.get_cell_count (), cell_ids, cell_types, cell_conn)

    def reverse_element_ordering (self):
        last_offset = 0
        for offset in self._offset:
            c = self._connectivity[last_offset:offset].copy ()
            self._connectivity[last_offset:offset] = c[::-1]
            last_offset = offset


class EsmpUnstructured (Unstructured, EsmpGrid):
    name = 'ESMPUnstructured'


class EsmpStructured (Structured, EsmpGrid):
    name = 'ESMPStructured'


class EsmpRectilinear (Rectilinear, EsmpGrid):
    name = 'ESMPRectilinear'


class EsmpUniformRectilinear (UniformRectilinear, EsmpStructured):
    name = 'ESMPUniformRectilinear'


class EsmpField (IField):
    def __init__ (self, *args, **kwargs):
        super (EsmpField, self).__init__ (*args, **kwargs) 
        self._fields = {}

    def add_field (self, field_name, val, centering='zonal'):

        if centering not in centering_choices:
            raise CenteringValueError (centering)

        if centering=='zonal' and val.size != self.get_cell_count ():
            raise DimensionError (val.size, self.get_cell_count ())
        elif centering!='zonal' and val.size != self.get_point_count ():
            raise DimensionError (val.size, self.get_point_count ())

        if centering=='zonal':
            meshloc=ESMP.ESMP_MESHLOC_ELEMENT
        else:
            meshloc=ESMP.ESMP_MESHLOC_NODE

        field = ESMP.ESMP_FieldCreate (self._mesh, field_name, meshloc=meshloc)
        field_ptr = ESMP.ESMP_FieldGetPtr(field, 0)
        field_ptr.flat = val.flat

        self._fields[field_name] = field

    def get_field (self, field_name):
        field = self._fields[field_name]
        return ESMP.ESMP_FieldGetPtr(field, 0)

    def as_esmp (self, field_name):
        return self._fields[field_name]


class EsmpStructuredField (EsmpStructured, EsmpField):
    def add_field (self, field_name, val, centering='zonal'):
        if centering=='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()-1):
                raise DimensionError (val.shape, self.get_shape ()-1)
        elif centering!='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()):
                raise DimensionError (val.shape, self.get_shape ())
        try:
            super (EsmpStructuredField, self).add_field (field_name, val, centering=centering)
        except DimensionError, CenteringValueError:
            raise


class EsmpUnstructuredField (EsmpUnstructured, EsmpField):
    pass


class EsmpRectilinearField (EsmpRectilinear, EsmpStructuredField):
    pass


class EsmpRasterField (EsmpUniformRectilinear, EsmpRectilinearField):
    pass


def run_regridding(srcfield, dstfield, method=ESMP.ESMP_REGRIDMETHOD_CONSERVE,
                   unmapped=ESMP.ESMP_UNMAPPEDACTION_ERROR):
    '''
    PRECONDITIONS: Two ESMP_Fields have been created and a regridding operation 
                   is desired from 'srcfield' to 'dstfield'.
    POSTCONDITIONS: An ESMP regridding operation has set the data on 'dstfield'.
    '''
    #print 'Running an ESMF regridding operation. . .'

    # call the regridding functions
    routehandle = ESMP.ESMP_FieldRegridStore(srcfield, dstfield,
                                             method, unmapped)
    ESMP.ESMP_FieldRegrid(srcfield, dstfield, routehandle)
    ESMP.ESMP_FieldRegridRelease(routehandle)

    return dstfield


if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)
