from functools import reduce as red
from Pyro4 import expose


class Solver:

    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        try:
            b, m = self.read_input()
            n = len(b)
            step = n / len(self.workers)

            mapped = []
            for i in range(0, len(self.workers)):
                mapped.append(self.workers[i].mymap(b, m, step, step*i))

            reduced = self.myreduce(mapped)
            self.write_output(reduced)
        except Exception:
            self.write_output(-1)

    @staticmethod
    @expose
    def chinese_remainder(m, a):
        sum = 0
        prod = red(lambda acc, b: acc * b, m)
        for n_i, a_i in zip(m, a):
            p = prod // n_i
            sum += a_i * Solver.mul_inv(p, n_i) * p
        return [sum % prod, prod]

    @staticmethod
    @expose
    def mul_inv(a, b):
        b0 = b
        x0, x1 = 0, 1
        if b == 1:
            return 1
        while a > 1:
            q = a // b
            a, b = b, a % b
            x0, x1 = x1 - q * x0, x0
        if x1 < 0:
            x1 += b0
        return x1

    @staticmethod
    @expose
    def mymap(b, m, count, first):
        return Solver.chinese_remainder(m[first:first+count], b[first:first+count])

    @staticmethod
    @expose
    def myreduce(mapped):
        b = list()
        m = list()
        for s in mapped:
            b.append(s.value[0])
            m.append(s.value[1])
        res = Solver.chinese_remainder(m, b)
        return res

    def read_input(self):
        a = list()
        b = list()
        m = list()

        with open(self.input_file_name, 'r') as file:
            for line in file:
                s = line.rstrip().split(' ')
                a.append(int(s[0]))
                b.append(int(s[1]))
                m.append(int(s[2]))
        n = len(a)
        for i in range(0, n):
            if a[i] != 1:
                b[i] = b[i] * Solver.mul_inv(a[i], m[i])
                a[i] = 1
        return b, m

    def write_output(self, output):
        if output == -1:
            with open(self.output_file_name, 'w') as file:
                file.write('An error occurred! No solution for you.')
        else:
            with open(self.output_file_name, 'w') as file:
                file.write(str(output[0])+' mod '+str(output[1]))