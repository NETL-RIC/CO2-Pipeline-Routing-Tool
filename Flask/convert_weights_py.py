
import torch
import torch.nn as nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2

from agent import CustomTorchModel
from resnet.models import ResNet


class CustomTorchModel(TorchModelV2, nn.Module):
    
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        super(CustomTorchModel, self).__init__(obs_space, action_space, num_outputs, model_config, name)
        nn.Module.__init__(self)

        self.encoder = ResNet(in_channels=9, num_blocks=3)
        self.policy_fc = nn.Linear(in_features=256, out_features=8)
        self.value_fc = nn.Linear(in_features=256, out_features=1)
    
    def forward(self, observation, state, seq_lens):
        # is_training = input_dict.is_training
        # observation = input_dict['obs'] # observation must be passed as tensor for torch scripted

        assert isinstance(observation, torch.Tensor)
        # assert observation.shape[]
        # tensor = torch.tensor(observation).to(torch.float)
        # tensor = torch.tensor(observation, dtype=torch.float)
        # tensor = torch.moveaxis(observation, -1, 1)
        encoded_obs = self.encoder(observation)
        logits = self.policy_fc(encoded_obs)
        self.state_value = self.value_fc(encoded_obs)

        return logits, []
    
    def value_function(self):
        return self.state_value.squeeze(-1)


model = torch.load('./trained_model/model.pt')
type(model.policy_fc.out_features)


model.policy_fc.out_features = int(model.policy_fc.out_features)
type(model.policy_fc.out_features)


model_scripted = torch.jit.script(model) # Export to TorchScript
model_scripted.save('./trained_model/model_scripted_local.pt')