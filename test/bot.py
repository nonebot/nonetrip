import nonebot
from nonebot.adapters.cqhttp import Bot

nonebot.init(debug=True)
nonebot.get_driver().register_adapter('cqhttp', Bot)
nonebot.load_plugin('nonetrip')

import nonetrip

nonetrip.init()
nonetrip.load_builtin_plugins()

nonebot.run(port=2333)
