#A script to scrap match details from html files and export the data to csv and json files



from bs4 import BeautifulSoup		#for web scraping
import re 							#import regular expressions
import csv 							#for writing csv files
import sys 							#for using arguments for this script
import json 						#for writing json files
from datetime import datetime 		#for changing the date format
import os 							#for creating a directory 


#create a directory named files if it does not exist

if not os.path.exists('./files'):
    os.makedirs('./files')

# added to scrape multiple files at a time
#for looping to list of arguments

for arg in sys.argv[1:]:


	match_file = open(arg) 															#open the html file for reading
	matchdata = BeautifulSoup(match_file, 'lxml')

	match_result = str(matchdata.findAll('div', {'class':'innings-requirement'})[0].contents[0])
	match_id=int(matchdata.find('div', {'id':'matchId'})['data-matchid'])
	match_title = re.sub(r' \|.*$','',(matchdata.find('title').string))
	print(match_id, match_result, "check")

	if 'atch tied (' in match_result:
		winner = (re.search('.*\((.+?) won.*', match_result)).group(1)
	elif 'won' in match_result:
		winner = re.search('(.+?) won.*', match_result).group(1)
	elif 'Match tied' in match_result:
		winner = "none"
	else:
		print(match_id, "folder:", os.getcwd(), " Not written", match_title, match_result)
		continue

	team1 = re.sub(r' innings','', matchdata.findAll('table')[0].findAll('th')[1].contents[0].strip())
	team2 = re.sub(r' innings','', matchdata.findAll('table')[2].findAll('th')[1].contents[0].strip())

	if team1 == winner:
		winning_team_order = 'Batting First'
	else:
		winning_team_order = 'Batting second'

	
	
	match_venue =  re.findall(r'.*at (.*), ... ', match_title )[0]
	match_date_string =  re.findall(r'(... [0-9]+. [0-9]+)', match_title )[0]
	match_date = datetime.strptime(match_date_string, '%b %d, %Y').strftime('%Y-%m-%d')
	#match number was not denotes in many files
	#match_no = matchdata.find_all('a', {'class':'headLink'})[1].contents[0]
	ground = re.sub(r',.*$','', (matchdata.find_all('a', {'class':'headLink'})[3].contents[0]))

	max_overs = (re.findall(r'\d+',(matchdata.findAll('span', {'class':'normal'})[0].contents[0])))[0]

	team1 = re.sub(r' innings','', matchdata.findAll('table')[0].findAll('th')[1].contents[0].strip())

	first_innings_batting_table_columns = ['batsman','dismissal']
	#for i in range(2,8):
	#   first_innings_batting_table_columns.append(matchdata.findAll('th')[i].contents[0])
	for i in matchdata.findAll('table')[0].findAll('th')[2:]:
	    first_innings_batting_table_columns.append(i.get_text())

	first_innings_batting_table_columns.extend(('batting_order', 'match_id', 'innings', 'team', 'opposition'))

	# now the first_innings_batting_table_column include 'batsman', 'dismissal', 'R', 'M', 'B', '4s', '6s', 'SR', 
	#'batting_order', 'match_id', 'innings', 'team', 'opposition'

	table1 = matchdata.findAll('table')[0]

	table1_text=[[td.get_text() for td in row.find_all('td')] for row in table1.findAll('tr')]
	table1_text_final = [item[1:] for item in table1_text]

	#for creating data for the first innings batting

	first_innings_batting = []
	for row in table1_text_final[:-2]:
		if len(row)==8:
			i = (len(first_innings_batting)) + 1
			row.extend((i, match_id, 'first', team1, team2))
			row[2]=int(row[2])
			if row[3]=='':
				row[3]=0
			else:
				row[3]=int(row[3])
			row[4]=int(row[4])
			row[5]=int(row[5])
			row[6]=int(row[6])
			if row[7]== '-':
				row[7]='\\N'
			elif row[7]== "":
				row[7]='\\N'
			else:
				row[7]=float(row[7])
			row[9]=int(row[9])
			first_innings_batting.append(row)


	for item in first_innings_batting[0]:
		print(type(item), "batting_1")
	

	first_innings_total_details = table1_text_final[-1]
	first_innings_extras_details = table1_text_final[-2]

	first_innings_total = int(first_innings_total_details[2])

	#number of extras conceded in the first innings
	first_innings_extras = int(first_innings_extras_details[2])



	first_innings_wicket_details = (re.search(r'(\d+ wicket)|(all out)', first_innings_total_details[1])).group(0)

	if first_innings_wicket_details=='all out':
		first_innings_wicket_details='10 wickets'

	#number of wickets fell in the first innings

	first_innings_wickets = int(re.findall('\d+', first_innings_wicket_details)[0])

	first_innings_overs_bowled_details = (re.search(r'(\d+\.?\d* over)', first_innings_total_details[1])).group(0)

	#number of overs bowled in the first innings

	first_innings_overs_bowled = float(re.findall('\d+\.?\d*', first_innings_overs_bowled_details)[0])

	#first_innings_time_in_field_details = (re.search(r'(\d+ min)', first_innings_total_details[1])).group(0)

	#first_innings_time_in_field = int(re.findall('\d+', first_innings_time_in_field_details)[0])

	#scoring rate in the first innings

	first_innings_run_rate = float(re.search(r'(\d+\.?\d+)', first_innings_total_details[3]).group(0))

	first_innings_extras_lb_details = re.search(r'(lb \d+)', first_innings_extras_details[1])

	#number of leg-byes conceded in the first innings

	if first_innings_extras_lb_details is None:
		first_innings_extras_lb = 0
	else:
		first_innings_extras_lb = int(re.findall('\d+', first_innings_extras_lb_details.group(0))[0])

	first_innings_extras_bye_details = (re.search(r'([^ln]b \d+)', first_innings_extras_details[1]))

	#number of byes conceded in the first innings

	if first_innings_extras_bye_details is None:
		first_innings_extras_bye = 0
	else:
		first_innings_extras_bye = int(re.findall('\d+', first_innings_extras_bye_details.group(0))[0])

	first_innings_extras_wide_details = (re.search(r'(w \d+)', first_innings_extras_details[1]))

	#number of wides conceded in the first innings

	if first_innings_extras_wide_details is None:
		first_innings_extras_wide = 0
	else:
		first_innings_extras_wide = int(re.findall('\d+', first_innings_extras_wide_details.group(0))[0])


	first_innings_extras_nb_details = re.search(r'(nb \d+)', first_innings_extras_details[1])

	#number of no-balls conceded in the first innings

	if first_innings_extras_nb_details is None:
		first_innings_extras_nb = 0
	else:
		first_innings_extras_nb = int(re.findall('\d+', first_innings_extras_nb_details.group(0))[0])


	#first_innings_bowling


	first_innings_bowling_table_columns = ['bowler']

	table2 = matchdata.findAll('table')[1]
	for i in matchdata.findAll('table')[1].findAll('th')[2:7]:
		first_innings_bowling_table_columns.append(i.get_text().strip())

	first_innings_bowling_table_columns.extend(('bowling_order', 'match_id', 'innings', 'team', 'opposition'))

	#first innings bowling table's fields will be 'bowler', 'O', 'M', 'R', 'W', 'Econ', 'bowling_order',
	# 'match_id', 'innings', 'team', 'opposition'

	table2_text=[[td.get_text() for td in row.find_all('td')] for row in table2.findAll('tr')]

	#getting only the bowler's name, overs, maidens, runs conceded, wickets and economy rate
	#though the website has columns for number of 4s and sixes conceded with others, they are not present in every 
	#html file. So they were excluded for now

	table2_text_final = [item[1:7] for item in table2_text if len(item)>6]

	#getting the fields fields for first_innings_bowling table

	first_innings_bowling = []
	for row in table2_text_final:
		i = (len(first_innings_bowling)) + 1
		row.extend((i, match_id, 'first', team2, team1))
		row[1]=float(row[1])
		row[2]=int(row[2])
		row[3]=int(row[3])
		row[4]=int(row[4])
		row[5]=float(row[5])
		row[7]=int(row[7])
		first_innings_bowling.append(row)

	for item in first_innings_bowling[0]:
		print(type(item), "bowling_1")

