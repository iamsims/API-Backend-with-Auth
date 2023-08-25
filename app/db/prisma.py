from prisma import Prisma
from .config import DatabaseConfig
prisma = Prisma(
    datasource={
        'url': DatabaseConfig.url,
    },
)