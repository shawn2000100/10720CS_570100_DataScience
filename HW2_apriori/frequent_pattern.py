from sys import argv
import re


def create_C1(data_set):
    """
    掃描資料集，建立元素個數為1的項集C1，作為頻繁項集的候選項集C1
    """
    C1 = set()
    for t in data_set:
        for item in t:
            item_set = frozenset([item])
            """
            由於要使用字典（support_data）記錄項集的支援度，需要用項集作為key，
            而可變集合無法作為字典的key，因此在合適時機應將項集轉為固定集合frozenset。
            或者另一種用法：
            for item in t:
                C1.append([item])
            C1.sort()
            return map(frozenset,C1)
            """
            C1.add(item_set)
    return C1


def is_apriori(Ck_item, Lksub1):
    """
            進行剪枝，如果滿足APriori，即滿足支援度，返回True
            否則返回False，刪除
        """
    for item in Ck_item:
        sub_Ck = Ck_item - frozenset([item])
        if sub_Ck not in Lksub1:
            return False
    return True


def create_Ck(Lksub1, k):
    # print('create_c{0} receive {1}'.format(k, Lksub1))
    # print('======================')
    """
    由Lk-1生成Ck
    具體實現方法是在Lk-1中，對所有兩個項集之間只有最後一項item不同的項集的交集
    """
    Ck = set()
    len_Lksub1 = len(Lksub1)
    list_Lksub1 = list(Lksub1)
    # print('listLksub1 = ', Lksub1)
    # print('======================')
    for i in range(len_Lksub1):
        for j in range(1, len_Lksub1):
            l1 = list(list_Lksub1[i])
            l2 = list(list_Lksub1[j])
            l1.sort()
            l2.sort()
            if l1[0:k-2] == l2[0:k-2]:
                Ck_item = list_Lksub1[i] | list_Lksub1[j]           #求並集
                # 剪枝
                if is_apriori(Ck_item, Lksub1):
                    Ck.add(Ck_item)
    return Ck


def generate_Lk_by_Ck(data_set, Ck, min_support, support_data):
    """
        由候選頻繁k項集Ck生成頻繁k項集Lk
        主要內容是對Ck中的每個項集計算支援度，去掉不滿足最低支援度的項集
        返回Lk，記錄support_data
    """
    Lk = set()
    item_count = {}
    for t in data_set:                              #掃描所有商品，計算候選頻繁項集C中項集的支援度，t為訂單
        # print('t = ', t)
        for item in Ck:                             #item為C中的項集
            # print('item = ', item)
            if item.issubset(t):                    #如果C中的項集是t訂單的子集
                if item not in item_count:          #如果item_count中還沒有這個項集，計數為1
                    item_count[item] = 1
                else:                               #如果item_count中已經有了這個項集，計數加1
                    item_count[item] += 1
    t_num = float(len(data_set))                    #t_num，訂單總數
    # print('t_num = ', t_num)
    # print('======================')
    # print('item_count = ', item_count)
    # print('======================')
    for item in item_count:                         #item_count中已經有了所有的候選項集，計算支援度
        # if (item_count[item] / t_num) >= min_support:
        # print('item count = ', item)
        if item_count[item] >= min_support:         # Jay: adjust a little
            Lk.add(item)                            #滿足最小支援度的項集add進頻繁項集Lk中
            support_data[item] = item_count[item]       #記錄支援度，返回Lk
    # print('sup_data = ', support_data)
    # print('======================')
    return Lk