#Second_innings_batting

	second_innings_batting_table_columns = ['batsman', 'dismissal']

	for i in matchdata.findAll('table')[2].findAll('th')[2:]:
	    second_innings_batting_table_columns.append(i.get_text())

	second_innings_batting_table_columns.extend(('batting_order', 'match_id', 'innings', 'team', 'opposition'))

	# now the second_innings_batting_table_column include 'batsman', 'dismissal', 'R', 'M', 'B', '4s', '6s', 'SR', 
	#'batting_order', 'match_id', 'innings', 'team', 'opposition'

	table3 = matchdata.findAll('table')[2]

	table3_text=[[td.get_text() for td in row.find_all('td')] for row in table3.findAll('tr')]
	table3_text_final = [item[1:] for item in table3_text]

	#creating data for the second innings batting
	
	second_innings_batting = []
	for row in table3_text_final[:-2]:
		if len(row)==8:
			i = (len(second_innings_batting)) + 1
			row.extend((i, match_id, 'second', team2, team1))
			row[2]=int(row[2])
			if row[3]=='':
				row[3]=0
			else:
				row[3]=int(row[3])
			row[4]=int(row[4])
			row[5]=int(row[5])
			row[6]=int(row[6])
			if row[7]== '-':
				row[7]='\\N'
			elif row[7]== "":
				row[7]='\\N'
			else:
				row[7]=float(row[7])
			row[9]=int(row[9])
			second_innings_batting.append(row)

	for item in second_innings_batting[0]:
		print(type(item), "batting_2")


	second_innings_total_details = table3_text_final[-1]
	second_innings_extras_details = table3_text_final[-2]

	second_innings_total = int(second_innings_total_details[2])

	#number of extras conceded in the second innings

	second_innings_extras = int(second_innings_extras_details[2])


	second_innings_extras_total = table3_text_final[-2]

	second_innings_wicket_details = (re.search(r'(\d+ wicket)|(all out)', second_innings_total_details[1])).group(0)
	
	#number of wickets fell in the second innings
	
	if second_innings_wicket_details=='all out':
		second_innings_wicket_details='10 wickets'

	second_innings_wickets = int(re.findall('\d+', second_innings_wicket_details)[0])

	second_innings_overs_bowled_details = (re.search(r'(\d+\.?\d* over)', second_innings_total_details[1])).group(0)
	
	#number of overs bowled in the second innings

	second_innings_overs_bowled = float(re.findall('\d+\.?\d*', second_innings_overs_bowled_details)[0])

	#second_innings_time_in_field_details = (re.search(r'(\d+ min)', second_innings_total_details[1])).group(0)

	#second_innings_time_in_field = int(re.findall('\d+', second_innings_time_in_field_details)[0])
	
	#scoring rate in the second innings

	second_innings_run_rate = float(re.search(r'(\d+\.?\d+)', second_innings_total_details[3]).group(0))

	second_innings_extras_lb_details = re.search(r'(lb \d+)', second_innings_extras_details[1])
	
	#number of leg-byes conceded in the second innings

	if second_innings_extras_lb_details is None:
		second_innings_extras_lb = 0
	else:
		second_innings_extras_lb = int(re.findall('\d+', second_innings_extras_lb_details.group(0))[0])

	second_innings_extras_bye_details = (re.search(r'([^ln]b \d+)', second_innings_extras_details[1]))
	
	#number of byes conceded in the second innings

	if second_innings_extras_bye_details is None:
		second_innings_extras_bye = 0
	else:
		second_innings_extras_bye = int(re.findall('\d+', second_innings_extras_bye_details.group(0))[0])

	second_innings_extras_wide_details = (re.search(r'(w \d+)', second_innings_extras_details[1]))
	
	#number of wides conceded in the second innings

	if second_innings_extras_wide_details is None:
		second_innings_extras_wide = 0
	else:
		second_innings_extras_wide = int(re.findall('\d+', second_innings_extras_wide_details.group(0))[0])


	second_innings_extras_nb_details = re.search(r'(nb \d+)', second_innings_extras_details[1])
	
	#number of no-balls conceded in the second innings

	if second_innings_extras_nb_details is None:
		second_innings_extras_nb = 0
	else:
		second_innings_extras_nb = int(re.findall('\d+', second_innings_extras_nb_details.group(0))[0])

	#second_innings_bowling


	second_innings_bowling_table_columns = ['bowler']


	table4 = matchdata.findAll('table')[3]
	for i in matchdata.findAll('table')[3].findAll('th')[2:7]:
		second_innings_bowling_table_columns.append(i.get_text().strip())

	second_innings_bowling_table_columns.extend(('bowling_order', 'match_id', 'innings', 'team', 'opposition'))
	
	#second innings bowling table's fields will be 'bowler', 'O', 'M', 'R', 'W', 'Econ', 'bowling_order',
	# 'match_id', 'innings', 'team', 'opposition'

	table4_text=[[td.get_text() for td in row.find_all('td')] for row in table4.findAll('tr')]

	#getting only the bowler's name, overs, maidens, runs conceded, wickets and economy rate
	#though the website has columns for number of 4s and sixes conceded with others, they are not present in every 
	#html file. So they were excluded for now

	table4_text_final = [item[1:7] for item in table4_text if len(item)>6]
	
	#getting the fields fields for second_innings_bowling table

	second_innings_bowling = []
	for row in table4_text_final:
		i = (len(second_innings_bowling)) + 1
		row.extend((i, match_id, 'second', team1, team2))
		row[1]=float(row[1])
		row[2]=int(row[2])
		row[3]=int(row[3])
		row[4]=int(row[4])
		row[5]=float(row[5])
		row[7]=int(row[7])
		second_innings_bowling.append(row)
	
	for item in second_innings_bowling[0]:
		print(type(item), "bowling_2")

	#Writing_csv

	#writing csv file containing match_details with columns, 'match_id', 'team1', 'team2', 
	#'winner', 'match_venue', 'match_date', 'ground', 'max_overs', 'match_title', 'match_result'
	match_details_columns=['match_id', 'team1', 'team2', 'winner', 'match_venue', 'match_date', 'ground', 'max_overs', 'match_title', 'match_result']
	match_details_values = [match_id, team1, team2, winner, match_venue, match_date, ground, max_overs, match_title, match_result]

	for item in match_details_values:
		print(type(item), "match_details")


	with open('./files/match_details.'+str(match_id)+'.csv', 'w') as csvfile5:
		writer = csv.writer(csvfile5, delimiter=',', lineterminator='\n')
		writer.writerow(match_details_columns)
		writer.writerow(match_details_values)
	
	#writing json file containing match_details 
	with open('./files/match_details.'+str(match_id)+'.json', 'w') as jsonfile:
		field_names=tuple(match_details_columns)
		dict1 = {}
		for i in range(len(field_names)):
			dict1[field_names[i]]=match_details_values[i]
		json.dump(dict1, jsonfile,sort_keys=False, indent=4, separators=(',', ': '))
		jsonfile.write('\n')
	
	#writing csv file containing score details with the columns, 'innings_total', 'innings_extras', 'innings_wickets', 'innings_overs_bowled', 'innings_run_rate', 'innings_extras_lb', 'innings_extras_bye', 'innings_extras_wide', 'innings_extras_nb', innings and 'match_id'
	
	score_details_columns = ['innings_total', 'innings_extras', 'innings_wickets', 'innings_overs_bowled', 'innings_run_rate', 'first_innings_extras_lb', 'first_innings_extras_bye', 'first_innings_extras_wide', 'first_innings_extras_nb','second_innings_total', 'second_innings_extras', 'second_innings_wickets', 'second_innings_overs_bowled', 'second_innings_run_rate', 'second_innings_extras_lb', 'second_innings_extras_bye', 'second_innings_extras_wide', 'second_innings_extras_nb', 'match_id']

	first_innings_score_details_values = [first_innings_total, first_innings_extras, first_innings_wickets, first_innings_overs_bowled, first_innings_run_rate, first_innings_extras_lb, first_innings_extras_bye, first_innings_extras_wide, first_innings_extras_nb, 'first', match_id]

	second_innings_score_details_values = [second_innings_total, second_innings_extras, second_innings_wickets, second_innings_overs_bowled, second_innings_run_rate, second_innings_extras_lb, second_innings_extras_bye, second_innings_extras_wide, second_innings_extras_nb, 'second' match_id]

	for item in score_details_values:
		print(type(item), "score_details")

	with open('./files/score_details.'+str(match_id)+'.csv', 'w') as csvfile5:
		writer = csv.writer(csvfile5, delimiter=',', lineterminator='\n')
		writer.writerow(score_details_columns)
		writer.writerow(first_innings_score_details_values)
		writer.writerow(second_innings_score_details_values)

	#writing json file containing score details

	with open('./files/score_details.'+str(match_id)+'.json', 'w') as jsonfile:
		field_names=tuple(score_details_columns)
		dict1 = {}
		for i in range(len(field_names)):
			dict1[field_names[i]]=score_details_values[i]
		json.dump(dict1, jsonfile,sort_keys=False, indent=4, separators=(',', ': '))
		jsonfile.write('\n')

	#writing csv file containing first innings batting details

	with open('./files/first_innings_batting.'+str(match_id)+'.csv', 'w') as csvfile1:
		writer = csv.writer(csvfile1, delimiter=',', lineterminator='\n')
		writer.writerow(first_innings_batting_table_columns)
		for batsman in first_innings_batting:
			writer.writerow(batsman)
	
	#writing json file containing first innings batting details

	with open('./files/first_innings_batting.'+str(match_id)+'.json', 'w') as jsonfile:
		field_names=tuple(first_innings_batting_table_columns)
		for row in first_innings_batting:
			dict1 = {}
			for i in range(len(field_names)):
				dict1[field_names[i]]=row[i]
			#writer.writerow(dict1)
			json.dump(dict1, jsonfile,sort_keys=False, indent=4, separators=(',', ': '))
			jsonfile.write('\n')
	
	#writing csv file containing first innings bowling details

	with open('./files/first_innings_bowling.'+str(match_id)+'.csv', 'w') as csvfile2:
		writer = csv.writer(csvfile2, delimiter=',', lineterminator='\n')
		writer.writerow(first_innings_bowling_table_columns)
		for bowler in first_innings_bowling:
			writer.writerow(bowler)

	#writing json file containing first innings bowling details

	with open(('./files/first_innings_bowling.'+str(match_id)+'.json'), 'w') as jsonfile:
		field_names=tuple(first_innings_bowling_table_columns)
		for row in first_innings_bowling:
			dict1 = {}
			for i in range(len(field_names)):
				dict1[field_names[i]]=row[i]
			json.dump(dict1, jsonfile,sort_keys=False, indent=4, separators=(',', ': '))
			jsonfile.write('\n')
	
	#writing csv file containing second innings batting details

	with open('./files/second_innings_batting.'+str(match_id)+'.csv', 'w') as csvfile3:
		writer = csv.writer(csvfile3, delimiter=',', lineterminator='\n')
		writer.writerow(second_innings_batting_table_columns)
		for batsman in second_innings_batting:
			writer.writerow(batsman)

	#writing json file containing second innings batting details

	with open('./files/second_innings_batting.'+str(match_id)+'.json', 'w') as jsonfile:
		field_names=tuple(second_innings_batting_table_columns)
		for row in second_innings_batting:
			dict1 = {}
			for i in range(len(field_names)):
				dict1[field_names[i]]=row[i]
			json.dump(dict1, jsonfile,sort_keys=False, indent=4, separators=(',', ': '))
			jsonfile.write('\n')
	
	#writing csv file containing second innings bowling details

	with open('./files/second_innings_bowling.'+str(match_id)+'.csv', 'w') as csvfile4:
		writer = csv.writer(csvfile4, delimiter=',', lineterminator='\n')
		writer.writerow(second_innings_bowling_table_columns)
		for bowler in second_innings_bowling:
			writer.writerow(bowler)

	#writing json file containing second innings bowling details

	with open('./files/second_innings_bowling.'+str(match_id)+'.json', 'w') as jsonfile:
		field_names=tuple(second_innings_bowling_table_columns)
		for row in second_innings_bowling:
			dict1 = {}
			for i in range(len(field_names)):
				dict1[field_names[i]]=row[i]
			json.dump(dict1, jsonfile,sort_keys=False, indent=4, separators=(',', ': '))
			jsonfile.write('\n')

	print("success, written ", match_id, "folder:", os.getcwd(), match_title, match_result)
