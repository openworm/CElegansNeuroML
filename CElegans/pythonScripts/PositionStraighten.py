#!/usr/bin/env python
#
# (c) 2013  Petr Baudis <pasky@ucw.cz>
# MIT licence
#
# Python script for straightening NeuroML2 worm data (positions) assuming that
# (i) the worm is already straight along the x axis, and (ii) we have output
# of blenderExportSpine.py stashed somewhere. Run that script on the VirtualWorm
# Blender model that includes a spine curve.
#
# Usage: PositionStraighten.py NMLFILE SPINETSVFILE
#
# Algorithm: The spine curve is converted to a densely segmented line;
# then, for each position, the nearest point on this line is found,
# distance on the line (from its beginning) is used as the y coordinate,
# distance of the vertex from the line is used as the z coordinate.

import math
import numpy
import sys

import neuroml
import neuroml.loaders as loaders
import neuroml.writers as writers


# NeuroML data has been created from WRL (VRML) files exported from
# Blender by using the coordinates as-is, without any transformations
# applied, most notably a scale transformation. Therefore, the spine
# info is in different scale and needs to be multiplied by WRL_UPSCALE
# to match the ratio scale of NeuroML coordinates.
WRL_UPSCALE = 100.

def load_spline(stfile):
    """
    Load spline TSV, as produced by blenderExportSpine.py.
    """
    with open(stfile, 'r') as f:
        return [numpy.array([
                        [float(d) * WRL_UPSCALE for d in pt.split(",")]
                    for pt in line.split("\t")])
                for line in f]

def bezier_poly(p, t):
    """
    Evaluate the Bezier polynomial at a particular @t point.
    """
    return (1-t)**3*p[0] + 3*(1-t)**2*t*p[1] + 3*(1-t)*t**2*p[2] + t**3*p[3]

def bezier_pointset(p, resolution = 100):
    """
    Interpolate the Bezier curve of given control points.
    """
    t = numpy.linspace(0.0, 1.0, resolution)
    coordset = numpy.array([numpy.zeros(resolution), bezier_poly(p[:,1], t), bezier_poly(p[:,2], t)])
    return coordset.T

def bezier_spline_pointset(bzspline):
    """
    bzspline is a sequence of bezier curves where each curve
    is described by a left endpoint, two control points and
    right endpoint.

    Interpolate a set of points on this bzspline.
    """
    pointsets = []

    for i in range(len(bzspline)):
        ctrlpoints = bzspline[i]
        # print('===', i, ctrlpoints)

        pointset_1 = bezier_pointset(ctrlpoints)
        if i < len(bzspline)-1:
            # remove the last point, which will be re-added
            # by the next spline segment
            pointset_1 = numpy.delete(pointset_1, len(pointset_1)-1, 0)
            pass
        pointsets.append(pointset_1)

    return numpy.concatenate(pointsets)


def pointset_mileage(pointset):
    """
    Distance (approximated by straight lines) from the spine beginning,
    to be used as the Y coordinate of straightened worm.
    """
    # @distances lists pointwise distances between successive pairs
    # of points
    distances = numpy.sqrt(numpy.sum((pointset[1:] - pointset[:-1]) ** 2, 1))

    mileage = 0.
    mileageset = [0.]
    # Simple accumulation
    for i in range(len(distances)):
        mileage += distances[i]
        mileageset.append(mileage)
    return mileageset


def nearest_point_pair(pointset, coord):
    """
    Return the two nearest points in pointset, leftmost first.
    """
    # XXX: Extremely naive, compute distances to all points and sort
    distances = numpy.sqrt((pointset[:,0] - coord[0]) ** 2 + (pointset[:,1] - coord[1]) ** 2 + (pointset[:,2] - coord[2]) ** 2)
    dist_i = sorted(zip(distances, range(len(distances))), key = lambda o: o[0])
    i, j = dist_i[0][1], dist_i[1][1]
    if i > j:
        i, j = j, i
    return (i, j)

