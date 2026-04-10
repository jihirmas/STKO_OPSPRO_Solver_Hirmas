class CAEComponentGroupUIDs:
    """
    This class contains the UIDs of the component groups in the application.
    These UIDs are used to identify the component groups in the application,
    so that they can be easily referenced throughout the code without hardcoding strings everywhere.
    """
    SETTINGS = '000-settings'
    USER_NOTES = '001-user-notes'
    MATERIALS = '002-materials'
    SECTIONS = '003-sections'
    BEAM_HINGES = '004-beam-hinges'
    # Internal groups are always last (lexicographic sort by UID used during
    # deserialization, so '999-...' is guaranteed to be restored after all
    # user-visible groups).
    INTERNAL = '999-internal'