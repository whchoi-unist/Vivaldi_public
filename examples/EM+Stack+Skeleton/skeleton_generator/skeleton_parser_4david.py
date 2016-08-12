import numpy
import math, sys

exception = [ ]

data_array = []
def reorganizing(data):
	result_buffer = []
	for elem in sequence:
		target_data = []
		local_result_buffer = []
		for elem1 in data:
			tag = elem1[0]
			if tag == elem:
				target_data.append(elem1)

		target_data = numpy.array(target_data)
		if len(target_data) == 0:
			continue

		starting_list = []
		parents_set = target_data[:, 1]
		name_set = target_data[:, 2]

		
		for elem1 in parents_set:
			if elem1 not in name_set:
				starting_list.append(elem1)

		key = None
		for elem1 in starting_list:
			target = numpy.where(parents_set == elem1)[0]
			if len(target) == 0:
				continue
			key = target_data[target][0][2]

			while key in parents_set:
				target = numpy.where(name_set == key)[0]
				local_result_buffer.append(list(target_data[target][0]))

				target = target_data[target][0][2]
	
				target = numpy.where(parents_set == target)
				if len(target) == 0:
					break
				key = target_data[target][0][2]

		for elem1 in local_result_buffer:
			result_buffer.append(elem1)

	return result_buffer		

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

mapping_dict = {}



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "USAGE : python %s target_skeleton_file output_prefix"%sys.argv[0]
		exit(0)
	else:
		lines = open('new_points_0224.txt').readlines()
		target_skeleton = open(sys.argv[1]).readlines()
		sequence = [int(elem.split(' ')[0]) for elem in target_skeleton]
		colors   = [(elem.split(' ')[1][:-1]) for elem in target_skeleton]
		out_file     = open(sys.argv[2]+'_coord',"w")
		out_tag_file = open(sys.argv[2]+'_tag',"w")
		out_color    = open(sys.argv[2]+'_color',"w")

	colors = map(lambda x:hex_to_rgb(x), colors)
	for elem in colors:
		out_color.write(str(elem)[1:-1].replace(',','')+'\n')

	prev = [-999, -999, -999]
	prev_tag = -1
	Prev_Tag = -1
	tag_list = []
	count = 0
	local_cnt = -1
	tag_cnt = -1
	curr_cnt = 0
	start_cnt = 0
	change_flag = False
	

	alt_list = {}
	alt_file = open("cnt_list.txt", "r")
	aa = alt_file.readlines()
	for elem in aa:
		bb = elem.split(' ')
		alt_list[int(bb[0])]=int(bb[1])

	new_lines = []
	for elem in lines:
		vals = elem.split(" ")
		vals = [int(float(val)) for val in vals]
		new_lines.append(vals)

	lines = reorganizing(new_lines)
		
	elem = [0, 0, 0]
	for elem1 in lines:
		# Skeleton current_id parent_id x y z
		Tag, tmp_tag, tag, elem[0], elem[1], elem[2] = elem1

		elem[0] = elem[0]  /10
		elem[1] = elem[1]  /10

		elem[2] = alt_list[int(elem[2])] /10

		if Prev_Tag != Tag:
			print Tag
			tag_cnt += 1

		if prev_tag != tmp_tag :
			local_cnt += 1
			count = 0
			start_cnt = curr_cnt


		if int(elem[2]) == int(prev[2]) and int(elem[0]) == int(prev[0]) and int(elem[1])==int(prev[1]):
			prev_tag = tag
			continue


		out_file.write("%d %d %d %d\n"%(elem[0],elem[1],elem[2],local_cnt)) 
		out_tag_file.write("%d\n"%tag_cnt)
		count += 1
	
		prev_tag = tag
		aaa = tag
		Prev_Tag = Tag
		prev = list(elem)
		
	out_file.close()