def generate_L(data_set, k, min_support):
    """
        生成頻繁集Lk，通過呼叫generate_Lk_by_Ck
        從C1開始共進行k輪迭代，將每次生成的Lk都append到L中，同時記錄支援度support_data
        """
    support_data = {}
    C1 = create_C1(data_set)            #生成C1
    # print('C1 = ', C1)
    # print('======================')
    L1 = generate_Lk_by_Ck(data_set, C1, min_support, support_data)     #由C1生成L1，呼叫generate_Lk_by_Ck函式
    # print('L1 = ', L1)
    # print('======================')
    Lksub1 = L1.copy()
    L = []
    L.append(Lksub1)
    # print('L = ', L)
    # print('======================')
    # print('------------進入迴圈-------')
    for i in range(2, k+1):                                             #由k已知進行重複迭代
        Ci = create_Ck(Lksub1, i)                                       #由Lk生成Lk+1，呼叫create_Ck函式
        # print('C{0} = {1}'.format(i, Ci))
        # print('======================')
        Li = generate_Lk_by_Ck(data_set, Ci, min_support, support_data)
        # print('L{0} = {1}'.format(i, Li))
        # print('======================')
        Lksub1 = Li.copy()
        L.append(Lksub1)
    # print('------------離開迴圈-------')
    # print('L = ', L)
    # print('Sup = ', support_data)
    # print('======================')
    return L, support_data


def apriori_implement(transactions, max_trans_len, min_sup):
    L, support_data = generate_L(transactions, max_trans_len, min_sup)
    return support_data


# 負責讀進input abstract並作字串前處理
def read_input_and_preprocess(transactions, input_file_name):
    # read stop word list
    with open('stop_words.txt', 'r') as f:
        words = f.readlines()
        stop_words = []  # 用來存所有的stop words
        for word in words:
            stop_words.append(word.strip('\n'))
    # read input abstracts
    with open(input_file_name, 'r') as f:
        abstracts = f.readlines()  # 把一堆摘要讀進來，並塞進list

    # 準備開始剖析所有abstract，先拆成各自的句子，再接著細分出transaction
    max_trans_len = 44  # 預設值，到時候會變大
    for abs in abstracts:  # 到摘要池中依序抓摘要出來，並準備拆分出句子
        abs = re.sub('[\\n]', ' ', abs.lower())
        abs = re.sub('[!@#$%^&*()\\n$:;]+', '', abs)
        # sentences = re.split('[.,?]+', abs)  # 每一篇abstract都拆成sentences了 (依照. , ?拆分) 後來助教說這樣拆會有問題...
        sentences = re.split('(?<![0-9])([\.,?])', abs)
        stop_words.extend(['.', ',', '?'])
        # print(sentences)
        for sentence in sentences:
            word = sentence.strip().split(' ')  # 把一個sentence拆成好幾個words
            # print(word)

            # 上一步將sentence拆成words還不夠，需接著再處理stop word跟空字串
            word_item = []
            for w in word:
                if w not in stop_words and len(w) >= 1:
                    word_item.append(w)
            if len(word_item) >= 1:  # 需做這一檢查是因為有可能word_item = [] (完全沒加進任何東西)
                transactions.append(word_item)
                # print(word_item)
                # print('--------')
                max_trans_len = max(max_trans_len, len(word_item)) # 單筆交易最大的單詞數量

    return max_trans_len, transactions


# 排序Sup結果用的函式
def  sort_pattern(freq_pat):
    new_type_of_freq = []
    for i in freq_pat:
        new_list = []
        keywords = []
        sup_val = freq_pat[i]
        for j in i:
            keywords.append(j)
        keywords.sort() # 順便把裡面排一排
        new_list.append(keywords)
        new_list.append(sup_val)
        new_type_of_freq.append(new_list)

    new_type_of_freq.sort() # 實在想不太到辦法了，只好靠這招來sort外部
    return new_type_of_freq


# 輸出txt檔
def output_file(freq_pat, output_name):
    with open(output_name, 'w') as f:
        for i in freq_pat:
            sup_num = i[1]
            for j in i[0]:
                f.write(str(j) + ' ')
            f.write(str(sup_num))
            f.write('\n')


