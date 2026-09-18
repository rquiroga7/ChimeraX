# vim: set expandtab ts=4 sw=4:

# === UCSF ChimeraX Copyright ===
# Copyright 2025 Regents of the University of California. All rights reserved.
# The ChimeraX application is provided pursuant to the ChimeraX license
# agreement, which covers academic and commercial uses. For more details, see
# <https://www.rbvi.ucsf.edu/chimerax/docs/licensing.html>
#
# You can also
# redistribute and/or modify it under the terms of the GNU Lesser General
# Public License version 2.1 as published by the Free Software Foundation.
# For more details, see
# <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>
#
# THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER
# EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE. ADDITIONAL LIABILITY
# LIMITATIONS ARE DESCRIBED IN THE GNU LESSER GENERAL PUBLIC LICENSE
# VERSION 2.1
#
# This notice must be embedded in or attached to all copies, including partial
# copies, of the software or any revisions or derivations thereof.
# === UCSF ChimeraX Copyright ===

# Reader for Vinardock (2Vinardo) docking output.  The geometry is in the same
# PDBQT/PDBT layout, so parsing is delegated to the AutoDock PDBQT reader; this
# module only adds the Vinardock energy/RMSD metadata that the ViewDock tool
# displays.  Vinardock writes them per pose as:
#   REMARK 980   NORMALIZED BINDING FREE ENERGY : -11.111 KCAL/MOL
#   REMARK 990      RMSD FROM INIT :   0.000 ANGSTROM

from chimerax.viewdock import RATING_KEY, DEFAULT_RATING


def open_vinardock(session, path, file_name, auto_style, atomic):
    from .pdbqt import open_pdbqt
    structures, status = open_pdbqt(session, path, file_name, auto_style, atomic)
    _extract_metadata(session, path, structures)
    return structures, status


def _extract_metadata(session, path, structures):
    from chimerax.atomic import Structure as SC
    from chimerax.io import open_input
    model_index = -1
    values = None
    with open_input(path, encoding='utf-8') as f:
        for line in f:
            record_type = line[:6]
            if record_type == "MODEL ":
                model_index += 1
                values = {RATING_KEY: DEFAULT_RATING}
            elif record_type == "REMARK" and values is not None:
                remark_num = line[7:10].strip()
                text = line.split(":", 1)[1].split() if ":" in line else []
                if remark_num == "980" and text:
                    values["Score"] = text[0]
                elif remark_num == "990" and text:
                    values["RMSD"] = text[0]
            elif record_type == "ENDMDL":
                if values and 0 <= model_index < len(structures):
                    SC.register_attr(session, "viewdock_data", "ViewDock")
                    structures[model_index].viewdock_data = values
                values = None
    return structures
