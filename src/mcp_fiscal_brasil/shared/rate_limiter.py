"""Rate limiter de janela deslizante por endpoint."""

import asyncio
import time
from collections import defaultdict, deque

from .exceptions import RateLimitError


class SlidingWindowRateLimiter:
    """
    Implementa um rate limiter de janela deslizante por chave (ex: endpoint).

    Permite configurar N requisicoes por janela de tempo (em segundos).
    Thread-safe via asyncio.Lock.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: dict[str, deque[float]] = defaultdict(deque)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def acquire(self, key: str) -> None:
        """
        Tenta adquirir um slot para a chave informada.

        Levanta RateLimitError se o limite for excedido.
        """
        async with self._locks[key]:
            now = time.monotonic()
            window_start = now - self.window_seconds
            timestamps = self._timestamps[key]

            # Remove requisicoes fora da janela atual
            while timestamps and timestamps[0] < window_start:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                # Calcula quanto tempo falta para liberar um slot
                oldest = timestamps[0]
                retry_after = self.window_seconds - (now - oldest)
                raise RateLimitError(endpoint=key, retry_after=retry_after)

            timestamps.append(now)

    def remaining(self, key: str) -> int:
        """Retorna quantas requisicoes ainda podem ser feitas na janela atual."""
        now = time.monotonic()
        window_start = now - self.window_seconds
        timestamps = self._timestamps[key]
        active = sum(1 for t in timestamps if t >= window_start)
        return max(0, self.max_requests - active)

    def reset(self, key: str) -> None:
        """Limpa o historico de uma chave (util para testes)."""
        self._timestamps[key].clear()


# Limiters pre-configurados para as principais APIs

# Receita Federal / BrasilAPI: conservador para nao ser bloqueado
receita_limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60.0)

# BrasilAPI: documentado em 3 req/s por IP
brasil_api_limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=1.0)

# SEFAZ: muito conservador, servico governamental sensivel
sefaz_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60.0)

# APIs de NFSe (variam por prefeitura, usar limite padrao)
nfse_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10.0)
