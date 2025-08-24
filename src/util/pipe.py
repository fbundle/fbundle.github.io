from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator

import multiprocess as mp

Map = Callable[[Any], Any]


class Value:
    def __init__(self, x: Any):
        self.x = x

    def __rshift__(self, m: Map) -> Value:
        return self.apply(m=m)

    def apply(self, m: Map) -> Value:
        return Value(x=m(self.x))


class ValueIter:
    def __init__(self, x_iter: Iterable):
        self.x_iter = x_iter

    def __iter__(self) -> Iterator:
        return self.x_iter.__iter__()

    def __rshift__(self, m: Map) -> ValueIter:
        return self.apply(m=m)

    def apply(self, m: Map) -> ValueIter:
        def iter_func(x_iter: Iterable, m: Map) -> Iterator:
            for x in x_iter:
                new_x = m(x)
                if new_x is None:
                    continue
                yield new_x

        return ValueIter(x_iter=iter_func(x_iter=self.x_iter, m=m))

    def apply_parallel(self,
                       make_map: Callable[[int], Map],
                       nproc: int | None = None,
                       ctx: mp.context.BaseContext | None = None,
                       ) -> ValueIter:
        if nproc is None:
            nproc = mp.cpu_count()
            if hasattr(self.x_iter, "__len__"):
                nproc = min(nproc, self.x_iter.__len__())

        if nproc == 1:
            m = make_map(0)
            return self.apply(m)

        if ctx is None:
            ctx = mp.get_context("fork")

        def iter_func(x_iter: Iterable, make_map: Callable[[int], Map], nproc: int):
            qi = ctx.Queue(maxsize=64 * nproc)
            qo = ctx.Queue(maxsize=64 * nproc)

            def put_task(qi: mp.Queue, x_iter: Iterable, nproc: int):
                for x in x_iter:
                    qi.put(x)
                for _ in range(nproc):
                    qi.put(None)  # send nproc stop signals

            def apply_task(qi: mp.Queue, qo: mp.Queue, make_map: Callable[[int], Map], i: int):
                m = make_map(i)
                while True:
                    x = qi.get()
                    if x is None:  # recv stop signal
                        qo.put(None)
                        break
                    new_x = m(x)
                    if new_x is None:
                        continue
                    qo.put(new_x)

            # run put and apply
            proc_list = []

            proc_list.append(ctx.Process(target=put_task, args=(qi, x_iter, nproc)))
            for i in range(nproc):
                proc_list.append(ctx.Process(target=apply_task, args=(qi, qo, make_map, i)))

            for proc in proc_list:
                proc.start()

            # recv
            process_done_count = 0
            while True:
                new_x = qo.get()
                if new_x is not None:
                    yield new_x
                    continue
                # recv stop signal
                process_done_count += 1
                if process_done_count >= nproc:
                    break

            # join
            for proc in proc_list:
                proc.join()

        return ValueIter(x_iter=iter_func(x_iter=self.x_iter, make_map=make_map, nproc=nproc))


if __name__ == "__main__":
    v = Value(4) >> (lambda x: x + 1) >> (lambda x: x * 2)
    print(v.x)
    v = ValueIter(range(1, 4)) >> (lambda x: x + 1) >> (lambda x: x * 2)
    print(list(v.x_iter))
    v = ValueIter(range(0, 1000)).apply_parallel(make_map=lambda i: (lambda x: x + i), nproc=4)
    print(sorted(list(v.x_iter)))