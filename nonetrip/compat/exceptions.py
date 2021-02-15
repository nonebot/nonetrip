from nonebot.exception import ActionFailed as BaseActionFailed
from nonebot.exception import ApiNotAvailable as BaseApiNotAvailable


class NoneTripException(Exception):
    pass


class ActionFailed(BaseActionFailed, NoneTripException):
    pass


class ApiNotAvailable(BaseApiNotAvailable, NoneTripException):
    pass


class NoneTripCompException(NoneTripException):
    pass
