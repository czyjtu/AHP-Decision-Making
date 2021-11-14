import numpy as np



class ComprehensionMatrix:
    def __init__(self, Matrix: np.matrix):
        self.matrix: np.matrix = Matrix

    def complete(self) -> None:
        for i in range(len(self.matrix)):
            self.matrix[i, i] = 1.0

        try:
            for i in range(len(self.matrix)):
                for j in range(len(self.matrix)):
                    if self.matrix[i, j] == .0:
                        self.matrix[i, j] = 1/self.matrix[j, i]
                    elif self.matrix[j, i] == .0:
                        self.matrix[j, i] = 1 / self.matrix[i, j]
        except ZeroDivisionError:
            raise ValueError("incomplete matrix!")

    def calculate_weights(self):
        matrix = np.array(self.matrix)
        sum = sum(matrix.reshape(-1))
        self.weights = sum(matrix) / sum

    def CR(self) -> float:
        self.complete()
        self.calculate_weights()







