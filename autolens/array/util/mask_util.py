import numpy as np
from skimage.transform import rescale

from autolens import decorator_util
from autolens import exc
from autolens.array.mapping_util import mask_mapping_util


@decorator_util.jit()
def mask_centres_from_shape_pixel_scale_and_centre(shape, pixel_scale, centre):
    """Determine the (y,x) arc-second central coordinates of a mask from its shape, pixel-scales and centre.

     The coordinate system is defined such that the positive y axis is up and positive x axis is right.

    Parameters
     ----------
    shape : (int, int)
        The (y,x) shape of the 2D array the arc-second centre is computed for.
    pixel_scales : (float, float)
        The (y,x) arc-second to pixel scales of the 2D array.
    centre : (float, flloat)
        The (y,x) centre of the 2D mask.

    Returns
    --------
    tuple (float, float)
        The (y,x) arc-second central coordinates of the input array.

    Examples
    --------
    centres_arcsec = centres_from_shape_pixel_scales_and_centre(shape=(5,5), pixel_scales=(0.5, 0.5), centre=(0.0, 0.0))
    """
    y_centre_arcsec = (float(shape[0] - 1) / 2) - (centre[0] / pixel_scale)
    x_centre_arcsec = (float(shape[1] - 1) / 2) + (centre[1] / pixel_scale)

    return (y_centre_arcsec, x_centre_arcsec)


@decorator_util.jit()
def total_pixels_from_mask(mask):
    """Compute the total number of unmasked pixels in a mask.

    Parameters
     ----------
    mask : ndarray
        A 2D array of bools, where *False* values are unmasked and included when counting pixels.

    Returns
    --------
    int
        The total number of pixels that are unmasked.

    Examples
    --------

    mask = np.array([[True, False, True],
                 [False, False, False]
                 [True, False, True]])

    total_regular_pixels = total_regular_pixels_from_mask(mask=mask)
    """

    total_regular_pixels = 0

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if not mask[y, x]:
                total_regular_pixels += 1

    return total_regular_pixels


@decorator_util.jit()
def total_sub_pixels_from_mask_and_sub_grid_size(mask, sub_grid_size):
    """Compute the total number of sub-pixels in unmasked pixels in a mask.
    
    Parameters
     ----------
    mask : ndarray
        A 2D array of bools, where *False* values are unmasked and included when counting sub pixels.
    sub_grid_size : int
        The size of the sub-grid that each pixel of the 2D mask array is divided into.

    Returns
    --------
    int
        The total number of sub pixels that are unmasked.

    Examples
    --------

    mask = np.array([[True, False, True],
                     [False, False, False]
                     [True, False, True]])

    total_sub_pixels = total_sub_pixels_from_mask(mask=mask, sub_grid_size=2)
    """
    return total_pixels_from_mask(mask) * sub_grid_size ** 2


@decorator_util.jit()
def total_sparse_pixels_from_mask(mask, unmasked_sparse_grid_pixel_centres):
    """Given the full (i.e. without removing pixels which are outside the mask) pixelization grid's pixel \ 
    center and the mask, compute the total number of pixels which are within the mask and thus used \ \
    by the pixelization grid.

    Parameters
    -----------
    mask : ccd.mask.Mask
        The mask within which pixelization pixels must be inside
    unmasked_sparse_grid_pixel_centres : ndarray
        The centres of the unmasked pixelization grid pixels.
    """

    total_sparse_pixels = 0

    for unmasked_sparse_pixel_index in range(
        unmasked_sparse_grid_pixel_centres.shape[0]
    ):

        y = unmasked_sparse_grid_pixel_centres[unmasked_sparse_pixel_index, 0]
        x = unmasked_sparse_grid_pixel_centres[unmasked_sparse_pixel_index, 1]

        if not mask[y, x]:
            total_sparse_pixels += 1

    return total_sparse_pixels


