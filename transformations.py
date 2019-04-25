from larch import Interpreter
from larch_plugins.xafs import pre_edge, pre_edge_baseline, fluo_corr

import constants

larchInstance = Interpreter()


def calculate_pre_edge(lineSet):
    data = lineSet.get_data()

    pre_edge(data,
             group=data,
             pre1=constants.Fe.pre1,
             pre2=constants.Fe.pre2,
             norm1=constants.Fe.norm1,
             norm2=constants.Fe.norm2,
             _larch=larchInstance)
    return


def fe_calculate_mu(lineSet):
    data = lineSet.get_data()

    data.mu = (data.fe_ka1 + data.fe_ka2 + data.fe_ka3 + data.fe_ka4) / data.i0
    return


def fe_calculate_abs_corr(lineSet):
    data = lineSet.get_data()

    if data.mu is None:
        fe_calculate_mu(lineSet)

    fluo_corr(energy=data.energy,
              mu=data.mu,
              group=data,
              elem=constants.Fe.fe,
              formula=lineSet.get_formula(),
              _larch=larchInstance)
    return
