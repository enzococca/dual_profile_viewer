"""
/***************************************************************************
 DualProfileViewer
                                 A QGIS plugin
 Archaeological dual profile analysis with vector export
                             -------------------
        begin                : 2024-01-01
        copyright            : (C) 2024
        email                : your.email@example.com
 ***************************************************************************/
"""

def classFactory(iface):
    """Load DualProfileViewer class from file dual_profile_viewer.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .dual_profile_viewer import DualProfileViewer
    return DualProfileViewer(iface)
