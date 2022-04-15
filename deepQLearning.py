import torch
import torch.nn as nn
import numpy as np

class DeepQNetwork(nn.Module):
    def __init__(self, state_size, action_size, hidden_dim, lr=0.001) -> None:
        super().__init__()
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_dim = hidden_dim
        self.fc1 = nn.Linear(state_size, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_size)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

        self.lr = lr
        self.optim = torch.optim.Adam(self.parameters(), lr=self.lr)

        self.batch_norm1 = nn.BatchNorm1d(hidden_dim)
        self.batch_norm2 = nn.BatchNorm1d(hidden_dim)
        self.batch_norm3 = nn.BatchNorm1d(action_size)

        self.episodes = 0
        self.loss = nn.HuberLoss()

    def forward(self, state):
        # layer 1
        x = self.fc1(state.view(-1, self.state_size))
        x = self.batch_norm1(x)
        x = self.relu(x)

        # layer 2
        x = self.fc2(x)
        x = self.batch_norm2(x)
        x = self.relu(x)

        # final layer
        x = self.fc3(x)
        q = self.batch_norm3(x)
        return q

    def update(self, reward, state, decision):
        self.optim.zero_grad()
        loss = -torch.log(torch.sum(self.forward(state) * reward))
        loss.backward()
        self.optim.step()
        self.episodes += 1
        if self.episodes % 1000 == 0:
            self.save_model()

    def trainloop(self, states, actions, rewards, next_states):
        self.optim.zero_grad()
        loss = -torch.log(torch.sum(self.forward(states) * rewards))
        loss.backward()
        self.optim.step()
        self.episodes += 1
        if self.episodes % 1000 == 0:
            self.save_model()

    def save_model(self, path='model.net'):
        torch.save(self.state_dict(), path)
    
    def load_model(self, path='model.net'):
        self.load_state_dict(torch.load(path))


class QAgent():
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size, n_actions,
                    max_mem_size = 10000, eps_end=0.01,  eps_dec=5e-4, model_name="agent.net", hidden_dim=64):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.lr = lr

        self.acition_space = [i for i in range(n_actions)]
        self.mem_size = max_mem_size

        self.batch_size = batch_size
        self.mem_cntr = 0

        self.Q_eval = DeepQNetwork(lr=self.lr, state_size=input_dims,  action_size=n_actions, hidden_dim=hidden_dim)
        self.Q_eval.eval()
        self.state_memory = np.zeros((self.mem_size, input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, input_dims), dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int64)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

        self.total_episodes = 0
        self.model_name = model_name

    def store_transition(self, state, action, reward, state_, done=False):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.terminal_memory[index] = done
        self.mem_cntr += 1

    def choose_action(self, obseration):
        if np.random.random() > self.epsilon:
            state = torch.from_numpy(obseration).float()
            self.Q_eval.eval()
            actions =   self.Q_eval.forward(state)
            return torch.argmax(actions).item()
        
        return np.random.choice(self.acition_space)
    
    def learn(self):
        """
        Only runs when the batchsize is complete
        Samples a random batch from memory
         * performs a batch gradient descent step
         * saves the model
        """
        if self.mem_cntr < self.batch_size:
            return
        
        self.Q_eval.train()
        self.Q_eval.optim.zero_grad()

        # Take the index of the last saved state
        max_mem = min(self.mem_cntr, self.mem_size)

        # Sample a random batch from the memory
        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        
        batch_index = torch.tensor(np.arange(self.batch_size))

        state_batch = torch.tensor(self.state_memory[batch])
        new_state_batch = torch.tensor(self.new_state_memory[batch])
        reward_batch = torch.tensor(self.reward_memory[batch])
        terminal_batch = torch.tensor(self.terminal_memory[batch])

        action_batch = torch.tensor(self.action_memory[batch])

        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]

        q_next = self.Q_eval.forward(new_state_batch)

        q_next[terminal_batch] = 0.0

        q_target = reward_batch + self.gamma * torch.max(q_next, 1)[0]

        loss = self.Q_eval.loss(q_target, q_eval)
        loss.backward()
        self.Q_eval.optim.step()

        self.epsilon = self.epsilon - self.eps_dec if self.epsilon > self.eps_min else self.eps_min

        self.mem_cntr = 0
        
        self.total_episodes += 1

        if self.total_episodes % 1000 == 0:
            print("total experiences: ", self.total_episodes, "epsilon: ", self.epsilon)
        self.save_agent(self.model_name)
        self.Q_eval.train()


    def recover_agent(self, trash="model.net"):
        with open(self.model_name, "rb") as f:
            checkpoint =  torch.load(f)
            self.epsilon = checkpoint['epsilon']
            self.total_episodes = checkpoint['total_episodes']
            self.Q_eval.load_state_dict(checkpoint['state_dict'])

    def save_agent(self, trash=None):
        torch.save({
            'total_episodes': self.total_episodes,
            'epsilon': self.epsilon,
            'state_dict': self.Q_eval.state_dict()
        }, self.model_name)