@decorator_util.jit()
def mask_circular_from_shape_pixel_scale_and_radius(
    shape, pixel_scale, radius_arcsec, centre=(0.0, 0.0)
):
    """Compute a circular mask from the 2D mask array shape and radius of the circle.

    This creates a 2D array where all values within the mask radius are unmasked and therefore *False*.

    Parameters
     ----------
    shape: (int, int)
        The (y,x) shape of the mask in units of pixels.
    pixel_scale: float
        The arc-second to pixel conversion factor of each pixel.
    radius_arcsec : float
        The radius (in arc seconds) of the circle within which pixels unmasked.
    centre: (float, float)
        The centre of the circle used to mask pixels.

    Returns
    --------
    ndarray
        The 2D mask array whose central pixels are masked as a circle.

    Examples
    --------
    mask = mask_circular_from_shape_pixel_scale_and_radius( \
        shape=(10, 10), pixel_scale=0.1, radius_arcsec=0.5, centre=(0.0, 0.0))
    """

    mask = np.full(shape, True)

    centres_arcsec = mask_centres_from_shape_pixel_scale_and_centre(
        shape=mask.shape, pixel_scale=pixel_scale, centre=centre
    )

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):

            y_arcsec = (y - centres_arcsec[0]) * pixel_scale
            x_arcsec = (x - centres_arcsec[1]) * pixel_scale

            r_arcsec = np.sqrt(x_arcsec ** 2 + y_arcsec ** 2)

            if r_arcsec <= radius_arcsec:
                mask[y, x] = False

    return mask


@decorator_util.jit()
def mask_circular_annular_from_shape_pixel_scale_and_radii(
    shape, pixel_scale, inner_radius_arcsec, outer_radius_arcsec, centre=(0.0, 0.0)
):
    """Compute an annular mask from an input inner and outer mask radius and shape.

    This creates a 2D array where all values within the inner and outer radii are unmasked and therefore *False*.

    Parameters
     ----------
    shape : (int, int)
        The (y,x) shape of the mask in units of pixels.
    pixel_scale: float
        The arc-second to pixel conversion factor of each pixel.
    inner_radius_arcsec : float
        The radius (in arc seconds) of the inner circle outside of which pixels are unmasked.
    outer_radius_arcsec : float
        The radius (in arc seconds) of the outer circle within which pixels are unmasked.
    centre: (float, float)
        The centre of the annulus used to mask pixels.

    Returns
    --------
    ndarray
        The 2D mask array whose central pixels are masked as a annulus.

    Examples
    --------
    mask = mask_annnular_from_shape_pixel_scale_and_radius( \
        shape=(10, 10), pixel_scale=0.1, inner_radius_arcsec=0.5, outer_radius_arcsec=1.5, centre=(0.0, 0.0))
    """

    mask = np.full(shape, True)

    centres_arcsec = mask_centres_from_shape_pixel_scale_and_centre(
        shape=mask.shape, pixel_scale=pixel_scale, centre=centre
    )

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):

            y_arcsec = (y - centres_arcsec[0]) * pixel_scale
            x_arcsec = (x - centres_arcsec[1]) * pixel_scale

            r_arcsec = np.sqrt(x_arcsec ** 2 + y_arcsec ** 2)

            if outer_radius_arcsec >= r_arcsec >= inner_radius_arcsec:
                mask[y, x] = False

    return mask


@decorator_util.jit()
def mask_circular_anti_annular_from_shape_pixel_scale_and_radii(
    shape,
    pixel_scale,
    inner_radius_arcsec,
    outer_radius_arcsec,
    outer_radius_2_arcsec,
    centre=(0.0, 0.0),
):
    """Compute an annular mask from an input inner and outer mask radius and shape."""

    mask = np.full(shape, True)

    centres_arcsec = mask_centres_from_shape_pixel_scale_and_centre(
        shape=mask.shape, pixel_scale=pixel_scale, centre=centre
    )

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):

            y_arcsec = (y - centres_arcsec[0]) * pixel_scale
            x_arcsec = (x - centres_arcsec[1]) * pixel_scale

            r_arcsec = np.sqrt(x_arcsec ** 2 + y_arcsec ** 2)

            if (
                inner_radius_arcsec >= r_arcsec
                or outer_radius_2_arcsec >= r_arcsec >= outer_radius_arcsec
            ):
                mask[y, x] = False

    return mask


