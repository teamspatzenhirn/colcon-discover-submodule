import subprocess

from colcon_core.logging import colcon_logger
from colcon_core.package_discovery import PackageDiscoveryExtensionPoint
from colcon_core.plugin_system import satisfies_version

logger = colcon_logger.getChild(__name__)


def is_in_git_repo():
    result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0 or not result.stdout.decode("utf-8").startswith("true"):
        return False
    return True


class SubmoduleDiscovery(PackageDiscoveryExtensionPoint):
    PRIORITY = 120  # Run before recursive crawl

    def __init__(self):
        super().__init__()
        satisfies_version(PackageDiscoveryExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def has_default(self):
        return False

    def has_parameters(self, *, args):
        return False

    def discover(self, *, args, identification_extensions):
        if not is_in_git_repo():
            logger.warn("Not inside a git repo!")
            return set()

        result = subprocess.run(["git", "submodule", "update", "--init", "--recursive"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            errormessage = "Error when running git.\n" + \
                           "Stdout:\n" + result.stdout.decode("utf-8") + \
                           "\nStderr:\n" + result.stderr.decode("utf-8")
            raise Exception(errormessage)
        logger.info("Updated submodules.")
        return set()
