from autoarray.plotters import plotters, mat_objs
from autoastro.plots import lensing_plotters
from autolens.plots import plane_plots

@plotters.set_subplot_filename
def subplot_tracer(
    tracer,
    grid,
    mask=None,
    positions=None,
    include=lensing_plotters.Include(),
    sub_plotter=plotters.SubPlotter(),
):
    """Plot the observed _tracer of an analysis, using the *Imaging* class object.

    The visualization and output type can be fully customized.

    Parameters
    -----------
    tracer : autolens.imaging.tracer.Imaging
        Class containing the _tracer,  noise_map-mappers and PSF that are to be plotted.
        The font size of the figure ylabel.
    output_path : str
        The path where the _tracer is output if the output_type is a file format (e.g. png, fits)
    output_format : str
        How the _tracer is output. File formats (e.g. png, fits) output the _tracer to harddisk. 'show' displays the _tracer \
        in the python interpreter window.
    """

    number_subplots = 6

    sub_plotter.setup_subplot_figure(number_subplots=number_subplots)

    sub_plotter.setup_subplot(number_subplots=number_subplots, subplot_index=1)

    profile_image(
        tracer=tracer,
        grid=grid,
        mask=mask,
        positions=positions,
        include=include,
        plotter=sub_plotter,
    )

    if tracer.has_mass_profile:

        sub_plotter.setup_subplot(number_subplots=number_subplots, subplot_index= 2)

        convergence(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=sub_plotter,
        )

        sub_plotter.setup_subplot(number_subplots=number_subplots, subplot_index= 3)

        potential(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=sub_plotter,
        )

    sub_plotter.setup_subplot(number_subplots=number_subplots, subplot_index= 4)

    source_plane_grid = tracer.traced_grids_of_planes_from_grid(grid=grid)[-1]

    plane_plots.plane_image(
        plane=tracer.source_plane,
        grid=source_plane_grid,
        lines=include.caustics_from_obj(obj=tracer),
        include=include,
        plotter=sub_plotter,
    )

    if tracer.has_mass_profile:

        sub_plotter.setup_subplot(number_subplots=number_subplots, subplot_index= 5)

        deflections_y(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=sub_plotter,
        )

        sub_plotter.setup_subplot(number_subplots=number_subplots, subplot_index= 6)

        deflections_x(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=sub_plotter,
        )

    sub_plotter.output.subplot_to_figure()

    sub_plotter.close_figure()


def individual(
    tracer,
    grid,
    mask=None,
    positions=None,
    plot_profile_image=False,
    plot_source_plane=False,
    plot_convergence=False,
    plot_potential=False,
    plot_deflections=False,
    plot_magnification=False,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):
    """Plot the observed _tracer of an analysis, using the *Imaging* class object.

    The visualization and output type can be fully customized.

    Parameters
    -----------
    tracer : autolens.imaging.tracer.Imaging
        Class containing the _tracer, noise_map-mappers and PSF that are to be plotted.
        The font size of the figure ylabel.
    output_path : str
        The path where the _tracer is output if the output_type is a file format (e.g. png, fits)
    output_format : str
        How the _tracer is output. File formats (e.g. png, fits) output the _tracer to harddisk. 'show' displays the _tracer \
        in the python interpreter window.
    """

    if plot_profile_image:

        profile_image(
            tracer=tracer,
            grid=grid,
            mask=mask,
            positions=positions,
            include=include,
            plotter=plotter,
        )

    if plot_convergence:

        convergence(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=plotter,
        )

    if plot_potential:

        potential(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=plotter,
        )

    if plot_source_plane:

        source_plane_grid = tracer.traced_grids_of_planes_from_grid(grid=grid)[-1]

        plane_plots.plane_image(
            plane=tracer.source_plane,
            grid=source_plane_grid,
            lines=include.caustics_from_obj(obj=tracer),
            positions=None,
            include=include,
            plotter=plotter.plotter_with_new_output(
                output=mat_objs.Output(filename="source_plane")
            ),
        )

    if plot_deflections:

        deflections_y(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=plotter,
        )

        deflections_x(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=plotter,
        )

    if plot_magnification:

        magnification(
            tracer=tracer,
            grid=grid,
            mask=mask,
            include=include,
            plotter=plotter,
        )


@plotters.set_labels
def profile_image(
    tracer,
    grid,
    mask=None,
    positions=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    plotter.array.plot(
        array=tracer.profile_image_from_grid(grid=grid),
        mask=mask,
        points=positions,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )


@plotters.set_labels
def convergence(
    tracer,
    grid,
    mask=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    plotter.array.plot(
        array=tracer.convergence_from_grid(grid=grid),
        mask=mask,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )


@plotters.set_labels
def potential(
    tracer,
    grid,
    mask=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    plotter.array.plot(
        array=tracer.potential_from_grid(grid=grid),
        mask=mask,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )


@plotters.set_labels
def deflections_y(
    tracer,
    grid,
    mask=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    deflections = tracer.deflections_from_grid(grid=grid)
    deflections_y = grid.mapping.array_stored_1d_from_sub_array_1d(
        sub_array_1d=deflections[:, 0]
    )

    plotter.array.plot(
        array=deflections_y,
        mask=mask,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )


@plotters.set_labels
def deflections_x(
    tracer,
    grid,
    mask=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    deflections = tracer.deflections_from_grid(grid=grid)
    deflections_x = grid.mapping.array_stored_1d_from_sub_array_1d(
        sub_array_1d=deflections[:, 1]
    )

    plotter.array.plot(
        array=deflections_x,
        mask=mask,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )

@plotters.set_labels
def magnification(
    tracer,
    grid,
    mask=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    plotter.array.plot(
        array=tracer.magnification_from_grid(grid=grid),
        mask=mask,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )

@plotters.set_labels
def contribution_map(
    tracer,
    mask=None,
    positions=None,
    include=lensing_plotters.Include(),
    plotter=plotters.Plotter(),
):

    plotter.array.plot(
        array=tracer.contribution_map,
        mask=mask,
        points=positions,
        lines=include.critical_curves_from_obj(obj=tracer),
        centres=include.mass_profile_centres_of_planes_from_obj(obj=tracer),
    )