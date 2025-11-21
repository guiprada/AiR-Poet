# table_scheme/environment.py
class Environment:
    """A class to manage variable bindings and function definitions."""

    def __init__(self, outer=None):
        """
        Initialize an environment.

        Parameters
        ----------
        outer : Environment, optional
            The outer (enclosing) environment. If None, this is a global environment.
        """
        self.bindings = {}
        self.outer = outer

    def define(self, name, value):
        """
        Define a variable in this environment.

        Parameters
        ----------
        name : str
            The variable name.
        value : Any
            The value to bind.
        """
        self.bindings[name] = value

    def get(self, name):
        """
        Get a value by name, searching up the environment chain.

        Parameters
        ----------
        name : str
            The variable name to look up.

        Returns
        -------
        Any
            The value bound to the name.

        Raises
        ------
        NameError
            If the name is not found in any environment.
        """
        if name in self.bindings:
            return self.bindings[name]
        if self.outer is not None:
            return self.outer.get(name)
        raise NameError(f"Undefined variable: {name}")

    def set(self, name, value):
        """
        Set a value for a name, either in this environment or the outer one.

        Parameters
        ----------
        name : str
            The variable name.
        value : Any
            The value to set.
        """
        if name in self.bindings:
            self.bindings[name] = value
        elif self.outer is not None:
            self.outer.set(name, value)
        else:
            raise NameError(f"Cannot set undefined variable: {name}")

    def __repr__(self):
        """String representation of the environment."""
        return f"Environment(bindings={self.bindings}, outer={self.outer is not None})"