
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier


# In[2]:


training = pd.read_csv('train_data.csv',header=None)
label = training[17].values
training = training.drop(17,axis=1)
training = training.drop(0,axis=1)

testing = pd.read_csv('test_data.csv',header=None)
test_idx = testing[0].values
testing = testing.drop(0,axis=1)
training_len = len(training)


# In[3]:


def count_mode(data_arr,dim):
    vec = data_arr[:,dim]
    ct = {}
    for v in vec:
        if v in ct:
            ct[v] += 1
        else:
            ct[v] = 1
    ct.pop('unknown')
    max_count = 0
    ret_k = 0
    for k , v in ct.items():
        if v > max_count:
            max_count = v
            ret_k = k
    return ret_k


# In[4]:


all_data = pd.concat([training,testing])
cat_feat = [2,3,4,5,7,8,9,11,16]
cat_feat_np = [i-1 for i in cat_feat]
for col in cat_feat:
    mp = {}
    cnt = 0
    for a in all_data[col]:
        if a != 'unknown' and a not in mp:
            mp[a] = cnt
            cnt += 1
    mp['unknown'] = 'unknown'
    all_data[col] = all_data[col].map(mp)
    print(sum(all_data[col] == 'unknown'))
all_data_arr = all_data.values


# In[5]:


for cur_dim in cat_feat_np:
    print(cur_dim)
    all_index = [i for i in range(all_data_arr.shape[1])]
    for d in cat_feat_np:
        all_index.remove(d)
    tmp_data = all_data_arr[:,all_index]
    unk_mask = all_data_arr[:,cur_dim]=='unknown'

    tmp_label = all_data_arr[:,cur_dim][~unk_mask].astype(int)
    tmp_train = tmp_data[~unk_mask]
    tmp_test = tmp_data[unk_mask]
    pred = np.zeros(tmp_test.shape[0])
    mode_num = count_mode(all_data_arr,cur_dim)
    print('mode_num is {}'.format(mode_num))
    pred[:] = mode_num
    all_data_arr[:,cur_dim][unk_mask] = pred[:]


# In[6]:


all_data_arr = all_data_arr.astype(float)


# In[7]:


training_data = all_data_arr[:training_len]
testing_data =all_data_arr[training_len:]

rf = RandomForestClassifier(n_estimators=200 , n_jobs=4 , random_state=386)
rf.fit(training_data , label)
prediction = rf.predict(testing_data)


# In[8]:


with open('sample_output.csv','w') as f:
    f.write('Id,Prediction\n')
    for idex , p in zip(test_idx,prediction):
        f.write('{},{}\n'.format(idex,p))

