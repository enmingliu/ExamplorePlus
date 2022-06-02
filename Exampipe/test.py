import sys

def call_me(first):
    return first + " Zac"

if __name__ == "__main__":
    
    print(call_me(sys.argv[1]))