def transform_coord(pointset, newyset, coord):
    """
    Reinterpolate the coordinate of each vertex of each object
    by using pointset as the axis guide.
    """
    i, j = nearest_point_pair(pointset, coord)
    #print(i, pointset[i], j, pointset[j])

    # We are interested in the nearest point @k on line [i,j];
    # this point can be then used to interpolate y from newyset,
    # distance from @k to @coord is then z.

    # Note that pointset[.], coord [0] is the x-coordinate which
    # we are not recomputing (the worm is already straight along
    # the x axis). The other indices are therefore used shifted
    # accordingly.

    d_ij = pointset[j] - pointset[i]
    v = numpy.array([d_ij[1], d_ij[2]])
    w = numpy.array([-v[1], v[0]]) # w is perpendicular to v; v always points rightwards
    w = w / numpy.sqrt(numpy.dot(w, w)) # normalize w
    #print('v', v, 'w', w)

    # Find an intersection between lines [i] + s*v and coord + t*w:
    # [i]0 + s*v0 = coord0 + t*w0      [i]1 + s*v1 = coord1 + t*w1
    # t = ([i]0 + s*v0 - coord0) / w0  [i]1 + s*v1 = coord1 + ([i]0 + s*v0 - coord0) * w1/w0
    # => [i]1 + s*v1 = coord1 + [i]0*w1/w0 + s*v0*w1/w0 - coord0*w1/w0
    # => s*v1 - s*v0*w1/w0 = coord1 + [i]0*w1/w0 - [i]1 - coord0*w1/w0
    # => s = (coord1 + [i]0*w1/w0 - [i]1 - coord0*w1/w0) / (v1 - v0*w1/w0)
    s = (coord[2] + pointset[i][1]*w[1]/w[0] - pointset[i][2] - coord[1]*w[1]/w[0]) / (v[1] - v[0]*w[1]/w[0])
    t = (pointset[i][1] + s*v[0] - coord[1]) / w[0]

    # s is in [0,1], usable for interpolation
    # t is unit vector, so we can directly use it as z (distance from spine)
    y = (1. - s) * newyset[i] + s * newyset[j]
    z = t
    return numpy.array([coord[0], y, z])

def transform_segments(pointset, newyset, segmentset):
    """
    Reinterpolate the coordinate of each segment
    by using pointset as the axis guide.
    """

    for s in segmentset:
        for c in [s.proximal, s.distal]:
            if c is None:
                continue
            coord_in = [c.x, c.y, c.z]
            coord_out = transform_coord(pointset, newyset, coord_in)
            #print('in', coord_in, 'out', coord_out)
            c.x = coord_out[0]
            c.y = coord_out[1]
            c.z = coord_out[2]


def pointset_to_objects(pointset):
    """
    This function is just for visualization of intermediate data
    (i.e. debugging).
    """
    doc = neuroml.NeuroMLDocument()
    for i in range(len(pointset)):
        point = pointset[i]
        p = neuroml.Point3DWithDiam(x=point[0], y=point[1], z=point[2], diameter=1)

        soma = neuroml.Segment(proximal=p, distal=p)
        soma.name = "Soma"
        soma.id = 0
        sg = neuroml.SegmentGroup()
        sg.id = "Soma"
        sgm = neuroml.Member(segments = 0)
        sg.members.append(sgm)

        morphology = neuroml.Morphology()
        morphology.segments.append(soma)
        morphology.segment_groups.append(sg)

        cell = neuroml.Cell()
        cell.id = "pseudocell for bbpt " + str(i);
        cell.morphology = morphology
        doc.cells.append(cell)

    writers.NeuroMLWriter.write(doc, "backbone.nml")


if __name__ == '__main__':
    nmlfile = sys.argv[1]
    stfile = sys.argv[2]

    doc = loaders.NeuroMLLoader.load(nmlfile)
    if not doc.cells:
        sys.exit(1)
    cell = doc.cells[0]

    # Convert the spine to a dense sequence of sampled points on the spine
    bzspline = load_spline(stfile)
    pointset = bezier_spline_pointset(bzspline)

    # Debug stop along the way:
    #pointset_to_objects(pointset)

    # Compute Y coordinates in straightened worm corresponding to the pointset
    mileageset = pointset_mileage(pointset)
    newybase = mileageset[-1] / 2.
    newyset = list(map(lambda x: x - newybase, mileageset))

    # Transform segment coordinates by interpolation
    transform_segments(pointset, newyset, cell.morphology.segments)

    writers.NeuroMLWriter.write(doc, nmlfile)