@decorator_util.jit()
def elliptical_radius_from_y_x_phi_and_axis_ratio(y_arcsec, x_arcsec, phi, axis_ratio):
    r_arcsec = np.sqrt(x_arcsec ** 2 + y_arcsec ** 2)

    theta_rotated = np.arctan2(y_arcsec, x_arcsec) + np.radians(phi)

    y_arcsec_elliptical = r_arcsec * np.sin(theta_rotated)
    x_arcsec_elliptical = r_arcsec * np.cos(theta_rotated)

    return np.sqrt(
        x_arcsec_elliptical ** 2.0 + (y_arcsec_elliptical / axis_ratio) ** 2.0
    )


@decorator_util.jit()
def mask_elliptical_from_shape_pixel_scale_and_radius(
    shape, pixel_scale, major_axis_radius_arcsec, axis_ratio, phi, centre=(0.0, 0.0)
):
    """Compute an elliptical mask from an input major-axis mask radius, axis-ratio, rotational angle phi, shape and \
    centre.

    This creates a 2D array where all values within the ellipse are unmasked and therefore *False*.

    Parameters
     ----------
    shape: (int, int)
        The (y,x) shape of the mask in units of pixels.
    pixel_scale: float
        The arc-second to pixel conversion factor of each pixel.
    major_axis_radius_arcsec : float
        The major-axis (in arc seconds) of the ellipse within which pixels are unmasked.
    axis_ratio : float
        The axis-ratio of the ellipse within which pixels are unmasked.
    phi : float
        The rotation angle of the ellipse within which pixels are unmasked, (counter-clockwise from the positive \
         x-axis).
    centre: (float, float)
        The centre of the ellipse used to mask pixels.

    Returns
    --------
    ndarray
        The 2D mask array whose central pixels are masked as an ellipse.

    Examples
    --------
    mask = mask_elliptical_from_shape_pixel_scale_and_radius( \
        shape=(10, 10), pixel_scale=0.1, major_axis_radius_arcsec=0.5, axis_ratio=0.5, phi=45.0, centre=(0.0, 0.0))
    """

    mask = np.full(shape, True)

    centres_arcsec = mask_centres_from_shape_pixel_scale_and_centre(
        shape=mask.shape, pixel_scale=pixel_scale, centre=centre
    )

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):

            y_arcsec = (y - centres_arcsec[0]) * pixel_scale
            x_arcsec = (x - centres_arcsec[1]) * pixel_scale

            r_arcsec_elliptical = elliptical_radius_from_y_x_phi_and_axis_ratio(
                y_arcsec, x_arcsec, phi, axis_ratio
            )

            if r_arcsec_elliptical <= major_axis_radius_arcsec:
                mask[y, x] = False

    return mask


@decorator_util.jit()
def mask_elliptical_annular_from_shape_pixel_scale_and_radius(
    shape,
    pixel_scale,
    inner_major_axis_radius_arcsec,
    inner_axis_ratio,
    inner_phi,
    outer_major_axis_radius_arcsec,
    outer_axis_ratio,
    outer_phi,
    centre=(0.0, 0.0),
):
    """Compute an elliptical annular mask from an input major-axis mask radius, axis-ratio, rotational angle phi for \
     both the inner and outer elliptical annuli and a shape and centre for the mask.

    This creates a 2D array where all values within the elliptical annuli are unmasked and therefore *False*.

    Parameters
     ----------
    shape: (int, int)
        The (y,x) shape of the mask in units of pixels.
    pixel_scale: float
        The arc-second to pixel conversion factor of each pixel.
    inner_major_axis_radius_arcsec : float
        The major-axis (in arc seconds) of the inner ellipse within which pixels are masked.
    inner_axis_ratio : float
        The axis-ratio of the inner ellipse within which pixels are masked.
    inner_phi : float
        The rotation angle of the inner ellipse within which pixels are masked, (counter-clockwise from the \
        positive x-axis).
    outer_major_axis_radius_arcsec : float
        The major-axis (in arc seconds) of the outer ellipse within which pixels are unmasked.
    outer_axis_ratio : float
        The axis-ratio of the outer ellipse within which pixels are unmasked.
    outer_phi : float
        The rotation angle of the outer ellipse within which pixels are unmasked, (counter-clockwise from the \
        positive x-axis).
    centre: (float, float)
        The centre of the elliptical annuli used to mask pixels.

    Returns
    --------
    ndarray
        The 2D mask array whose elliptical annuli pixels are masked

    Examples
    --------
    mask = mask_elliptical_annuli_from_shape_pixel_scale_and_radius( \
        shape=(10, 10), pixel_scale=0.1,
         inner_major_axis_radius_arcsec=0.5, inner_axis_ratio=0.5, inner_phi=45.0,
         outer_major_axis_radius_arcsec=1.5, outer_axis_ratio=0.8, outer_phi=90.0,
         centre=(0.0, 0.0))
    """

    mask = np.full(shape, True)

    centres_arcsec = mask_centres_from_shape_pixel_scale_and_centre(
        shape=mask.shape, pixel_scale=pixel_scale, centre=centre
    )

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):

            y_arcsec = (y - centres_arcsec[0]) * pixel_scale
            x_arcsec = (x - centres_arcsec[1]) * pixel_scale

            inner_r_arcsec_elliptical = elliptical_radius_from_y_x_phi_and_axis_ratio(
                y_arcsec, x_arcsec, inner_phi, inner_axis_ratio
            )

            outer_r_arcsec_elliptical = elliptical_radius_from_y_x_phi_and_axis_ratio(
                y_arcsec, x_arcsec, outer_phi, outer_axis_ratio
            )

            if (
                inner_r_arcsec_elliptical >= inner_major_axis_radius_arcsec
                and outer_r_arcsec_elliptical <= outer_major_axis_radius_arcsec
            ):
                mask[y, x] = False

    return mask


