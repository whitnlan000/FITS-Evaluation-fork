from math import exp

import numpy as np
from astropy.io import fits
from astropy.stats import median_absolute_deviation, sigma_clipped_stats
from astropy.table import Table
from photutils.detection import DAOStarFinder, IRAFStarFinder
import pandas as pd

def analyze_fits(file_path, is_stack=False, single_frame_noise=None):
    # Load the FITS file
    with fits.open(file_path) as hdul:
        data = hdul[0].data.astype(float)

        header = fits.getheader(file_path)
        object_name = ""
        gain = ""
        rotation = ""
        telescope = ""
        exposure = ""
        focal_length = ""
        date = header["DATE-OBS"]
        software = ""
        total_images = ""

    if data.ndim == 3:
        if data.shape[0] == 3:
            # It's an RGB stacked FITS file; select just one channel (e.g., Green) for star finding
            data = data[1, :, :] 
            object_name = 'Stacked'            
        else:
            # It's a mono frame with a phantom 3rd dimension (e.g., shape is (1, Y, X))
            data = data.squeeze()
    if not is_stack:
        object_name = header["OBJECT"]
       # gain = header["GAIN"]
      #  rotation = header["ROTATOR"]
        telescope = header["TELESCOP"]
        exposure = header["EXPOSURE"]
        focal_length = header["FOCALLEN"]
        
    else:
        object_name = 'Stacked'
        exposure = header["EXPTIME"] / 3600
      #  software = header["SOFTWARE"]

        # if "ncombine" in header:
        #     total_images = header["ncombine"]
        # else: 
        #     total_images = header["stackcnt"]
    
    # 1. Advanced Background & Noise Estimation
    # Sigma clipping removes stars so we only measure the true sky background
    mean, median, std_dev = sigma_clipped_stats(data, sigma=3.0)
    robust_noise = median_absolute_deviation(data)
    
    # 2. Extract Signal (Target minus Background)
    true_signal = data - median
    top_signal = np.median(true_signal[true_signal > np.percentile(true_signal, 95)])
    
    # 3. Calculate Math SNR
    snr = top_signal / robust_noise
    
    # 4. Star Detection & FWHM (Focus/Seeing Estimate)
    # Detect stars that are at least 5 standard deviations above the noise
    daofind = DAOStarFinder(fwhm=4.0, threshold=5.0 * std_dev)
    sources = daofind(data - median)
    iraffind = IRAFStarFinder(fwhm=4.0, threshold=5.0 * std_dev)
    sources = iraffind(data - median)

    star_count = len(sources) if sources is not None else 0

    # IRAFStarFinder natively returns a 'fwhm' column in pixels
    if star_count > 0:
        avg_fwhm = np.median(sources['fwhm'])
    else:
        avg_fwhm = 0
    
    #Print Results
    out = []

    print(f"--- Analysis for: {file_path} ---\n")
    out.append(f"--- Analysis for: {file_path} ---\n")

    print(f"--- HEADER INFO ---")
    out.append(f"--- HEADER INFO ---")

    print(f"Object Name: {object_name}")
    out.append(f"Object Name: {object_name}")

    print(f"Date: {date}")
    out.append(f"Date: {date}")

    if not is_stack:
        print(f"Camera Gain: {gain}")
        print(f"Rotation: {rotation}")
        print(f"Telescope: {telescope}")
        print(f"Exposure: {exposure} seconds")
        print(f"Focal Length: {focal_length}mm \n")

        out.append(f"Camera Gain: {gain}")
        out.append(f"Rotation: {rotation}")
        out.append(f"Telescope: {telescope}")
        out.append(f"Exposure: {exposure} seconds")
        out.append(f"Focal Length: {focal_length}mm \n")

    else:
        print(f"Exposure: {exposure} hours")
        print(f"Software: {software}")
        print(f"# Images In Stack: {total_images}\n")

        out.append(f"Exposure: {exposure} hours")
        out.append(f"Software: {software}")
        out.append(f"# Images In Stack: {total_images}\n")

    print(f"--- IMAGE SPECS ---")
    print(f"Calculated SNR:        {snr:.2f}")
    print(f"Background Sky Level:  {median:.1f} ADU")
    print(f"Background Noise (σ):  {robust_noise:.2f} ADU")
    print(f"Detected Stars:        {star_count}")

    out.append(f"--- IMAGE SPECS ---")
    out.append(f"Calculated SNR:        {snr:.2f}")
    out.append(f"Background Sky Level:  {median:.1f} ADU")
    out.append(f"Background Noise:  {robust_noise:.2f} ADU")
    out.append(f"Detected Stars:    {star_count}")


    if star_count > 0:
        print(f"Average Star FWHM:     {avg_fwhm:.2f} pixels")
        out.append(f"Average Star FWHM:   {avg_fwhm:.2f} pixels")

    # 5. Calculate SNR Gain if comparing a stack to a single sub
    if is_stack and single_frame_noise:
        noise_reduction = single_frame_noise / robust_noise
        theoretical_frames = noise_reduction ** 2
        print(f"Stacking Efficiency:   Noise reduced by {noise_reduction:.1f} (Equivalent to stacking ~{int(theoretical_frames)} perfect frames)")
        out.append(f"Stacking Efficiency: {noise_reduction:.1f} pixels")

    print("-" * 40)
    print ("\n")

    out.append("-" * 40)
    out.append("\n")
    
    return robust_noise,out

# --- How to use it ---
# 1. Run your single frame first to grab its noise floor
# single_noise = analyze_fits('single_sub.fits')

# 2. Run the stack and pass the single frame's noise to see the efficiency gain
# analyze_fits('final_stack.fits', is_stack=True, single_frame_noise=single_noise)
