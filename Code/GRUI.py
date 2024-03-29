import torch
import torch.nn as nn

torch.manual_seed(0)

class GRUICell(nn.Module):
    def __init__(self, num_inputs, num_hiddens):
        super(GRUICell, self).__init__()
        self.num_inputs = num_inputs
        self.num_hiddens = num_hiddens
        # self.num_outputs = num_outputs
        def normal(shape):
            return torch.randn(size=shape) * 0.01
        def three():
            return (nn.Parameter(normal((num_inputs, num_hiddens))), 
                    nn.Parameter(normal((num_hiddens, num_hiddens))), 
                    nn.Parameter(torch.zeros(num_hiddens)))
        self.W_xz, self.W_hz, self.b_z = three() # Parameters of update gate
        self.W_xr, self.W_hr, self.b_r = three() # Parameters of reset gate
        self.W_xh, self.W_hh, self.b_h = three() # Parameters of candidate hidden state
        # Parameters of decay vector
        self.W_beta = nn.Parameter(normal((num_inputs, num_hiddens)))
        self.b_beta = nn.Parameter(torch.zeros(num_hiddens))
        # Parameters of output layer
        # self.W_hq = nn.Parameter(normal((num_hiddens, num_outputs)))
        # self.b_q = nn.Parameter(torch.zeros(num_outputs))

    def forward(self, X, Delta, H):
        H = H.detach()
        beta = torch.exp(torch.minimum(torch.zeros(self.num_hiddens), Delta @ self.W_beta + self.b_beta))
        H = beta * H
        Z = torch.sigmoid((X @ self.W_xz) + (H @ self.W_hz) + self.b_z)
        R = torch.sigmoid((X @ self.W_xr) + (H @ self.W_hr) + self.b_r)
        H_tilde = torch.tanh((X @ self.W_xh) + ((R * H) @ self.W_hh) + self.b_h)
        H = Z * H + (1 - Z) * H_tilde
        # Y = H @ self.W_hq + self.b_q
        return H

class GRUIModel(nn.Module):
    def __init__(self, num_inputs, num_hiddens):
        super(GRUIModel, self).__init__()
        self.name = 'GRUI'
        self.num_hiddens = num_hiddens
        self.gruicell = GRUICell(num_inputs, num_hiddens)

    def forward(self, X, Delta, H):
        if H is None:
            H_new = torch.zeros(X.shape[1], self.num_hiddens)
        else:
            H_new = H
        H_new.detach_()
        H = torch.tensor([])
        #H_detach = torch.tensor([])
        for index in range(X.shape[0]):
            H_new = self.gruicell(X[index], Delta[index], H_new)
            H = torch.cat((H, H_new), dim = 0)
            #H_detach = torch.cat((H_detach, H_new.detach()), dim = 0)
        return H