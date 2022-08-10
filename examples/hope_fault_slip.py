import os.path
import numpy as np
import meshio
import cutde.halfspace as HS
from tiff import write_tiff


# Grid of x and y to calculate sea surface displacements at
x_data = np.arange(0, 4205000, 5000)
y_data = np.arange(2200000, 8005000, 5000)

xmesh, ymesh = np.meshgrid(x_data, y_data)


mesh_name = "Hope_combined.stl"
out_name = "hope_surface_disps.tif"
if all([os.path.exists(mesh_name), not os.path.exists(out_name)]):
    # Read in vtk
    mesh = meshio.read(mesh_name)

    # Triangles in right format for cutde
    vertices = mesh.points
    triangle_nums = mesh.cells_dict["triangle"]
    triangles = vertices[triangle_nums]

    # Read slip and rake and turn into strike-slip and dip-slip
    slip = mesh.cell_data["slip"][0]
    rake = mesh.cell_data["rake"][0]
    dip_slip = slip * np.sin(np.radians(rake))
    strike_slip = slip * np.cos(np.radians(rake))
    slip_array = np.vstack([strike_slip, dip_slip, 0. * dip_slip]).T

    # Region to calculate displacements
    xpoints = xmesh[mask_loc]
    ypoints = ymesh[mask_loc]
    # Change into cutde format
    pts = np.vstack((xpoints, ypoints, xpoints * 0.)).T

    # Calculate displacements
    disps = HS.disp_free(obs_pts=pts, tris=triangles, slips=slip_array, nu=0.25)

    # Put displacements into the right place in teh grid
    out_data = np.zeros(mask.shape)
    out_data[mask_loc] = disps[:, -1]

    # Write out tiff
    write_tiff(out_name, x_data, y_data, out_data)