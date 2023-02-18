"""Simple model for testing.

- Author: Jinwoo Park
- Email: jinwoo.park@annotation-ai.com
"""

import torch


class Simple(torch.nn.Module):
    """Identity model."""

    def forward(self, inputs: torch.ByteTensor) -> torch.ByteTensor:
        """Forward."""
        return inputs


path = "model_repository/identity_core/1/model.pt"
script_model = torch.jit.script(Simple())
torch.jit.save(script_model, path)
print("saved as", path)
