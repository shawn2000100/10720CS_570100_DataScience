import torch
import torch.nn as nn
import torch.nn.functional as F
import gym
from collections import namedtuple
import numpy as np
import timeit
from itertools import count
from torch.distributions import Categorical
from PIL import Image
import pickle # 保存Model用
import matplotlib.pyplot as plt # 畫圖顯示 epoch 與 spent time

# 宣告強化學習神經網路的結構
class policyNet(nn.Module):
    def __init__(self):
        super(policyNet, self).__init__()
        self.L1 = nn.Linear(4, 30)
        self.out = nn.Linear(30, 2)
    def forward(self, x):
        x = F.relu(self.L1(x))
        x = self.out(x)
        x = F.softmax(x)
        return x

# 我把訓練過程寫成函式，以後不用每次都重訓練了
def start_training_model():
    # 宣告Model的環境、epoch......等超參數
    env = gym.make('CartPole-v0').unwrapped
    policy_net = policyNet()
    optimizer = torch.optim.RMSprop(policy_net.parameters(), lr=0.01)
    batch_size = 4  # 預設為 16 我改成 4 變超強!
    SAR = namedtuple('sar', ['state', 'action', 'reward'])
    steps = 0
    duration = []
    SAR_list = []
    global epoch
    epoch = 100  # 從這裡更改訓練回合數，訓練太久很花時間
    epoch_data = []
    global spend_time
    spend_time = []
    # 開始訓練
    try:
        for e in range(epoch):
            print('start ', e)
            state = env.reset()
            state = torch.Tensor(state)
            start = timeit.default_timer()  # start time
            for t in count():
                env.render()
                probs = policy_net(state)
                m = Categorical(probs)
                action = m.sample()
                next_state, reward, done, _ = env.step(action.item())

                if done:
                    reward = 0
                sar = SAR(state, action, reward)
                SAR_list.append(sar)
                state = next_state
                state = torch.Tensor(state)

                steps += 1
                if done:
                    break

            duration.append(t)

            if e > 0 and e % batch_size == 0:
                rewards = np.zeros([steps])
                gamma = 0.99
                cur_reward = 0

                for i in reversed(range(steps)):
                    sar = SAR_list[i]
                    r = sar.reward
                    if r == 0:
                        cur_reward = 0
                    else:
                        cur_reward = gamma * cur_reward + r
                        rewards[i] = cur_reward

                reward_mean = np.mean(rewards)
                reward_std = np.std(rewards)
                rewards = (rewards - reward_mean) / reward_std
                # rewards = rewards + (timeit.default_timer() - start)**2 # 這邊嘗試新的 Reward Shaping

                optimizer.zero_grad()
                loss = 0

                for i in range(steps):
                    # TODO:
                    # Take out state, action, reward from SAR_list
                    # Compute loss
                    sar = SAR_list[i]
                    cur_state = sar.state
                    cur_action = sar.action
                    cur_reward = rewards[i]

                    probs = policy_net(cur_state)  # <= hint: feed something into policy network
                    m = Categorical(probs)
                    loss += -m.log_prob(cur_action) * cur_reward
                    # END TODO

                loss /= batch_size
                loss.backward()
                optimizer.step()

                steps = 0
                SAR_list = []

            stop = timeit.default_timer()  # stop time
            print('Spent Time: {:.4f}'.format(stop - start))   # spend time
            epoch_data.append(e)
            spend_time.append(float("{:.4f}".format(stop - start)))
    finally:
        env.close()
        # 輸出Model成Pickle
        with open('CartPole-v0_100epoch.pickle', 'wb') as file:
            pickle.dump(policy_net, file)


# 開始訓練
print('--- 開始訓練Model! ---')
start_training_model()
print('--- Model 訓練完成! ---')

# 使用先前訓練好之 Model 來做GIF
with open('CartPole-v0_100epoch.pickle', 'rb') as file:
    policy_net = pickle.load(file)
print('--- 讀取先前之Model... ---')
env = gym.make('CartPole-v0').unwrapped
state = env.reset()
state = torch.Tensor(state)
frames = []
try:
    for t in count():
        env.render()
        frames.append(Image.fromarray(env.render(mode='rgb_array')))
        probs = policy_net(state)
        m = Categorical(probs)
        action = m.sample()
        state , reward , done , _ = env.step(action.item())
        state = torch.Tensor(state)
        if done:
            break
finally:
    env.close()
    print('--- 開始GIF輸出... ---')
    with open('CartPole-v0_100epoch.gif','wb') as f: # 這邊的 epoch number要手動改一下
        im = Image.new('RGB', frames[0].size)
        im.save(f, save_all=True, append_images=frames)
        print('--- GIF輸出完成! ---')

    plt.figure()
    plt.plot(spend_time, label='Spent Time')
    plt.xlabel('epoch')
    plt.ylabel('Time (s)')
    plt.title('batch size = 4, epoch = 100, default RS')
    plt.legend(shadow=True, loc='best', fontsize=12)
    plt.show()