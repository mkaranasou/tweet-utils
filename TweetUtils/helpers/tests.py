__author__ = 'mariakaranasou'


def create_test_file():
    """Create a test file with a random tweet"
    with open('../data/tweets.txt', 'w') as tf:
        for i in range(0, 8000):
            tf.write("I liked a @YouTube video http://t.co/9D1KqSWkED Classic Game Room - GRAND THEFT AUTO 3 review for PS2\n")

if __name__ == "__main__":
    create_test_file()
