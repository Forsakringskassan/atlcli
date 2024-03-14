#!python
"""
This module contains the class Version, used to represent semantic versions.
"""


class Version:
    """Used to compare names in a semantic version aware fashion.

    The constructor splits the input parameter into parts using full stop (.) as separator. If the value has any
    full stops in it, it is considered a semantic version.
    """
    def __init__(self, value):
        """Constructor.
        Parameters
        ----------
        value : str
            Any string which may contain a semantic version.
        """
        # print("{}.__init__({})".format(os.path.basename(__file__), value))
        self.value = value
        self.values = value.split('.')
        # for v in self.values:
        #    print("{}.__init__() v={}".format(os.path.basename(__file__), v))

    def __eq__(self, other):
        """Operator function equals.

        If both self and other are not semantic versions, an ordinary string comparison is performed.

        I self or other is a semantic version, comparision is done using semantic version rules.
        Parameters
        ----------
        other : Version
            The other version object to compare to
        Returns
        -------
        bool
            True if self is equal to other
        """
        # print('__eq__')
        self_len = len(self.values)
        other_len = len(other.values)
        # Special case when not a semantic version
        if self_len == 1 and other_len == 1:
            return self.value == other.value
        for i in range(0, min(self_len, other_len)):
            self_value = self.values[i]
            other_value = other.values[i]
            if self_value == other_value:
                continue
            if len(self_value) != len(other_value):
                return False
            if self_value != other_value:
                return False
        return self_len == other_len

    def __gt__(self, other):
        """Operator function greater than.

        If both self and other are not semantic versions, an ordinary string comparison is performed.

        I self or other is a semantic version, comparision is done using semantic version rules.
        Parameters
        ----------
        other : Version
            The other version object to compare to
        Returns
        -------
        bool
            True if self is larger than other
        """
        # print('__gt__')
        self_len = len(self.values)
        other_len = len(other.values)
        # Special case when not a semantic version
        if self_len == 1 and other_len == 1:
            return self.value > other.value
        for i in range(0, min(self_len, other_len)):
            self_value = self.values[i]
            other_value = other.values[i]
            if self_value == other_value:
                continue
            if len(self_value) > len(other_value):
                return True
            elif len(other_value) > len(self_value):
                return False
            return self_value > other_value
        return self_len > other_len

    def __str__(self):
        """Gets string represenatation
        Returns
        -------
        str
            The string represenation of the Version object
        """
        return self.value


if __name__ == "__main__":
    print("Testing Version.py")
    v1 = Version('kalle')
    v2 = Version('olle')
    assert(v2 > v1)
    assert(not(v1 > v2))
    assert(not(v1 > v1))
    assert(v1 == v1)
    assert(not(v1 == v2))
    assert(not(v2 == v1))
    v1_str = str(v1)
    # print(v1_str)
    assert(v1_str == 'kalle')
    v1 = Version('v1.2.1')
    v2 = Version('v1.12.1')
    assert(v1 == v1)
    assert(not(v1 == v2))
    assert(not(v2 == v1))
    assert(v2 > v1)
    assert(not(v1 > v2))
    assert(not(v1 > v1))
    v2 = Version('v1.2.1.1')
    assert(v2 > v1)
    assert(not(v1 > v2))
    assert(not(v1 > v1))
    assert(v1 == v1)
    assert(not(v1 == v2))
    assert(not(v2 == v1))
    # print("Testing Version.py ok")
