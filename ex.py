import numpy as np

def compute_PTDF(ref, Y, A, B, n_nodes):

    B_minus_ref = np.concatenate((B[:, 0:ref], B[:, (ref + 1):]), axis=1)

    B_minus_ref = np.concatenate((B_minus_ref[0:ref,:], B_minus_ref[(ref + 1):,:]), axis=0)

    B_minus_ref_inv = np.linalg.inv(B_minus_ref)

    #### now include the reference buses again with zero coefficients
    # include a column with zeros
    B_with_ref_inv = np.concatenate((np.concatenate((B_minus_ref_inv[:, 0:ref],
                                                        np.zeros((n_nodes - 1, 1))), axis=1),
                                                        B_minus_ref_inv[:, ref:]), axis=1)

    # include a row with zeros
    B_with_ref_inv = np.concatenate((np.concatenate((B_with_ref_inv[0:ref, :],
                                                        np.zeros((1, n_nodes))), axis=0),
                                                        B_with_ref_inv[ref:, :]), axis=0)

    return np.matmul(np.matmul(Y, A), B_with_ref_inv)


#              1    2    3    4    5    6    7    8    9   10   11   12   13  14
A = np.array([[1 , -1 , 0  , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [1 , 0  ,  0 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 1  , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 1  ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 1  ,  0 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  1 ,  0 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  1 ,  0 ,  0 ,  0 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  1 ,  0 ,  0 ,  0 ,  0 , -1 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  1 ,  0 ,  0 ,  0 ,  0 ,  0 , -1 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  1 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0 ,  0 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1 , 0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 ,-1]], dtype='d')

Y = np.diag(10 * np.ones(18, dtype='d'))

B = np.matmul(np.transpose(A), np.matmul(Y, A))

original_PTDF = compute_PTDF(ref=1, Y=Y, A=A, B=B, n_nodes=14)


#              1    2    3    4    5    6    7    9   10   11
A = np.array([[1 , -1 , 0  , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [1 , 0  ,  0 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 1  , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 1  ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 1  ,  0 ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  0 ,  1 ,  0 ,  0 , -1 ,  0 ,  0 ,  0],
              [0 , 0  ,  0 ,  1 ,  0 ,  0 ,  0 , -1 ,  0 ,  0],
              [0 , 0  ,  0 ,  0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  0 ,  0 ,  0 ,  1 ,  0 ,  0 ,  0 , -1],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0 ,  0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1]], dtype='d')

Y = np.diag(10 * np.ones(14, dtype='d'))

B = np.matmul(np.transpose(A), np.matmul(Y, A))

PTDF_after_end_line_nodes = compute_PTDF(ref=1, Y=Y, A=A, B=B, n_nodes=10)


# assume that the external node is the first one. nodes 1 and 2 are then frontier nodes.
#              2    4    5    7    9   10   11
A = np.array([[0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0],
              [0 ,  1 ,  0 , -1 ,  0 ,  0 ,  0],
              [0 ,  1 ,  0 ,  0 , -1 ,  0 ,  0],
              [0 ,  0 ,  0 ,  1 , -1 ,  0 ,  0],
              [0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0],
              [0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1],
              [1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0],
              [1 ,  0 , -1 ,  0 ,  0 ,  0 ,  0],
              [0 ,  0 ,  1 ,  0 ,  0 ,  0 , -1]], dtype='d')

Y = np.diag(10 * np.ones(9, dtype='d'))
Y[6, 6] = 5 + 10        # susceptance of 5 from the new branch plus 10 from the parallel branch
Y[7, 7] = 5 + 10        # susceptance of 5 from the new branch plus 10 from the parallel branch
Y[8, 8] = 5             # the new branch has a susceptance of 5

B = np.matmul(np.transpose(A), np.matmul(Y, A))

PTDF_after_nodes_1_and_3_and_6 = compute_PTDF(ref=0, Y=Y, A=A, B=B, n_nodes=7)

print("wait")
