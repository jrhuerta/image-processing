import click
import numpy as np
from astropy.io import fits


# Function for gamma correction
# Gamma correction compensates for the non-linear way in which humans perceive brightness.
# It converts the image from linear to non-linear representation (sRGB), making it suitable for display.
def gamma_correction(channel):
    return np.where(
        channel > 0.04045, ((channel + 0.055) / 1.055) ** 2.4, channel / 12.92
    )


# Function to convert XYZ to LAB color space
# This transformation is used to enhance and manipulate the image based on human perception of colors.
def f(t):
    return np.where(t > 0.008856, t ** (1 / 3), (7.787 * t) + (16 / 116))


# Inverse function to convert LAB back to XYZ
# This reverses the previous transformation, preparing the image for final output.
def inv_f(t):
    return np.where(t > 0.008856, t**3, (t - 16 / 116) / 7.787)


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--mode",
    default=1,
    type=int,
    help="Data type: 0=linear, 1=non-linear",
    show_default=True,
)
@click.option(
    "--lightness",
    default=0,
    type=int,
    help="Lightness adjustment: 0=OFF, 1=Original, 2=Ha, 3=SII, 4=OIII",
    show_default=True,
)
@click.option(
    "--scnr", default=0, type=int, help="SCNR: 0=OFF, 1=On", show_default=True
)
@click.option(
    "--blackpoint",
    default=1.00,
    type=float,
    help="Blackpoint adjustment (0 to 1)",
    show_default=True,
)
@click.option(
    "--sii_boost", default=1.00, type=float, help="SII boost factor", show_default=True
)
@click.option(
    "--oiii_boost",
    default=1.00,
    type=float,
    help="OIII boost factor",
    show_default=True,
)
@click.option(
    "--hl_recover",
    default=1.00,
    type=float,
    help="Highlight recovery factor",
    show_default=True,
)
@click.option(
    "--hl_reduction",
    default=1.00,
    type=float,
    help="Highlight reduction factor",
    show_default=True,
)
@click.option(
    "--brightness",
    default=1.00,
    type=float,
    help="Brightness adjustment factor",
    show_default=True,
)
@click.option("--save_channels", is_flag=True, help="Save each channel independently")
def process_image(
    input_file,
    output_file,
    mode,
    lightness,
    scnr,
    blackpoint,
    sii_boost,
    oiii_boost,
    hl_recover,
    hl_reduction,
    brightness,
    save_channels,
):
    """Process an astronomical image with normalization and enhancement adjustments."""
    # Load the image data from a FITS file
    with fits.open(input_file) as hdul:
        image_data = hdul[0].data

    # Basic Image Statistics Calculation
    # Compute minimum and median values to determine the blackpoint level.
    min_value = np.min(image_data)
    median_value = np.median(image_data)
    # Calculate M, a baseline for normalization, using the blackpoint adjustment.
    m = min_value + blackpoint * (median_value - min_value)
    # Calculate E0, which involves the absolute deviation (MAD) converted to an approximate standard deviation.
    # The constant 1.2533 converts MAD to standard deviation for a normal distribution.
    adev_value = np.mean(np.abs(image_data - np.mean(image_data)))
    e0 = adev_value / 1.2533 + np.mean(image_data) - m

    # Channel Normalization
    # Normalize SII and OIII channels based on the calculated values and boost factors.
    a0 = e0 / m
    e1 = (a0[1] * (1 - a0[0]) / (a0[1] - 2 * a0[1] * a0[0] + a0[0])) / oiii_boost
    e2 = np.clip((image_data[1] - m) / (1 - m), 0, 1)
    e3 = 1 - ((1 - e1) * (1 - e2) * (1 - np.minimum(image_data[1], m)))

    a1 = e0 / m
    e4 = (a0[2] * (1 - a0[0]) / (a0[2] - 2 * a0[2] * a0[0] + a0[0])) / sii_boost
    e5 = np.clip((image_data[2] - m) / (1 - m), 0, 1)
    e6 = 1 - ((1 - e1) * (1 - e5) * (1 - np.minimum(image_data[2], m)))

    # Assign the normalized channels to RGB variables.
    # Apply SCNR (Selective Color Noise Reduction) if specified.
    r = image_data[0]
    g = np.where(scnr == 0, e3, np.minimum(np.mean([image_data[0], e6]), e3))
    b = e6

    # Gamma Correction (sRGB)
    # Apply gamma correction to convert from linear to sRGB space for accurate display.
    r1 = gamma_correction(r)
    g1 = gamma_correction(g)
    b1 = gamma_correction(b)

    # Convert RGB to XYZ color space, a standard color space used for accurate color representation.
    x = r1 * 0.4360747 + g1 * 0.3850649 + b1 * 0.1430804
    y = r1 * 0.2225045 + g1 * 0.7168786 + b1 * 0.0606169
    z = r1 * 0.0139322 + g1 * 0.0971045 + b1 * 0.7141733

    # Convert XYZ to LAB color space, which is perceptually uniform and useful for color manipulation.
    x1 = f(x)
    y1 = f(y)
    z1 = f(z)

    # Calculate the LAB values
    l = 116 * y1 - 16
    a = 500 * (x1 - y1)
    b = 200 * (y1 - z1)

    # Apply lightness correction based on user selection
    y2 = np.where(
        lightness == 0,
        (l + 16) / 116,
        np.where(
            lightness == 1,
            (CIEL(image_data) + 0.16) / 1.16,
            np.where(
                lightness == 2,
                (image_data[0] + 0.16) / 1.16,
                np.where(
                    lightness == 3,
                    (image_data[2] + 0.16) / 1.16,
                    (image_data[1] + 0.16) / 1.16,
                ),
            ),
        ),
    )

    # Convert LAB back to XYZ
    x2 = (a / 500) + y2
    z2 = y2 - (b / 200)

    # Convert XYZ back to RGB
    x3 = inv_f(x2)
    y3 = inv_f(y2)
    z3 = inv_f(z2)

    r2 = (x3 * 3.1338561) + (y3 * -1.6168667) + (z3 * -0.4906146)
    g2 = (x3 * -0.9787684) + (y3 * 1.9161415) + (z3 * 0.0334540)
    b2 = (x3 * 0.0719453) + (y3 * -0.2289914) + (z3 * 1.4052427)

    # Apply gamma correction for display purposes
    r3 = np.where(r2 > 0.0031308, 1.055 * (r2 ** (1 / 2.4)) - 0.055, 12.92 * r2)
    g3 = np.where(g2 > 0.0031308, 1.055 * (g2 ** (1 / 2.4)) - 0.055, 12.92 * g2)
    b3 = np.where(b2 > 0.0031308, 1.055 * (b2 ** (1 / 2.4)) - 0.055, 12.92 * b2)

    # Final RGB composition based on mode (linear or non-linear)
    e10 = np.where(
        mode == 0,
        np.where(
            image_data == image_data[0], r, np.where(image_data == image_data[1], g, b)
        ),
        np.where(
            image_data == image_data[0],
            r3,
            np.where(image_data == image_data[1], g3, b3),
        ),
    )

    # Highlight Reduction and Brightness Adjustment
    # Apply highlight reduction and brightness adjustment to enhance image details.
    e11 = (1 - (1 / hl_reduction * 0.5)) * e10 * e10 + e10 * (1 - e10)
    e12 = (1 / brightness * 0.5) * e11
    e13 = np.clip(e12, 0, hl_recover)

    # Save the output
    if save_channels:
        # Save each channel independently
        fits.writeto(output_file.replace(".fits", "_r.fits"), r3, overwrite=True)
        fits.writeto(output_file.replace(".fits", "_g.fits"), g3, overwrite=True)
        fits.writeto(output_file.replace(".fits", "_b.fits"), b3, overwrite=True)
    else:
        # Combine channels and save
        combined_image = np.stack([r3, g3, b3], axis=-1)
        fits.writeto(output_file, combined_image, overwrite=True)


if __name__ == "__main__":
    process_image()
