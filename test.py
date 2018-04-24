import decorators
import time

@decorators.profiler('test with topic')
def foo1(a):
    print('foo1 begin:', a)
    time.sleep(0.5)
    print('foo1 end:', a)

print('decorationg w-o topic')

@decorators.profiler('foo')
def foo2(a):
    print('foo2 begin:', a)
    time.sleep(0.5)
    print('foo2 end:', a)


print('send baz to foo1')
foo1('baz')
print('send bar to foo2')
foo2('bar')
