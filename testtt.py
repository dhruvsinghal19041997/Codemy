# n=int(input())
# arr = list(map(int, input().split()))
# sum = 0
# arr=sorted(arr)
# sum += abs(arr[0] - arr[1])
# sum += abs(arr[-1] - arr[-2])
# for i in range(1,n-1):
#     sum += min(abs(arr[i] - arr[i - 1]),abs(arr[i] - arr[i + 1]))
# print(sum)
#----------------------------------

# def getMaxToys(N, P, k, x, toys):
    # Write your code here
#     min_abs = abs(P - x[0])
#     min_abs_pos = 0
#     for i in range(1, N):
#         if min_abs > abs(P - x[i]):
#             min_abs = abs(P - x[i])
#             min_abs_pos = i
#             print(min_abs)
#         elif min_abs == abs(P - x[i]):
#             print(toys[i])
#             print(toys[min_abs_pos])
#             if toys[i] > toys[min_abs_pos]:
#                 min_abs_pos = i
#     print(min_abs_pos)
#
#
# T = int(input())
# for _ in range(T):
#     N = int(input())
#     P = int(input())
#     k = int(input())
#     x = list(map(int, input().split()))
#     toys = list(map(int, input().split()))
#     out_ = getMaxToys(N, P, k, x, toys)
#     print(out_)

class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        print("bark bark!")

    def doginfo(self):
        print(self.name + " is " + str(self.age) + " year(s) old.")

ozzy = Dog("Ozzy", 2)
skippy = Dog("Skippy", 12)
filou = Dog("Filou", 8)
ozzy.doginfo()
skippy.doginfo()
filou.doginfo()