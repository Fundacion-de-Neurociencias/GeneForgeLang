import torch
import torch.nn as nn

class TranslateLSTM(nn.Module):
    """
    LSTM ligero para predecir eficiencia de traducción (TE) usando:
    - Secuencia UTR (one-hot 4 canales)
    - Secuencia CDS inicial (one-hot 4 canales)
    - Features adicionales (GC%, ΔG, #uAUG, #sites RBP, #sites miR)
    """
    def __init__(self, utr_length=300, cds_length=100, feature_dim=5, hidden_dim=128):
        super().__init__()
        self.utr_lstm = nn.LSTM(input_size=4, hidden_size=hidden_dim, num_layers=2,
                                 bidirectional=True, batch_first=True)
        self.cds_lstm = nn.LSTM(input_size=4, hidden_size=hidden_dim, num_layers=2,
                                 bidirectional=True, batch_first=True)
        self.fc_features = nn.Linear(feature_dim, hidden_dim*2)
        self.fc_out = nn.Linear(hidden_dim*4 + hidden_dim*2, 1)

    def forward(self, utr_seq_onehot, cds_seq_onehot, extra_features):
        # utr_seq_onehot: [batch, utr_len, 4]
        # cds_seq_onehot: [batch, cds_len, 4]
        # extra_features:   [batch, feature_dim]
        _, (h_utr, _) = self.utr_lstm(utr_seq_onehot)
        _, (h_cds, _) = self.cds_lstm(cds_seq_onehot)
        # concatenar últimos estados bidireccionales
        h_utr = torch.cat([h_utr[-2], h_utr[-1]], dim=1)  # [batch, hidden_dim*2]
        h_cds = torch.cat([h_cds[-2], h_cds[-1]], dim=1)  # [batch, hidden_dim*2]
        # proyección de features
        h_feat = torch.relu(self.fc_features(extra_features))  # [batch, hidden_dim*2]
        # concatenar todas las representaciones
        h_comb = torch.cat([h_utr, h_cds, h_feat], dim=1)  # [batch, hidden_dim*6]
        out = torch.sigmoid(self.fc_out(h_comb))           # [batch, 1]
        return out
