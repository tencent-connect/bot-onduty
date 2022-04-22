import os

from qqbot.core.util.yaml_util import YamlUtil

config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "../config.yaml"))
