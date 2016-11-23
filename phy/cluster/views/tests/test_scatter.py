# -*- coding: utf-8 -*-

"""Test scatter view."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import numpy as np

from phy.gui import GUI
from phy.utils import Bunch
from ..scatter import ScatterView


#------------------------------------------------------------------------------
# Test scatter view
#------------------------------------------------------------------------------

def test_scatter_view(qtbot):
    n = 1000
    v = ScatterView(coords=lambda c: Bunch(x=np.random.randn(n),
                                           y=np.random.randn(n),
                                           spike_ids=np.arange(n),
                                           )
                    # data_bounds=[-3, -3, 3, 3],
                    )
    gui = GUI()
    gui.show()
    v.attach(gui)

    # qtbot.waitForWindowShown(gui)

    v.on_select([])
    v.on_select([0])
    v.on_select([0, 2, 3])
    v.on_select([0, 2])

    # qtbot.stop()
    gui.close()
