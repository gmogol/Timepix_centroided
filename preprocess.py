import numpy as np
from os.path import isfile

def get_cols(file_name,tot_lines = -1): 
    #we want to iterate over trig id's so we extract them first
    with open(file_name,'r') as rfile:
        ids = []
        first_line = True
        line_counter = 0
        for line in rfile:
            if first_line:
                first_line = False
                continue
            if line_counter == tot_lines:
                break
            line_counter +=1
            line_list = line.split(',')
            ids.append(int(line_list[0]))
        print('Extracted Trigger IDs')
        return ids

def preprocess(rfile_name,wfile_name,tdc2_filename,**kwargs):
    """
    Args:
    rfile_name : string
            the file to read
    wfile_name : string
	    the file to write
    tdc2_filename : string
            the file that contains tdc2 data
    Kwargs:
    tot_lines : int
            total number of lines to read
    unphysical_threshold : float
            rejecting events that come later than this threshold [ns]
    
    Returns:
	None
    """
    write_check = input(f'This will write over {wfile_name}! Continue? y/n')
    if write_check =='n':
        print('Aborted')
        return None
    
    TOT_NUM_LINES = kwargs.get('tot_lines',-1)
    unphysical_threshold = kwargs.get('unphysical_threshold',5e3)   # in [ns]
    trig_id_filename = rfile_name[:-4]+'_trig_id.csv'
    
 
            
            
    if not isfile(trig_id_filename):
        trig_id_list = get_cols(rfile_name)
        np.array(trig_id_list).tofile(trig_id_filename,sep=',')
    else:
        trig_id_list = list(np.loadtxt(trig_id_filename,delimiter=','))
        
    

    num_lines = 0    #counter of lines
    num_batches = 0   #counter of laser hits
    bit_to_ns = 6.1e-3   #conversion from bits to nanoseconds

    trig_id_iter = iter(trig_id_list)
    trig_id = -1
    trig_id_next = next(trig_id_iter)

    tdc2_list = list(np.loadtxt(tdc2_filename))
    tdc2_iter = iter(tdc2_list)
    tdc2 = next(tdc2_iter)
    tdc2_next = next(tdc2_iter)

    many_electron_counter = 0   
    many_electron = False
    unphysical_counter = 0

    counters_list = ['num_lines','num_batches','many_electron_counter','unphysical_counter']

    with open(wfile_name,'w') as wfile:
        wfile.write('')



    with open(rfile_name,'r') as rfile:
        with open(wfile_name,'w') as wfile:
            try:   #see except for the reason of this try
                for line in rfile:
                    
                    if num_lines == TOT_NUM_LINES:
                        for counter in counters_list:
                            print(f'{counter}: {eval(counter):_}')
                        break
                        
                    if num_lines % 100_000 == 0:
                        print(f'Line {num_lines:_} read.')
                        
                    if num_lines == 0:    # extract the header
                        header = line
                        num_lines += 1
                        header_list = header.split(',')
                        


                        for i in range(len(header_list)): # get rid of pound sign in the header cols
                            col = header_list[i]
                            if col[0] == '#':
                                col = col[1:]
                            header_list[i] = col
                        
                        header = ','.join(header_list)
                        header = header[:-1] + 'delta_t' + header[-1]
                        wfile.write(header)
                        continue
                        
                    num_lines += 1
                    trig_id = trig_id_next
                    trig_id_next = next(trig_id_iter)
                    


                    if trig_id == trig_id_next:  #if trig_ids are the same then we have many electron event

                        many_electron = True
                        continue
                    if many_electron:   #this takes care of the 'last' electron of the many electron event
                                        #otherwise you include the last one as if it's a single electron
                        many_electron = False
                        many_electron_counter += 1
                        num_batches += 1
                        continue
                        
                    num_batches += 1
                    line_list = line.split(',')
                    tdc1 = float(line_list[1])  #finally get tdc1 info

                    while abs(tdc1-tdc2) >= abs(tdc1-tdc2_next):
                        # we find the optimal tdc2 by minimizing tdc1-tdc2 difference
                        # i.e. choosing the next tdc2 would increase the difference
                        tdc2 = tdc2_next
                        tdc2_next = next(tdc2_iter)
                    if tdc1> tdc2:  # physically tdc1 (laser) needs to be before tdc2 (phospor screen)
                        continue
                    if (tdc2-tdc1)*bit_to_ns > unphysical_threshold:
                        # we reject events that come too late. usually physical events are around 4us
                        # and certainly <5us
                        unphysical_counter +=1 
                        continue
                    delta_t = (tdc2-tdc1)*bit_to_ns
                    line = line[:-1] + str(delta_t) + line[-1]
                    wfile.write(line)
                    
                    #### After Everything is Done ####
            except StopIteration:
                # the loop ends because we run out of tdc2's this exception captures it
                with open(rfile_name[:-4] + '_notes','w') as notes_file:
                    for counter in counters_list:
                        print(f'{counter}: {eval(counter):_}')
                        notes_file.write(f'{counter}: {eval(counter):_} \n')
                    


preprocess(folder_name + 'data_5real30mins_080V060V_000000_cent.csv',
          'test.csv',
          folder_name + 'data_5real30mins_080V060V_000000_TDC2.csv')







    
        
