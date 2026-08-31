from functools import wraps

from sqlalchemy import text


def async_transaction(read_only: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            async with self.uow:
                if self.uow.session.in_transaction():
                    return await func(self, *args, **kwargs)
                async with self.uow.session.begin():
                    if read_only:
                        await self.uow.session.execute(
                            text("SET TRANSACTION READ ONLY")
                        )

                    return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def sync_transaction(read_only: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.uow, self.uow.session.begin():
                if read_only:
                    self.uow.session.execute(text("SET TRANSACTION READ ONLY"))

                return func(self, *args, **kwargs)

        return wrapper

    return decorator
