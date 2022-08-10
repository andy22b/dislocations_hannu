import numpy as np
import rasterio

def write_tiff(filename: str, x: np.ndarray, y: np.ndarray, z: np.ndarray, epsg: int = 2193, reverse_y: bool = False,
               compress_lzw: bool = True):
    """
    Write x, y, z into geotiff format.
    :param filename:
    :param x: x coordinates
    :param y: y coordinates
    :param z: z coordinates: must have ny rows and nx columns
    :param epsg: Usually NZTM (2193)
    :param reverse_y: y starts at y_max and decreases
    :param compress_lzw: lzw compression
    :return:
    """
    # Check data have correct dimensions
    assert all([a.ndim == 1 for a in (x, y)])
    assert z.shape == (len(y), len(x))

    # Change into y-ascending format (reverse_y option changes it back later)
    if y[0] > y[-1]:
        y = y[::-1]
        z = z[::-1, :]

    # To allow writing in correct format
    z = np.array(z, dtype=np.float64)

    # Calculate x and y spacing
    x_spacing = (max(x) - min(x)) / (len(x) - 1)
    y_spacing = (max(y) - min(y)) / (len(y) - 1)

    # Set affine transform from x and y
    if reverse_y:
        # Sometimes GIS prefer y values to descend.
        transform = rasterio.transform.Affine(x_spacing, 0., min(x), 0., -1 * y_spacing, max(y))
    else:
        transform = rasterio.transform.Affine(x_spacing, 0., min(x), 0., y_spacing, min(y))

    # create tiff profile (no. bands, data type etc.)
    profile = rasterio.profiles.DefaultGTiffProfile(count=1, dtype=np.float64, transform=transform, width=len(x),
                                                    height=len(y))

    # Set coordinate system if specified
    if epsg is not None:
        if epsg not in [2193, 4326, 32759, 32760, 27200]:
            print("EPSG:{:d} Not a recognised NZ coordinate system...".format(epsg))
            print("Writing anyway...")
        crs = rasterio.crs.CRS.from_epsg(epsg)
        profile["crs"] = crs

    # Add compression if desired
    if compress_lzw:
        profile["compress"] = "lzw"

    # Open raster file for writing
    fid = rasterio.open(filename, "w", **profile)
    # Write z to band one (depending whether y ascending/descending required).
    if reverse_y:
        fid.write(z[-1::-1], 1)
    else:
        fid.write(z, 1)
    # Close file
    fid.close()