if __name__ == '__main__':
    # 需在命令列模式執行 e.g., python frequent_pattern.py sample_in.txt out1.txt 10
    if len(argv) == 4:
        input_name = argv[1]
        output_name = argv[2]
        minimum_support_num = int(argv[3])
        max_trans_len = 44
        transactions = []
        max_trans_len, transactions = read_input_and_preprocess(transactions, input_name)
        # print(transactions)
        # print(max_trans_len)
        freq_pat = apriori_implement(transactions, max_trans_len, minimum_support_num)
        # print(freq_pat)
        freq_pat = sort_pattern(freq_pat)
        # print(freq_pat)
        output_file(freq_pat, output_name)

    # 單機測試用，寫得滿亂的
    else:
        transactions = [['deep', 'reinforcement', 'learning', 'enabled', 'control', 'increasingly', 'complex', 'high-dimensional', 'problems'],
            ['however'],
            ['need', 'vast', 'amounts', 'data', 'reasonable', 'performance', 'attained', 'prevents', 'widespread',
             'application'],
            ['employ', 'binary', 'corrective', 'feedback', 'general', 'intuitive', 'manner', 'incorporate', 'human',
             'intuition', 'domain', 'knowledge', 'model-free', 'machine', 'learning'],
            ['uncertainty', 'policy', 'corrective', 'feedback', 'combined', 'directly', 'action', 'space',
             'probabilistic', 'conditional', 'exploration'],
            ['result'],
            ['greatest', 'part', 'otherwise', 'ignorant', 'learning', 'process', 'avoided'],
            ['demonstrate', 'proposed', 'method'],
            ['predictive', 'probabilistic', 'merging', 'policies', 'ppmp'],
            ['combination', 'ddpg'],
            ['experiments', 'continuous', 'control', 'problems', 'openai', 'gym'],
            ['achieve', 'drastic', 'improvements', 'sample', 'efficiency'],
            ['final', 'performance'],
            ['robustness', 'erroneous', 'feedback'],
            ['human', 'synthetic', 'feedback'],
            ['additionally'],
            ['show', 'solutions', 'beyond', 'demonstrated', 'knowledge'],
            ['quantum', 'annealing', 'qa', 'heuristic', 'algorithm', 'finding', 'low-energy', 'configurations',
             'system'],
            ['applications', 'optimization'],
            ['machine', 'learning'],
            ['quantum', 'simulation'],
            ['implementations', 'qa', 'limited', 'qubits', 'coupled', 'via', 'single', 'degree', 'freedom'],
            ['gives', 'rise', 'stoquastic', 'hamiltonian', 'sign', 'problem', 'quantum', 'monte', 'carlo', 'qmc',
             'simulations'],
            ['paper'],
            ['report', 'implementation', 'measurements', 'two', 'superconducting', 'flux', 'qubits', 'coupled', 'via',
             'two', 'canonically', 'conjugate', 'degrees', 'freedom', 'charge', 'flux', 'achieve', 'nonstoquastic',
             'hamiltonian'],
            ['coupling', 'enhance', 'performance', 'qa', 'processors'],
            ['extend', 'range', 'quantum', 'simulations'],
            ['perform', 'microwave', 'spectroscopy', 'extract', 'circuit', 'parameters', 'show', 'charge', 'coupling',
             'manifests', 'yy', 'interaction', 'computational', 'basis'],
            ['observe', 'destructive', 'interference', 'quantum', 'coherent', 'oscillations', 'computational', 'basis',
             'states', 'two-qubit', 'system'],
            ['finally'],
            ['show', 'extracted', 'hamiltonian', 'nonstoquastic', 'wide', 'range', 'parameters'],
            ['multilayer', 'switch', 'networks', 'proposed', 'artificial', 'generators', 'high-dimensional', 'discrete',
             'data', 'e'],
            ['g'],
            ['binary', 'vectors'],
            ['categorical', 'data'],
            ['natural', 'language'],
            ['network', 'log', 'files'],
            ['discrete-valued', 'time', 'series'],
            ['unlike', 'deconvolution', 'networks', 'generate', 'continuous-valued', 'data', 'consist', 'upsampling',
             'filters', 'reverse', 'pooling', 'layers'],
            ['multilayer', 'switch', 'networks', 'composed', 'adaptive', 'switches', 'model', 'conditional',
             'distributions', 'discrete', 'random', 'variables'],
            ['interpretable'],
            ['statistical', 'framework', 'introduced', 'training', 'nonlinear', 'networks', 'based',
             'maximum-likelihood', 'objective', 'function'],
            ['learn', 'network', 'parameters'],
            ['stochastic', 'gradient', 'descent', 'applied', 'objective'],
            ['direct', 'optimization', 'stable', 'convergence'],
            ['involve', 'back-propagation', 'separate', 'encoder', 'decoder', 'networks'],
            ['adversarial', 'training', 'dueling', 'networks'],
            ['training', 'remains', 'tractable', 'moderately', 'sized', 'networks'],
            ['markov-chain', 'monte', 'carlo', 'mcmc', 'approximations', 'gradients', 'derived', 'deep', 'networks',
             'contain', 'latent', 'variables'],
            ['statistical', 'framework', 'evaluated', 'synthetic', 'data'],
            ['high-dimensional', 'binary', 'data', 'handwritten', 'digits'],
            ['web-crawled', 'natural', 'language', 'data'],
            ['aspects', "model's", 'framework', 'interpretability'],
            ['computational', 'complexity'],
            ['generalization', 'ability', 'discussed'],
            ['introduce', 'tucker', 'tensor', 'layer', 'ttl'],
            ['alternative', 'dense', 'weight-matrices', 'fully', 'connected', 'layers', 'feed-forward', 'neural',
             'networks', 'nns'],
            ['answer', 'long', 'standing', 'quest', 'compress', 'nns', 'improve', 'interpretability'],
            ['achieved', 'treating', 'weight-matrices', 'unfolding', 'higher', 'order', 'weight-tensor'],
            ['enables', 'us', 'introduce', 'framework', 'exploiting', 'multi-way', 'nature', 'weight-tensor', 'order',
             'efficiently', 'reduce', 'number', 'parameters'],
            ['virtue', 'compression', 'properties', 'tensor', 'decompositions'],
            ['tucker', 'decomposition', 'tkd', 'employed', 'decompose', 'weight-tensor', 'core', 'tensor', 'factor',
             'matrices'],
            ['re-derive', 'back-propagation', 'within', 'framework'],
            ['extending', 'notion', 'matrix', 'derivatives', 'tensors'],
            ['way'],
            ['physical', 'interpretability', 'tkd', 'exploited', 'gain', 'insights', 'training'],
            ['process', 'computing', 'gradients', 'respect', 'factor', 'matrix'],
            ['proposed', 'framework', 'validated', 'synthetic', 'data', 'fashion-mnist', 'dataset'],
            ['emphasizing', 'relative', 'importance', 'various', 'data', 'features', 'training'],
            ['hence', 'mitigating', '"black-box"', 'issue', 'inherent', 'nns'],
            ['experiments', 'mnist', 'fashion-mnist', 'illustrate', 'compression', 'properties', 'ttl'],
            ['achieving', '66'],
            ['63', 'fold', 'compression', 'whilst', 'maintaining', 'comparable', 'performance', 'uncompressed', 'nn'],
            ['ensuring', 'program', 'operates', 'correctly', 'difficult', 'task', 'large'],
            ['complex', 'systems'],
            ['enshrining', 'invariants', '--', 'desired', 'properties', 'correct', 'execution', '--', 'code',
             'comments', 'support', 'maintainability', 'help', 'sustain', 'correctness'],
            ['tools', 'automatically', 'infer', 'recommend', 'invariants', 'thus', 'beneficial'],
            ['however'],
            ['current', 'invariant-suggesting', 'tools'],
            ['daikon'],
            ['suffer', 'high', 'rates', 'false', 'positives'],
            ['part', 'leverage', 'traced', 'program', 'values', 'available', 'test', 'cases'],
            ['rather', 'directly', 'exploiting', 'knowledge', 'source', 'code', 'per', 'se'],
            ['propose', 'machine-learning', 'approach', 'judging', 'validity', 'invariants'],
            ['specifically', 'method', 'pre-', 'post-conditions'],
            ['based', 'directly', "method's", 'source', 'code'],
            ['introduce', 'new'],
            ['scalable', 'approach', 'creating', 'labeled', 'invariants', 'using', 'programs', 'large', 'test-suites'],
            ['generate', 'daikon', 'invariants', 'using', 'traces', 'subsets', 'test-suites'],
            ['label', 'valid/invalid', 'cross-validating', 'held-out', 'tests'],
            ['process', 'induces', 'large', 'set', 'labels', 'provide', 'form', 'noisy', 'supervision'],
            ['used', 'train', 'deep', 'neural', 'model'],
            ['based', 'gated', 'graph', 'neural', 'networks'],
            ['model', 'learns', 'map', 'lexical'],
            ['syntactic'],
            ['semantic', 'structure', 'given', "method's", 'body', 'probability', 'candidate', 'pre-', 'post-condition',
             "method's", 'body', 'correct', 'able', 'accurately', 'label', 'invariants', 'based', 'noisy', 'signal'],
            ['even', 'cross-project', 'settings'],
            ['importantly'],
            ['performs', 'well', 'hand-curated', 'dataset', 'invariants'],
            ['catastrophic', 'forgetting/interference', 'critical', 'problem', 'lifelong', 'learning', 'machines'],
            ['impedes', 'agents', 'maintaining', 'previously', 'learned', 'knowledge', 'learning', 'new', 'tasks'],
            ['neural', 'networks'],
            ['particular'],
            ['suffer', 'plenty', 'catastrophic', 'forgetting', 'phenomenon'],
            ['recently', 'several', 'efforts', 'towards', 'overcoming', 'catastrophic', 'forgetting', 'neural',
             'networks'],
            ['propose', 'biologically', 'inspired', 'method', 'toward', 'overcoming', 'catastrophic', 'forgetting'],
            ['specifically'],
            ['define', 'attention-based', 'selective', 'plasticity', 'synapses', 'based', 'cholinergic',
             'neuromodulatory', 'system', 'brain'],
            ['define', 'synaptic', 'importance', 'parameters', 'addition', 'synaptic', 'weights', 'use', 'hebbian',
             'learning', 'parallel', 'backpropagation', 'algorithm', 'learn', 'synaptic', 'importances', 'online',
             'seamless', 'manner'],
            ['test', 'proposed', 'method', 'benchmark', 'tasks', 'including', 'permuted', 'mnist', 'split', 'mnist',
             'problems', 'show', 'competitive', 'performance', 'compared', 'state-of-the-art', 'methods'],
            ['well-known', 'gumbel-max', 'trick', 'sampling', 'categorical', 'distribution', 'extended', 'sample', 'k',
             'elements', 'without', 'replacement'],
            ['show', 'implicitly', 'apply', "'gumbel-top-k'", 'trick', 'factorized', 'distribution', 'sequences'],
            ['allowing', 'draw', 'exact', 'samples', 'without', 'replacement', 'using', 'stochastic', 'beam', 'search'],
            ['even', 'exponentially', 'large', 'domains'],
            ['number', 'model', 'evaluations', 'grows', 'linear', 'k', 'maximum', 'sampled', 'sequence', 'length'],
            ['algorithm', 'creates', 'theoretical', 'connection', 'sampling', 'deterministic', 'beam', 'search', 'used',
             'principled', 'intermediate', 'alternative'],
            ['translation', 'task'],
            ['proposed', 'method', 'compares', 'favourably', 'alternatives', 'obtain', 'diverse', 'yet', 'good',
             'quality', 'translations'],
            ['show', 'sequences', 'sampled', 'without', 'replacement', 'used', 'construct', 'low-variance',
             'estimators', 'expected', 'sentence-level', 'bleu', 'score', 'model', 'entropy'],
            ['generative', 'adversarial', 'network', 'gan', 'widely', 'used', 'image', 'synthesis', 'via', 'generative',
             'modelling', 'suffers', 'peculiarly', 'training', 'instability'],
            ['one', 'known', 'reasons', 'instability', 'passage', 'uninformative', 'gradients', 'discriminator',
             'generator', 'due', 'learning', 'imbalance', 'training'],
            ['work'],
            ['propose', 'multi-scale', 'gradients', 'generative', 'adversarial', 'network', 'msg-gan'],
            ['simplistic', 'effective', 'technique', 'addressing', 'problem', 'allowing', 'flow', 'gradients',
             'discriminator', 'generator', 'multiple', 'scales'],
            ['results', 'generator', 'acquiring', 'ability', 'synthesize', 'synchronized', 'images', 'multiple',
             'resolutions', 'simultaneously'],
            ['highlight', 'suite', 'techniques', 'together', 'buttress', 'stability', 'training', 'without',
             'excessive', 'hyperparameter', 'tuning'],
            ['msg-gan', 'technique', 'generic', 'mathematical', 'framework', 'multiple', 'instantiations'],
            ['present', 'intuitive', 'form', 'technique', 'uses', 'concatenation', 'operation', 'discriminator',
             'computations', 'empirically', 'validate', 'experiments', 'celeba-hq'],
            ['cifar10', 'oxford102', 'flowers', 'datasets', 'comparing', 'current', 'state-of-the-art', 'techniques'],
            ['assistive', 'robots', 'virtual', 'agents', 'achieve', 'ubiquity'],
            ['machines', 'need', 'anticipate', 'needs', 'human', 'counterparts'],
            ['field', 'learning', 'demonstration', 'lfd', 'sought', 'enable', 'machines', 'infer', 'predictive',
             'models', 'human', 'behavior', 'autonomous', 'robot', 'control'],
            ['however'],
            ['humans', 'exhibit', 'heterogeneity', 'decision-making'],
            ['traditional', 'lfd', 'approaches', 'fail', 'capture'],
            ['overcome', 'challenge'],
            ['propose', 'bayesian', 'lfd', 'framework', 'infer', 'integrated', 'representation', 'human', 'task',
             'demonstrators', 'inferring', 'human-specific', 'embeddings'],
            ['thereby', 'distilling', 'unique', 'characteristics'],
            ['validate', 'approach', 'able', 'outperform', 'state-of-the-art', 'techniques', 'synthetic', 'real-world',
             'data', 'sets'],
            ['paper'],
            ['introduce', 'machine', 'learning', 'approaches', 'used', 'prioritize', 'outpatients', 'op', 'according',
             'current', 'health', 'state'],
            ['resulting', 'self-optimizing', 'heterogeneous', 'networks', 'hetnet', 'intelligently', 'adapt',
             'according', "users'", 'needs'],
            ['use', 'naïve', 'bayesian', 'classifier', 'analyze', 'data', 'acquired', "ops'", 'medical', 'records'],
            ['alongside', 'data', 'medical', 'internet', 'things', 'iot', 'sensors', 'provide', 'current', 'state',
             'op'],
            ['use', 'machine', 'learning', 'algorithm', 'calculate', 'likelihood', 'life-threatening', 'medical',
             'condition'],
            ['case', 'imminent', 'stroke']]
        input_name = 'sample_in.txt'  # 單機預設值
        output_name = 'out1_test.txt'      # 單機預設值
        max_trans_len = 44            # 單機預設值
        minimum_support_num = 4  # 單機預設值
        # max_trans_len, transactions = read_input_and_preprocess(transactions, input_name)
        # print(transactions)
        # print(max_trans_len)
        freq_pat = apriori_implement(transactions, max_trans_len, minimum_support_num)
        print(freq_pat)
        freq_pat = sort_pattern(freq_pat)
        print(freq_pat)
        output_file(freq_pat, output_name)
