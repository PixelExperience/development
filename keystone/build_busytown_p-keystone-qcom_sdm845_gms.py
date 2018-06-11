"""Builds p-keystone-qcom sdm845 on an Busytown build host.
"""

import build_busytown

build_busytown.build_target('sdm845_gms', 'userdebug')
