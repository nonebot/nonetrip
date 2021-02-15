from nonetrip import CommandSession, on_command
from nonetrip import permission as perm
from nonetrip.message import unescape


@on_command('echo')
async def echo(session: CommandSession):
    await session.send(session.state.get('message') or session.current_arg)


@on_command('say', permission=perm.SUPERUSER)
async def say(session: CommandSession):
    await session.send(
        unescape(session.state.get('message') or session.current_arg))
