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
#              1   2   5
A = np.array([[1, -1,  0],
              [1,  0, -1]], dtype='d')

Y = np.diag(10 * np.ones(2, dtype='d'))
B = np.matmul(np.transpose(A), np.matmul(Y, A))

b_front_idxs = [1, 2]

B_front_ext = B[b_front_idxs, :][:, [0]]

B_ext_ext_inv = np.linalg.inv(B[[0], :][:, [0]])

B_front_front_new = B[b_front_idxs, :][:, b_front_idxs] - np.matmul(B_front_ext,
                                                        np.matmul(B_ext_ext_inv,
                                                                B[[0], :][:, b_front_idxs]))

B_ext_impact = -1*np.matmul(B_front_ext, B_ext_ext_inv)

#              2    3    4    5    6    7    9   10   11
A = np.array([[1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [1 , 0  , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 1  , -1 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  1 , -1 ,  0 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  1 ,  0 ,  0 , -1 ,  0 ,  0 ,  0],
              [0 , 0  ,  1 ,  0 ,  0 ,  0 , -1 ,  0 ,  0],
              [0 , 0  ,  0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0],
              [0 , 0  ,  0 ,  0 ,  1 ,  0 ,  0 ,  0 , -1],
              [0 , 0  ,  0 ,  0 ,  0 ,  1 , -1 ,  0 ,  0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  1 , -1 ,  0],
              [0 , 0  ,  0 ,  0 ,  0 ,  0 ,  0 ,  1 , -1],
              [1 , 0  ,  0 , -1 ,  0 ,  0 ,  0 ,  0 ,  0]], dtype='d')

Y = np.diag(10 * np.ones(12, dtype='d'))
Y[11, 11] = - B_front_front_new[0][1] + 10

B = np.matmul(np.transpose(A), np.matmul(Y, A))

PTDF_after_node_6 = compute_PTDF(ref=0, Y=Y, A=A, B=B, n_nodes=9)

print("wait")
