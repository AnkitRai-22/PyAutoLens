from autolens.pipeline import pipeline as pl
from pipelines import profile_pipeline
from autolens.pipeline import phase as ph
from autolens.autopipe import model_mapper
from autolens.autopipe import non_linear
from autolens.imaging import image as im
from autolens.profiles import light_profiles
from autolens.profiles import mass_profiles
from autolens.analysis import galaxy_prior as gp
from autolens.analysis import galaxy as g
import numpy as np
import pytest

shape = (50, 50)


@pytest.fixture(name="profile_only_pipeline")
def make_profile_only_pipeline():
    return profile_pipeline.make()


@pytest.fixture(name="image")
def make_image():
    return im.Image(np.ones(shape), pixel_scale=0.2, noise=np.ones(shape), psf=im.PSF(np.ones((3, 3))))


@pytest.fixture(name="results_1")
def make_results_1():
    const = model_mapper.ModelInstance()
    var = model_mapper.ModelMapper()
    const.lens_galaxy = g.Galaxy(elliptical_sersic=light_profiles.EllipticalSersicLP())
    var.lens_galaxy = gp.GalaxyPrior(elliptical_sersic=light_profiles.EllipticalSersicLP)
    return ph.LensMassAndSourceProfilePhase.Result(constant=const, likelihood=1, variable=var,
                                                   analysis=MockAnalysis(number_galaxies=2, shape=shape, value=0.5))


@pytest.fixture(name="results_2")
def make_results_2():
    const = model_mapper.ModelInstance()
    var = model_mapper.ModelMapper()
    var.lens_galaxy = gp.GalaxyPrior(sie=mass_profiles.SphericalIsothermalMP)
    var.source_galaxy = gp.GalaxyPrior(elliptical_sersic=light_profiles.EllipticalSersicLP)
    const.lens_galaxy = g.Galaxy(sie=mass_profiles.SphericalIsothermalMP())
    const.source_galaxy = g.Galaxy(elliptical_sersic=light_profiles.EllipticalSersicLP())
    return ph.LensMassAndSourceProfilePhase.Result(constant=const, likelihood=1, variable=var,
                                                   analysis=MockAnalysis(number_galaxies=2, shape=shape, value=0.5))


@pytest.fixture(name="results_3")
def make_results_3():
    const = model_mapper.ModelInstance()
    var = model_mapper.ModelMapper()
    var.lens_galaxy = gp.GalaxyPrior(sie=mass_profiles.SphericalIsothermalMP,
                                     elliptical_sersic=light_profiles.EllipticalSersicLP)
    var.source_galaxy = gp.GalaxyPrior(elliptical_sersic=light_profiles.EllipticalSersicLP)
    const.lens_galaxy = g.Galaxy(sie=mass_profiles.SphericalIsothermalMP(),
                                 elliptical_sersic=light_profiles.EllipticalSersicLP())
    const.source_galaxy = g.Galaxy(elliptical_sersic=light_profiles.EllipticalSersicLP())
    return ph.LensMassAndSourceProfilePhase.Result(constant=const, likelihood=1, variable=var,
                                                   analysis=MockAnalysis(number_galaxies=2, shape=shape, value=0.5))


@pytest.fixture(name="results_3h")
def make_results_3h():
    const = model_mapper.ModelInstance()
    var = model_mapper.ModelMapper()
    const.lens_galaxy = g.Galaxy(hyper_galaxy=g.HyperGalaxy())
    const.source_galaxy = g.Galaxy(hyper_galaxy=g.HyperGalaxy())
    return ph.LensMassAndSourceProfilePhase.Result(constant=const, likelihood=1, variable=var,
                                                   analysis=MockAnalysis(number_galaxies=2, shape=shape, value=0.5))


