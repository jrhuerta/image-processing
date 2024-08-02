# Astronomical Image Normalization CLI Tool

## Overview

This CLI tool is designed to process and enhance astronomical images using a series of normalization and enhancement adjustments. It is inspired by the PixelMath script "Normalize HOS/HSO/HOO/SHO data with Pixelmath - V8" by Bill Blanshan and Mike Cranfield. The tool uses various image processing techniques to adjust the brightness, contrast, and color balance of astronomical images, making them more visually appealing.

## Features

- **Normalization of Image Channels:** The tool normalizes the different narrowband channels (such as H-alpha, SII, OIII) based on user-defined parameters.
- **Gamma Correction:** Applies gamma correction to the image to ensure proper brightness and contrast when viewed on standard display devices.
- **Color Space Conversion:** Converts images between different color spaces (RGB, XYZ, LAB) for better color manipulation and enhancement.
- **Highlight and Brightness Adjustments:** Provides options to adjust highlights and overall brightness, improving the visibility of faint details.
- **Save Options:** Users can choose to save the processed image as a combined RGB file or save each channel independently.

## Installation

To install this package from PyPI, use the following command:

```bash
pip install astro-image-normalizer
```

## Usage
Once installed, the tool can be used from the command line. Below is the basic usage:

```bash
astro-image-normalizer INPUT_FILE OUTPUT_FILE [OPTIONS]
```

Options
--mode: Data type (0 for linear, 1 for non-linear). Default is 1.
--lightness: Lightness adjustment (0=OFF, 1=Original, 2=Ha, 3=SII, 4=OIII). Default is 0.
--scnr: SCNR (Selective Color Noise Reduction) (0=OFF, 1=On). Default is 0.
--blackpoint: Blackpoint adjustment (0 to 1). Default is 1.00.
--sii_boost: SII boost factor. Default is 1.00.
--oiii_boost: OIII boost factor. Default is 1.00.
--hl_recover: Highlight recovery factor. Default is 1.00.
--hl_reduction: Highlight reduction factor. Default is 1.00.
--brightness: Brightness adjustment factor. Default is 1.00.
--save_channels: Save each channel independently.

Example

To normalize an image and save the combined result:

```bash
nbn my_image.fits normalized_image.fits --mode 1 --brightness 1.2
```

To normalize an image and save each channel independently:

```bash
nbn my_image.fits normalized_image.fits --save_channels
```

## License
This project is licensed under the CC ATTRIBUTION-SHAREALIKE 4.0 INTERNATIONAL. 
See the [LICENSE](https://creativecommons.org/licenses/by-sa/4.0/) file for more details.

