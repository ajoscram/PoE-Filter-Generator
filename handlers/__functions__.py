"""This module includes general purpose functions used by handlers commonly.

This exports:
    hide_section: Function used to hide a section.
    show_section: Function used to show a section.
"""

from classes.section import Section

def hide_section(section: Section):
    """Attempts to completely hide a section by setting it to 'Hide' and commenting out the lines that show effects on the screen if they are present."""
    section.swap("Show", "Hide")
    section.comment("PlayAlertSoundPositional")
    section.comment("MinimapIcon")
    section.comment("PlayEffect")

def show_section(section: Section):
    """Attempts to show a section fully, by setting it to 'Show' and un-commenting out the lines that show effects on the screen if they are present. This is the reverse function to hide_section."""
    section.swap("Hide", "Show")
    section.uncomment("PlayAlertSoundPositional")
    section.uncomment("MinimapIcon")
    section.uncomment("PlayEffect")