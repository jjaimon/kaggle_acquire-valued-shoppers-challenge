# -*- coding: UTF-8 -*-

"""
Kaggle Challenge: 
"http://www.kaggle.com/c/acquire-valued-shoppers-challenge/" 
'Reduce the data and generate features' by Triskelion 
After a forum post by BreakfastPirate
Very mediocre and hacky code, single-purpose, but pretty fast
Some refactoring by Zygmunt Zając <zygmunt@fastml.com>
"""

from datetime import datetime, date
from collections import defaultdict

loc_offers = "data/offers.csv"
loc_transactions = "data/transactions.csv"
loc_train = "data/trainHistory.csv"
loc_test = "data/testHistory.csv"

# will be created
loc_reduced = "data/reduced.csv" 
loc_out_train = "data/train.csv"
loc_out_test = "data/test.csv"

###


def diff_days(s1,s2):
	date_format = "%Y-%m-%d"
	a = datetime.strptime(s1, date_format)
	b = datetime.strptime(s2, date_format)
	delta = b - a
	return delta.days

def generate_features(loc_train, loc_test, loc_transactions, loc_out_train, loc_out_test):
	#keep a dictionary with the offerdata
	offers = {}
	for e, line in enumerate( open(loc_offers) ):
		row = line.strip().split(",")
		offers[ row[0] ] = row

	#keep two dictionaries with the shopper id's from test and train
	train_ids = {}
	test_ids = {}
	for e, line in enumerate( open(loc_train) ):
		if e > 0:
			row = line.strip().split(",")
			train_ids[row[0]] = row
	for e, line in enumerate( open(loc_test) ):
		if e > 0:
			row = line.strip().split(",")
			test_ids[row[0]] = row
	#open two output files
	keys = ["label", "offer_quantity", "offer_value", "total_spend", "has_bought_company", "has_bought_company_a", "has_bought_company_q", "has_bought_company_30", "has_bought_company_a_30", "has_bought_company_q_30", "has_bought_company_60", "has_bought_company_a_60", "has_bought_company_q_60", "has_bought_company_90", "has_bought_company_a_90", "has_bought_company_q_90", "has_bought_company_180", "has_bought_company_a_180", "has_bought_company_q_180", "has_bought_category", "has_bought_category_a", "has_bought_category_q", "has_bought_category_30", "has_bought_category_a_30", "has_bought_category_q_30", "has_bought_category_60", "has_bought_category_a_60", "has_bought_category_q_60", "has_bought_category_90", "has_bought_category_a_90", "has_bought_category_q_90", "has_bought_category_180", "has_bought_category_a_180", "has_bought_category_q_180", "has_bought_brand", "has_bought_brand_a", "has_bought_brand_q", "has_bought_brand_30", "has_bought_brand_a_30", "has_bought_brand_q_30", "has_bought_brand_60", "has_bought_brand_a_60", "has_bought_brand_q_60", "has_bought_brand_90", "has_bought_brand_a_90", "has_bought_brand_q_90", "has_bought_brand_180", "has_bought_brand_a_180", "has_bought_brand_q_180", "never_bought_company", "never_bought_category", "never_bought_brand", "has_bought_brand_company_category", "has_bought_brand_category", "has_bought_brand_company"]
	with open(loc_out_train, "wb") as out_train, open(loc_out_test, "wb") as out_test:
		#iterate through reduced dataset 
		last_id = 0
		features = {key: 0.0 for key in keys}

		# Write the header first
		csvheader = ""
		for k in keys:
			csvheader += k + ", "
			if k == "label":
				csvheader += "id, "
		csvheader = csvheader[:-2] + "\n"	
		out_test.write( csvheader )
		out_train.write( csvheader )

		for e, line in enumerate( open(loc_transactions) ):
			if e > 0: #skip header
				#poor man's csv reader
				row = line.strip().split(",")
				#write away the features when we get to a new shopper id
				if last_id != row[0] and e != 1:
					
					#generate negative features
					if "has_bought_company" not in features:
						features['never_bought_company'] = 1
					
					if "has_bought_category" not in features:
						features['never_bought_category'] = 1
						
					if "has_bought_brand" not in features:
						features['never_bought_brand'] = 1
						
					if "has_bought_brand" in features and "has_bought_category" in features and "has_bought_company" in features:
						features['has_bought_brand_company_category'] = 1
					
					if "has_bought_brand" in features and "has_bought_category" in features:
						features['has_bought_brand_category'] = 1
					
					if "has_bought_brand" in features and "has_bought_company" in features:
						features['has_bought_brand_company'] = 1
					
					outline = ""
					csvline = ""
					test = False
					#for k, v in features.items():
					for k in keys:
						v = features[k]
						
						if k == "label" and v == 0.5:
							#test
							#outline = "1 '" + last_id + " |f" + outline
							csvline = "1, " + last_id + csvline
							test = True
						elif k == "label":
							#outline = str(v) + " '" + last_id + " |f" + outline
							csvline = str(v) + ", " + last_id + csvline
						else:
							#outline += " " + k+":"+str(v) 
							csvline += ", " + ("NA" if v == 0.0 else str(v))
					#outline += "\n"
					csvline += "\n"
					#print "outline: ", outline
					#print "csvline: ", csvline
					if test:
						out_test.write( csvline )
					else:
						out_train.write( csvline )
					#print "Writing features or storing them in an array"
					#reset features
					#features = defaultdict(float)
					features = {key: 0.0 for key in keys}
				#generate features from transaction record
				#check if we have a test sample or train sample
				if row[0] in train_ids or row[0] in test_ids:
					#generate label and history
					if row[0] in train_ids:
						history = train_ids[row[0]]
						if train_ids[row[0]][5] == "t":
							features['label'] = 1
						else:
							features['label'] = 0
					else:
						history = test_ids[row[0]]
						features['label'] = 0.5
						
					#print "label", features['label']
					#print "trainhistory", train_ids[row[0]]
					#print "transaction", row
					#print "offers", offers[ train_ids[row[0]][2] ]
					#print
					
					features['offer_value'] = offers[ history[2] ][4]
					features['offer_quantity'] = offers[ history[2] ][2]
					offervalue = offers[ history[2] ][4]
					
					features['total_spend'] += float( row[10] )
					
					if offers[ history[2] ][3] == row[4]:
						features['has_bought_company'] += 1.0
						features['has_bought_company_q'] += float( row[9] )
						features['has_bought_company_a'] += float( row[10] )
						
						date_diff_days = diff_days(row[6],history[-1])
						if date_diff_days < 30:
							features['has_bought_company_30'] += 1.0
							features['has_bought_company_q_30'] += float( row[9] )
							features['has_bought_company_a_30'] += float( row[10] )
						if date_diff_days < 60:
							features['has_bought_company_60'] += 1.0
							features['has_bought_company_q_60'] += float( row[9] )
							features['has_bought_company_a_60'] += float( row[10] )
						if date_diff_days < 90:
							features['has_bought_company_90'] += 1.0
							features['has_bought_company_q_90'] += float( row[9] )
							features['has_bought_company_a_90'] += float( row[10] )
						if date_diff_days < 180:
							features['has_bought_company_180'] += 1.0
							features['has_bought_company_q_180'] += float( row[9] )
							features['has_bought_company_a_180'] += float( row[10] )
					
					if offers[ history[2] ][1] == row[3]:
						
						features['has_bought_category'] += 1.0
						features['has_bought_category_q'] += float( row[9] )
						features['has_bought_category_a'] += float( row[10] )
						date_diff_days = diff_days(row[6],history[-1])
						if date_diff_days < 30:
							features['has_bought_category_30'] += 1.0
							features['has_bought_category_q_30'] += float( row[9] )
							features['has_bought_category_a_30'] += float( row[10] )
						if date_diff_days < 60:
							features['has_bought_category_60'] += 1.0
							features['has_bought_category_q_60'] += float( row[9] )
							features['has_bought_category_a_60'] += float( row[10] )
						if date_diff_days < 90:
							features['has_bought_category_90'] += 1.0
							features['has_bought_category_q_90'] += float( row[9] )
							features['has_bought_category_a_90'] += float( row[10] )						
						if date_diff_days < 180:
							features['has_bought_category_180'] += 1.0
							features['has_bought_category_q_180'] += float( row[9] )
							features['has_bought_category_a_180'] += float( row[10] )				
					if offers[ history[2] ][5] == row[5]:
						features['has_bought_brand'] += 1.0
						features['has_bought_brand_q'] += float( row[9] )
						features['has_bought_brand_a'] += float( row[10] )
						date_diff_days = diff_days(row[6],history[-1])
						if date_diff_days < 30:
							features['has_bought_brand_30'] += 1.0
							features['has_bought_brand_q_30'] += float( row[9] )
							features['has_bought_brand_a_30'] += float( row[10] )
						if date_diff_days < 60:
							features['has_bought_brand_60'] += 1.0
							features['has_bought_brand_q_60'] += float( row[9] )
							features['has_bought_brand_a_60'] += float( row[10] )
						if date_diff_days < 90:
							features['has_bought_brand_90'] += 1.0
							features['has_bought_brand_q_90'] += float( row[9] )
							features['has_bought_brand_a_90'] += float( row[10] )						
						if date_diff_days < 180:
							features['has_bought_brand_180'] += 1.0
							features['has_bought_brand_q_180'] += float( row[9] )
							features['has_bought_brand_a_180'] += float( row[10] )	
				last_id = row[0]
				if e % 100000 == 0:
					print e
					
#generate_features(loc_train, loc_test, loc_transactions, loc_out_train, loc_out_test)


if __name__ == '__main__':
	generate_features(loc_train, loc_test, loc_reduced, loc_out_train, loc_out_test)

	
	
