# Neural Computation (Extended)
# CW1: Backpropagation and Softmax
# Autumn 2020
#

import numpy as np
import time
import fnn_utils


# Some activation functions with derivatives.
# Choose which one to use by updating the variable phi in the code below.

def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))
def sigmoid_d(x):
    m = sigmoid(x)
    return m * (1 - m)
def relu(x):
    return np.maximum(x, 0)
def relu_d(x):
    return 1. * (x > 0)


class BackPropagation:

    # The network shape list describes the number of units in each
    # layer of the network. The input layer has 784 units (28 x 28
    # input pixels), and 10 output units, one for each of the ten
    # classes.

    def __init__(self, network_shape=[784, 40, 40, 40, 10]):

        # Read the training and test data using the provided utility functions
        self.trainX, self.trainY, self.testX, self.testY = fnn_utils.read_data()

        # Number of layers in the network
        self.L = len(network_shape)

        self.crossings = [(1 if i < 1 else network_shape[i - 1], network_shape[i]) for i in range(self.L)]

        # Create the network
        # activations
        self.a = [np.zeros(m) for m in network_shape]
        self.db = [np.zeros(m) for m in network_shape]
        self.b = [np.random.normal(0, 1 / 10, m) for m in network_shape]
        self.z = [np.zeros(m) for m in network_shape]
        self.delta = [np.zeros(m) for m in network_shape]
        self.w = [np.random.uniform(-1 / np.sqrt(m0), 1 / np.sqrt(m0), (m1, m0)) for (m0, m1) in self.crossings]
        self.dw = [np.zeros((m1, m0)) for (m0, m1) in self.crossings]
        self.nabla_C_out = np.zeros(network_shape[-1])

        # Choose activation function
        self.phi = relu
        self.phi_d = relu_d

        # Store activations over the batch for plotting
        self.batch_a = [np.zeros(m) for m in network_shape]
        self.network_shape = network_shape

    def forward(self, x):
        """ Set first activation in input layer equal to the input vector x (a 24x24 picture), 
            feed forward through the layers, then return the activations of the last layer.
        """
        self.a[0] = (x / 255) - 0.5  # Center the input values between [-0.5,0.5]

        for l in range(1, self.L):
            self.z[l] = np.dot(self.w[l], self.a[l - 1]) + self.b[l]
            self.a[l] = self.phi(self.z[l])

        self.a[self.L - 1] = self.softmax(self.a[self.L - 1])
        return self.a[self.L - 1]

    def softmax(self, z):
        e_x = np.exp(z - np.max(z))
        return e_x / e_x.sum(axis=0)

    def loss(self, pred, y):
        return -np.log(pred[np.argmax(y)])

    def backward(self, x, y):
        """ Compute local gradients, then return gradients of network.
        """
        # TODO
        # Output layer
        self.delta[self.L-1] = self.a[self.L-1] - y
        for l in reversed(range(0, self.L-1)):
            # hidden layer
            self.delta[l] = np.multiply(self.phi_d(self.z[l]), np.dot(self.w[l+1].T, self.delta[l+1]))
            
            # If not input layer
            if l != 0:
                self.dw[l] = np.matmul(np.array([self.delta[l]]).T, np.array([self.a[l - 1]]))
                self.db[l] = self.delta[l]

    def predict(self, x):
        self.forward(x)
        return np.argmax(self.a[self.L - 1])

    # Return predicted percentage for class j
    def predict_pct(self, j):
        return self.a[self.L - 1][j]  # TODO

    def evaluate(self, X, Y, N):
        """ Evaluate the network on a random subset of size N. """
        num_data = min(len(X), len(Y))
        samples = np.random.randint(num_data, size=N)
        results = [(self.predict(x), np.argmax(y)) for (x, y) in zip(X[samples], Y[samples])]
        return sum(int(x == y) for (x, y) in results) / N

    def sgd(self,
            batch_size=100,
            epsilon=0.2,
            epochs=10):

        """ Mini-batch gradient descent on training data.

            batch_size: number of training examples between each weight update
            epsilon:    learning rate
            epochs:     the number of times to go through the entire training data
        """
        # Compute the number of training examples and number of mini-batches.
        N = min(len(self.trainX), len(self.trainY))
        # N = 60000
        num_batches = int(N / batch_size)

        # Variables to keep track of statistics
        loss_log = []
        test_acc_log = []
        train_acc_log = []

        timestamp = time.time()
        timestamp2 = time.time()

        predictions_not_shown = True

        # In each "epoch", the network is exposed to the entire training set.
        for t in range(epochs):

            # We will order the training data using a random permutation.
            permutation = np.random.permutation(N)

            # Evaluate the accuracy on 1000 samples from the training and test data
            test_acc_log.append(self.evaluate(self.testX, self.testY, 1000))
            train_acc_log.append(self.evaluate(self.trainX, self.trainY, 1000))
            batch_loss = 0

            for k in range(num_batches):

                # Reset buffer containing updates
                # TODO
                tmpdw = [np.zeros((m1, m0)) for (m0, m1) in self.crossings]
                tmpdb = [np.zeros(m) for m in self.network_shape]

                # Mini-batch loop
                for i in range(batch_size):

                    # Select the next training example (x,y)
                    x = self.trainX[permutation[k * batch_size + i]]
                    y = self.trainY[permutation[k * batch_size + i]]

                    # Feed forward inputs
                    # TODO
                    self.forward(x=x)

                    # Compute gradients
                    # TODO
                    self.backward(x=[], y=y) # Unsure if x was required here. We did not use it and the assignment did not mention it.

                    for l in range(self.L): # Total gradient
                        tmpdw[l] += self.dw[l] / batch_size
                        tmpdb[l] += self.db[l] / batch_size

                    # Update loss log
                    batch_loss += self.loss(self.a[self.L - 1], y)

                    for l in range(self.L):
                        self.batch_a[l] += self.a[l] / batch_size

                # Update the weights at the end of the mini-batch using gradient descent
                for l in range(1, self.L):
                    # print(self.w[l].shape, self.dw[l-1].shape)
                    self.w[l] -= epsilon * tmpdw[l]  # TODO
                    self.b[l] -= epsilon * tmpdb[l]  # TODO

                # Update logs
                loss_log.append(batch_loss / batch_size)
                batch_loss = 0

                # Update plot of statistics every 10 seconds.
                if time.time() - timestamp > 10:
                    timestamp = time.time()
                    fnn_utils.plot_stats(self.batch_a,
                                         loss_log,
                                         test_acc_log,
                                         train_acc_log)

                # Display predictions every 20 seconds.
                if (time.time() - timestamp2 > 20) or predictions_not_shown:
                    predictions_not_shown = False
                    timestamp2 = time.time()
                    fnn_utils.display_predictions(self, show_pct=True)

                # Reset batch average
                for l in range(self.L):
                    self.batch_a[l].fill(0.0)


# Start training with default parameters.

def main():
    bp = BackPropagation()

    ## Function Testing

    # task 1: softmax test
    # z = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    # print(bp.softmax(z=z))

    # task 2: forward test
    # print(bp.forward(bp.trainX[0]))

    # task 3: loss test
    # bp.forward(bp.trainX[0])
    # print(bp.loss(bp.a[bp.L - 1], bp.trainY[0]))

    # task 4: backward test
    # print(bp.dw[1])
    # bp.forward(bp.trainX[0])
    # bp.backward(x=None, y=bp.trainY[0])
    # print('dw', np.argmax(bp.dw[1]))

    t1 = time.time() # Get current system time
    bp.sgd(32, 0.2, 10)
    print("Time taken: " + str(time.time() - t1)) # Print time taken for training

if __name__ == "__main__":
    main()