@decorator_util.jit()
def blurring_mask_from_mask_and_psf_shape(mask, psf_shape):
    """Compute a blurring mask from an input mask and psf shape.

    The blurring mask corresponds to all pixels which are outside of the mask but will have a fraction of their \
    light blur into the masked region due to PSF convolution. The PSF shape is used to determine which pixels these are.
    
    If a pixel is identified which is outside the 2D dimensionos of the input mask, an error is raised and the user \
    should pad the input mask (and associated images).
    
    Parameters
    -----------
    mask : ndarray
        A 2D array of bools, where *False* values are unmasked.
    psf_shape : (int, int)
        The 2D shape of the PSF which is used to compute the blurring mask.
        
    Returns
    --------
    ndarray
        The 2D blurring mask array whose unmasked values (*False*) correspond to where the mask will have PSF light \
        blurred into them.

    Examples
    --------
    mask = np.array([[True, True, True],
                     [True, False, True]
                     [True, True, True]])      
    
    blurring_mask = blurring_mask_from_mask_and_psf_shape(mask=mask, psf_shape=(3,3)) 
    
    """

    blurring_mask = np.full(mask.shape, True)

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if not mask[y, x]:
                for y1 in range((-psf_shape[0] + 1) // 2, (psf_shape[0] + 1) // 2):
                    for x1 in range((-psf_shape[1] + 1) // 2, (psf_shape[1] + 1) // 2):
                        if (
                            0 <= x + x1 <= mask.shape[1] - 1
                            and 0 <= y + y1 <= mask.shape[0] - 1
                        ):
                            if mask[y + y1, x + x1]:
                                blurring_mask[y + y1, x + x1] = False
                        else:
                            raise exc.MaskException(
                                "setup_blurring_mask extends beyond the sub_grid_size "
                                "of the mask - pad the datas array before masking"
                            )

    return blurring_mask


@decorator_util.jit()
def mask_from_shape_and_mask_1d_index_to_mask_2d_index(
    shape, mask_1d_index_to_mask_2d_index
):
    """For a 1D array that was computed by mapping_util unmasked values from a 2D array of shape (rows, columns), map its \
    indexes back to the original 2D array to create the origianl 2D mask.

    This uses a 1D array 'one_to_two' where each index gives the 2D pixel indexes of the 1D array's unmasked pixels, \
    for example:

    - If one_to_two[0] = [0,0], the first value of the 1D array maps to the pixel [0,0] of the 2D array.
    - If one_to_two[1] = [0,1], the second value of the 1D array maps to the pixel [0,1] of the 2D array.
    - If one_to_two[4] = [1,1], the fifth value of the 1D array maps to the pixel [1,1] of the 2D array.

    Parameters
     ----------
    shape : (int, int)
        The shape of the 2D array which the pixels are defined on.
    mask_1d_index_to_mask_2d_index : ndarray
        An array describing the 2D array index that every 1D array index maps too.

    Returns
    --------
    ndarray
        A 2D mask array where unmasked values are *False*.

    Examples
    --------
    one_to_two = np.array([[0,1], [1,0], [1,1], [1,2], [2,1]])

    mask = mask_from_shape_and_one_to_two(shape=(3,3), one_to_two=one_to_two)
    """

    mask = np.ones(shape)

    for index in range(len(mask_1d_index_to_mask_2d_index)):
        mask[
            mask_1d_index_to_mask_2d_index[index, 0],
            mask_1d_index_to_mask_2d_index[index, 1],
        ] = False

    return mask


@decorator_util.jit()
def total_edge_pixels_from_mask(mask):
    """Compute the total number of borders-pixels in a mask."""

    edge_pixel_total = 0

    for y in range(1, mask.shape[0] - 1):
        for x in range(1, mask.shape[1] - 1):
            if not mask[y, x]:
                if (
                    mask[y + 1, x]
                    or mask[y - 1, x]
                    or mask[y, x + 1]
                    or mask[y, x - 1]
                    or mask[y + 1, x + 1]
                    or mask[y + 1, x - 1]
                    or mask[y - 1, x + 1]
                    or mask[y - 1, x - 1]
                ):
                    edge_pixel_total += 1

    return edge_pixel_total


@decorator_util.jit()
def edge_pixels_from_mask(mask):
    """Compute a 1D array listing all edge pixel indexes in the mask. An edge pixel is a pixel which is not fully \
    surrounding by False mask values i.e. it is on an edge."""

    edge_pixel_total = total_edge_pixels_from_mask(mask)

    edge_pixels = np.zeros(edge_pixel_total)
    edge_index = 0
    regular_index = 0

    for y in range(1, mask.shape[0] - 1):
        for x in range(1, mask.shape[1] - 1):
            if not mask[y, x]:
                if (
                    mask[y + 1, x]
                    or mask[y - 1, x]
                    or mask[y, x + 1]
                    or mask[y, x - 1]
                    or mask[y + 1, x + 1]
                    or mask[y + 1, x - 1]
                    or mask[y - 1, x + 1]
                    or mask[y - 1, x - 1]
                ):
                    edge_pixels[edge_index] = regular_index
                    edge_index += 1

                regular_index += 1

    return edge_pixels


@decorator_util.jit()
def check_if_border_pixel(mask, edge_pixel_1d, mask_1d_index_to_mask_2d_index):
    edge_pixel_index = int(edge_pixel_1d)

    y = int(mask_1d_index_to_mask_2d_index[edge_pixel_index, 0])
    x = int(mask_1d_index_to_mask_2d_index[edge_pixel_index, 1])

    if (
        np.sum(mask[0:y, x]) == y
        or np.sum(mask[y, x : mask.shape[1]]) == mask.shape[1] - x - 1
        or np.sum(mask[y : mask.shape[0], x]) == mask.shape[0] - y - 1
        or np.sum(mask[y, 0:x]) == x
    ):
        return True
    else:
        return False


@decorator_util.jit()
def total_border_pixels_from_mask_and_edge_pixels(
    mask, edge_pixels, mask_1d_index_to_mask_2d_index
):
    """Compute the total number of borders-pixels in a mask."""

    border_pixel_total = 0

    for i in range(edge_pixels.shape[0]):

        if check_if_border_pixel(mask, edge_pixels[i], mask_1d_index_to_mask_2d_index):
            border_pixel_total += 1

    return border_pixel_total


@decorator_util.jit()
def border_pixels_from_mask(mask):
    """Compute a 1D array listing all borders pixel indexes in the mask. A borders pixel is a pixel which:

     1) is not fully surrounding by False mask values.
     2) Can reach the edge of the array without hitting a masked pixel in one of four directions (upwards, downwards,
     left, right).

     The borders pixels are thus pixels which are on the exterior edge of the mask. For example, the inner ring of edge \
     pixels in an annular mask are edge pixels but not borders pixels."""

    edge_pixels = edge_pixels_from_mask(mask=mask)
    mask_1d_index_to_mask_2d_index = mask_mapping_util.sub_mask_1d_index_to_sub_mask_2d_index_from_mask_and_sub_grid_size(
        mask=mask, sub_grid_size=1
    )

    border_pixel_total = total_border_pixels_from_mask_and_edge_pixels(
        mask=mask,
        edge_pixels=edge_pixels,
        mask_1d_index_to_mask_2d_index=mask_1d_index_to_mask_2d_index,
    )

    border_pixels = np.zeros(border_pixel_total)

    border_pixel_index = 0

    for edge_pixel_index in range(edge_pixels.shape[0]):

        if check_if_border_pixel(
            mask=mask,
            edge_pixel_1d=edge_pixels[edge_pixel_index],
            mask_1d_index_to_mask_2d_index=mask_1d_index_to_mask_2d_index,
        ):

            border_pixels[border_pixel_index] = edge_pixels[edge_pixel_index]
            border_pixel_index += 1

    return border_pixels


# @decorator_util.jit()
def sub_border_pixels_from_mask_and_sub_grid_size(mask, sub_grid_size):
    """Compute a 1D array listing all borders pixel indexes in the mask. A borders pixel is a pixel which:

     1) is not fully surrounding by False mask values.
     2) Can reach the edge of the array without hitting a masked pixel in one of four directions (upwards, downwards,
     left, right).

     The borders pixels are thus pixels which are on the exterior edge of the mask. For example, the inner ring of edge \
     pixels in an annular mask are edge pixels but not borders pixels."""

    border_pixels = border_pixels_from_mask(mask=mask)

    sub_border_pixels = np.zeros(shape=border_pixels.shape[0])

    mask_1d_index_to_sub_mask_2d_indexes = mask_mapping_util.mask_1d_index_to_sub_mask_1d_indexes_from_mask(
        mask=mask, sub_grid_size=sub_grid_size
    )

    border_1d_index = 0

    central_sub_pixel = int(sub_grid_size ** 2.0 / 2)

    for border_pixel in border_pixels:
        sub_border_pixels_of_border_pixel = mask_1d_index_to_sub_mask_2d_indexes[
            int(border_pixel)
        ]
        sub_border_pixels[border_1d_index] = sub_border_pixels_of_border_pixel[
            central_sub_pixel
        ]
        border_1d_index += 1

    return sub_border_pixels


@decorator_util.jit()
def edge_buffed_mask_from_mask(mask):

    edge_buffed_mask = mask.copy()

    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if not mask[y, x]:
                if y + 1 <= mask.shape[0] - 1:
                    edge_buffed_mask[y + 1, x] = False
                if y - 1 >= 0:
                    edge_buffed_mask[y - 1, x] = False
                if x + 1 <= mask.shape[1] - 1:
                    edge_buffed_mask[y, x + 1] = False
                if x - 1 >= 0:
                    edge_buffed_mask[y, x - 1] = False
                if y + 1 <= mask.shape[0] - 1 and x + 1 <= mask.shape[1] - 1:
                    edge_buffed_mask[y + 1, x + 1] = False
                if y + 1 <= mask.shape[0] - 1 and x - 1 >= 0:
                    edge_buffed_mask[y + 1, x - 1] = False
                if y - 1 >= 0 and x + 1 <= mask.shape[1] - 1:
                    edge_buffed_mask[y - 1, x + 1] = False
                if y - 1 >= 0 and x >= 0:
                    edge_buffed_mask[y - 1, x - 1] = False

    return edge_buffed_mask


def rescaled_mask_2d_from_mask_2d_and_rescale_factor(mask_2d, rescale_factor):
    rescaled_mask = rescale(
        image=mask_2d,
        scale=rescale_factor,
        mode="edge",
        anti_aliasing=False,
        multichannel=False,
    )

    rescaled_mask[0, :] = 1
    rescaled_mask[rescaled_mask.shape[0] - 1, :] = 1
    rescaled_mask[:, 0] = 1
    rescaled_mask[:, rescaled_mask.shape[1] - 1] = 1
    return np.isclose(rescaled_mask, 1)