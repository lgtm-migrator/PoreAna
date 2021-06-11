################################################################################
# Adsorption                                                                   #
#                                                                              #
"""Analyse adsorption in a pore."""
################################################################################


import numpy as np

import poreana.utils as utils


def calculate(link_data, res_cutoff=1, is_normalize=True):
    """This function calculates the values for the adsorption isotherms. This is
    done by counting the number of molecules inside the reservoir and within the
    pore over the whole simulation.

    By normalizing the summation by the number of frames, the resulting value
    is converted to a surface specific concentration inside the pore and volume
    specific concentration within the reservoir.

    The resulting value pair is a point in the adsorption isotherm.

    Parameters
    ----------
    link_data : string
        Link to data object generated by the density sample routine
        :func:`poreana.sample.Sample.init_density`
    res_cutoff : float, optional
        Area of the reservoir to remove from counting on both sides of the
        reservoir
    is_normalize : bool, optional
        True to normalize the number of atoms with the number of frames

    Returns
    -------
    adsorption : dictionary
        Normalized number of molecules outside and insidem and value pair of a
        point on the adsorption isotherm
        :math:`\\left[\\frac{\\text{mmol}}{\\text{l}}\\ ,\\frac{\\mu\\text{mol}}{\\text{m}^2}\\right]`
    """
    # Load data object
    sample = utils.load(link_data)

    # Load pore properties
    pore = sample["pore"]
    res = pore["res"]
    diam = pore["diam"]
    box = pore["box"]
    box[2] -= 2*res

    # Load bins
    bins = {}
    bins["in"] = sample["data"]["in"]
    bins["ex"] = sample["data"]["ex"]

    # Load Width
    width = {}
    width["in"] = sample["data"]["in_width"]
    width["ex"] = sample["data"]["ex_width"]

    # Load input data
    inp = sample["inp"]
    num_frames = inp["num_frame"]
    entry = inp["entry"]

    # Calculate number of molecules
    num = {}
    num["in"] = sum(bins["in"])
    num["ex"] = sum([num_mol for i, num_mol in enumerate(bins["ex"]) if width["ex"][i] <= res-res_cutoff and width["ex"][i] >= res_cutoff])

    # Normalize number of instances by the number of frames
    num["in"] /= num_frames if is_normalize else 1
    num["ex"] /= num_frames if is_normalize else 1

    # Calculate surface and volume
    surface = 2*np.pi*(diam)/2*(box[2]-2*entry)
    volume = 2*(res-2*res_cutoff)*box[0]*box[1]

    # Convert to concentrations
    conc = {}
    conc["mumol_m2"] = utils.mols_to_mumol_m2(num["in"], surface)
    conc["mmol_l"] = utils.mols_to_mmol_l(num["ex"], volume)

    return {"conc": conc, "num": num}
