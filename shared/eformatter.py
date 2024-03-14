from argparse import ArgumentDefaultsHelpFormatter


class Formatter(ArgumentDefaultsHelpFormatter):
    """
    https://stackoverflow.com/questions/12151306/argparse-way-to-include-default-values-in-help
    """

    def __init__(self, prog):
        """ Constructor.
        https://stackoverflow.com/questions/32888815/max-help-position-is-not-works-in-python-argparse-library

        :param prog: The name of the program
        """
        super(ArgumentDefaultsHelpFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _get_help_string(self, action):
        """ See linked code on stackoverflow.

        :param action:
        :return:
        """
        if action.default in (None, False):
            return action.help
        return super()._get_help_string(action)