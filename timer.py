import time

class Timer:
    def __init__( self, func=time.per_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started')
        self._start = self._func()

    def stop(self):
        if self.start is None:
            raise RuntimeError('Not started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0


    @property
    def running(self):
        self.start()
        return self

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args ):
        self.stop()

# to call
# t = Timer()
# t.start()
# t.stop()
# print( t.elapsed)

# as context manager
# with t:
#   countdown(200000)
# print( t.elapsed )
# with Timer() as t2:
#  countdown( 10000)
#print( t2.elapsed )

