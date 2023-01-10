# The tagger.py starter code for CSC384 A4.
# Currently reads in the names of the training files, test file and output file,
# and calls the tagger (which you need to implement)
import os
import sys

def tag(training_list, test_file, output_file):
    # Tag the words from the untagged input file and write them into the output file.
    # Doesn't do much else beyond that yet.
    print("Tagging the file.")
    #
    # YOUR IMPLEMENTATION GOES HERE
    #
    # import time
    
    # start = time.time()
    
    t_dict = None
    for file in training_list:
        training_file = open(file)
        data = training_file.read()
        if t_dict == None:
            t_dict = dict([item.split(" ").pop(0),item.split(" ").pop(-1)]  for item in data.split("\n"))
            t_all = [[item.split(" ").pop(0),item.split(" ").pop(-1)]  for item in data.split("\n")]
            t_words = [item.split(" ").pop(0)  for item in data.split("\n")]
            t_words_distinct = [x.lower() for x in list(set(t_words))] #TODO
            t_tags = [item.split(" ").pop(-1)  for item in data.split("\n")]
            t_tags_distinct = list(set(t_tags))
            t_tags_distinct.remove("")
        else:
            a_dict = dict([item.split(" ").pop(0),item.split(" ").pop(-1)]  for item in data.split("\n"))
            a_all = [[item.split(" ").pop(0),item.split(" ").pop(-1)]  for item in data.split("\n")]
            a_words = [item.split(" ").pop(0)  for item in data.split("\n")]
            a_words_distinct = [x.lower() for x in list(set(a_words))]
            a_tags = [item.split(" ").pop(-1)  for item in data.split("\n")]
            a_tags_distinct = list(set(a_tags))
            a_tags_distinct.remove("")
            
            t_dict = {**t_dict, **a_dict}
            t_all = t_all + a_all
            t_words = t_words + a_words
            t_words_distinct = t_words_distinct + a_words_distinct
            t_tags = t_tags + a_tags
            t_tags_distinct = t_tags_distinct + a_tags_distinct
        training_file.close()
    
    test_file = open(test_file)
    test_data = test_file.read()
    test_words = [item for item in test_data.split("\n")]
    test_file.close()
    
    
    #######################################################################################
    #HMM
    
    def group_by_count(words_lst, tags_lst, ind_lst):
        result = dict()
        for i in ind_lst:
            word = words_lst[i]
            tag = tags_lst[i]
            if word == '': continue
            elif tag not in result:
                if '-' in tag: #if ambiguity tag, check if the other version is alr present
                    eq_tag = tag.split('-')[1] + '-'+ tag.split('-')[0]
    #                 print(eq_tag)
                    if eq_tag not in result: result[tag] = 1
                    else: result[eq_tag] += 1
                else:
                    result[tag] = 1
            else:
                result[tag] += 1
        return result
    
    all_tag_count = group_by_count(t_words,t_tags,range(len(t_tags)))
    
    # Update ambiguity tags to be uniform: the same as all_tag_count dict
    def ambiguity_update(tags_lst):
        for i in range(len(tags_lst)):
            tag = tags_lst[i]
            if '-' in tag:
                if tag not in all_tag_count.keys():
                    eq_tag = tag.split('-')[1] + '-'+ tag.split('-')[0]
                    tags_lst[i] = eq_tag
        return tags_lst
    
    t_tags = ambiguity_update(t_tags)
    t_tags_distinct = ambiguity_update(t_tags_distinct)
    
    ##############################
    # Probability Table 1: P(S_0)
    # Result: I_prob
    ##############################
    #Find first word of sentences
    def find_first_word_ind(words_lst):
        first_word_ind = [0]
        for i in range(len(words_lst)):
            if words_lst[i] in ['.','?','!']: #does semicolon end a sentence?
        #         print(t_words[i+1])
    #             if words_lst[i+1] != '"':
                    first_word_ind.append(i+1)
    #             else:
    # #             elif words_lst[i+2] != '"':
    #                 first_word_ind.append(i+2) #including "
    #             else:
    #                 first_word_ind.append(i+3)
        return first_word_ind
                
    first_word_ind = find_first_word_ind(t_words)            
    
    
    I_count = group_by_count(t_words,t_tags,first_word_ind)
    
    I = dict()
    for tag in I_count.keys():
        I[tag] = I_count[tag]/len(first_word_ind) #total_first_words
    
    # print(I_count)
    # print(I_prob)
    
    ##############################################################################
    # Probability Table 2: T[i,i'] P(S_t|S_t-1) P(S_t|not S_t-1)
    # Probability of transitioning tag i at time t to hidden state i' at time t+1
    # Result: T_prob
    ##############################################################################
    
    # this tag and next tag
    T_count = dict()
    T = dict()
    for i in range(len(t_tags)):
        word = t_words[i]
        if word == '': continue
        transition_str = t_tags[i] + "->" + t_tags[i+1]
        if transition_str not in T_count:
            T_count[transition_str] = 1
            T[transition_str] = 1/all_tag_count[t_tags[i]]
        else:
            T_count[transition_str] += 1
            T[transition_str] += 1/all_tag_count[t_tags[i]]
    
    # print(T_count)
    # print(T)
    
    ###########################################################################
    # Probability Table 3: M[i,e] P(E_t|S_t) P(E_t|not S_t)
    # Probability of hidden state (tag) i to generate observation (word) e
    # Result = M_prob
    ###########################################################################
    M_count = dict()
    M = dict()
    for i in range(len(t_tags)):
        word = t_words[i].lower()
        tag = t_tags[i]
        if word == '': continue
        word_tag = word + "|" + tag
        if word_tag not in M:
            M_count[word_tag] = 1
            M[word_tag] = 1/all_tag_count[tag]
        else:
            M_count[word_tag] += 1
            M[word_tag] += 1/all_tag_count[tag]
    
    # print(M_count)
    # print(M)
    
    ###########################
    # Viterbi
    ###########################
    
    # all_pos_tags = ['AJ0','AJC','AJS','AT0','AV0','AVP','AVQ','CJC','CJS','CJT','CRD','DPS','DT0','DTQ','EX0','ITJ','NN0','NN1','NN2','NP0','ORD','PNI','PNP','PNQ','PNX','POS','PRF','PRP','PUL','PUN','PUQ','PUR','TO0','UNC','VBB','VBD','VBG','VBI','VBN','VBZ','VDB','VDD','VDG','VDI','VDN','VDZ','VHB','VHD','VHG','VHI','VHN','VHZ','VM0','VVB','VVD','VVG','VVI','VVN','VVZ','XX0','ZZ0']
    add_amb_tags = ['AJ0-AV0', 'AJ0-VVN', 'AJ0-VVD', 'AJ0-NN1', 'AJ0-VVG','AVP-PRP', 'AVQ-CJS', 'CJS-PRP', 'CJT-DT0', 'CRD-PNI','NN1-NP0', 'NN1-VVB', 'NN1-VVG', 'NN2-VVZ', 'VVD-VVN']
    
    t_tags.append('') #to solve indexerror in heur
    
    # I: initial probabilities. T: transition matrix: tag + "->" + next tag. M: emission matrix: word + "|" + tag
    # E: test words. S: a set of hidden state values - tags.
    def Viterbi(E, S, I, T, M, NP0_list):  
        prob = dict()
        prev = dict()
        #Construct nested dict
        for i in range(len(E)):
            prob[i] = {}
            prev[i] = {}
        # Determine values for time step 0
        for i in range(len(S)):
            word = E[0].lower()
            tag = S[i]
            if word + "|" + tag not in M.keys(): M_val = 0
            else: M_val = M[word + "|" + tag] 
            if tag not in I.keys(): I_val = 0
            else: I_val = I[tag]
            prob[0][tag] = I_val * M_val
            prev[0][tag] = None  
        #If first word never existed,
        if max(prob[0].values()) == 0:
            for i in range(len(S)):
                tag = S[i]
                prob[0][tag] = I_val
                
        # For time steps 1 to length(E)-1, 
        # find each current state's most likely prior state x.
    
        for t in range(1,len(E)): #for each word or timestep
            word = E[t].lower()
            
            #If its a potential name, heuristics
            if word.isalnum() and not word.isdigit() and E[t][0] == E[t][0].upper() and E[t] in NP0_list:
                prob[t]['NP0'] = 1
                prev[t]['NP0'] = max(prob[t-1], key=prob[t-1].get)
                
            #If word is not present in training file, heuristics
            elif word not in t_words_distinct:
            #Find tag with largest prob from previous time step
                tags_before = []
                if t > 1:
                    tags_before.append(max(prob[t-2], key=prob[t-2].get))
                
                tags_before.append(max(prob[t-1], key=prob[t-1].get))
    
                #build a prob dist with words usually after tag_before
                #get sequence index
                seq = [t_tags[i+len(tags_before)+1] for i in range(len(t_tags)) if t_tags[i:i+len(tags_before)] == tags_before] #i+len(tags_before)+1, positions: (i, i+len(tags_before))
                est_prob = {x:seq.count(x)/len(seq) for x in seq}
                
                #If two prev tags don't exist,
                if len(est_prob) == 0:
                    tags_before = tags_before[-1:]
                    # print(tags_before, t_tags[48584], i+len(tags_before)+1, len(t_tags))

                    seq = [t_tags[i+len(tags_before)+1] for i in range(len(t_tags)) if t_tags[i:i+len(tags_before)] == tags_before] #i+len(tags_before)+1, positions: (i, i+len(tags_before))
                    est_prob = {x:seq.count(x)/len(seq) for x in seq}
    
                for poss in est_prob.keys():
                    prob[t][poss] = est_prob[poss]
                    prev[t][poss] = tags_before[-1]
                    

            #Normal Viterbi
            else:
                for i in range(len(S)): #for each possible tag for this word
                    tag = S[i]
                    word_tag = word + "|" + tag
                    if word + "|" + tag not in M.keys(): M_val = 0
                    else: M_val = M[word + "|" + tag] 
    
                    largest_prob = [0,None]
                    inner_prob = dict()
                    # for j in range(len(S)): #for each possible tag from previous word/time step
                    for l in prob[t-1].keys():
                        #x = argmax_x in (prob[t-1,x] * T[x,i] * M[word + "|" + tag)
                        # prev_tag = S[j]
                        prev_tag = l
                        if prev_tag+"->"+tag not in T.keys(): T_val = 0
                        else: T_val = T[prev_tag+"->"+tag]
                        
                        if prev_tag not in prob[t-1].keys(): prob_val = 0
                        else: prob_val = prob[t-1][prev_tag]
    
                        inner_prob[prev_tag] = prob_val * T_val * M_val
                        if largest_prob[0] < prob_val * T_val * M_val: #If this is larger than prev largest
                            largest_prob[0] = prob_val * T_val * M_val
                            largest_prob[1] = prev_tag        
                    if largest_prob[0] > 0:
                        prob[t][tag] = largest_prob[0]
                        prev[t][tag] = largest_prob[1]
                        
                if not prob[t].values(): #if list is empty
                    tags_before = []
                    if t > 1:
                        tags_before.append(max(prob[t-2], key=prob[t-2].get))
                    
                    tags_before.append(max(prob[t-1], key=prob[t-1].get))
    
                    #build a prob dist with words usually after tag_before
                    #get sequence index
                    seq = [t_tags[i+len(tags_before)+1] for i in range(len(t_tags)) if t_tags[i:i+len(tags_before)] == tags_before] #i+len(tags_before)+1, positions: (i, i+len(tags_before))
                    est_prob = {x:seq.count(x)/len(seq) for x in seq}
                    
                    if len(est_prob) == 0:
                        tags_before = tags_before[-1:]
    
                        seq = [t_tags[i+len(tags_before)+1] for i in range(len(t_tags)) if t_tags[i:i+len(tags_before)] == tags_before] #i+len(tags_before)+1, positions: (i, i+len(tags_before))
                        est_prob = {x:seq.count(x)/len(seq) for x in seq}
    
                    for poss in est_prob.keys():
                        prob[t][poss] = est_prob[poss]
                        prev[t][poss] = tags_before[-1]
                        
        return prob, prev
    
    def Backtrack(prob,prev,max_i):
        answer = {}
        this_tag = max(prob[max_i], key=prob[max_i].get)
        answer[max_i] = this_tag
        # print(prev)
        for i in range(max_i,0,-1):
            answer[i-1] = prev[i][this_tag]
            this_tag = prev[i][this_tag]
        return answer
    
    #Split test_words into sentences
    from itertools import islice
    
    test_first_word_ind = find_first_word_ind(test_words)
    sent_lens = [test_first_word_ind[i+1]-test_first_word_ind[i] for i in range(len(test_first_word_ind)-1)]
    
    iter_lst = iter(test_words)
    test_sentence = [list(islice(iter_lst, x)) for x in sent_lens]
        
    NP0_list = set()
    #Test 1 sentence first:
    # prob, prev = Viterbi(test_sentence[2404], t_tags_distinct, I, T, M, NP0_list)
    # tag_results = Backtrack(prob,prev,len(test_sentence[2404])-1)
    
    no = 0
    with open(output_file,'w') as o:
        for sentence in test_sentence:
            print("Running sentence no.", no)
            print(sentence)
            prob, prev = Viterbi(sentence, t_tags_distinct, I, T, M, NP0_list)
            tag_results = Backtrack(prob,prev,len(sentence)-1)
            for i in range(len(sentence)):
                if len(tag_results[i]) > 3:
                    tag = tag_results[i]
                    if tag not in add_amb_tags:
                        tag_results[i] = tag.split('-')[1] + '-'+ tag.split('-')[0]
                o.write(sentence[i] + " : " + tag_results[i])
                o.write('\n')
                if tag_results[i] == 'NP0' and sentence[i][0] == sentence[i][0].upper() and sentence[i].isalnum() and not sentence[i].isdigit():
                    NP0_list.add(sentence[i])
            no+=1
    # print("Runtime: ", time.time()-start)
    # print(NP0_list)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training files> -t <test file> -o <output file>"
    parameters = sys.argv
    training_list = parameters[parameters.index("-d")+1:parameters.index("-t")]
    test_file = parameters[parameters.index("-t")+1]
    output_file = parameters[parameters.index("-o")+1]
    # print("Training files: " + str(training_list))
    # print("Test file: " + test_file)
    # print("Output file: " + output_file)

    # Start the training and tagging operation.
    tag (training_list, test_file, output_file)