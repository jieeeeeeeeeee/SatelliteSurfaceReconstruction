import os
from ssr.utility.os_extension import mkdir_safely
from ssr.utility.logging_extension import logger
from ssr.config.vissat_config import create_vissat_config_from_ssr_config
from ssr.config.ssr_config import SSRConfig


class VisSatPipeline:
    """ A thin wrapper for VisSat's stereo_pipeline """

    def __init__(self, pm):
        self.pm = pm
        self.ssr_config = SSRConfig.get_instance()
        colmap_vissat_exe_fp = self.ssr_config.get_option_value(
            "colmap_vissat_exe_fp", str
        )
        self.colmap_vissat_exe_fp = colmap_vissat_exe_fp
        assert os.path.isfile(colmap_vissat_exe_fp)
        self.colmap_vissat_exe_dp = os.path.dirname(colmap_vissat_exe_fp)

    def run(self, reconstruct_sfm_mvs):
        dataset_dp = self.ssr_config.get_option_value(
            "satellite_image_pan_dp", str
        )
        workspace_dp = self.ssr_config.get_option_value(
            "workspace_vissat_dp", str
        )
        mkdir_safely(workspace_dp)
        create_vissat_config_from_ssr_config(
            vissat_config_ofp=self.pm.vissat_config_fp,
            dataset_dp=dataset_dp,
            workspace_dp=workspace_dp,
            ssr_config=self.ssr_config,
            clean_data=True,
            crop_image=True,
            derive_approx=True,
            choose_subset=True,
            colmap_sfm_perspective=True,
            inspect_sfm_perspective=True,
            reparam_depth=True,
            colmap_mvs=True,
            aggregate_2p5d=False,
            aggregate_3d=True,
        )

        if reconstruct_sfm_mvs:
            logger.vinfo("self.pm.vissat_config_fp", self.pm.vissat_config_fp)

            assert os.path.isdir(self.colmap_vissat_exe_dp)
            os.environ["PATH"] += os.pathsep + self.colmap_vissat_exe_dp

            # see https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/stereo_pipeline.py
            from stereo_pipeline import StereoPipeline as VisSatStereoPipeline

            # https://github.com/Kai-46/VisSatSatelliteStereo
            #   Our pipeline is written in a module way; you can run it step by step
            #   by choosing what steps to execute in the configuration file.
            #       Steps to run
            #           clean_data (see clean_data() in clean_data.py)
            #               creates the folder "cleaned_data"
            #                   copies the NTF-files contained in the input PAN folder
            #                   extracts the xml- and the jpg-files contained in the tar-files in the input PAN folder
            #           crop_image (see image_crop() and image_crop_worker() in image_crop.py)
            #               creates the folder "images"
            #                   uses the bounding box specified in the config-json-file to crop the corresponding area
            #                   of the NTF-files contained in the "cleaned_data" folder
            #           derive_approx
            #           choose_subset
            #           colmap_sfm_perspective
            #           inspect_sfm_perspective
            #           reparam_depth
            #           colmap_mvs
            #           aggregate_2p5d
            #               creates the folder "mvs_results/aggregate_2p5d"
            #                   with a height-colorized point cloud and corresponding images
            #                   and a geo-registered geo-tiff file
            #           aggregate_3d
            #               creates the folder "mvs_results/aggregate_3d"
            #                   with a 3d point cloud and corresponding images
            #                   and a geo-registered geo-tiff file

            pipeline = VisSatStereoPipeline(self.pm.vissat_config_fp)
            # Logs are created in the working_directory/logs folder
            pipeline.run()
