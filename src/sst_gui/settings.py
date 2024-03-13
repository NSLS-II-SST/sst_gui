import IPython
from os.path import join


def get_ipython_startup_dir(profile_name="default", ipython_dir=None):
    """
    Get the directory of an IPython profile.

    Parameters
    ----------
    profile_name : str, optional
        The name of the IPython profile. Defaults to 'default'.

    Returns
    -------
    str
        The path to the specified IPython profile startup directory.
    """
    # Load the IPython application to access its configuration
    if ipython_dir is not None:
        return join(ipython_dir, f"profile_{profile_name}", "startup")

    ipython_app = IPython.get_ipython()
    if ipython_app is None:
        # If called outside of an IPython environment, create an application instance
        ipython_app = IPython.Application.instance()
    ipython_app.initialize(argv=[])

    # Access the profile directory through the application's configuration
    startup_dir = join(
        ipython_app.profile_dir.location, f"profile_{profile_name}", "startup"
    )

    return startup_dir


class Settings:
    http_server_uri = None
    http_server_api_key = None
    zmq_re_manager_control_addr = None
    zmq_re_manager_info_addr = None
    object_config = None
    gui_config = None


SETTINGS = Settings()
