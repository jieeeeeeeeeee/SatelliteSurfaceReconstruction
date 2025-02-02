import os
import subprocess
from ssr.utility.logging_extension import logger
from ssr.utility.os_extension import get_corresponding_files_in_directories
from ssr.utility.os_extension import mkdir_safely
from ssr.gdal_utility.run_gdal import run_gdal_cmd

def perform_pan_sharpening(
    pan_ifp, msi_ifp, ofp, resampling_algorithm="cubic"
):
    # https://gdal.org/programs/gdal_pansharpen.html
    # https://gis.stackexchange.com/questions/270476/pansharpening-using-gdal-tools
    #   GDAL pan sharpening algorithm = weighted Brovey algorithm

    ext = os.path.splitext(ofp)[1]
    of = ext[1:]

    call_params = ["python C:/Users/Administrator/anaconda3/envs/colmap_sat/Lib/site-packages/osgeo/scripts/gdal_pansharpen.py"]
    call_params += ["-of", of, "-r", resampling_algorithm]

    call_params += [pan_ifp, msi_ifp, ofp]
    logger.vinfo("call_params", call_params)
    # for windows
    call_params = ' '.join(call_params)
    print(call_params)
    run_gdal_cmd(call_params)
    #sharp_process = subprocess.Popen(call_params)
   # sharp_process.wait()


def perform_pan_sharpening_for_folder(
    pan_idp, msi_idp, odp, resampling_algorithm="cubic"
):

    # The created files are using the PAN (AND NOT THE MSI) STEM (i.e. P1BS
    # instead of M1BS) so they can directly be used to replace the original
    # PAN images
    mkdir_safely(odp)

    def get_correspondence_callback(pan_fn):
        # PAN example name: 0001_WV03_15JAN05_135727-P1BS-500497282040_01_P001.png
        # MSI example name: 0001_WV03_15JAN05_135727-M1BS-500497282040_01_P001.png

        pan_parts = pan_fn.split("-P1BS-", 1)
        msi_fn = pan_parts[0] + "-M1BS-" + pan_parts[1]
        return msi_fn

    pan_list, msi_list = get_corresponding_files_in_directories(
        pan_idp,
        msi_idp,
        get_correspondence_callback=get_correspondence_callback,
    )

    for pan_ifp, msi_ifp in zip(pan_list, msi_list):
        msi_sharpened_ofp = os.path.join(odp, os.path.basename(pan_ifp))
        perform_pan_sharpening(
            pan_ifp,
            msi_ifp,
            msi_sharpened_ofp,
            resampling_algorithm=resampling_algorithm,
        )


if __name__ == "__main__":

    # ========================= Single File =======================
    # pan_ifp = '/path/to/0001_WV03_15JAN05_135727-P1BS-500497282040_01_P001_PAN.png'
    # msi_ifp = '/path/to/0001_WV03_15JAN05_135727-M1BS-500497282040_01_P001_MSI.png'
    # ofp = 'path/to/0001_WV03_15JAN05_135727-P1BS-500497282040_01_P001_SHARPENED.png'
    #
    # perform_pan_sharpening(
    #     pan_ifp,
    #     msi_ifp,
    #     ofp,
    #     resampling_algorithm='cubic')

    # ========================= Single File =======================
    #pan_idp = "/path/to/pan"
    #msi_idp = "/path/to/msi"
    #odp = "path/to/pansharped"
#
    #perform_pan_sharpening_for_folder(
    #    pan_idp, msi_idp, odp, resampling_algorithm="cubic"
    #)


    # ========================= Single File =======================
    pan_ifp = r"D:\experiment\site1-5-13\ssr\pan\images\0000_WV03_15APR02_134716-P1BS-500276959010_02_P001.png"
    msi_ifp = r'D:\experiment\site1-5-13\ssr\msi\images\0000_WV03_15APR02_134716-M1BS-500276959010_02_P001.png'
    ofp = r'D:\experiment\site1-5-13\ssr\sharpened_with_skew/a.png'
    perform_pan_sharpening(
        pan_ifp,
        msi_ifp,
        ofp,
        resampling_algorithm='cubic')
