from classes.section import Section

def hide_section(section: Section):
    """Attempts to completely hide a section by setting it to 'Hide' and commenting out the lines that show effects on the screen if they are present."""
    section.swap("Show", "Hide")
    section.comment("PlayAlertSoundPositional")
    section.comment("MinimapIcon")
    section.comment("PlayEffect")

def show_section(section: Section):
    """Does the inverse of the function 'hide_section'."""
    section.swap("Hide", "Show")
    section.uncomment("PlayAlertSoundPositional")
    section.uncomment("MinimapIcon")
    section.uncomment("PlayEffect")