class TestProfileOnlyPipeline(object):
    def test_phase1(self, profile_only_pipeline, image):
        phase1 = profile_only_pipeline.phases[0]
        analysis = phase1.make_analysis(image)

        assert isinstance(phase1.lens_galaxy, gp.GalaxyPrior)
        assert phase1.source_galaxy is None

        assert analysis.masked_image == np.ones((716,))
        assert analysis.masked_image.sub_grid_size == 1
        assert analysis.previous_results is None

    def test_phase2(self, profile_only_pipeline, image, results_1):
        phase2 = profile_only_pipeline.phases[1]
        previous_results = ph.ResultsCollection([results_1])
        analysis = phase2.make_analysis(image, previous_results)

        assert analysis.masked_image == np.full((704,), 0.5)

        assert isinstance(phase2.lens_galaxy, gp.GalaxyPrior)
        assert isinstance(phase2.source_galaxy, gp.GalaxyPrior)
        assert phase2.lens_galaxy.sie.centre == previous_results.first.variable.lens_galaxy.elliptical_sersic.centre

    def test_phase3(self, profile_only_pipeline, image, results_1, results_2):
        phase3 = profile_only_pipeline.phases[2]
        previous_results = ph.ResultsCollection([results_1, results_2])

        analysis = phase3.make_analysis(image, previous_results)

        assert isinstance(phase3.lens_galaxy, gp.GalaxyPrior)
        assert isinstance(phase3.source_galaxy, gp.GalaxyPrior)

        assert analysis.masked_image == np.ones((716,))

        assert phase3.lens_galaxy.elliptical_sersic == results_1.variable.lens_galaxy.elliptical_sersic
        assert phase3.lens_galaxy.sie == results_2.variable.lens_galaxy.sie
        assert phase3.source_galaxy == results_2.variable.source_galaxy

    # def test_phase3h(self, profile_only_pipeline, image, results_1, results_2, results_3):
    #     phase3h = profile_only_pipeline.phases[3]
    #     previous_results = ph.ResultsCollection([results_1, results_2, results_3])
    #
    #     analysis = phase3h.make_analysis(image, previous_results)
    #
    #     assert isinstance(phase3h.lens_galaxies, gp.GalaxyPrior)
    #     assert isinstance(phase3h.source_galaxies, gp.GalaxyPrior)
    #
    #     assert analysis.masked_image == np.ones((716,))
    #
    #     assert phase3h.lens_galaxies.elliptical_sersic == results_3.constant.lens_galaxies.elliptical_sersic
    #     assert phase3h.lens_galaxies.sie == results_3.constant.lens_galaxies.sie
    #     assert phase3h.source_galaxies.elliptical_sersic == results_3.constant.source_galaxies.elliptical_sersic
    #
    #     assert isinstance(phase3h.lens_galaxies.hyper_galaxy, model_mapper.PriorModel)
    #     assert isinstance(phase3h.source_galaxies.hyper_galaxy, model_mapper.PriorModel)

    def test_phase4(self, profile_only_pipeline, image, results_1, results_2, results_3, results_3h):
        phase4 = profile_only_pipeline.phases[4]
        previous_results = ph.ResultsCollection([results_1, results_2, results_3, results_3h])

        analysis = phase4.make_analysis(image, previous_results)

        assert isinstance(phase4.lens_galaxy, gp.GalaxyPrior)
        assert isinstance(phase4.source_galaxy, gp.GalaxyPrior)

        assert analysis.masked_image == np.ones((716,))

        assert isinstance(phase4.lens_galaxy.hyper_galaxy, g.HyperGalaxy)

        assert phase4.lens_galaxy.hyper_galaxy == results_3h.constant.lens_galaxy.hyper_galaxy
        assert phase4.source_galaxy.hyper_galaxy == results_3h.constant.source_galaxy.hyper_galaxy

        assert phase4.lens_galaxy.elliptical_sersic == results_3.variable.lens_galaxy.elliptical_sersic
        assert phase4.lens_galaxy.sie == results_3.variable.lens_galaxy.sie
        assert phase4.source_galaxy.elliptical_sersic == results_3.variable.source_galaxy.elliptical_sersic