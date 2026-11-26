from elements.input import Input


class Textarea(Input):
    # MUI renders a second, aria-hidden textarea for autosizing.
    control_selector = 'textarea:not([aria-hidden="true"])'
